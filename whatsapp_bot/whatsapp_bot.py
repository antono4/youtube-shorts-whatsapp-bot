"""
WhatsApp Bot for YouTube Shorts Content Delivery
Auto-generates and sends YouTube Shorts scripts via WhatsApp

Requirements:
- pywhatkit: pip install pywhatkit
- selenium: pip install selenium
- Chrome browser installed

Alternative: Use WhatsApp Web API with selenium
"""

import json
import sys
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import required libraries
try:
    import pywhatkit as pw
    PYWHATKIT_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ pywhatkit not installed. Run: pip install pywhatkit")
    PYWHATKIT_AVAILABLE = False
    pw = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ selenium not installed. Run: pip install selenium")
    SELENIUM_AVAILABLE = False


class YouTubeShortsWhatsAppBot:
    """WhatsApp Bot that delivers YouTube Shorts content"""
    
    # Niche topics in Bahasa Indonesia
    NICHES = [
        "Teknologi & Gadget",
        "Tips Kesehatan & Fitness",
        "Keuangan & Investasi",
        "Masakan & Resep",
        "Motivasi & Produktivitas",
        "Gaming",
        "Fashion & Gaya Hidup",
        "Berita & Event Trending"
    ]
    
    # Command prefixes
    COMMANDS = {
        "!help": "Tampilkan semua perintah",
        "!topics": "Daftar semua topik yang tersedia",
        "!generate": "Generate script YouTube Shorts baru",
        "!generate <topik>": "Generate script untuk topik tertentu",
        "!list": "Lihat semua script yang sudah dibuat",
        "!script <nomor>": "Lihat script tertentu dari history",
        "!save": "Simpan script terakhir ke file",
        "!export": "Export semua script ke file JSON",
        "!schedule": "Setup jadwal auto-generate (5 menit)",
        "!stop": "Stop auto-generate schedule",
        "!stats": "Statistik penggunaan bot",
        "!about": "Tentang bot ini"
    }
    
    def __init__(self, session_path: str = "./whatsapp_session", output_dir: str = "whatsapp_bot/scripts"):
        self.session_path = session_path
        self.output_dir = output_dir
        self.scripts = []
        self.schedule_active = False
        self.schedule_task = None
        self.current_niche_index = 0
        # WhatsApp client + default target used by the auto-generate schedule.
        # Configure these (via set_whatsapp_client / the CLI) before !start.
        self.whatsapp_client = None
        self.target_number = None
        self.stats = {
            "total_generated": 0,
            "total_sent": 0,
            "start_time": datetime.now().isoformat()
        }

        # YouTube Shorts Generator (imported from the package root)
        from youtube_shorts_generator import YouTubeShortsGenerator
        self.generator = YouTubeShortsGenerator()

    def set_whatsapp_client(self, client, target_number: Optional[str] = None) -> None:
        """Attach a WhatsApp client and optional default target for `!start`."""
        self.whatsapp_client = client
        if target_number is not None:
            self.target_number = target_number
    
    def format_script_message(self, script: Dict) -> str:
        """Format script untuk dikirim via WhatsApp"""
        meta = script["meta"]
        metadata = script["youtube_metadata"]
        content = script["content"]
        
        # Header
        header = f"""
🎬 *YOUTUBE SHORTS SCRIPT*
━━━━━━━━━━━━━━━━━━

📌 *Topic:* {meta['topic']}
👥 *Target:* {meta['target_audience']}
🏷️ *Keywords:* {', '.join(meta['seo_keywords'][:5])}

━━━━━━━━━━━━━━━━━━

📝 *TITLE:* 
{metadata['title']}

━━━━━━━━━━━━━━━━━━

📋 *DESKRIPSI:* 
{metadata['description'][:200]}...

━━━━━━━━━━━━━━━━━━

⏱️ *SCRIPT ({len(content)} segments):*
"""
        
        # Content segments
        segments = []
        for i, seg in enumerate(content, 1):
            segment_text = f"""
[{seg['timestamp_range']}]
🎙️ VO: {seg['voiceover']}
📹 B-ROLL: {seg['visual_broll']}
📌 TEXT: {seg['text_overlay']}
🔊 SFX: {seg['audio_sfx']}
"""
            segments.append(segment_text)
        
        # Footer
        footer = f"""
━━━━━━━━━━━━━━━━━━

⏰ Generated: {script['timestamp']}

💡 *Tips:* Copy paste script ini ke video editor!
📎 Kirim *!save* untuk menyimpan ke file

_by YouTube Shorts Bot 🇮🇩_
"""
        
        return header + "\n".join(segments) + footer
    
    def format_topics_list(self) -> str:
        """Format daftar topik"""
        header = """
📚 *DAFTAR TOPIK TERSEDIA*
━━━━━━━━━━━━━━━━━━

"""
        topics = []
        for i, niche in enumerate(self.NICHES, 1):
            topics.append(f"{i}. {niche}")
        
        footer = """
━━━━━━━━━━━━━━━━━━

📌 Contoh: *!generate Teknologi & Gadget*
"""
        return header + "\n".join(topics) + footer
    
    def format_help(self) -> str:
        """Format help message"""
        header = """
🤖 *YOUTUBE SHORTS BOT HELP*
━━━━━━━━━━━━━━━━━━

*Perintah yang tersedia:*

"""
        commands = []
        for cmd, desc in self.COMMANDS.items():
            commands.append(f"• {cmd} - {desc}")
        
        footer = """
━━━━━━━━━━━━━━━━━━

💡 Ketik *!generate* untuk mulai!
"""
        return header + "\n".join(commands) + footer
    
    def generate_script(self, niche: Optional[str] = None) -> Dict:
        """Generate YouTube Shorts script"""
        if niche and niche in self.NICHES:
            script = self.generator.generate_script(niche)
        elif niche:
            # Try partial match
            matched = [n for n in self.NICHES if niche.lower() in n.lower()]
            if matched:
                script = self.generator.generate_script(matched[0])
            else:
                return None
        else:
            script = self.generator.generate_script()
        
        self.scripts.append(script)
        self.stats["total_generated"] += 1
        return script
    
    def get_script_by_number(self, number: int) -> Optional[Dict]:
        """Get script by number from history"""
        index = number - 1
        if 0 <= index < len(self.scripts):
            return self.scripts[index]
        return None
    
    def save_last_script(self) -> str:
        """Save last script to file"""
        if not self.scripts:
            return "❌ Belum ada script yang dibuat!"
        
        last_script = self.scripts[-1]
        filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Ensure directory exists
        path = Path(self.output_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(last_script, f, ensure_ascii=False, indent=2)

        return f"✅ Script disimpan ke: {path}"
    
    def export_all_scripts(self) -> str:
        """Export all scripts to JSON file"""
        if not self.scripts:
            return "❌ Belum ada script untuk di-export!"
        
        filename = f"all_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        path = Path(self.output_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "total_scripts": len(self.scripts),
                "scripts": self.scripts
            }, f, ensure_ascii=False, indent=2)

        return f"✅ {len(self.scripts)} script di-export ke: {path}"
    
    def get_stats(self) -> str:
        """Get bot statistics"""
        uptime = datetime.now() - datetime.fromisoformat(self.stats["start_time"])
        
        stats_text = f"""
📊 *BOT STATISTICS*
━━━━━━━━━━━━━━━━━━

🤖 Total Script Generated: {self.stats['total_generated']}
📤 Total Script Sent: {self.stats['total_sent']}
📁 Script in Memory: {len(self.scripts)}
⏰ Uptime: {uptime}

📅 Started: {self.stats['start_time']}
"""
        return stats_text
    
    async def start_schedule(self, whatsapp_client, target_number: str):
        """Start auto-generate schedule every 5 minutes"""
        if self.schedule_active:
            return "⚠️ Schedule sudah aktif!"
        
        self.schedule_active = True
        self.schedule_task = asyncio.create_task(
            self._schedule_loop(whatsapp_client, target_number)
        )
        return "✅ Auto-generate schedule dimulai! (setiap 5 menit)"
    
    async def _schedule_loop(self, whatsapp_client, target_number: str):
        """Internal schedule loop.

        Note: ``WhatsAppClient.send_message`` is synchronous (it hands the
        message to pywhatkit/selenium), so it must NOT be awaited here.
        """
        while self.schedule_active:
            try:
                # Generate script
                script = self.generate_script()
                message = self.format_script_message(script)

                # Send via WhatsApp (synchronous method - do not await)
                ok = whatsapp_client.send_message(target_number, message)
                if ok:
                    self.stats["total_sent"] += 1

                # Wait 5 minutes
                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                print(f"❌ Schedule error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    def stop_schedule(self):
        """Stop auto-generate schedule"""
        if not self.schedule_active:
            return "⚠️ Tidak ada schedule yang aktif!"
        
        self.schedule_active = False
        if self.schedule_task:
            self.schedule_task.cancel()
        return "✅ Auto-generate schedule dihentikan!"
    
    def handle_command(self, command: str) -> str:
        """Handle incoming command"""
        command = command.strip().lower()
        
        # Parse command and arguments
        parts = command.split(" ", 1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else None
        
        # Command handlers
        if cmd == "!help":
            return self.format_help()
        
        elif cmd == "!about":
            return """
🇮🇩 *YOUTUBE SHORTS BOT*
━━━━━━━━━━━━━━━━━━

Bot ini membuat konten YouTube Shorts
dalam Bahasa Indonesia secara otomatis.

✨ Fitur:
• Generate script 8 niche berbeda
• Format siap pakai untuk video
• B-roll, SFX, text overlay
• Auto-generate setiap 5 menit
• WhatsApp delivery

🛠️ Built with Python
📅 Version: 1.0.0

_by OpenHands Agent 🤖_
"""
        
        elif cmd == "!topics":
            return self.format_topics_list()
        
        elif cmd == "!generate":
            if args:
                script = self.generate_script(args)
                if script:
                    return self.format_script_message(script)
                else:
                    return f"❌ Topik '{args}' tidak ditemukan!\n\nKetik *!topics* untuk melihat daftar topik."
            else:
                script = self.generate_script()
                return self.format_script_message(script)
        
        elif cmd == "!list":
            if not self.scripts:
                return "❌ Belum ada script yang dibuat!\n\nKetik *!generate* untuk mulai."
            
            list_text = """
📁 *SCRIPT HISTORY*
━━━━━━━━━━━━━━━━━━
"""
            for i, script in enumerate(self.scripts, 1):
                list_text += f"{i}. [{script['meta']['topic']}] {script['youtube_metadata']['title'][:40]}...\n"
            
            list_text += "\n📌 Ketik *!script <nomor>* untuk lihat detail"
            return list_text
        
        elif cmd == "!script":
            if not args:
                return "❌ Gunakan format: *!script <nomor>*"
            
            try:
                number = int(args)
                script = self.get_script_by_number(number)
                if script:
                    return self.format_script_message(script)
                else:
                    return f"❌ Script #{number} tidak ditemukan!"
            except ValueError:
                return "❌ Nomor tidak valid!"
        
        elif cmd == "!save":
            return self.save_last_script()
        
        elif cmd == "!export":
            return self.export_all_scripts()
        
        elif cmd == "!stats":
            return self.get_stats()
        
        elif cmd == "!schedule":
            return self._schedule_status()

        elif cmd == "!start":
            return self._start_schedule_command()

        elif cmd == "!stop":
            return self.stop_schedule()

        else:
            return f"❌ Perintah '{cmd}' tidak dikenal!\n\nKetik *!help* untuk melihat semua perintah."

    def _schedule_status(self) -> str:
        """Report the current auto-generate schedule state."""
        if not self.whatsapp_client:
            return ("⚠️ Auto-generate belum dikonfigurasi!\n\n"
                    "Pasang WhatsApp client dengan:\n"
                    "`bot.set_whatsapp_client(wa_client, '+628xxxx')`\n"
                    "atau jalankan CLI dengan flag `--target`.")
        if self.schedule_active:
            return "⏳ Auto-generate schedule sedang berjalan! (setiap 5 menit)"
        return f"📅 Auto-generate siap ke: {self.target_number or '?'}\nKetik *!start* untuk mulai."

    def _start_schedule_command(self) -> str:
        """Start the auto-generate schedule if a WhatsApp client is configured."""
        if not self.whatsapp_client:
            return ("❌ WhatsApp client belum dikonfigurasi!\n\n"
                    "Pasang dengan `bot.set_whatsapp_client(wa_client, target)`\n"
                    "atau jalankan CLI dengan flag `--target <nomor>`.")
        if not self.target_number:
            return "❌ Nomor tujuan belum disetel! Gunakan `set_whatsapp_client(client, '+628xxxx')`."

        # Schedule needs a running event loop (start_schedule creates a task).
        try:
            asyncio.get_running_loop()
            loop_running = True
        except RuntimeError:
            loop_running = False

        if loop_running:
            if self.schedule_active:
                return "⚠️ Schedule sudah aktif!"
            self.schedule_active = True
            self.schedule_task = asyncio.ensure_future(
                self._schedule_loop(self.whatsapp_client, self.target_number)
            )
            return "✅ Auto-generate schedule dimulai! (setiap 5 menit)"
        return ("⚠️ Auto-generate membutuhkan event loop berjalan.\n"
                "Gunakan CLI: `python -m whatsapp_bot.whatsapp_bot --schedule --target <nomor>`")


class WhatsAppClient:
    """
    WhatsApp Web Client wrapper using pywhatkit or selenium
    
    Method 1: pywhatkit (simpler, requires Chrome)
    Method 2: Selenium (more control, requires Chrome + webdriver)
    """
    
    def __init__(self, session_path: str = "./whatsapp_session"):
        self.session_path = session_path
        self.driver = None
        self.connected = False
        self.method = None
    
    def connect_pywhatkit(self, phone_number: str = None) -> bool:
        """Connect using pywhatkit - simpler method"""
        if not PYWHATKIT_AVAILABLE:
            logger.error("❌ pywhatkit not installed. Run: pip install pywhatkit")
            return False
        
        self.method = "pywhatkit"
        logger.info("📱 pywhatkit mode ready")
        logger.info("💡 Use send_message() to send WhatsApp messages")
        self.connected = True
        return True
    
    def connect_selenium(self) -> bool:
        """Connect using Selenium - requires Chrome"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ selenium not installed. Run: pip install selenium")
            return False
        
        try:
            logger.info("📱 Initializing Chrome WebDriver...")
            options = webdriver.ChromeOptions()
            options.add_argument("--user-data-dir=./whatsapp_profile")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Run in headless mode (no browser window)
            # options.add_argument("--headless")
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.get("https://web.whatsapp.com/")
            
            self.method = "selenium"
            self.connected = True
            
            logger.info("✅ Chrome WebDriver initialized")
            logger.info("📱 Please scan QR code on WhatsApp Web")
            logger.info("⏳ Waiting for WhatsApp to load...")
            
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def send_message_pywhatkit(self, phone_number: str, message: str, wait_time: int = 15) -> bool:
        """
        Send message using pywhatkit
        
        Args:
            phone_number: WhatsApp number with country code (e.g., +6281234567890)
            message: Message to send
            wait_time: Seconds to wait for WhatsApp to load
        
        Returns:
            bool: True if message sent successfully
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("❌ pywhatkit not installed")
            return False
        
        try:
            logger.info(f"📤 Sending message to {phone_number}...")
            
            # pywhatkit.sendwhatmsg(phone_no, message, time_hour, time_min)
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1  # Send in next minute
            
            if minute >= 60:
                hour = (hour + 1) % 24
                minute = minute % 60
            
            pw.sendwhatmsg(phone_number, message, hour, minute, wait_time=wait_time)
            
            logger.info("✅ Message queued successfully")
            logger.info("⏳ Message will be sent within 1 minute")
            return True
            
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return False
    
    def send_message_selenium(self, phone_number: str, message: str) -> bool:
        """
        Send message using Selenium
        
        Args:
            phone_number: WhatsApp number with country code
            message: Message to send
        
        Returns:
            bool: True if message sent successfully
        """
        if not SELENIUM_AVAILABLE or not self.driver:
            logger.error("❌ Selenium not connected")
            return False
        
        try:
            logger.info(f"📤 Sending message to {phone_number}...")
            
            # Open chat with phone number
            url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(url)
            
            # Wait for chat to load
            time.sleep(10)
            
            # Find message input box
            xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            message_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            
            # Type message
            message_box.send_keys(message)
            
            # Find and click send button
            send_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
            send_button.click()
            
            logger.info(f"✅ Message sent to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return False
    
    def send_message(self, phone_number: str, message: str) -> bool:
        """Send message using available method"""
        if self.method == "pywhatkit":
            return self.send_message_pywhatkit(phone_number, message)
        elif self.method == "selenium":
            return self.send_message_selenium(phone_number, message)
        else:
            logger.error("❌ No WhatsApp method connected")
            logger.info("💡 Run connect_pywhatkit() or connect_selenium() first")
            return False
    
    def send_image_with_caption(self, phone_number: str, image_path: str, caption: str) -> bool:
        """Send image with caption"""
        if not PYWHATKIT_AVAILABLE:
            logger.error("❌ pywhatkit not available for image sending")
            return False
        
        try:
            pw.sendwhats_image(phone_number, image_path, caption)
            logger.info(f"✅ Image sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"❌ Image send failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WhatsApp"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.connected = False
        self.method = None
        logger.info("🔌 Disconnected from WhatsApp")


def _parse_args(argv=None):
    """Parse CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="yts-bot",
        description="YouTube Shorts WhatsApp bot - Indonesian content generator",
    )
    parser.add_argument("--demo", action="store_true",
                        help="Run the formatting self-test and exit")
    parser.add_argument("--generate", action="store_true",
                        help="Generate one script and print it as JSON")
    parser.add_argument("--niche", default=None,
                        help="Niche to generate (default: rotate through all)")
    parser.add_argument("--save", metavar="DIR", default=None,
                        help="Also save the generated script into DIR")
    parser.add_argument("--schedule", action="store_true",
                        help="Start the auto-generate loop (every 5 minutes)")
    parser.add_argument("--target", default=None,
                        help="Target WhatsApp number, with country code (e.g. +628...)")
    parser.add_argument("--method", choices=["pywhatkit", "selenium"], default="pywhatkit",
                        help="WhatsApp send method (default: pywhatkit)")
    return parser.parse_args(argv)


async def run_cli(args) -> None:
    """Drive the bot from parsed CLI arguments."""
    bot = YouTubeShortsWhatsAppBot()

    if args.demo:
        await _demo(bot)
        return

    # Generate (and optionally save) one script.
    if args.generate or args.niche:
        script = bot.generate_script(args.niche)
        print(json.dumps(script, ensure_ascii=False, indent=2))
        if args.save:
            from youtube_shorts_generator import YouTubeShortsGenerator
            path = YouTubeShortsGenerator().save_script(script, output_dir=args.save)
            print(f"✅ Saved to: {path}", file=sys.stderr)

    # Auto-generate schedule every 5 minutes.
    if args.schedule:
        if not args.target:
            print("❌ --schedule membutuhkan --target <nomor>", file=sys.stderr)
            return

        wa_client = WhatsAppClient()
        if args.method == "pywhatkit":
            if not PYWHATKIT_AVAILABLE:
                print("❌ pywhatkit tidak tersedia. Jalankan: pip install pywhatkit", file=sys.stderr)
                return
            wa_client.connect_pywhatkit()
        else:
            if not SELENIUM_AVAILABLE or not wa_client.connect_selenium():
                print("❌ Selenium tidak tersedia / gagal konek.", file=sys.stderr)
                return

        bot.set_whatsapp_client(wa_client, args.target)
        # start_schedule is async and kicks off the background loop — MUST await it,
        # otherwise the coroutine never runs, schedule_active stays False, and the
        # while loop below exits immediately.
        print(await bot.start_schedule(wa_client, args.target))
        try:
            while bot.schedule_active:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print(bot.stop_schedule())


async def _demo(bot) -> None:
    """Print a formatted sample script and exercise a few commands."""
    print("=" * 50)
    print("🎬 YouTube Shorts WhatsApp Bot - demo")
    print("=" * 50)

    script = bot.generate_script()
    print(f"\n✅ Generated: {script['meta']['topic']}")
    print(f"📌 Title: {script['youtube_metadata']['title']}")
    print("\n" + "=" * 50)
    print("PREVIEW (WhatsApp Format):")
    print("=" * 50)
    print(bot.format_script_message(script))

    print("\n" + "=" * 50)
    print("TESTING COMMANDS:")
    print("=" * 50)
    for cmd in ["!help", "!topics", "!stats", "!list", "!schedule"]:
        print(f"\n> {cmd}")
        print(bot.handle_command(cmd))


def cli(argv=None) -> int:
    """Console-script entry point (sync wrapper around the async driver)."""
    args = _parse_args(argv)
    try:
        asyncio.run(run_cli(args))
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
