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
from scrapers.apify_linkedin_scraper import ApifyJobScraper
from utils.enhanced_application_processor import EnhancedApplicationProcessor
from applications.application_handler import ApplicationHandler

# Configure logging with UTF-8 encoding for Unicode support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('himanshu_job_automation.log', encoding='utf-8'),
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
        self.apify_scraper = None
        self.application_handler = None
        self.enhanced_processor = None
        
        # Initialize Apify scraper (doesn't need browser)
        try:
            self.apify_scraper = ApifyJobScraper()
            logger.info("Apify job scraper initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Apify scraper: {e}")
            self.apify_scraper = None
        
        # Setup browser with error handling (only for application handler)
        try:
            self.driver = self.browser_manager.setup_browser()
            if self.driver:
                # Initialize application handler for automated applications
                self.application_handler = ApplicationHandler(self.driver)
                logger.info("Application handler initialized successfully")
            else:
                logger.warning("Browser setup failed - applications will be manual only")
        except Exception as e:
            logger.error(f"Error during browser initialization: {e}")
            self.driver = None
        
        # Initialize enhanced application processor
        try:
            self.enhanced_processor = EnhancedApplicationProcessor(self.driver)
            logger.info("Enhanced application processor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing enhanced processor: {e}")
            self.enhanced_processor = None
        
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
    
    # Legacy methods removed - now using Apify for all job discovery
    # Job details are provided directly from Apify response
    
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
    
    # Legacy region processing removed - now using Apify for all job discovery
    
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
    
    def discover_jobs_with_apify(self, region_config=None, max_jobs=50, platforms=['linkedin']):
        """
        Use Apify Job Scrapers for intelligent job discovery across multiple platforms
        This is the primary method for finding jobs at scale
        """
        if not self.apify_scraper:
            logger.error("Apify scraper not available")
            return []
        
        try:
            logger.info(f"🔍 Starting job discovery with Apify across platforms: {platforms}")
            
            # Use region-specific preferences if provided
            if region_config:
                keywords = region_config.get('keywords', '').split(' OR ')
                locations = region_config.get('locations', [])
            else:
                # Use default job preferences
                keywords = self.apify_scraper.job_preferences.job_titles
                locations = self.apify_scraper.job_preferences.locations
            
            # Search across multiple platforms
            jobs = self.apify_scraper.search_multiple_platforms(
                platforms=platforms,
                keywords=keywords,
                locations=locations[:2],  # Limit to 2 locations to manage costs
                max_jobs_per_platform=max_jobs // len(platforms)
            )
            
            logger.info(f"✅ Discovered {len(jobs)} jobs using Apify across {platforms}")
            
            # Convert Apify job format to your system's format
            converted_jobs = []
            for job in jobs:
                converted_job = {
                    'url': job['url'],
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'description': job['description'],
                    'priority_score': job.get('priority_score', 0),
                    'source': job['source'],
                    'platform': job['platform'],
                    'scraped_at': job['scraped_at'],
                    'salary': job.get('salary', ''),
                    'experience_level': job.get('experience_level', ''),
                    'raw_apify_data': job.get('raw_data', {})
                }
                converted_jobs.append(converted_job)
            
            return converted_jobs
            
        except Exception as e:
            logger.error(f"Error in Apify job discovery: {e}")
            return []
    
    def search_target_companies_with_apify(self, company_list=None):
        """
        Search for jobs at specific target companies using Apify
        """
        if not self.apify_scraper:
            logger.error("Apify scraper not available")
            return []
        
        if not company_list:
            # Use default target companies
            company_list = (JobPreferences.TOP_STARTUPS + 
                          JobPreferences.ESTABLISHED_GOOD_COMPANIES)[:10]  # Limit to 10 companies
        
        try:
            logger.info(f"🎯 Searching jobs at target companies: {company_list}")
            
            jobs = self.apify_scraper.search_specific_companies(
                company_names=company_list,
                keywords=['Frontend Developer', 'React Developer', 'JavaScript Developer'],
                max_jobs_per_company=5
            )
            
            logger.info(f"✅ Found {len(jobs)} jobs at target companies")
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching target companies with Apify: {e}")
            return []

    def run_automation(self):
        """
        Main automation execution with Apify-powered job discovery
        """
        logger.info("STARTING: Himanshu Rawat's Advanced Job Automation with Apify")
        
        all_applications = []
        
        try:
            # Phase 1: High-volume job discovery with Apify
            logger.info("PHASE 1: Discovering jobs with Apify Multi-Platform Scraper")
            
            apify_jobs = []
            
            # Discover general jobs across platforms (LinkedIn + Indeed + German Jobs)
            available_platforms = ['linkedin', 'indeed', 'german_jobs']  # Multi-platform including German market
            general_jobs = self.discover_jobs_with_apify(
                max_jobs=30, 
                platforms=available_platforms
            )
            apify_jobs.extend(general_jobs)
            
            # Specific German job market search if rate limits allow
            if self.apify_scraper and self.apify_scraper._check_rate_limits():
                logger.info("🇩🇪 Searching German job market...")
                german_jobs = self.apify_scraper.search_german_jobs(
                    keywords=["Frontend Entwickler", "UI Entwickler", "React Entwickler"],
                    locations=["Berlin", "München", "Hamburg"],
                    max_jobs=15
                )
                apify_jobs.extend(german_jobs)
                logger.info(f"✅ Found {len(german_jobs)} German jobs")
            
            # Search target companies if rate limits allow
            if self.apify_scraper and self.apify_scraper._check_rate_limits():
                target_company_jobs = self.search_target_companies_with_apify()
                apify_jobs.extend(target_company_jobs)
            
            logger.info(f"✅ Apify discovered {len(apify_jobs)} total jobs")
            
            # Phase 2: Process discovered jobs for applications
            logger.info("PHASE 2: Processing applications for discovered jobs")
            
            for job in apify_jobs[:JobPreferences.MAX_APPLICATIONS_PER_DAY]:
                if self.applications_today >= JobPreferences.MAX_APPLICATIONS_PER_DAY:
                    logger.info("Daily application limit reached")
                    break
                
                try:
                    # Process job application
                    application_result = self.process_apify_job_application(job)
                    
                    if application_result:
                        all_applications.append(application_result)
                        self.applications_today += 1
                        
                        # Log to sheets/CSV
                        self.sheets_manager.log_application(job, application_result)
                        
                        logger.info(f"✅ Applied to {job['title']} at {job['company']} "
                                  f"(Priority: {job.get('priority_score', 'N/A')})")
                    
                    # Rate limiting between applications
                    time.sleep(30)  # 30 seconds between applications
                    
                except Exception as e:
                    logger.error(f"Error processing job application: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in main automation: {e}")
        
        # Generate summary and dashboard
        self.generate_daily_summary(all_applications)
        
        logger.info(f"🎉 Automation completed! Processed {len(all_applications)} applications")
        logger.info(f"📊 Spreadsheet: {self.sheets_manager.spreadsheet.url}")
        
        # Cleanup
        if self.driver:
            self.browser_manager.close_browser()
        
        return all_applications
    
    def process_apify_job_application(self, job):
        """
        Process a job application for a job discovered via Apify using enhanced processor
        """
        try:
            if not self.enhanced_processor:
                logger.error("Enhanced processor not available")
                return None
            
            # Use enhanced processor for complete application handling
            result = self.enhanced_processor.process_apify_job_application(
                job_data=job,
                automation_mode=True  # Enable automation if browser is available
            )
            
            logger.info(f"✅ Enhanced application processing complete for {job.get('title')} at {job.get('company')}")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced application processing: {e}")
            
            # Fallback to basic processing
            return {
                'job_info': {
                    'title': job.get('title', 'Unknown'),
                    'company': job.get('company', 'Unknown'),
                    'platform': job.get('platform', 'Unknown')
                },
                'status': 'processing_failed',
                'error': str(e),
                'fallback': 'Manual application required'
            }

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