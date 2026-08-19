"""Tests for the WhatsApp bot command layer. Fully offline (fake client)."""

import asyncio
import json

import pytest

import whatsapp_bot.whatsapp_bot as botmod
from whatsapp_bot.whatsapp_bot import WhatsAppClient, YouTubeShortsWhatsAppBot


def make_bot(**kwargs):
    return YouTubeShortsWhatsAppBot(**kwargs)


# ---------------------------------------------------------------- instantiation


def test_bot_instantiates_from_package_root():
    # Regression: the old sys.path hack made `from youtube_shorts_generator
    # import YouTubeShortsGenerator` fail when cwd was the repo root.
    bot = make_bot()
    assert bot.generator is not None
    assert bot.scripts == []
    assert bot.stats["total_generated"] == 0


def test_output_dir_default():
    assert make_bot().output_dir == "whatsapp_bot/scripts"


# ---------------------------------------------------------------- formatting


def test_format_script_message_contains_key_fields():
    bot = make_bot()
    script = bot.generator.generate_script("Gaming")
    msg = bot.format_script_message(script)
    assert script["meta"]["topic"] in msg
    assert script["youtube_metadata"]["title"] in msg
    assert "YOUTUBE SHORTS SCRIPT" in msg


def test_format_topics_list_lists_all_niches():
    msg = make_bot().format_topics_list()
    for niche in botmod.YouTubeShortsWhatsAppBot.NICHES:
        assert niche in msg


# ---------------------------------------------------------------- commands


def test_help_command():
    out = make_bot().handle_command("!help")
    assert "!generate" in out and "!help" in out


def test_topics_command():
    out = make_bot().handle_command("!topics")
    assert "Teknologi & Gadget" in out


def test_about_command():
    out = make_bot().handle_command("!about")
    assert "YOUTUBE SHORTS BOT" in out


def test_generate_command_adds_script_and_stats():
    bot = make_bot()
    out = bot.handle_command("!generate")
    assert "SCRIPT" in out
    assert bot.stats["total_generated"] == 1
    assert bot.scripts


def test_generate_niche_partial_match():
    bot = make_bot()
    out = bot.handle_command("!generate teknolo")
    assert "SCRIPT" in out
    assert bot.scripts[-1]["meta"]["topic"] == "Teknologi & Gadget"


def test_generate_unknown_niche():
    bot = make_bot()
    out = bot.handle_command("!generate notaniche")
    assert "tidak ditemukan" in out
    assert bot.scripts == []


def test_list_empty_then_after_generate():
    bot = make_bot()
    assert "Belum ada script" in bot.handle_command("!list")
    bot.handle_command("!generate")
    out = bot.handle_command("!list")
    assert "SCRIPT HISTORY" in out and "1." in out


def test_script_by_number():
    bot = make_bot()
    bot.handle_command("!generate")
    out = bot.handle_command("!script 1")
    assert "SCRIPT" in out
    assert "tidak ditemukan" in bot.handle_command("!script 99")


def test_script_invalid_number():
    bot = make_bot()
    assert "Nomor tidak valid" in bot.handle_command("!script abc")


def test_stats_command():
    bot = make_bot()
    out = bot.handle_command("!stats")
    assert "BOT STATISTICS" in out


def test_unknown_command():
    assert "tidak dikenal" in make_bot().handle_command("!wat")


# ---------------------------------------------------------------- save / export


def test_save_last_script_writes_to_output_dir(tmp_path):
    bot = make_bot(output_dir=str(tmp_path))
    bot.handle_command("!generate")
    out = bot.save_last_script()
    assert str(tmp_path) in out
    files = list(tmp_path.glob("script_*.json"))
    assert len(files) == 1
    with open(files[0], encoding="utf-8") as f:
        assert json.load(f)["meta"]["topic"]


def test_save_last_script_empty():
    assert "Belum ada script" in make_bot().save_last_script()


