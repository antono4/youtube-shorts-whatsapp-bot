"""
WhatsApp Bot Launcher
Run YouTube Shorts generator and send scripts via WhatsApp

Usage:
    python run_bot.py --phone 0895338853706

Requirements:
    - pywhatkit
    - selenium
    - Chrome browser installed
"""

import argparse
import sys
import time
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from whatsapp_bot.whatsapp_bot import YouTubeShortsWhatsAppBot, WhatsAppClient, PYWHATKIT_AVAILABLE, SELENIUM_AVAILABLE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='WhatsApp Bot for YouTube Shorts')
    parser.add_argument('--phone', '-p', default='0895338853706', 
                        help='WhatsApp phone number (default: 0895338853706)')
    parser.add_argument('--niche', '-n', default=None,
                        help='Specific niche to generate (default: random)')
    parser.add_argument('--interval', '-i', type=int, default=0,
                        help='Auto-generate interval in minutes (0 = disabled)')
    parser.add_argument('--test', '-t', action='store_true',
                        help='Send test message only')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List available niches')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎬 YouTube Shorts WhatsApp Bot")
    print("🇮🇩 Indonesian Content Generator")
    print("=" * 60)
    
    # Initialize bot
    bot = YouTubeShortsWhatsAppBot()
    
    # Format phone number
    phone = args.phone
    if not phone.startswith('+'):
        phone = '+62' + phone.lstrip('0')
    
    print(f"\n📱 Target: {phone}")
    
    # List niches
    if args.list:
        print(bot.format_topics_list())
        return
    
    # Initialize WhatsApp client
    wa_client = WhatsAppClient()
    
    if not PYWHATKIT_AVAILABLE:
        logger.error("❌ pywhatkit not installed")
        logger.info("💡 Run: pip install pywhatkit")
        return
    
    print("\n🔗 Connecting to WhatsApp...")
    wa_client.connect_pywhatkit()
    
    # Test mode
    if args.test:
        print("\n📤 Sending test message...")
        test_msg = """
🤖 *WhatsApp Bot Connected!*

Bot YouTube Shorts sudah aktif dan siap menerima perintah:

• Ketik *!help* untuk bantuan
• Ketik *!topics* untuk melihat topik
• Ketik *!generate* untuk generate script baru

_by YouTube Shorts Bot 🇮🇩_
"""
        success = wa_client.send_message(phone, test_msg)
        if success:
            print("✅ Test message sent!")
        else:
            print("❌ Failed to send test message")
        return
    
    # Generate and send script
    print("\n📝 Generating YouTube Shorts script...")
    script = bot.generate_script(args.niche)
    
    print(f"✅ Topic: {script['meta']['topic']}")
    print(f"📌 Title: {script['youtube_metadata']['title']}")
    
    # Format message
    message = bot.format_script_message(script)
    
    print("\n📤 Sending to WhatsApp...")
    success = wa_client.send_message(phone, message)
    
    if success:
        print("✅ Script sent successfully!")
    else:
        print("❌ Failed to send message")
    
    # Auto-generate loop
    if args.interval > 0:
        print(f"\n⏰ Auto-generate enabled: every {args.interval} minutes")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(args.interval * 60)
                
                # Generate new script
                script = bot.generate_script()
                message = bot.format_script_message(script)
                
                # Send
                logger.info(f"Sending: {script['youtube_metadata']['title']}")
                wa_client.send_message(phone, message)
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Bot stopped by user")
    
    # Show commands
    print("\n" + "=" * 60)
    print("💡 Available Commands for WhatsApp:")
    print("=" * 60)
    print(bot.format_help())


if __name__ == "__main__":
    main()
