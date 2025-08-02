"""
Cloud Document Management for Resumes and Cover Letters
AWS S3 + GitHub Gist Hybrid Storage Solution
"""

import os
import json
import logging
from datetime import datetime
import requests
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self):
        self.setup_storage_services()
        
    def setup_storage_services(self):
        """Setup cloud storage services (S3 + GitHub Gist)"""
        try:
            from config.api_keys import APIKeys
            
            # Detect environment
            self.is_aws_environment = self._detect_aws_environment()
            
            # Setup S3 for AWS deployment
            if self.is_aws_environment:
                try:
                    self.s3_client = boto3.client('s3')
                    self.bucket_name = os.getenv('S3_BUCKET_NAME', 'himanshu-job-automation-docs')
                    logger.info("AWS S3 setup completed")
                except Exception as e:
                    logger.warning(f"S3 setup failed, falling back to GitHub: {e}")
                    self.is_aws_environment = False
            
            # Setup GitHub Gist (fallback or development)
            self.github_token = getattr(APIKeys, 'GITHUB_TOKEN', None)
            self.github_api_url = "https://api.github.com/gists"
            
            logger.info(f"Storage setup: AWS={self.is_aws_environment}, GitHub={'✓' if self.github_token else '✗'}")
            
        except Exception as e:
            logger.error(f"Error setting up storage services: {e}")
    
    def _detect_aws_environment(self):
        """Detect if running in AWS environment"""
        aws_indicators = [
            os.getenv('AWS_EXECUTION_ENV'),
            os.getenv('AWS_LAMBDA_FUNCTION_NAME'),
            os.getenv('AWS_REGION'),
            os.path.exists('/var/task'),  # Lambda indicator
            os.path.exists('/opt/aws')     # EC2 indicator
        ]
        return any(aws_indicators)
    
    def create_resume_document(self, tailored_resume, job_details):
        """Create and store tailored resume document"""
        try:
            company_name = job_details.get('company', 'Company').replace(' ', '_').replace('/', '_')
            job_title = job_details.get('title', 'Job').replace(' ', '_').replace('/', '_')
            date_str = datetime.now().strftime('%Y%m%d_%H%M')
            
            filename = f"Resume_Himanshu_{company_name}_{job_title}_{date_str}"
            
            # Try AWS S3 first, fallback to GitHub Gist
            if self.is_aws_environment and hasattr(self, 's3_client'):
                return self._upload_to_s3(tailored_resume, filename, 'resume')
            else:
                return self._create_github_gist(tailored_resume, filename, 'resume', job_details)
            
        except Exception as e:
            logger.error(f"Error creating resume document: {e}")
            return f"Resume creation failed: {str(e)}"
    
    def create_cover_letter_document(self, cover_letter, job_details):
        """Create and store cover letter document"""
        try:
            company_name = job_details.get('company', 'Company').replace(' ', '_').replace('/', '_')
            job_title = job_details.get('title', 'Job').replace(' ', '_').replace('/', '_')
            date_str = datetime.now().strftime('%Y%m%d_%H%M')
            
            filename = f"CoverLetter_Himanshu_{company_name}_{job_title}_{date_str}"
            
            # Try AWS S3 first, fallback to GitHub Gist
            if self.is_aws_environment and hasattr(self, 's3_client'):
                return self._upload_to_s3(cover_letter, filename, 'cover_letter')
            else:
                return self._create_github_gist(cover_letter, filename, 'cover_letter', job_details)
            
        except Exception as e:
            logger.error(f"Error creating cover letter document: {e}")
            return f"Cover letter creation failed: {str(e)}"
    
    def _upload_to_s3(self, content, filename, doc_type):
        """Upload document to AWS S3"""
        try:
            key = f"{doc_type}s/{filename}.txt"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain',
                ACL='public-read'  # Make publicly accessible
            )
            
            # Return public URL
            public_url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            logger.info(f"Document uploaded to S3: {public_url}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            # Fallback to GitHub Gist
            return self._create_github_gist(content, filename, doc_type, {})
    
    def save_document(self, content, filename, doc_type='document', job_details=None):
        """
        Generic save document method for enhanced application processor
        """
        try:
            if not job_details:
                job_details = {}
            
            # Try AWS S3 first, fallback to GitHub Gist
            if self.is_aws_environment and hasattr(self, 's3_client'):
                return self._upload_to_s3(content, filename, doc_type)
            else:
                return self._create_github_gist(content, filename, doc_type, job_details)
            
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return f"Document save failed: {str(e)}"
    
    def _create_github_gist(self, content, filename, doc_type, job_details):
        """Create GitHub Gist as fallback storage"""
        try:
            if not self.github_token:
                logger.warning("No GitHub token available")
                return f"Document saved locally: {filename}.txt"
            
            # Prepare gist data
            company = job_details.get('company', 'Company')
            title = job_details.get('title', 'Position')
            
            gist_data = {
                "description": f"{doc_type.title()} for {title} at {company} - Generated {datetime.now().strftime('%Y-%m-%d')}",
                "public": True,  # Make it publicly accessible
                "files": {
                    f"{filename}.txt": {
                        "content": content
                    }
                }
            }
            
            # Create gist
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.post(self.github_api_url, 
                                   headers=headers, 
                                   json=gist_data,
                                   timeout=10)
            
            if response.status_code == 201:
                gist_url = response.json().get('html_url')
                raw_url = response.json().get('files', {}).get(f"{filename}.txt", {}).get('raw_url')
                
                logger.info(f"GitHub Gist created: {gist_url}")
                return raw_url or gist_url  # Prefer raw URL for direct access
            else:
                logger.error(f"GitHub Gist creation failed: {response.status_code}")
                return f"Document created but upload failed: {filename}.txt"
            
        except Exception as e:
            logger.error(f"GitHub Gist creation failed: {e}")
            return f"Document saved locally: {filename}.txt"