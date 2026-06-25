"""
WhatsApp Bot - Desktop Version
Jalankan di komputer kamu untuk kirim pesan ke nomor sendiri

Setup:
1. Install Chrome browser
2. pip install -r requirements.txt
3. python send_to_my_number.py

Bot akan:
1. Buka WhatsApp Web
2. Kirim script YouTube Shorts ke nomor kamu
"""

import sys
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from whatsapp_bot.whatsapp_bot import YouTubeShortsWhatsAppBot

# ============================================
# KONFIGURASI - GANTI NOMOR INI
# ============================================
TARGET_PHONE = "0895338853706"  # Ganti dengan nomor kamu


def format_phone(phone: str) -> str:
    """Format nomor HP ke format WhatsApp"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+"):
        return phone
    elif phone.startswith("0"):
        return "62" + phone[1:]  # Indonesia
    elif phone.startswith("62"):
        return phone
    else:
        return "62" + phone


def send_via_web():
    """
    Kirim pesan via WhatsApp Web
    Requires: Chrome browser + internet
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
    except ImportError:
        logger.error("❌ Selenium belum install")
        logger.info("Run: pip install selenium")
        return False
    
    logger.info("🔗 Opening WhatsApp Web...")
    
    # Setup Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Comment line di bawah jika mau lihat browser
    # options.add_argument("--headless")  
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Generate script
        logger.info("📝 Generating YouTube Shorts script...")
        bot = YouTubeShortsWhatsAppBot()
        script = bot.generate_script()
        
        logger.info(f"✅ Topic: {script['meta']['topic']}")
        logger.info(f"📌 Title: {script['youtube_metadata']['title']}")
        
        # Format message
        message = bot.format_script_message(script)
        
        # Buka WhatsApp Web
        phone_formatted = format_phone(TARGET_PHONE)
        url = f"https://web.whatsapp.com/send?phone={phone_formatted}"
        
        logger.info(f"📱 Opening chat: {TARGET_PHONE}")
        driver.get(url)
        
        # Wait untuk load
        logger.info("⏳ Waiting for WhatsApp Web to load...")
        logger.info("⚠️ JIKA BELUM LOGIN: Scan QR code dulu!")
        logger.info("⏳ Waiting 20 seconds for page to load...")
        time.sleep(20)
        
        # Try to find message input
        try:
            # WhatsApp Web message input
            input_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            
            logger.info("📝 Typing message...")
            message_box = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, input_xpath))
            )
            message_box.send_keys(message)
            time.sleep(1)
            
            # Click send
            logger.info("📤 Sending...")
            send_btn = driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
            send_btn.click()
            
            logger.info("✅ Message sent successfully!")
            time.sleep(3)
            
            return True
            
        except TimeoutException:
            logger.error("❌ Gagal menemukan input pesan")
            logger.info("💡 Pastikan WhatsApp Web sudah loaded dan chat terbuka")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return False
    finally:
        input("\n\nPress ENTER to close browser...")
        driver.quit()


def main():
    print("=" * 60)
    print("📱 WhatsApp Script Sender")
    print("🎬 YouTube Shorts Generator")
    print("🇮🇩 Bahasa Indonesia")
    print("=" * 60)
    
    print(f"\n📱 Target: {TARGET_PHONE}")
    print(f"📱 Format: {format_phone(TARGET_PHONE)}")
    
    print("\n⚙️ Prerequisites:")
    print("   1. Chrome browser installed")
    print("   2. Internet connection")
    print("   3. WhatsApp Web logged in (scan QR if needed)")
    
    confirm = input("\n🚀 Tekan ENTER untuk kirim, Ctrl+C untuk cancel: ")
    
    print("\n" + "-" * 60)
    
    success = send_via_web()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SELESAI! Script sudah dikirim ke WhatsApp kamu!")
        print("=" * 60)
    else:
        print("\n❌ Gagal mengirim pesan")


if __name__ == "__main__":
    main()
