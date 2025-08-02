"""
API Keys Configuration
Loads API keys from environment variables for security
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class APIKeys:
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Service Account JSON - constructed from environment variables
    @staticmethod
    def get_google_credentials():
        """Get Google credentials with proper private key formatting"""
        private_key = os.getenv('GOOGLE_PRIVATE_KEY')
        if private_key:
            # Replace escaped newlines with actual newlines
            private_key = private_key.replace('\\n', '\n')
        
        return {
            "type": "service_account",
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": private_key,
            "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
            "token_uri": os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
            "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
        }
    
    # Make GOOGLE_CREDENTIALS accessible as a class attribute
    GOOGLE_CREDENTIALS = None  # Will be set after class definition
    
    # LinkedIn API credentials (if needed)
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # GitHub token for Gist storage
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # Other job site API keys (add as needed)
    NAUKRI_API_KEY = os.getenv('NAUKRI_API_KEY')
    
    @staticmethod
    def validate_keys():
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not APIKeys.OPENAI_API_KEY:
            missing_keys.append('OPENAI_API_KEY')
        
        google_creds = APIKeys.GOOGLE_CREDENTIALS
        if not google_creds or not google_creds.get('project_id'):
            missing_keys.append('GOOGLE_PROJECT_ID')
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True

# Set GOOGLE_CREDENTIALS as a class attribute after class definition
APIKeys.GOOGLE_CREDENTIALS = APIKeys.get_google_credentials()
