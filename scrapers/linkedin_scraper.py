"""
LinkedIn-specific job scraping functionality
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

class LinkedInScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.is_logged_in = False
        self.login_attempts = 0
        self.max_login_attempts = 3
    def login_to_linkedin(self):
        """Handle LinkedIn login for better access"""
        if self.is_logged_in or self.login_attempts >= self.max_login_attempts:
            return self.is_logged_in
            
        try:
            logger.info("Attempting LinkedIn login...")
            self.login_attempts += 1
            
            # Navigate to LinkedIn login page
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            # Clear fields and enter credentials
            email_field.clear()
            password_field.clear()
            
            # Type credentials with human-like delays
            linkedin_email = os.getenv('LINKEDIN_EMAIL', 'officialhimanshurawat@gmail.com')
            linkedin_password = os.getenv('LINKEDIN_PASSWORD', '$ox&fIvei8ac2n72VJcvjeekwjUhoz')
            
            self._type_like_human(email_field, linkedin_email)
            time.sleep(random.uniform(1, 2))
            self._type_like_human(password_field, linkedin_password)
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete and check for success
            time.sleep(random.uniform(3, 6))
            
            # Check if login was successful
            if self._verify_login_success():
                self.is_logged_in = True
                logger.info("LinkedIn login successful!")
                return True
            else:
                logger.warning(f"LinkedIn login attempt {self.login_attempts} failed")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn login error: {e}")
            return False
    
    def _type_like_human(self, element, text):
        """Type text with human-like delays to avoid bot detection"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def _verify_login_success(self):
        """Verify if login was successful"""
        try:
            # Check for various indicators of successful login
            success_indicators = [
                "linkedin.com/feed",
                "linkedin.com/mynetwork",
                "linkedin.com/jobs",
                "global-nav__me"
            ]
            
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            # Check URL indicators
            for indicator in success_indicators[:3]:
                if indicator in current_url:
                    return True
            
            # Check for profile menu (indicates logged in)
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".global-nav__me, .feed-identity-module")
                return True
            except:
                pass
            
            # Check if we're still on login page (failed login)
            if "login" in current_url or "challenge" in current_url:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error verifying login: {e}")
            return False
    
    def search_jobs_with_rate_limiting(self, query, location="", date_posted="past-week"):
        """Search jobs with built-in rate limiting and login check"""
        try:
            # Ensure we're logged in
            if not self.is_logged_in:
                if not self.login_to_linkedin():
                    logger.error("Cannot search jobs without login")
                    return []
            
            # Construct search URL
            search_params = {
                'keywords': query,
                'location': location,
                'f_TPR': date_posted,  # past-week, past-month, etc.
                'f_JT': 'F'  # Full-time jobs
            }
            
            # Build URL
            params_str = '&'.join([f"{k}={v}" for k, v in search_params.items() if v])
            search_url = f"https://www.linkedin.com/jobs/search/?{params_str}"
            
            logger.info(f"Searching LinkedIn jobs: {query} in {location}")
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(3, 7))
            
            self.driver.get(search_url)
            time.sleep(random.uniform(4, 8))
            
            # Handle potential CAPTCHA or verification
            if self._handle_verification():
                return self.get_job_links()
            else:
                logger.warning("LinkedIn verification required - skipping this search")
                return []
                
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
            return []
    
    def _handle_verification(self):
        """Handle LinkedIn verification challenges"""
        try:
            # Check for common verification elements
            verification_selectors = [
                ".challenge-page",
                ".captcha-container",
                ".security-challenge-page"
            ]
            
            for selector in verification_selectors:
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    logger.warning("LinkedIn verification challenge detected")
                    # Wait a bit and try to continue
                    time.sleep(random.uniform(10, 20))
                    return False
            
            return True
            
        except Exception:
            return True

    def extract_job_details(self, job_url):
        """Extract comprehensive job details from LinkedIn with improved error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay before accessing job details
                time.sleep(random.uniform(2, 4))
                
                self.driver.get(job_url)
                time.sleep(random.uniform(3, 5))
                
                # Wait for page to load
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card__job-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-view-layout"))
                    )
                )
                
                # Extract job title with multiple fallbacks
                title_selectors = [
                    ".job-details-jobs-unified-top-card__job-title h1",
                    ".jobs-unified-top-card__job-title h1",
                    ".job-view-layout .job-details-jobs-unified-top-card__job-title",
                    ".t-24.t-bold",
                    "h1[data-automation-id='jobPostingHeader']"
                ]
                job_title = self.robust_element_extraction(title_selectors, "text")
                
                # Extract company name with multiple fallbacks
                company_selectors = [
                    ".job-details-jobs-unified-top-card__company-name a",
                    ".jobs-unified-top-card__company-name a",
                    ".jobs-unified-top-card__subtitle-primary-grouping a",
                    ".job-details-jobs-unified-top-card__company-name",
                    "a[data-automation-id='jobPostingCompanyLink']"
                ]
                company = self.robust_element_extraction(company_selectors, "text")
                
                # Extract location with multiple fallbacks
                location_selectors = [
                    ".job-details-jobs-unified-top-card__bullet",
                    ".jobs-unified-top-card__bullet",
                    ".jobs-unified-top-card__subtitle-secondary-grouping",
                    ".job-details-jobs-unified-top-card__primary-description-container .tvm__text",
                    "[data-automation-id='jobPostingLocation']"
                ]
                location = self.robust_element_extraction(location_selectors, "text")
                
                # Extract salary with multiple fallbacks
                salary_selectors = [
                    ".jobs-unified-top-card__job-insight span",
                    ".job-details-jobs-unified-top-card__job-insight span",
                    ".job-details-jobs-unified-top-card__job-insight",
                    ".compensation__salary"
                ]
                salary = self.extract_salary_info(salary_selectors)
                
                # Extract job description with multiple fallbacks
                description_selectors = [
                    ".jobs-box__html-content",
                    ".jobs-description-content__text",
                    ".jobs-description__content",
                    ".job-details-jobs-unified-top-card__job-description",
                    "[data-automation-id='jobPostingDescription']"
                ]
                description = self.robust_element_extraction(description_selectors, "text")
                
                # Find recruiter information
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
                        'portal': 'LinkedIn'
                    }
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Insufficient data extracted, retrying... (attempt {attempt + 1})")
                        time.sleep(random.uniform(3, 6))
                        continue
                    else:
                        logger.error(f"Failed to extract essential job data after {max_retries} attempts")
                        return None
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error extracting LinkedIn job details (attempt {attempt + 1}): {e}")
                    time.sleep(random.uniform(3, 6))
                    continue
                else:
                    logger.error(f"Failed to extract LinkedIn job details after {max_retries} attempts: {e}")
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
        """Find LinkedIn recruiter information with improved selectors"""
        try:
            hiring_selectors = [
                ".hirer-card__hirer-information",
                ".jobs-poster",
                ".hiring-team",
                ".job-details-jobs-unified-top-card__primary-description-container .hirer-card",
                ".artdeco-card.job-details-how-you-match",
                ".jobs-unified-top-card__content--two-pane .hiring-insights"
            ]
            
            for selector in hiring_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    try:
                        # Try multiple name selectors
                        name_selectors = [
                            ".base-main-card__title",
                            ".jobs-poster__name",
                            ".hirer-card__hirer-information .t-16",
                            ".hiring-insights__hiring-manager-name"
                        ]
                        
                        name = ""
                        profile_link = ""
                        
                        for name_selector in name_selectors:
                            name_elements = elements[0].find_elements(By.CSS_SELECTOR, name_selector)
                            if name_elements:
                                name = name_elements[0].text.strip()
                                break
                        
                        # Try to find profile link
                        profile_elements = elements[0].find_elements(By.CSS_SELECTOR, "a")
                        if profile_elements:
                            profile_link = profile_elements[0].get_attribute("href")
                        
                        if name:
                            return {
                                'name': name,
                                'contact': profile_link,
                                'platform': 'LinkedIn'
                            }
                    except Exception as e:
                        logger.debug(f"Error extracting recruiter info with selector {selector}: {e}")
                        continue
        except Exception as e:
            logger.debug(f"Error finding recruiter info: {e}")
        return None
    
    def get_job_links(self):
        """Get job links from LinkedIn search results with improved reliability"""
        try:
            # Wait for search results with multiple possible selectors
            WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results__list")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results-list")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list"))
                )
            )
            
            # Multiple selectors for job elements
            job_list_selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                ".jobs-search__results-list .jobs-search-result",
                ".jobs-search-result"
            ]
            
            job_elements = []
            for selector in job_list_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    job_elements = elements
                    logger.info(f"Found {len(elements)} job elements using selector: {selector}")
                    break
            
            if not job_elements:
                logger.warning("No job elements found with any selector")
                return []
            
            links = []
            
            # Process up to 10 jobs (increased from 8 for better coverage)
            for i, element in enumerate(job_elements[:10]):
                try:
                    # Multiple selectors for job links
                    link_selectors = [
                        ".job-card-container__link",
                        ".job-card-list__title",
                        "a[data-control-name='job_card_click']",
                        ".jobs-search-result__job-card-container a",
                        ".job-card-container a",
                        "h3 a"
                    ]
                    
                    job_url = None
                    for selector in link_selectors:
                        try:
                            link_elements = element.find_elements(By.CSS_SELECTOR, selector)
                            for link_element in link_elements:
                                url = link_element.get_attribute("href")
                                if url and 'linkedin.com/jobs/view' in url:
                                    job_url = url
                                    break
                            if job_url:
                                break
                        except Exception as e:
                            logger.debug(f"Link selector {selector} failed: {e}")
                            continue
                    
                    if job_url:
                        # Clean up the URL (remove tracking parameters)
                        if '?' in job_url:
                            job_url = job_url.split('?')[0]
                        links.append(job_url)
                        logger.debug(f"Found job link {i+1}: {job_url}")
                    else:
                        logger.debug(f"No valid link found for job element {i+1}")
                        
                except Exception as e:
                    logger.debug(f"Error processing job element {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(links)} job links from LinkedIn")
            return links
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job links: {e}")
            return []