"""
WhatsApp Auto-Reply Bot
Bot yang merespon pesan masuk dan generate YouTube Shorts script

Usage:
    python auto_reply_bot.py

Requirements:
    - Chrome browser installed
    - Selenium
    - Scan QR code WhatsApp Web sekali saja
"""

import time
import logging
import sys
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from whatsapp_bot.whatsapp_bot import YouTubeShortsWhatsAppBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WhatsAppAutoReplyBot:
    """WhatsApp bot yang auto-reply pesan masuk"""
    
    def __init__(self, session_path: str = "./whatsapp_session"):
        self.session_path = session_path
        self.driver = None
        self.bot = YouTubeShortsWhatsAppBot()
        self.running = False
        self.processed_messages = set()  # Track processed messages
        self.last_check = None
        
    def setup_driver(self):
        """Setup Chrome driver untuk WhatsApp Web"""
        logger.info("🔧 Setting up Chrome driver...")
        
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.session_path}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Profile untuk persist login
        profile_dir = Path(self.session_path)
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Chrome driver initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False
    
    def connect(self):
        """Connect ke WhatsApp Web"""
        logger.info("📱 Connecting to WhatsApp Web...")
        
        if not self.setup_driver():
            return False
        
        try:
            self.driver.get("https://web.whatsapp.com/")
            
            # Wait untuk QR code atau chat list
            logger.info("⏳ Waiting for WhatsApp to load...")
            logger.info("📱 Jika ada QR code, scan dengan WhatsApp kamu")
            logger.info("📱 Jika sudah login, tunggu sampai chat list muncul")
            
            # Wait sampai chat list visible
            try:
                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]'))
                )
                logger.info("✅ WhatsApp connected!")
                return True
            except TimeoutException:
                logger.error("❌ Timeout waiting for WhatsApp")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def get_unread_chats(self):
        """Get list of unread chats"""
        try:
            # Find unread message indicators
            unread = self.driver.find_elements(By.XPATH, 
                '//span[contains(@class, "x10l6tqz")]//span[contains(@class, "x193iq5w")]')
            
            unread_chats = []
            for elem in unread:
                try:
                    # Click on unread chat
                    parent = elem.find_element(By.XPATH, './ancestor::div[@data-testid="chat-list-cell"]')
                    parent.click()
                    time.sleep(1)
                    
                    # Get chat name
                    try:
                        name_elem = self.driver.find_element(By.XPATH, 
                            '//div[contains(@class, "x1n2onr6")]//span[@title]')
                        chat_name = name_elem.get_attribute('title')
                        
                        # Get last message
                        try:
                            messages = self.driver.find_elements(By.XPATH,
                                '//div[contains(@class, "message-in")]//span[@class=" selectable-text"]')
                            last_msg = messages[-1].text if messages else ""
                        except:
                            last_msg = ""
                        
                        unread_chats.append({
                            'name': chat_name,
                            'last_message': last_msg,
                            'element': parent
                        })
                    except NoSuchElementException:
                        pass
                        
                except Exception:
                    pass
            
            return unread_chats
            
        except Exception as e:
            logger.error(f"Error getting unread chats: {e}")
            return []
    
    def send_reply(self, message: str):
        """Send reply message"""
        try:
            # Find message input box
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                )
            )
            
            # Type message
            input_box.clear()
            input_box.send_keys(message)
            time.sleep(0.5)
            
            # Click send button
            send_button = self.driver.find_element(By.XPATH, 
                '//button[@aria-label="Send" or @data-testid="send"]')
            send_button.click()
            
            logger.info("✅ Reply sent")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send reply: {e}")
            return False
    
    def handle_message(self, message: str) -> str:
        """Handle incoming message and return response"""
        message = message.strip().lower()
        
        logger.info(f"📩 Processing: {message}")
        
        # Process command
        response = self.bot.handle_command(message)
        return response
    
    def monitor_messages(self, interval: int = 5):
        """
        Monitor for new messages and auto-reply
        
        Args:
            interval: Seconds between checks
        """
        logger.info(f"🔄 Starting message monitor (check every {interval}s)")
        logger.info("💡 Bot will auto-reply to incoming messages")
        logger.info("⏹️ Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            while self.running:
                try:
                    # Check for new unread messages
                    unread = self.get_unread_chats()
                    
                    for chat in unread:
                        msg_id = f"{chat['name']}_{chat['last_message']}"
                        
                        # Skip if already processed
                        if msg_id in self.processed_messages:
                            continue
                        
                        logger.info(f"📨 New message from: {chat['name']}")
                        logger.info(f"   Message: {chat['last_message'][:50]}...")
                        
                        # Process and reply
                        response = self.handle_message(chat['last_message'])
                        self.send_reply(response)
                        
                        # Mark as processed
                        self.processed_messages.add(msg_id)
                        
                        # Keep only last 100 messages
                        if len(self.processed_messages) > 100:
                            self.processed_messages = set(list(self.processed_messages)[-100:])
                    
                    time.sleep(interval)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Monitor error: {e}")
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            logger.info("\n⏹️ Bot stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        if self.driver:
            self.driver.quit()
            self.driver = None
        logger.info("🔌 Bot disconnected")


def main():
    print("=" * 60)
    print("📱 WhatsApp Auto-Reply Bot")
    print("🎬 YouTube Shorts Content Generator")
    print("🇮🇩 Indonesian Language Support")
    print("=" * 60)
    
    bot = WhatsAppAutoReplyBot()
    
    # Connect
    if not bot.connect():
        logger.error("❌ Failed to connect to WhatsApp")
        return
    
    # Check for pending messages first
    print("\n📋 Checking pending messages...")
    
    # Start monitoring
    bot.monitor_messages(interval=5)


if __name__ == "__main__":
    main()
