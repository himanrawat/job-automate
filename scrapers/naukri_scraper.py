"""
Naukri.com-specific job scraping functionality
"""

import time
import logging
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class NaukriScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.is_logged_in = False
        self.login_attempts = 0
        self.max_login_attempts = 3
    def login_to_naukri(self):
        """Handle Naukri login for better access"""
        if self.is_logged_in or self.login_attempts >= self.max_login_attempts:
            return self.is_logged_in
            
        try:
            logger.info("Attempting Naukri login...")
            self.login_attempts += 1
            
            # Navigate to Naukri login page
            self.driver.get("https://www.naukri.com/nlogin/login")
            time.sleep(random.uniform(2, 4))
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "usernameField"))
            )
            password_field = self.driver.find_element(By.ID, "passwordField")
            
            # Clear fields and enter credentials
            email_field.clear()
            password_field.clear()
            
            # Type credentials with human-like delays
            naukri_email = os.getenv('NAUKRI_EMAIL', 'officialhimanshurawat@gmail.com')
            naukri_password = os.getenv('NAUKRI_PASSWORD', '@DL3sec3864')
            
            self._type_like_human(email_field, naukri_email)
            time.sleep(random.uniform(1, 2))
            self._type_like_human(password_field, naukri_password)
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .loginButton")
            login_button.click()
            
            # Wait for login to complete and check for success
            time.sleep(random.uniform(3, 6))
            
            # Check if login was successful
            if self._verify_naukri_login_success():
                self.is_logged_in = True
                logger.info("Naukri login successful!")
                return True
            else:
                logger.warning(f"Naukri login attempt {self.login_attempts} failed")
                return False
                
        except Exception as e:
            logger.error(f"Naukri login error: {e}")
            return False
    
    def _type_like_human(self, element, text):
        """Type text with human-like delays to avoid bot detection"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def _verify_naukri_login_success(self):
        """Verify if Naukri login was successful"""
        try:
            # Check for various indicators of successful login
            success_indicators = [
                "naukri.com/mnjuser/homepage",
                "naukri.com/mnjuser/profile",
                "naukri.com/mnjuser/dashboard"
            ]
            
            current_url = self.driver.current_url
            
            # Check URL indicators
            for indicator in success_indicators:
                if indicator in current_url:
                    return True
            
            # Check for profile/dashboard elements (indicates logged in)
            try:
                profile_selectors = [
                    ".nI-gNb-drawer__icon",
                    ".mnjuser",
                    ".profileName",
                    "[data-track-label='profile_icon']"
                ]
                
                for selector in profile_selectors:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        return True
            except:
                pass
            
            # Check if we're still on login page (failed login)
            if "login" in current_url or "nlogin" in current_url:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error verifying Naukri login: {e}")
            return False
    
    def search_jobs_with_rate_limiting(self, query, location="", experience="0-3"):
        """Search Naukri jobs with built-in rate limiting and login check"""
        try:
            # Ensure we're logged in
            if not self.is_logged_in:
                if not self.login_to_naukri():
                    logger.error("Cannot search jobs without login")
                    return []
            
            # Construct search URL for Naukri
            base_url = "https://www.naukri.com"
            search_params = []
            
            if query:
                search_params.append(f"k={query.replace(' ', '%20')}")
            if location:
                search_params.append(f"l={location.replace(' ', '%20')}")
            if experience:
                search_params.append(f"experience={experience}")
            
            # Build search URL
            if search_params:
                search_url = f"{base_url}/{query.replace(' ', '-').lower()}-jobs?" + "&".join(search_params)
            else:
                search_url = f"{base_url}/jobs"
            
            logger.info(f"Searching Naukri jobs: {query} in {location}")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(3, 7))
            
            self.driver.get(search_url)
            time.sleep(random.uniform(4, 8))
            
            # Get job links using enhanced method
            return self.get_job_links()
                
        except Exception as e:
            logger.error(f"Error searching Naukri jobs: {e}")
            return []

    def extract_job_details(self, job_url):
        """Extract job details from Naukri.com with improved error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay before accessing job details
                time.sleep(random.uniform(2, 4))
                
                self.driver.get(job_url)
                time.sleep(random.uniform(3, 5))
                
                # Wait for page to load with multiple selectors
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jd-header-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                    )
                )
                
                # Extract job title with multiple fallbacks
                title_selectors = [
                    ".jd-header-title",
                    ".job-title",
                    "h1.jd-job-title",
                    ".jd-job-title h1",
                    "h1"
                ]
                job_title = self.robust_element_extraction(title_selectors, "text")
                
                # Extract company name with multiple fallbacks
                company_selectors = [
                    ".jd-header-comp-name",
                    ".comp-name",
                    ".jd-header-comp-name a",
                    ".company-name",
                    ".jd-company-name"
                ]
                company = self.robust_element_extraction(company_selectors, "text")
                
                # Extract location with multiple fallbacks
                location_selectors = [
                    ".jd-loc",
                    ".location",
                    ".jd-location",
                    ".job-location"
                ]
                location = self.robust_element_extraction(location_selectors, "text")
                
                # Extract job description with multiple fallbacks
                description_selectors = [
                    ".dang-inner-html",
                    ".job-description",
                    ".jd-desc",
                    ".job-summary",
                    ".jd-job-description"
                ]
                description = self.robust_element_extraction(description_selectors, "text")
                
                # Extract salary with specific Naukri patterns
                salary_selectors = [
                    ".salary",
                    ".jd-salary",
                    ".salary-range",
                    ".ctc"
                ]
                salary = self.extract_salary_info(salary_selectors)
                
                # Find recruiter contact
                recruiter_info = self.find_recruiter_info()
                
                # Validate that we got essential information
                if job_title or company:
                    return {
                        'title': job_title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'salary': salary,
                        'url': job_url,
                        'recruiter_info': recruiter_info,
                        'portal': 'Naukri'
                    }
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Insufficient data extracted from Naukri, retrying... (attempt {attempt + 1})")
                        time.sleep(random.uniform(3, 6))
                        continue
                    else:
                        logger.error(f"Failed to extract essential Naukri job data after {max_retries} attempts")
                        return None
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error extracting Naukri job details (attempt {attempt + 1}): {e}")
                    time.sleep(random.uniform(3, 6))
                    continue
                else:
                    logger.error(f"Failed to extract Naukri job details after {max_retries} attempts: {e}")
                    return None
        
        return None

    def robust_element_extraction(self, selectors, element_type="text"):
        """More robust element extraction with retry logic"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and elements[0]:
                    if element_type == "text":
                        text = elements[0].text.strip()
                        if text:  # Only return non-empty text
                            return text
                    elif element_type == "href":
                        href = elements[0].get_attribute("href")
                        if href:
                            return href
            except Exception:
                continue
        return ""
    
    def find_recruiter_info(self):
        """Find Naukri recruiter information with improved selectors"""
        try:
            recruiter_selectors = [
                ".rec-name",
                ".recruiter-name",
                ".contact-person",
                ".recruiter-info .name",
                ".hiring-manager",
                ".jd-recruiter-name"
            ]
            
            for selector in recruiter_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        name = elements[0].text.strip()
                        if name:
                            return {
                                'name': name,
                                'contact': 'Available on Naukri platform',
                                'platform': 'Naukri'
                            }
                except Exception as e:
                    logger.debug(f"Error extracting recruiter info with selector {selector}: {e}")
                    continue
        except Exception as e:
            logger.debug(f"Error finding Naukri recruiter info: {e}")
        return None
    
    def get_job_links(self):
        """Get job links from Naukri search results with improved reliability"""
        try:
            # Wait for search results with multiple possible selectors
            WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".title a")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-title a")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobTuple a"))
                )
            )
            
            # Multiple selectors for job link elements
            job_link_selectors = [
                ".title a",
                ".job-title a",
                ".jobTuple a",
                ".jobTupleHeader a",
                "article .title a",
                ".job-card .title a"
            ]
            
            job_elements = []
            for selector in job_link_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    job_elements = elements
                    logger.info(f"Found {len(elements)} Naukri job elements using selector: {selector}")
                    break
            
            if not job_elements:
                logger.warning("No Naukri job elements found with any selector")
                return []
            
            links = []
            
            # Process up to 10 jobs (increased from 8 for better coverage)
            for i, element in enumerate(job_elements[:10]):
                try:
                    job_url = element.get_attribute("href")
                    if job_url:
                        # Handle relative URLs
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        
                        # Validate that it's a proper Naukri job URL
                        if 'naukri.com' in job_url and ('/job-listings/' in job_url or '/jobs-' in job_url):
                            # Clean up the URL (remove tracking parameters)
                            if '?' in job_url:
                                job_url = job_url.split('?')[0]
                            links.append(job_url)
                            logger.debug(f"Found Naukri job link {i+1}: {job_url}")
                        else:
                            logger.debug(f"Invalid Naukri job URL format: {job_url}")
                    else:
                        logger.debug(f"No valid link found for Naukri job element {i+1}")
                        
                except Exception as e:
                    logger.debug(f"Error processing Naukri job element {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(links)} job links from Naukri")
            return links
            
        except Exception as e:
            logger.error(f"Error getting Naukri job links: {e}")
            return []