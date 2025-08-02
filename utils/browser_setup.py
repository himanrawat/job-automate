"""
Browser Configuration and Setup
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import logging
import os

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        """Setup Chrome browser with stealth options"""
        try:
            chrome_options = Options()
            
            # Basic options for headless and stealth mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Additional stability options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Try to use local Chrome installation if available
            chrome_binary_path = self._find_chrome_binary()
            if chrome_binary_path:
                chrome_options.binary_location = chrome_binary_path
                logger.info(f"Using Chrome binary at: {chrome_binary_path}")
            
            # Setup driver service - simplified approach without WebDriver Manager
            try:
                # Try with default ChromeDriver (expects it in PATH or uses local)
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("ChromeDriver setup successful via default method")
            except Exception as e:
                logger.error(f"ChromeDriver setup failed: {e}")
                logger.info("Note: Browser automation is optional. Core features (Apify scraping, document generation) will still work.")
                return None
            
            # Stealth script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Browser setup completed successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            return None
    
    def _find_chrome_binary(self):
        """Find Chrome binary on the system"""
        try:
            # Check if we have Chrome in our project folder
            project_chrome = os.path.join(os.getcwd(), "chrome-win64", "chrome.exe")
            if os.path.exists(project_chrome):
                return project_chrome
            
            # Common Chrome locations on Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    return path
            
            return None
            
        except Exception as e:
            logger.warning(f"Error finding Chrome binary: {e}")
            return None
    
    def close_browser(self):
        """Close browser safely"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        self.driver = None