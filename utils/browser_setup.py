"""
Browser Configuration and Setup
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser with stealth options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser setup completed successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            return None
    
    def close_browser(self):
        """Close browser safely"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed successfully")