def test_export_all_scripts(tmp_path):
    bot = make_bot(output_dir=str(tmp_path))
    assert "Belum ada script" in bot.export_all_scripts()
    bot.handle_command("!generate")
    bot.handle_command("!generate")
    out = bot.export_all_scripts()
    assert "2 script" in out
    files = list(tmp_path.glob("all_scripts_*.json"))
    assert len(files) == 1
    with open(files[0], encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_scripts"] == 2
    assert len(data["scripts"]) == 2


def test_get_script_by_number_boundaries():
    bot = make_bot()
    bot.handle_command("!generate")
    assert bot.get_script_by_number(1) is not None
    assert bot.get_script_by_number(0) is None
    assert bot.get_script_by_number(2) is None


# ---------------------------------------------------------------- schedule


class FakeClient:
    """Minimal stand-in for WhatsAppClient: send_message is SYNCHRONOUS."""

    def __init__(self):
        self.calls = []

    def send_message(self, phone_number, message):
        self.calls.append((phone_number, message))
        return True


def test_set_whatsapp_client():
    bot = make_bot()
    fc = FakeClient()
    bot.set_whatsapp_client(fc, "+628123")
    assert bot.whatsapp_client is fc
    assert bot.target_number == "+628123"


def test_schedule_guard_when_not_configured():
    bot = make_bot()
    assert "belum dikonfigurasi" in bot.handle_command("!schedule")
    assert "belum dikonfigurasi" in bot.handle_command("!start")


def test_start_command_without_running_loop():
    """!start with a configured client but no running loop returns the CLI hint."""
    bot = make_bot()
    bot.set_whatsapp_client(FakeClient(), "+628123")
    # No event loop is running in this sync test.
    out = bot.handle_command("!start")
    assert "event loop" in out


def test_schedule_loop_calls_sync_send_message():
    """Regression: the loop previously `await`ed the sync send_message, which
    raises TypeError on the first iteration. Now it must call it synchronously
    and increment total_sent without raising."""
    async def run():
        bot = make_bot()
        fc = FakeClient()
        bot.schedule_active = True
        loop_task = asyncio.ensure_future(bot._schedule_loop(fc, "+628123"))
        while not fc.calls:
            await asyncio.sleep(0.02)
        await asyncio.sleep(0.05)
        bot.schedule_active = False
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

        assert fc.calls, "send_message was never called"
        assert fc.calls[0][0] == "+628123"
        assert bot.stats["total_sent"] == 1

    asyncio.run(run())


def test_schedule_loop_survives_send_failure():
    """If the sync send returns False, the loop must not crash and must retry."""
    class FailingClient:
        def send_message(self, phone_number, message):
            return False

    async def run():
        bot = make_bot()
        fc = FailingClient()
        bot.schedule_active = True
        loop_task = asyncio.ensure_future(bot._schedule_loop(fc, "+628123"))
        # Give the loop one full iteration (send + sleep). Use a short sleep by
        # letting it run, then stop after a moment.
        original = asyncio.sleep
        slept = []

        async def short_sleep(s):
            slept.append(s)
            if s >= 300:  # the 5-minute wait ended the first iteration
                bot.schedule_active = False
            await original(0)

        asyncio.sleep = short_sleep
        try:
            await loop_task
        finally:
            asyncio.sleep = original

        assert slept  # loop ran at least one 300s wait
        assert bot.stats["total_sent"] == 0  # failed send not counted

    asyncio.run(run())


def test_stop_schedule_when_inactive():
    assert "Tidak ada schedule" in make_bot().stop_schedule()


def test_duplicate_start_schedule_guard():
    async def run():
        bot = make_bot()
        fc = FakeClient()
        bot.schedule_active = True
        out = await bot.start_schedule(fc, "+628123")
        assert "sudah aktif" in out

    asyncio.run(run())


def test_start_schedule_must_be_awaited_to_activate():
    """Regression for codereviewbot: run_cli called start_schedule without `await`,
    so the coroutine never ran, schedule_active stayed False, and the scheduling
    while-loop exited immediately. Awaiting it must flip schedule_active on."""
    async def run():
        bot = make_bot()
        fc = FakeClient()
        out = await bot.start_schedule(fc, "+628123")
        assert "dimulai" in out
        assert bot.schedule_active is True
        assert bot.schedule_task is not None

    asyncio.run(run())


# ---------------------------------------------------------------- CLI


def test_cli_parse_args_schedule_requires_target(tmp_path, capsys):
    args = botmod._parse_args(["--schedule"])
    # run_cli prints an error to stderr when --schedule lacks --target
    async def run():
        await botmod.run_cli(args)
    asyncio.run(run())
    err = capsys.readouterr().err
    assert "--target" in err


def test_cli_generate_prints_json(capsys):
    args = botmod._parse_args(["--generate", "--niche", "Gaming"])
    asyncio.run(botmod.run_cli(args))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["meta"]["topic"] == "Gaming"


def test_cli_demo_runs(capsys):
    args = botmod._parse_args(["--demo"])
    asyncio.run(botmod.run_cli(args))
    out = capsys.readouterr().out
    assert "PREVIEW (WhatsApp Format)" in out


# ---------------------------------------------------------------- WhatsAppClient


def test_whatsapp_client_send_message_routing():
    client = WhatsAppClient()
    sent = {}
    client.method = "pywhatkit"
    client.send_message_pywhatkit = lambda num, msg: sent.update(num=num, msg=msg) or True
    assert client.send_message("+1", "hi") is True
    assert sent == {"num": "+1", "msg": "hi"}


def test_whatsapp_client_send_no_method():
    client = WhatsAppClient()
    assert client.send_message("+1", "hi") is False
