"""
API Keys Configuration Template
Copy this file to api_keys.py and add your actual API keys
"""

class APIKeys:
    # OpenAI API Key - Get from https://platform.openai.com/api-keys
    OPENAI_API_KEY = "your_openai_api_key_here"
    
    # Google Service Account JSON - Get from Google Cloud Console
    GOOGLE_CREDENTIALS = {
        "type": "service_account",
        "project_id": "your_project_id",
        "private_key_id": "your_private_key_id", 
        "private_key": "your_private_key",
        "client_email": "your_service_account_email",
        "client_id": "your_client_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "your_cert_url"
    }
    
    # LinkedIn API credentials (if needed)
    LINKEDIN_CLIENT_ID = "your_linkedin_client_id"
    LINKEDIN_CLIENT_SECRET = "your_linkedin_client_secret"
    
    # Other job site API keys (add as needed)
    NAUKRI_API_KEY = "your_naukri_api_key"
