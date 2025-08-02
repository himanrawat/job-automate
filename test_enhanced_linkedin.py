#!/usr/bin/env python3
"""
Test Enhanced LinkedIn Scraping with Authentication
"""

import sys
import os
import logging
import time

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.browser_setup import setup_chrome_driver
from scrapers.linkedin_scraper import LinkedInScraper
from config.user_profile import HimanshuProfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_linkedin_scraping():
    """Test the enhanced LinkedIn scraping functionality"""
    driver = None
    try:
        logger.info("Starting enhanced LinkedIn scraping test...")
        
        # Setup browser
        logger.info("Setting up Chrome driver...")
        driver = setup_chrome_driver(headless=False)  # Set to True for headless mode
        
        # Initialize LinkedIn scraper
        linkedin_scraper = LinkedInScraper(driver)
        
        # Test login functionality
        logger.info("Testing LinkedIn login...")
        login_success = linkedin_scraper.login_to_linkedin()
        
        if not login_success:
            logger.error("LinkedIn login failed!")
            return False
        
        logger.info("✅ LinkedIn login successful!")
        
        # Test job search with rate limiting
        logger.info("Testing job search with rate limiting...")
        test_queries = [
            "Frontend Developer",
            "React Developer", 
            "JavaScript Developer"
        ]
        
        for query in test_queries:
            logger.info(f"Searching for: {query}")
            
            # Use the enhanced search method
            job_links = linkedin_scraper.search_jobs_with_rate_limiting(
                query=query,
                location="India",
                date_posted="past-week"
            )
            
            logger.info(f"Found {len(job_links)} job links for '{query}'")
            
            # Test extracting details from first few jobs
            for i, job_url in enumerate(job_links[:3]):  # Test first 3 jobs
                logger.info(f"Extracting details for job {i+1}: {job_url}")
                
                job_details = linkedin_scraper.extract_job_details(job_url)
                
                if job_details:
                    logger.info(f"✅ Successfully extracted job details:")
                    logger.info(f"   Title: {job_details.get('title', 'N/A')}")
                    logger.info(f"   Company: {job_details.get('company', 'N/A')}")
                    logger.info(f"   Location: {job_details.get('location', 'N/A')}")
                    logger.info(f"   Recruiter: {job_details.get('recruiter_info', {}).get('name', 'N/A')}")
                else:
                    logger.warning(f"❌ Failed to extract details for job {i+1}")
                
                # Add delay between job extractions
                time.sleep(3)
            
            # Add delay between different searches
            time.sleep(5)
        
        logger.info("✅ Enhanced LinkedIn scraping test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    success = test_enhanced_linkedin_scraping()
    if success:
        print("\n🎉 Enhanced LinkedIn scraping test PASSED!")
    else:
        print("\n💥 Enhanced LinkedIn scraping test FAILED!")
    
    sys.exit(0 if success else 1)
