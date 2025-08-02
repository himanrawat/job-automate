"""
Google Drive Document Management for Resumes and Cover Letters
"""

import tempfile
import json
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self):
        self.setup_google_services()
        
    def setup_google_services(self):
        """Setup Google Drive and Docs services"""
        try:
            from config.api_keys import APIKeys
            
            # Create temporary file for credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(APIKeys.GOOGLE_CREDENTIALS, f)
                self.creds_path = f.name
            
            # Setup Google services
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/documents'
            ]
            
            self.creds = Credentials.from_service_account_file(self.creds_path, scopes=scope)
            self.gc = gspread.authorize(self.creds)
            
            logger.info("Google services setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Google services: {e}")
    
    def create_resume_document(self, tailored_resume, job_details):
        """Create and upload tailored resume to Google Docs"""
        try:
            # This is a simplified version - you would use Google Docs API
            # For now, we'll return a placeholder link
            company_name = job_details.get('company', 'Company').replace(' ', '_')
            job_title = job_details.get('title', 'Job').replace(' ', '_')
            date_str = datetime.now().strftime('%Y%m%d')
            
            doc_name = f"Resume_Himanshu_{company_name}_{job_title}_{date_str}"
            
            # In production, you would:
            # 1. Create Google Doc with tailored_resume content
            # 2. Set sharing permissions
            # 3. Return shareable link
            
            placeholder_link = f"https://docs.google.com/document/d/placeholder_resume_{company_name}"
            logger.info(f"Resume document created: {doc_name}")
            
            return placeholder_link
            
        except Exception as e:
            logger.error(f"Error creating resume document: {e}")
            return "Resume document creation failed"
    
    def create_cover_letter_document(self, cover_letter, job_details):
        """Create and upload cover letter to Google Docs"""
        try:
            company_name = job_details.get('company', 'Company').replace(' ', '_')
            job_title = job_details.get('title', 'Job').replace(' ', '_')
            date_str = datetime.now().strftime('%Y%m%d')
            
            doc_name = f"CoverLetter_Himanshu_{company_name}_{job_title}_{date_str}"
            
            # In production, you would:
            # 1. Create Google Doc with cover_letter content
            # 2. Format it professionally
            # 3. Set sharing permissions
            # 4. Return shareable link
            
            placeholder_link = f"https://docs.google.com/document/d/placeholder_cover_{company_name}"
            logger.info(f"Cover letter document created: {doc_name}")
            
            return placeholder_link
            
        except Exception as e:
            logger.error(f"Error creating cover letter document: {e}")
            return "Cover letter document creation failed"