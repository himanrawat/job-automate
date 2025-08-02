"""
Quick test for shared spreadsheet access
"""
import gspread
from google.oauth2.service_account import Credentials
import tempfile
import json
import os
from config.api_keys import APIKeys

def quick_test():
    try:
        print("🧪 Testing shared spreadsheet access...")
        
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
        
        # Try to open the shared spreadsheet
        spreadsheet = gc.open("Himanshu Rawat - Job Applications Tracker")
        print(f"✓ SUCCESS: Accessed spreadsheet '{spreadsheet.title}'")
        print(f"✓ URL: {spreadsheet.url}")
        
        os.unlink(creds_path)
        return True
        
    except gspread.SpreadsheetNotFound:
        print("✗ FAILED: Spreadsheet not found or not shared with service account")
        print("Please make sure you:")
        print("1. Created the spreadsheet with exact name: 'Himanshu Rawat - Job Applications Tracker'")
        print("2. Shared it with: job-automate-sheet@job-automate-467805.iam.gserviceaccount.com")
        print("3. Set permission to 'Editor'")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    quick_test()
