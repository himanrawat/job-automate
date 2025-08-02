"""
Google Sheets Management for Job Application Tracking
"""

import logging
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
from config.api_keys import APIKeys
from config.user_profile import HimanshuProfile
import tempfile
import json

logger = logging.getLogger(__name__)

class SheetsManager:
    def __init__(self):
        self.setup_sheets()
        self.region_sheets = {}
        
    def setup_sheets(self):
        """Setup Google Sheets API"""
        try:
            # Create temporary credentials file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(APIKeys.GOOGLE_CREDENTIALS, f)
                creds_path = f.name
                
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(creds_path, scopes=scope)
            self.gc = gspread.authorize(creds)
            
            # Create or open main spreadsheet
            try:
                self.spreadsheet = self.gc.open("Himanshu Rawat - Job Applications Tracker")
            except gspread.SpreadsheetNotFound:
                self.spreadsheet = self.gc.create("Himanshu Rawat - Job Applications Tracker")
                self.spreadsheet.share(HimanshuProfile.PERSONAL_INFO['email'], perm_type='user', role='owner')
                self.spreadsheet.share('officialhimanshurawat@gmail.com', perm_type='user', role='writer')
            
            logger.info("Google Sheets setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Google Sheets: {e}")
    
    def create_region_worksheet(self, region_name):
        """Create worksheet for specific region"""
        try:
            worksheet_name = f"{region_name}_{datetime.now().strftime('%Y_%m')}"
            
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=25)
                
                # Enhanced headers for manual application tracking
                headers = [
                    'Date Applied', 'Job Title', 'Company', 'Location', 'Portal', 
                    'Job URL', 'Applied Status', 'Application Method', 'Salary Range',
                    'Recruiter Name', 'Recruiter Contact', 'Recruiter Platform', 
                    'Outreach Message', 'Response Status', 'Interview Date', 
                    'Follow-up Date', 'Notes', 'Job Description Keywords', 
                    'Match Score', 'Next Action', 'Visa Sponsorship', 'Job Type',
                    'Direct Application Link', 'Failure Reason', 'Suggested Approach', 
                    'Priority Level', 'Resume Link', 'Cover Letter Link', 'Est. Time'
                ]
                worksheet.append_row(headers)
                
                # Format headers
                worksheet.format('A1:AC1', {
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                })
            
            self.region_sheets[region_name] = worksheet
            return worksheet
            
        except Exception as e:
            logger.error(f"Error creating worksheet for {region_name}: {e}")
            return None
    
    def update_application_row(self, region, job_data):
        """Update spreadsheet with comprehensive job application data"""
        try:
            worksheet = self.region_sheets.get(region)
            if not worksheet:
                worksheet = self.create_region_worksheet(region)
            
            if not worksheet:
                return
            
            # Comprehensive row data with all manual application details
            row_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),    # Date Applied
                job_data.get('title', ''),                       # Job Title
                job_data.get('company', ''),                     # Company
                job_data.get('location', ''),                    # Location
                job_data.get('portal', ''),                      # Portal
                job_data.get('url', ''),                         # Job URL
                job_data.get('application_status', ''),          # Applied Status
                job_data.get('application_method', ''),          # Application Method
                job_data.get('salary', ''),                      # Salary Range
                job_data.get('recruiter_name', ''),              # Recruiter Name
                job_data.get('recruiter_contact', ''),           # Recruiter Contact
                job_data.get('recruiter_platform', ''),          # Recruiter Platform
                job_data.get('outreach_message', ''),            # Outreach Message
                'Pending',                                        # Response Status
                '',                                              # Interview Date
                (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),  # Follow-up Date
                job_data.get('notes', ''),                       # Notes
                job_data.get('keywords', ''),                    # Job Description Keywords
                job_data.get('match_score', ''),                 # Match Score
                job_data.get('next_action', ''),                 # Next Action
                job_data.get('visa_sponsorship', ''),            # Visa Sponsorship
                job_data.get('job_type', 'Full-time'),           # Job Type
                job_data.get('direct_application_link', ''),     # Direct Application Link
                job_data.get('failure_reason', ''),              # Failure Reason
                job_data.get('suggested_approach', ''),          # Suggested Approach
                job_data.get('priority_level', ''),              # Priority Level
                job_data.get('resume_link', ''),                 # Resume Link
                job_data.get('cover_letter_link', ''),           # Cover Letter Link
                job_data.get('estimated_time', '')               # Estimated Time
            ]
            
            # Append row to worksheet
            worksheet.append_row(row_data)
            
            # Apply conditional formatting based on status and priority
            row_number = len(worksheet.get_all_values())
            self.format_application_row(worksheet, row_number, job_data)
            
            logger.info(f"Updated {region} spreadsheet: {job_data.get('title', 'job')} at {job_data.get('company', 'company')}")
            
        except Exception as e:
            logger.error(f"Error updating spreadsheet for {region}: {e}")
    
    def format_application_row(self, worksheet, row_number, job_data):
        """Apply conditional formatting to application row"""
        try:
            status = job_data.get('application_status', '')
            priority = job_data.get('priority_level', '')
            
            # Color coding based on status and priority
            if status == "Applied Successfully":
                # Green for successful applications
                worksheet.format(f"A{row_number}:AC{row_number}", {
                    'backgroundColor': {'red': 0.8, 'green': 1, 'blue': 0.8}
                })
            elif "Manual Required" in status:
                if "High 🔥" in priority:
                    # Orange for high priority manual applications
                    worksheet.format(f"A{row_number}:AC{row_number}", {
                        'backgroundColor': {'red': 1, 'green': 0.8, 'blue': 0.6}
                    })
                else:
                    # Yellow for regular manual applications
                    worksheet.format(f"A{row_number}:AC{row_number}", {
                        'backgroundColor': {'red': 1, 'green': 1, 'blue': 0.8}
                    })
            else:
                # Light red for failed applications
                worksheet.format(f"A{row_number}:AC{row_number}", {
                    'backgroundColor': {'red': 1, 'green': 0.8, 'blue': 0.8}
                })
            
        except Exception as e:
            logger.error(f"Error formatting row: {e}")