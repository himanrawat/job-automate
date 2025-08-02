# scrapers/base_scraper.py
"""
Base scraper class with common functionality
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.user_profile import HimanshuProfile

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, driver):
        self.driver = driver
        
    def contains_avoided_keywords(self, job_description):
        """Check if job description contains keywords to avoid"""
        description_lower = job_description.lower()
        for keyword in HimanshuProfile.AVOID_KEYWORDS:
            if keyword.lower() in description_lower:
                return True
        return False
    
    def is_relevant_frontend_role(self, job_title):
        """Check if job title matches target frontend roles"""
        title_lower = job_title.lower()
        return any(role.lower() in title_lower for role in HimanshuProfile.TARGET_ROLES)
    
    def safe_find_element(self, selectors, default=""):
        """Safely find element using multiple selectors"""
        for selector in selectors if isinstance(selectors, list) else [selectors]:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except Exception:
                continue
        return default
    
    def extract_salary_info(self, selectors):
        """Extract salary information from multiple possible selectors"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text
                    if any(symbol in text for symbol in ['$', '₹', '£', '€', 'AU$', 'lakh', 'salary']):
                        return text
            except Exception:
                continue
        return "Not specified"