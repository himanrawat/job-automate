"""
Enhanced Application Processor for Apify Job Data
Integrates with enhanced content generator for better job applications
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Any
from utils.enhanced_content_generator import EnhancedContentGenerator
from utils.document_manager import DocumentManager
from utils.sheets_manager import SheetsManager
from applications.application_handler import ApplicationHandler

logger = logging.getLogger(__name__)

class EnhancedApplicationProcessor:
    def __init__(self, driver=None):
        self.content_generator = EnhancedContentGenerator()
        self.document_manager = DocumentManager()
        self.sheets_manager = SheetsManager()
        self.application_handler = ApplicationHandler(driver) if driver else None
        
    def process_apify_job_application(self, job_data: Dict, automation_mode: bool = True) -> Dict[str, Any]:
        """
        Process a complete job application for Apify job data
        
        Args:
            job_data: Job data from Apify (LinkedIn or Indeed)
            automation_mode: Whether to attempt automated application
            
        Returns:
            Complete application result with documents and tracking info
        """
        try:
            logger.info(f"Processing application for {job_data.get('title')} at {job_data.get('company')}")
            
            # Step 1: Extract contact details from job description
            logger.info("Step 1: Extracting contact details...")
            contact_details = self.content_generator.extract_contact_details(job_data)
            
            # Step 2: Generate tailored documents
            logger.info("Step 2: Generating tailored resume...")
            tailored_resume = self.content_generator.generate_tailored_resume(job_data, contact_details)
            
            logger.info("Step 3: Generating personalized cover letter...")
            cover_letter = self.content_generator.generate_personalized_cover_letter(job_data, contact_details)
            
            logger.info("Step 4: Generating LinkedIn outreach message...")
            linkedin_message = self.content_generator.generate_linkedin_message(job_data, contact_details)
            
            # Step 3: Format complete application package
            logger.info("Step 5: Formatting application package...")
            application_package = self.content_generator.format_application_package(
                job_data, contact_details, tailored_resume, cover_letter, linkedin_message
            )
            
            # Step 4: Save documents
            logger.info("Step 6: Saving documents...")
            document_paths = self._save_application_documents(job_data, application_package)
            
            # Step 5: Attempt automation if enabled
            automation_result = {}
            if automation_mode and self.application_handler:
                logger.info("Step 7: Attempting automated application...")
                automation_result = self._attempt_automated_application(job_data, application_package)
            else:
                automation_result = {
                    'status': 'manual_required',
                    'method': 'manual_application',
                    'reason': 'Automation disabled or no driver available'
                }
            
            # Step 6: Track in Google Sheets
            logger.info("Step 8: Tracking in Google Sheets...")
            tracking_result = self._track_application(job_data, application_package, automation_result, document_paths)
            
            # Step 7: Compile final result
            final_result = {
                'job_info': application_package['job_info'],
                'contact_details': contact_details,
                'documents': {
                    'resume_path': document_paths.get('resume'),
                    'cover_letter_path': document_paths.get('cover_letter'),
                    'linkedin_message': linkedin_message
                },
                'automation_result': automation_result,
                'tracking_result': tracking_result,
                'application_strategy': application_package['application_strategy'],
                'next_steps': application_package['next_steps'],
                'generated_at': datetime.now().isoformat(),
                'platform': job_data.get('platform'),
                'priority_score': job_data.get('priority_score', 0)
            }
            
            logger.info(f"SUCCESS: Application processing complete for {job_data.get('title')}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing application: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'job_info': {
                    'title': job_data.get('title', 'Unknown'),
                    'company': job_data.get('company', 'Unknown'),
                    'platform': job_data.get('platform', 'Unknown')
                }
            }
    
    def _save_application_documents(self, job_data: Dict, application_package: Dict) -> Dict[str, str]:
        """Save resume and cover letter documents"""
        try:
            company = job_data.get('company', 'Unknown').replace(' ', '_').replace(',', '')
            title = job_data.get('title', 'Unknown').replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save tailored resume
            resume_filename = f"{company}_{title}_Resume_{timestamp}.txt"
            resume_path = self.document_manager.save_document(
                application_package['documents']['tailored_resume'],
                resume_filename,
                doc_type='resume'
            )
            
            # Save cover letter
            cover_letter_filename = f"{company}_{title}_CoverLetter_{timestamp}.txt"
            cover_letter_path = self.document_manager.save_document(
                application_package['documents']['cover_letter'],
                cover_letter_filename,
                doc_type='cover_letter'
            )
            
            logger.info(f"Documents saved: Resume and Cover Letter for {company}")
            return {
                'resume': resume_path,
                'cover_letter': cover_letter_path
            }
            
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
            return {}
    
    def _attempt_automated_application(self, job_data: Dict, application_package: Dict) -> Dict[str, Any]:
        """Attempt automated application through the job platform"""
        try:
            if not self.application_handler:
                return {
                    'status': 'manual_required',
                    'method': 'no_automation',
                    'reason': 'No application handler available'
                }
            
            # Prepare job details in format expected by application handler
            job_details = {
                'url': job_data.get('url'),
                'title': job_data.get('title'),
                'company': job_data.get('company'),
                'location': job_data.get('location'),
                'portal': job_data.get('platform', 'unknown'),
                'description': job_data.get('description', '')
            }
            
            cover_letter = application_package['documents']['cover_letter']
            
            # Attempt application
            result = self.application_handler.apply_to_job(job_details, cover_letter)
            
            # Enhance result with additional information
            result['contact_strategy'] = self._get_contact_strategy(application_package['contact_details'])
            result['platform'] = job_data.get('platform')
            
            return result
            
        except Exception as e:
            logger.error(f"Error in automated application: {e}")
            return {
                'status': 'automation_failed',
                'method': 'automation_error',
                'error': str(e),
                'fallback': 'Manual application required'
            }
    
    def _get_contact_strategy(self, contact_details: Dict) -> str:
        """Generate contact strategy based on extracted contact details"""
        strategies = []
        
        if contact_details.get('emails'):
            strategies.append(f"📧 Direct email to {contact_details['emails'][0]}")
        
        if contact_details.get('contact_names'):
            strategies.append(f"👤 Personal outreach to {contact_details['contact_names'][0]}")
        
        if contact_details.get('linkedin_company'):
            strategies.append(f"🔗 LinkedIn company page: {contact_details['linkedin_company']}")
        
        if contact_details.get('phones'):
            strategies.append(f"📞 Phone contact: {contact_details['phones'][0]}")
        
        if not strategies:
            strategies.append("🌐 Standard application process")
        
        return " | ".join(strategies)
    
    def _track_application(self, job_data: Dict, application_package: Dict, 
                          automation_result: Dict, document_paths: Dict) -> Dict[str, Any]:
        """Track application in Google Sheets"""
        try:
            # Prepare tracking data with correct field names for sheets manager
            tracking_data = {
                'title': job_data.get('title', ''),
                'company': job_data.get('company', ''),
                'location': job_data.get('location', ''),
                'platform': job_data.get('platform', '').title(),
                'salary': job_data.get('salary', 'Not specified'),
                'url': job_data.get('url', ''),
                'priority_score': job_data.get('priority_score', 0),
                'status': automation_result.get('status', 'Processed'),
                'application_method': 'Enhanced Automation',
                'contact_details_count': len(application_package['contact_details'].get('emails', [])),
                'resume_link': document_paths.get('resume', ''),
                'cover_letter_link': document_paths.get('cover_letter', ''),
                'notes': f"Generated via Apify {job_data.get('platform', '')} integration",
                'job_type': job_data.get('job_type', 'Full-time'),
                'portal': job_data.get('platform', ''),
                'application_status': 'Applied',
                'outreach_message': application_package.get('linkedin_message', '')[:100] if application_package.get('linkedin_message') else ''
            }
            
            # Add to Google Sheets
            result = self.sheets_manager.add_job_application(tracking_data)
            
            logger.info(f"Application tracked in Google Sheets for {job_data.get('company')}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking application: {e}")
            return {'status': 'tracking_failed', 'error': str(e)}
    
    def generate_application_summary(self, applications: List[Dict]) -> str:
        """Generate a summary of processed applications"""
        try:
            total_apps = len(applications)
            successful_automations = len([app for app in applications if app.get('automation_result', {}).get('status') == 'success'])
            manual_required = len([app for app in applications if app.get('automation_result', {}).get('status') in ['manual_required', 'automation_failed']])
            
            platforms = {}
            for app in applications:
                platform = app.get('platform', 'unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
            
            companies = [app.get('job_info', {}).get('company', 'Unknown') for app in applications]
            
            summary = f'''
📊 APPLICATION PROCESSING SUMMARY
================================

✅ Total Applications Processed: {total_apps}
🤖 Automated Successfully: {successful_automations}
✋ Manual Required: {manual_required}

📱 Platform Breakdown:
{chr(10).join([f"   {platform.title()}: {count}" for platform, count in platforms.items()])}

🏢 Companies Applied To:
{chr(10).join([f"   • {company}" for company in companies[:10]])}
{"   • ... and more" if len(companies) > 10 else ""}

💡 Next Steps:
   1. Review manual applications and submit directly
   2. Follow up via LinkedIn with hiring managers  
   3. Monitor application status in Google Sheets
   4. Prepare for potential interviews

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            '''
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary generation failed: {str(e)}"

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample Apify job data
    sample_job = {
        'title': 'Frontend Developer',
        'company': 'Amazon Web Services',
        'description': 'Looking for React.js developer... Contact hiring@aws.com',
        'location': 'San Francisco, CA',
        'salary': '$120k-150k',
        'platform': 'indeed',
        'url': 'https://indeed.com/job/123',
        'priority_score': 85
    }
    
    processor = EnhancedApplicationProcessor()
    result = processor.process_apify_job_application(sample_job, automation_mode=False)
    print("Application processed:", result.get('job_info', {}).get('title'))
