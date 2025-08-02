"""
CSV-based data manager as fallback for Google Sheets
"""

import logging
import os
import csv
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class CSVDataManager:
    def __init__(self):
        self.data_dir = "job_data"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def get_csv_filename(self, region_name):
        """Get CSV filename for region"""
        current_month = datetime.now().strftime('%Y_%m')
        return os.path.join(self.data_dir, f"{region_name}_{current_month}.csv")
    
    def create_region_csv(self, region_name):
        """Create CSV file for specific region"""
        try:
            csv_file = self.get_csv_filename(region_name)
            
            # Headers for job application tracking
            headers = [
                'Date Applied', 'Job Title', 'Company', 'Location', 'Portal', 
                'Job URL', 'Applied Status', 'Application Method', 'Salary Range',
                'Recruiter Name', 'Recruiter Contact', 'Recruiter Platform', 
                'Application Priority', 'Required Skills', 'Experience Level',
                'Employment Type', 'Industry', 'Company Size', 'Remote Work',
                'Application Response', 'Interview Status', 'Follow-up Date',
                'Notes', 'Cover Letter Used', 'Resume Version'
            ]
            
            # Create CSV if it doesn't exist
            if not os.path.exists(csv_file):
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                logger.info(f"Created CSV file: {csv_file}")
            
            return csv_file
            
        except Exception as e:
            logger.error(f"Error creating CSV for {region_name}: {e}")
            return None
    
    def add_job_application(self, region_name, job_data):
        """Add job application to CSV"""
        try:
            csv_file = self.create_region_csv(region_name)
            if not csv_file:
                return False
            
            # Prepare data row
            row_data = [
                job_data.get('date_applied', datetime.now().strftime('%Y-%m-%d %H:%M')),
                job_data.get('job_title', ''),
                job_data.get('company', ''),
                job_data.get('location', ''),
                job_data.get('portal', ''),
                job_data.get('job_url', ''),
                job_data.get('applied_status', 'Manual Required'),
                job_data.get('application_method', ''),
                job_data.get('salary_range', ''),
                job_data.get('recruiter_name', ''),
                job_data.get('recruiter_contact', ''),
                job_data.get('recruiter_platform', ''),
                job_data.get('priority', ''),
                job_data.get('required_skills', ''),
                job_data.get('experience_level', ''),
                job_data.get('employment_type', ''),
                job_data.get('industry', ''),
                job_data.get('company_size', ''),
                job_data.get('remote_work', ''),
                job_data.get('application_response', ''),
                job_data.get('interview_status', ''),
                job_data.get('follow_up_date', ''),
                job_data.get('notes', ''),
                job_data.get('cover_letter_used', ''),
                job_data.get('resume_version', '')
            ]
            
            # Append to CSV
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row_data)
            
            logger.info(f"Added job application to {csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding job application: {e}")
            return False
    
    def get_applications_summary(self, region_name):
        """Get summary of applications for region"""
        try:
            csv_file = self.get_csv_filename(region_name)
            if not os.path.exists(csv_file):
                return {"total": 0, "today": 0}
            
            df = pd.read_csv(csv_file)
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            total_applications = len(df)
            today_applications = len(df[df['Date Applied'].str.contains(today_date, na=False)])
            
            return {
                "total": total_applications,
                "today": today_applications,
                "csv_file": csv_file
            }
            
        except Exception as e:
            logger.error(f"Error getting applications summary: {e}")
            return {"total": 0, "today": 0, "error": str(e)}
    
    def export_to_excel(self, region_name):
        """Export CSV data to Excel format"""
        try:
            csv_file = self.get_csv_filename(region_name)
            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found: {csv_file}")
                return None
            
            df = pd.read_csv(csv_file)
            excel_file = csv_file.replace('.csv', '.xlsx')
            df.to_excel(excel_file, index=False, engine='openpyxl')
            
            logger.info(f"Exported data to Excel: {excel_file}")
            return excel_file
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    def list_all_data_files(self):
        """List all data files created"""
        try:
            files = []
            if os.path.exists(self.data_dir):
                for file in os.listdir(self.data_dir):
                    if file.endswith(('.csv', '.xlsx')):
                        file_path = os.path.join(self.data_dir, file)
                        file_size = os.path.getsize(file_path)
                        files.append({
                            'name': file,
                            'path': file_path,
                            'size': file_size,
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                        })
            return files
        except Exception as e:
            logger.error(f"Error listing data files: {e}")
            return []
