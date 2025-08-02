"""
Main application runner for Himanshu's Job Automation
"""

import logging
import time
from datetime import datetime
from urllib.parse import quote_plus

# Import all components
from config.job_preferences import JobPreferences
from config.user_profile import HimanshuProfile
from utils.browser_setup import BrowserManager
from utils.priority_calculator import PriorityCalculator
from utils.content_generator import ContentGenerator
from utils.document_manager import DocumentManager
from utils.sheets_manager import SheetsManager
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.naukri_scraper import NaukriScraper
from applications.application_handler import ApplicationHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('himanshu_job_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HimanshuJobAutomator:
    def __init__(self):
        self.browser_manager = BrowserManager()
        self.priority_calculator = PriorityCalculator()
        self.content_generator = ContentGenerator()
        self.document_manager = DocumentManager()
        self.sheets_manager = SheetsManager()
        self.applications_today = 0
        self.driver = None
        self.linkedin_scraper = None
        self.naukri_scraper = None
        self.application_handler = None
        
        # Setup browser with error handling
        try:
            self.driver = self.browser_manager.setup_browser()
            if self.driver:
                # Initialize scrapers only if browser is available
                self.linkedin_scraper = LinkedInScraper(self.driver)
                self.naukri_scraper = NaukriScraper(self.driver)
                self.application_handler = ApplicationHandler(self.driver)
                logger.info("All components initialized successfully")
            else:
                logger.error("Browser setup failed - scrapers will not be available")
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            self.driver = None
        
    def get_regional_portals(self, region):
        """Get job portals for specific region"""
        portals = {
            'INDIA': [
                {
                    'name': 'Naukri_India',
                    'search_url': 'https://www.naukri.com/frontend-developer-jobs-in-{location}?k=frontend%20developer',
                    'locations': ['bangalore', 'delhi', 'noida', 'gurugram', 'chennai', 'hyderabad', 'mumbai']
                },
                {
                    'name': 'LinkedIn_India',
                    'search_url': 'https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400',
                    'locations': ['India', 'Bangalore, India', 'Delhi, India', 'Mumbai, India', 'Pune, India']
                },
                {
                    'name': 'Indeed_India',
                    'search_url': 'https://in.indeed.com/jobs?q={keywords}&l={location}&fromage=1',
                    'locations': ['Bangalore', 'Delhi', 'Mumbai', 'Pune', 'Hyderabad']
                }
            ],
            'USA': [
                {
                    'name': 'LinkedIn_USA',
                    'search_url': 'https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400',
                    'locations': ['United States', 'Remote', 'San Francisco, CA', 'New York, NY', 'Austin, TX']
                },
                {
                    'name': 'Indeed_USA',
                    'search_url': 'https://www.indeed.com/jobs?q={keywords}&l={location}&fromage=1',
                    'locations': ['United States', 'Remote', 'San Francisco, CA', 'New York, NY']
                }
            ],
            'AUSTRALIA': [
                {
                    'name': 'LinkedIn_Australia',
                    'search_url': 'https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400',
                    'locations': ['Australia', 'Sydney', 'Melbourne', 'Brisbane']
                }
            ],
            'UNITED_KINGDOM': [
                {
                    'name': 'LinkedIn_UK',
                    'search_url': 'https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400',
                    'locations': ['United Kingdom', 'London', 'Manchester', 'Birmingham']
                }
            ],
            'EUROPE': [
                {
                    'name': 'LinkedIn_Europe',
                    'search_url': 'https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_TPR=r86400',
                    'locations': ['Germany', 'Netherlands', 'Switzerland', 'Remote Europe']
                }
            ]
        }
        return portals.get(region, [])
    
    def search_jobs_on_portal(self, portal_config, keywords, region):
        """Search for jobs on specific portal"""
        portal_name = portal_config['name']
        locations = portal_config['locations']
        all_job_links = []
        
        # Check if browser and scrapers are available
        if not self.driver:
            logger.error(f"Browser not available - skipping {portal_name}")
            return []
        
        for location in locations[:3]:  # Limit to 3 locations per portal
            try:
                search_url = portal_config['search_url'].format(
                    keywords=quote_plus(keywords),
                    location=quote_plus(location)
                )
                
                logger.info(f"Searching {portal_name} in {location}")
                self.driver.get(search_url)
                time.sleep(5)
                
                # Get job links based on portal
                if 'linkedin' in portal_name.lower() and self.linkedin_scraper:
                    job_links = self.linkedin_scraper.get_job_links()
                elif 'naukri' in portal_name.lower() and self.naukri_scraper:
                    job_links = self.naukri_scraper.get_job_links()
                elif self.linkedin_scraper:
                    job_links = self.linkedin_scraper.get_job_links()  # Default to LinkedIn scraper
                else:
                    logger.warning(f"No suitable scraper available for {portal_name}")
                    job_links = []
                
                all_job_links.extend(job_links[:JobPreferences.MAX_APPLICATIONS_PER_PORTAL//len(locations)])
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error searching {portal_name} in {location}: {e}")
                continue
        
        return all_job_links[:JobPreferences.MAX_APPLICATIONS_PER_PORTAL]
    
    def extract_job_details(self, job_url, portal_name, region):
        """Extract job details using appropriate scraper"""
        try:
            if 'linkedin' in portal_name.lower():
                job_details = self.linkedin_scraper.extract_job_details(job_url)
            elif 'naukri' in portal_name.lower():
                job_details = self.naukri_scraper.extract_job_details(job_url)
            else:
                job_details = self.linkedin_scraper.extract_job_details(job_url)
            
            if job_details:
                job_details['region'] = region
                
                # Check if job is relevant and doesn't contain avoided keywords
                if not self.linkedin_scraper.is_relevant_frontend_role(job_details.get('title', '')):
                    logger.info(f"Skipping non-frontend role: {job_details.get('title', '')}")
                    return None
                    
                if self.linkedin_scraper.contains_avoided_keywords(job_details.get('description', '')):
                    logger.info(f"Skipping job with avoided keywords: {job_details.get('title', '')}")
                    return None
                    
            return job_details
            
        except Exception as e:
            logger.error(f"Error extracting job details from {job_url}: {e}")
            return None
    
    def process_single_job(self, job_url, portal_name, region):
        """Process a single job application"""
        try:
            # Extract job details
            job_details = self.extract_job_details(job_url, portal_name, region)
            if not job_details:
                return None
            
            # Calculate priority
            priority_level = self.priority_calculator.calculate_priority(job_details)
            
            # Generate tailored content
            tailored_resume = self.content_generator.tailor_resume_for_frontend(job_details, region)
            cover_letter = self.content_generator.generate_enthusiastic_cover_letter(job_details, region, priority_level)
            recruiter_message = self.content_generator.generate_direct_recruiter_message(job_details, region, priority_level)
            
            # Create documents and get links
            resume_link = self.document_manager.create_resume_document(tailored_resume, job_details)
            cover_letter_link = self.document_manager.create_cover_letter_document(cover_letter, job_details)
            
            # Try to apply to job
            application_result = self.application_handler.apply_to_job(job_details, cover_letter)
            
            # Calculate estimated time for manual applications
            estimated_time = self.calculate_estimated_time(application_result, priority_level)
            
            # Prepare comprehensive data for spreadsheet
            application_data = {
                'title': job_details['title'],
                'company': job_details['company'],
                'location': job_details['location'],
                'portal': job_details['portal'],
                'url': job_details['url'],
                'salary': job_details.get('salary', 'Not specified'),
                'application_status': self.get_application_status(application_result),
                'application_method': application_result.get('method', ''),
                'recruiter_name': job_details.get('recruiter_info', {}).get('name', '') if job_details.get('recruiter_info') else '',
                'recruiter_contact': job_details.get('recruiter_info', {}).get('contact', '') if job_details.get('recruiter_info') else '',
                'recruiter_platform': job_details.get('recruiter_info', {}).get('platform', '') if job_details.get('recruiter_info') else '',
                'outreach_message': recruiter_message,
                'keywords': self.extract_frontend_keywords(job_details['description']),
                'match_score': f"{self.priority_calculator.calculate_skill_match(job_details['description']):.1f}%",
                'next_action': self.get_next_action(application_result, priority_level),
                'visa_sponsorship': 'Required' if JobPreferences.REGIONS[region]['visa_required'] else 'Not Required',
                'job_type': self.determine_job_type(job_details),
                'direct_application_link': self.get_direct_application_link(job_details, application_result),
                'failure_reason': application_result.get('failure_reason', ''),
                'suggested_approach': application_result.get('suggested_approach', ''),
                'priority_level': priority_level,
                'resume_link': resume_link,
                'cover_letter_link': cover_letter_link,
                'estimated_time': estimated_time,
                'notes': f"Auto-processed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'region': region
            }
            
            # Update spreadsheet
            self.sheets_manager.update_application_row(region, application_data)
            
            # Track successful applications
            if application_result.get('status') == 'success':
                self.applications_today += 1
                logger.info(f"✅ Successfully applied: {job_details['title']} at {job_details['company']}")
            else:
                logger.info(f"📋 Manual required: {job_details['title']} at {job_details['company']} - {application_result.get('failure_reason', '')}")
            
            return application_data
            
        except Exception as e:
            logger.error(f"Error processing job {job_url}: {e}")
            return None
    
    def get_application_status(self, application_result):
        """Get human-readable application status"""
        status = application_result.get('status', 'failed')
        if status == 'success':
            return "Applied Successfully"
        elif status == 'manual_required':
            return "Manual Required"
        else:
            return "Failed"
    
    def get_next_action(self, application_result, priority_level):
        """Get next action based on application result"""
        if application_result.get('status') == 'success':
            return "Follow up with recruiter in 3 days"
        elif application_result.get('status') == 'manual_required':
            if "High 🔥" in priority_level:
                return "URGENT: Apply manually today - High priority"
            else:
                return "Apply manually within 2-3 days"
        else:
            return "Research alternative application methods"
    
    def calculate_estimated_time(self, application_result, priority_level):
        """Calculate estimated time for manual application"""
        if application_result.get('status') == 'success':
            return "0 minutes (automated)"
        else:
            return application_result.get('estimated_time', '10-15 minutes')
    
    def get_direct_application_link(self, job_details, application_result):
        """Get direct application link for manual applications"""
        if application_result.get('status') == 'manual_required':
            return job_details.get('url', '')
        return ""
    
    def extract_frontend_keywords(self, job_description):
        """Extract frontend-relevant keywords from job description"""
        import re
        frontend_keywords = ['react', 'javascript', 'html', 'css', 'frontend', 'ui', 'ux', 'responsive', 'typescript', 'next.js', 'tailwind']
        found_keywords = []
        
        for keyword in frontend_keywords:
            if keyword in job_description.lower():
                found_keywords.append(keyword)
        
        return ', '.join(found_keywords)
    
    def determine_job_type(self, job_details):
        """Determine job type from job details"""
        description_lower = job_details.get('description', '').lower()
        title_lower = job_details.get('title', '').lower()
        
        if any(keyword in description_lower or keyword in title_lower for keyword in ['contract', 'freelance']):
            return "Contract"
        elif any(keyword in description_lower or keyword in title_lower for keyword in ['part-time', 'part time']):
            return "Part-time"
        elif any(keyword in description_lower or keyword in title_lower for keyword in ['intern', 'internship']):
            return "Internship"
        else:
            return "Full-time"
    
    def process_region(self, region, region_config):
        """Process all jobs for a specific region"""
        logger.info(f"🌍 Processing {region} for Himanshu Rawat")
        
        # Create region worksheet
        self.sheets_manager.create_region_worksheet(region)
        
        portals = self.get_regional_portals(region)
        keywords = region_config['keywords']
        region_applications = []
        
        for portal_config in portals:
            try:
                if self.applications_today >= JobPreferences.MAX_APPLICATIONS_PER_DAY:
                    logger.info("📊 Daily application limit reached")
                    break
                    
                logger.info(f"🔍 Processing {portal_config['name']} for {region}")
                
                # Search for jobs
                job_links = self.search_jobs_on_portal(portal_config, keywords, region)
                
                for job_url in job_links:
                    if self.applications_today >= JobPreferences.MAX_APPLICATIONS_PER_DAY:
                        break
                    
                    # Process individual job
                    application_data = self.process_single_job(job_url, portal_config['name'], region)
                    
                    if application_data:
                        region_applications.append(application_data)
                    
                    # Add delay between applications (human-like behavior)
                    time.sleep(45)
                
                # Add delay between portals
                time.sleep(120)
                
            except Exception as e:
                logger.error(f"Error processing {portal_config['name']} for {region}: {e}")
                continue
        
        logger.info(f"✅ Completed {region}: {len(region_applications)} applications processed")
        return region_applications
    
    def generate_daily_summary(self, all_applications):
        """Generate daily summary report"""
        try:
            successful = [app for app in all_applications if app['application_status'] == 'Applied Successfully']
            manual_required = [app for app in all_applications if 'Manual Required' in app['application_status']]
            high_priority_manual = [app for app in manual_required if 'High 🔥' in app['priority_level']]
            
            summary = f"""
🚀 HIMANSHU'S JOB AUTOMATION SUMMARY - {datetime.now().strftime('%Y-%m-%d')}
================================================================

📊 RESULTS:
- Total Applications Processed: {len(all_applications)}
- ✅ Successfully Applied: {len(successful)}
- 📋 Manual Applications Required: {len(manual_required)}
- 🔥 High Priority Manual: {len(high_priority_manual)}
- 📈 Success Rate: {(len(successful)/len(all_applications)*100):.1f}%

🎯 HIGH PRIORITY ACTIONS (Apply Today):
"""
            
            for app in high_priority_manual[:5]:  # Top 5 high priority
                summary += f"- {app['title']} at {app['company']} ({app['estimated_time']})\n"
                summary += f"  📋 Action: {app['suggested_approach']}\n"
                summary += f"  🔗 Apply: {app['direct_application_link']}\n"
                summary += f"  📄 Resume: {app['resume_link']}\n"
                summary += f"  📝 Cover Letter: {app['cover_letter_link']}\n\n"
            
            summary += f"""
📊 Full tracking available at: {self.sheets_manager.spreadsheet.url}

🎉 Great work, Himanshu! Your frontend skills are in high demand!
Focus on the high priority manual applications first.
"""
            
            # Save summary
            with open(f"himanshu_daily_summary_{datetime.now().strftime('%Y%m%d')}.txt", "w", encoding='utf-8') as f:
                f.write(summary)
            
            print(summary)
            logger.info("📋 Daily summary generated")
            
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
    
    def run_automation(self):
        """Main automation execution"""
        logger.info("🚀 Starting Himanshu Rawat's Frontend Developer Job Automation")
        
        all_applications = []
        region_order = ['INDIA', 'USA', 'AUSTRALIA', 'UNITED_KINGDOM', 'EUROPE']
        
        for region in region_order:
            if region in JobPreferences.REGIONS:
                try:
                    applications = self.process_region(region, JobPreferences.REGIONS[region])
                    all_applications.extend(applications)
                    
                    # Break if daily limit reached
                    if self.applications_today >= JobPreferences.MAX_APPLICATIONS_PER_DAY:
                        break
                    
                    # Add delay between regions
                    if region != region_order[-1]:
                        time.sleep(300)  # 5 minutes
                        
                except Exception as e:
                    logger.error(f"Error processing {region}: {e}")
                    continue
        
        # Generate summary and dashboard
        self.generate_daily_summary(all_applications)
        
        logger.info(f"🎉 Automation completed! Processed {len(all_applications)} applications")
        logger.info(f"📊 Spreadsheet: {self.sheets_manager.spreadsheet.url}")
        
        # Cleanup
        self.browser_manager.close_browser()
        
        return all_applications

# Run the automation
if __name__ == "__main__":
    print("🚀 Starting Himanshu Rawat's Job Application Automation")
    print("=" * 60)
    
    try:
        automator = HimanshuJobAutomator()
        applications = automator.run_automation()
        
        print(f"\n🎉 Automation completed successfully!")
        print(f"📊 Total applications processed: {len(applications)}")
        print(f"📋 Check your Google Sheets for detailed tracking")
        print(f"📧 Summary saved to daily report file")
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        print(f"❌ Automation failed: {e}")