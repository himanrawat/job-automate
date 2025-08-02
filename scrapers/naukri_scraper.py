"""
Naukri.com-specific job scraping functionality
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class NaukriScraper(BaseScraper):
    def extract_job_details(self, job_url):
        """Extract job details from Naukri.com"""
        try:
            self.driver.get(job_url)
            time.sleep(3)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jd-header-title, .job-title"))
            )
            
            # Extract job details using safe selectors
            job_title = self.safe_find_element([".jd-header-title", ".job-title", "h1"])
            company = self.safe_find_element([".jd-header-comp-name", ".comp-name"])
            location = self.safe_find_element([".jd-loc", ".location"])
            description = self.safe_find_element([".dang-inner-html", ".job-description", ".jd-desc"])
            
            # Extract salary with specific Naukri patterns
            salary_selectors = [".salary", ".jd-salary"]
            salary = self.extract_salary_info(salary_selectors)
            
            # Find recruiter contact
            recruiter_info = self.find_recruiter_info()
            
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
            
        except Exception as e:
            logger.error(f"Error extracting Naukri job details: {e}")
            return None
    
    def find_recruiter_info(self):
        """Find Naukri recruiter information"""
        try:
            recruiter_selectors = [".rec-name", ".recruiter-name", ".contact-person"]
            
            for selector in recruiter_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return {
                        'name': element.text,
                        'contact': 'Available on Naukri platform',
                        'platform': 'Naukri'
                    }
                except:
                    continue
        except:
            pass
        return None
    
    def get_job_links(self):
        """Get job links from Naukri search results"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".title a, .job-title a"))
            )
            
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".title a, .job-title a")
            links = []
            
            for element in job_elements[:8]:
                try:
                    job_url = element.get_attribute("href")
                    if job_url:
                        if job_url.startswith('/'):
                            job_url = f"https://www.naukri.com{job_url}"
                        links.append(job_url)
                except:
                    continue
            
            return links
            
        except Exception as e:
            logger.error(f"Error getting Naukri job links: {e}")
            return []