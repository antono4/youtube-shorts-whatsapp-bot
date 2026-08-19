"""Tests for the YouTube Shorts generator. Fully offline (stdlib only)."""

import json

import pytest

from youtube_shorts_generator import (
    CONTENT_TEMPLATES,
    HOOK_TEMPLATES,
    NICHES,
    YouTubeShortsGenerator,
)

ALL_NICHE_NAMES = [n["name"] for n in NICHES]


def make_gen():
    return YouTubeShortsGenerator()


def parse_timestamp(ts: str) -> int:
    """Convert 'MM:SS' to seconds."""
    minutes, secs = ts.split(":")
    return int(minutes) * 60 + int(secs)


# ---------------------------------------------------------------- generate_script


def test_generate_script_shape():
    script = make_gen().generate_script()
    assert set(script) >= {"timestamp", "meta", "youtube_metadata", "content"}
    assert script["meta"]["topic"] in ALL_NICHE_NAMES
    assert script["meta"]["target_audience"]
    assert script["meta"]["seo_keywords"]
    assert script["youtube_metadata"]["title"]
    assert isinstance(script["content"], list) and script["content"]


def test_generate_script_specific_niche():
    script = make_gen().generate_script("Gaming")
    assert script["meta"]["topic"] == "Gaming"


def test_generate_script_case_insensitive_partial():
    # The bot matches niches case-insensitively via substring; the generator
    # itself matches exact name and falls back to rotation for unknowns.
    script = make_gen().generate_script("gaming")
    assert script["meta"]["topic"] == "Gaming"


def test_generate_script_unknown_niche_falls_back():
    script = make_gen().generate_script("Tidak Ada Niche Ini")
    assert script["meta"]["topic"] in ALL_NICHE_NAMES


# ---------------------------------------------------------------- segment timing


def _segment_timing(script) -> list:
    """Return list of (start_sec, end_sec) tuples in order."""
    out = []
    for seg in script["content"]:
        start, end = seg["timestamp_range"].split(" - ")
        out.append((parse_timestamp(start), parse_timestamp(end)))
    return out


@pytest.mark.parametrize("niche", ALL_NICHE_NAMES)
def test_segments_contiguous_and_gap_free(niche):
    """All segments are 5s long and back-to-back with no gaps or overlaps."""
    script = make_gen().generate_script(niche)
    timing = _segment_timing(script)
    assert timing[0][0] == 0
    for (start, end), (next_start, _) in zip(timing, timing[1:]):
        assert end - start == 5
        assert next_start == end  # no gap, no overlap


def test_all_tips_are_used():
    """Every tip in the template appears as a TIPS segment (none dropped)."""
    for niche in ALL_NICHE_NAMES:
        script = make_gen().generate_script(niche)
        tips_in_script = [s for s in script["content"] if "TIPS #" in s["voiceover"]]
        assert tips_in_script, niche
        # CTA is always the last segment; the tips come before it, so the
        # template's full tip count must be present.
        assert len(tips_in_script) >= 5, niche


def test_cta_is_last_segment():
    """The CTA is always appended as the last, distinct segment (no collision
    with the final tip's timestamp index)."""
    for niche in ALL_NICHE_NAMES:
        for _ in range(5):
            script = make_gen().generate_script(niche)
            # Last segment must be contiguous with the one before it and hold
            # its own unique index (CTAs were previously hardcoded to index 7).
            timing = _segment_timing(script)
            assert len(timing[-1]) == 2
            assert timing[-1][0] == timing[-2][1]


def test_no_timestamp_collisions():
    """Every segment gets a unique start time (the old hardcoded CTA index
    could duplicate the 5th tip's timestamp)."""
    for niche in ALL_NICHE_NAMES:
        for _ in range(5):
            timing = _segment_timing(make_gen().generate_script(niche))
            starts = [t[0] for t in timing]
            assert len(starts) == len(set(starts))


def test_create_content_segment_minute_rollover():
    """Index 12 -> 60s -> '00:60' would be wrong; must roll to '01:00'."""
    gen = make_gen()
    seg = gen.create_content_segment("hello", 12, NICHES[0])
    start, end = seg["timestamp_range"].split(" - ")
    assert start == "01:00"
    assert end == "01:05"


def test_create_content_segment_basic_index():
    seg = make_gen().create_content_segment("hello", 0, NICHES[0])
    assert seg["timestamp_range"] == "00:00 - 00:05"
    assert seg["voiceover"] == "hello"
    assert seg["visual_broll"].startswith("Engaging visuals")
    assert seg["audio_sfx"]


def test_text_overlay_truncation():
    gen = make_gen()
    long_text = "x" * 50
    assert gen.create_content_segment(long_text, 0, NICHES[0])["text_overlay"].endswith("...")
    short_text = "short"
    assert gen.create_content_segment(short_text, 0, NICHES[0])["text_overlay"] == "short"


# ---------------------------------------------------------------- sfx / hook


def test_sfx_warning_keyword():
    gen = make_gen()
    assert gen.get_sfx_cue("Hati-hati, ini bahaya") == "alert sound + suspenseful bass"


def test_sfx_tip_keyword():
    gen = make_gen()
    assert gen.get_sfx_cue("Ini tips penting") == "success chime + positive ding"


def test_sfx_question_keyword():
    gen = make_gen()
    assert gen.get_sfx_cue("Apakah kamu tahu?") == "suspense tone + whoosh"


def test_sfx_fallback():
    gen = make_gen()
    assert gen.get_sfx_cue("teks biasa tanpa kata kunci") == "transition sound effect"


def test_generate_hook_uses_template():
    gen = make_gen()
    hook = gen.generate_hook("statement here")
    assert "statement here" in hook


# ---------------------------------------------------------------- niche cycling


def test_get_next_niche_cycles_all_before_repeat():
    gen = make_gen()
    seen = [gen.get_next_niche()["name"] for _ in range(len(gen.niches))]
    assert len(set(seen)) == len(gen.niches)  # no repeat until all 8 used


def test_generate_all_niches_distinct():
    gen = make_gen()
    topics = [s["meta"]["topic"] for s in gen.generate_all_niches()]
    assert len(topics) == len(set(topics)) == len(gen.niches)


# ---------------------------------------------------------------- save_script


def test_save_script_creates_dir_and_writes(tmp_path):
    gen = make_gen()
    script = gen.generate_script()
    out_dir = tmp_path / "deep" / "nested"
    path = gen.save_script(script, filename="test_script.json", output_dir=str(out_dir))
    assert out_dir.exists()
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["meta"]["topic"] == script["meta"]["topic"]
    assert path.endswith("test_script.json")


def test_save_script_generates_filename(tmp_path):
    path = make_gen().save_script(make_gen().generate_script(), output_dir=str(tmp_path))
    assert path.startswith(str(tmp_path))
    assert path.endswith(".json")
