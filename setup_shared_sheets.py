"""
Alternative Google Sheets Setup - Using Personal Drive Storage
Creates spreadsheets in your personal Drive account and shares them with the service account
"""

import gspread
from google.oauth2.service_account import Credentials
import tempfile
import json
import os
from config.api_keys import APIKeys
from config.user_profile import HimanshuProfile

def setup_shared_spreadsheet():
    """
    Setup approach that creates spreadsheets in your personal account
    and shares them with the service account
    """
    print("🔧 Setting up shared spreadsheet approach...")
    
    try:
        # Get service account credentials
        credentials_dict = APIKeys.get_google_credentials()
        service_account_email = credentials_dict.get('client_email')
        
        print(f"Service Account: {service_account_email}")
        print("\n📋 MANUAL SETUP REQUIRED:")
        print("Since the service account has limited storage, you need to:")
        print("1. Go to https://sheets.google.com")
        print("2. Create a new spreadsheet named 'Himanshu Rawat - Job Applications Tracker'")
        print("3. Click 'Share' button")
        print(f"4. Add this email as an Editor: {service_account_email}")
        print("5. Make sure 'Notify people' is unchecked")
        print("6. Click 'Send'")
        print("\nOnce you've done this, the application will work properly!")
        
        return service_account_email
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_existing_spreadsheet():
    """Test if we can access an existing shared spreadsheet"""
    try:
        print("\n🧪 Testing access to existing spreadsheet...")
        
        credentials_dict = APIKeys.get_google_credentials()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            creds_path = f.name
            
        scope = [
            'https://spreadsheets.google.com/feeds', 
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        gc = gspread.authorize(creds)
        
        # Try to open the expected spreadsheet
        try:
            spreadsheet = gc.open("Himanshu Rawat - Job Applications Tracker")
            print(f"✓ Successfully accessed shared spreadsheet: {spreadsheet.title}")
            print(f"✓ Spreadsheet URL: {spreadsheet.url}")
            
            # Test writing to it
            worksheet = spreadsheet.sheet1
            worksheet.update('A1', 'Test from service account')
            print("✓ Successfully wrote to shared spreadsheet")
            
            os.unlink(creds_path)
            return True, "Shared spreadsheet access working perfectly!"
            
        except gspread.SpreadsheetNotFound:
            print("✗ Spreadsheet not found or not shared with service account")
            os.unlink(creds_path)
            return False, "Spreadsheet not found - please create and share it manually"
            
    except Exception as e:
        return False, f"Error testing spreadsheet: {str(e)}"

if __name__ == "__main__":
    print("🚀 Google Sheets Shared Setup Helper")
    print("=" * 50)
    
    # Show setup instructions
    service_account = setup_shared_spreadsheet()
    
    if service_account:
        print("\n" + "=" * 50)
        print("Press Enter after you've completed the manual setup to test...")
        input()
        
        # Test the setup
        success, message = test_existing_spreadsheet()
        print(f"\n📊 TEST RESULT: {'✓ SUCCESS' if success else '✗ FAILED'}")
        print(f"Message: {message}")
        
        if success:
            print("\n🎉 Great! Your application should now work with Google Sheets!")
        else:
            print("\n❌ Setup incomplete. Please follow the manual steps above.")
