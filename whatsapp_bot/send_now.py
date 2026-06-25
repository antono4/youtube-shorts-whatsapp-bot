"""
Simple WhatsApp Message Sender
Langsung kirim pesan YouTube Shorts script ke nomor kamu

Usage:
    python send_now.py
    
Requirements:
    - Chrome browser installed
    - pywhatkit
"""

import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pywhatkit as pw
from whatsapp_bot.whatsapp_bot import YouTubeShortsWhatsAppBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_phone(phone: str) -> str:
    """Format nomor HP ke format internasional"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+"):
        return phone
    elif phone.startswith("0"):
        return "+62" + phone[1:]
    elif phone.startswith("62"):
        return "+" + phone
    else:
        return "+" + phone


def send_youtube_shorts_script(phone: str, niche: str = None):
    """
    Generate dan kirim YouTube Shorts script via WhatsApp
    
    Args:
        phone: Nomor WhatsApp tujuan (contoh: 0895338853706)
        niche: Topic niche (opsional, random jika None)
    """
    # Format phone
    phone = format_phone(phone)
    logger.info(f"📱 Target: {phone}")
    
    # Generate script
    logger.info("📝 Generating YouTube Shorts script...")
    bot = YouTubeShortsWhatsAppBot()
    script = bot.generate_script(niche)
    
    logger.info(f"✅ Topic: {script['meta']['topic']}")
    logger.info(f"📌 Title: {script['youtube_metadata']['title']}")
    
    # Format message
    message = bot.format_script_message(script)
    
    logger.info(f"📤 Sending message ({len(message)} chars)...")
    
    # Get current time
    now = time.localtime()
    hour = now.tm_hour
    minute = now.tm_min + 1  # Send dalam 1 menit
    
    if minute >= 60:
        hour = (hour + 1) % 24
        minute = minute % 60
    
    try:
        # Kirim via pywhatkit
        # pywhatkit akan membuka browser dan kirim pesan
        logger.info(f"⏰ Scheduled for {hour:02d}:{minute:02d}")
        logger.info("🌐 Opening WhatsApp Web...")
        
        # Kirim pesan (buka browser, cari kontak, ketik, kirim)
        pw.sendwhatmsg(phone, message, hour, minute, wait_time=15)
        
        logger.info("✅ Message scheduled!")
        logger.info("📱 Cek WhatsApp Web untuk konfirmasi")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("📱 WhatsApp Script Sender")
    print("🎬 YouTube Shorts Generator")
    print("🇮🇩 Bahasa Indonesia")
    print("=" * 60)
    
    # Target phone number
    PHONE = "0895338853706"
    
    print(f"\n📱 Target: {format_phone(PHONE)}")
    print("\n📚 Niche yang tersedia:")
    print("1. Teknologi & Gadget")
    print("2. Tips Kesehatan & Fitness")
    print("3. Keuangan & Investasi")
    print("4. Masakan & Resep")
    print("5. Motivasi & Produktivitas")
    print("6. Gaming")
    print("7. Fashion & Gaya Hidup")
    print("8. Berita & Event Trending")
    print("\nTekan ENTER untuk random, atau ketik nomor niche: ", end="")
    
    choice = input().strip()
    
    niche = None
    niches = [
        "Teknologi & Gadget",
        "Tips Kesehatan & Fitness",
        "Keuangan & Investasi",
        "Masakan & Resep",
        "Motivasi & Produktivitas",
        "Gaming",
        "Fashion & Gaya Hidup",
        "Berita & Event Trending"
    ]
    
    if choice.isdigit() and 1 <= int(choice) <= 8:
        niche = niches[int(choice) - 1]
        print(f"\n📌 Topic: {niche}")
    else:
        print("\n📌 Topic: Random")
    
    print("\n" + "-" * 60)
    
    # Send
    success = send_youtube_shorts_script(PHONE, niche)
    
    if success:
        print("\n✅ Script akan dikirim dalam ~1 menit!")
        print("📱 Pastikan WhatsApp Web terbuka di browser")
    else:
        print("\n❌ Gagal mengirim pesan")


if __name__ == "__main__":
    main()
