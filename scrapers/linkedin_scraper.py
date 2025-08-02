"""
LinkedIn-specific job scraping functionality
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    def extract_job_details(self, job_url):
        """Extract comprehensive job details from LinkedIn"""
        try:
            self.driver.get(job_url)
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title"))
            )
            
            # Extract job title
            title_selectors = [
                ".job-details-jobs-unified-top-card__job-title h1",
                ".jobs-unified-top-card__job-title h1",
                ".t-24.t-bold"
            ]
            job_title = self.safe_find_element(title_selectors)
            
            # Extract company name
            company_selectors = [
                ".job-details-jobs-unified-top-card__company-name a",
                ".jobs-unified-top-card__company-name a",
                ".jobs-unified-top-card__subtitle-primary-grouping a"
            ]
            company = self.safe_find_element(company_selectors)
            
            # Extract location
            location_selectors = [
                ".job-details-jobs-unified-top-card__bullet",
                ".jobs-unified-top-card__bullet",
                ".jobs-unified-top-card__subtitle-secondary-grouping"
            ]
            location = self.safe_find_element(location_selectors)
            
            # Extract salary
            salary_selectors = [
                ".jobs-unified-top-card__job-insight span",
                ".job-details-jobs-unified-top-card__job-insight span"
            ]
            salary = self.extract_salary_info(salary_selectors)
            
            # Extract job description
            description_selectors = [
                ".jobs-box__html-content",
                ".jobs-description-content__text",
                ".jobs-description__content"
            ]
            description = self.safe_find_element(description_selectors)
            
            # Find recruiter information
            recruiter_info = self.find_recruiter_info()
            
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
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job details: {e}")
            return None
    
    def find_recruiter_info(self):
        """Find LinkedIn recruiter information"""
        try:
            hiring_selectors = [
                ".hirer-card__hirer-information",
                ".jobs-poster",
                ".hiring-team"
            ]
            
            for selector in hiring_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    try:
                        name_element = elements[0].find_element(By.CSS_SELECTOR, ".base-main-card__title, .jobs-poster__name")
                        profile_element = elements[0].find_element(By.CSS_SELECTOR, "a")
                        
                        return {
                            'name': name_element.text,
                            'contact': profile_element.get_attribute("href"),
                            'platform': 'LinkedIn'
                        }
                    except:
                        continue
        except:
            pass
        return None
    
    def get_job_links(self):
        """Get job links from LinkedIn search results"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-results__list, .jobs-search-results-list"))
            )
            
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item, .job-card-container")
            links = []
            
            for element in job_elements[:8]:
                try:
                    link_selectors = [
                        ".job-card-container__link",
                        ".job-card-list__title",
                        "a[data-control-name='job_card_click']"
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = element.find_element(By.CSS_SELECTOR, selector)
                            job_url = link_element.get_attribute("href")
                            if job_url and 'linkedin.com' in job_url:
                                links.append(job_url)
                                break
                        except:
                            continue
                except:
                    continue
            
            return links
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job links: {e}")
            return []