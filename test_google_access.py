"""
Google Drive API Test Script
Tests your current service account setup
"""

import os
import sys
import tempfile
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.api_keys import APIKeys

def test_google_drive_access():
    """Test Google Drive API access with current credentials"""
    try:
        print("🔍 Testing Google Drive API access...")
        
        # Get credentials
        credentials_dict = APIKeys.get_google_credentials()
        print(f"✓ Loaded credentials for project: {credentials_dict.get('project_id', 'Unknown')}")
        print(f"✓ Service account: {credentials_dict.get('client_email', 'Unknown')}")
        
        # Create temporary credentials file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(credentials_dict, f)
            creds_path = f.name
            
        # Create credentials object
        scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        print("✓ Credentials loaded successfully")
        
        # Test Drive API
        drive_service = build('drive', 'v3', credentials=creds)
        print("✓ Drive service created")
        
        # Test: List files (this should work)
        print("\n📂 Testing file listing...")
        results = drive_service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"✓ Found {len(files)} files in Drive")
        for file in files[:3]:
            print(f"  - {file['name']} (ID: {file['id']})")
        
        # Test: Create a test file (this might fail)
        print("\n📝 Testing file creation...")
        file_metadata = {
            'name': 'test-job-automation-access',
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        try:
            test_file = drive_service.files().create(body=file_metadata).execute()
            print(f"✓ Successfully created test file: {test_file['name']} (ID: {test_file['id']})")
            
            # Clean up test file
            drive_service.files().delete(fileId=test_file['id']).execute()
            print("✓ Test file cleaned up")
            
            return True, "All tests passed! Your service account has proper permissions."
            
        except Exception as create_error:
            error_msg = str(create_error)
            print(f"✗ Failed to create test file: {error_msg}")
            
            if "quotaExceeded" in error_msg or "storage quota" in error_msg:
                return False, "QUOTA_ISSUE: Your Google Drive storage is full or service account lacks storage permissions"
            elif "forbidden" in error_msg or "403" in error_msg:
                return False, "PERMISSION_ISSUE: Service account lacks proper Drive permissions"
            else:
                return False, f"UNKNOWN_ISSUE: {error_msg}"
        
        # Clean up temp file
        os.unlink(creds_path)
        
    except Exception as e:
        return False, f"SETUP_ERROR: {str(e)}"

def test_sheets_api():
    """Test Google Sheets API access"""
    try:
        print("\n📊 Testing Google Sheets API...")
        import gspread
        
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
        print("✓ Sheets client authorized")
        
        # Try to list spreadsheets by creating a simple test sheet
        try:
            # Test creating a spreadsheet (this should work even with storage limits)
            test_sheet = gc.create('test-job-automation-sheets-access')
            print(f"✓ Successfully created test spreadsheet: {test_sheet.title}")
            
            # Try to access the sheet
            worksheet = test_sheet.sheet1
            worksheet.update('A1', 'Test')
            print("✓ Successfully wrote to spreadsheet")
            
            # Clean up test spreadsheet
            gc.del_spreadsheet(test_sheet.id)
            print("✓ Test spreadsheet cleaned up")
            
            return True, "Sheets API access working perfectly"
            
        except Exception as sheets_error:
            error_msg = str(sheets_error)
            print(f"✗ Sheets test failed: {error_msg}")
            
            if "quotaExceeded" in error_msg or "storage quota" in error_msg:
                return False, f"STORAGE_ISSUE: {error_msg}"
            elif "forbidden" in error_msg or "403" in error_msg:
                return False, f"PERMISSION_ISSUE: {error_msg}"
            else:
                return False, f"SHEETS_ERROR: {error_msg}"
        
        os.unlink(creds_path)
        
    except Exception as e:
        return False, f"Sheets API error: {str(e)}"

if __name__ == "__main__":
    print("🚀 Google Drive & Sheets API Test")
    print("=" * 50)
    
    # Test Drive API
    drive_success, drive_message = test_google_drive_access()
    
    # Test Sheets API  
    sheets_success, sheets_message = test_sheets_api()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"Drive API: {'✓ PASS' if drive_success else '✗ FAIL'} - {drive_message}")
    print(f"Sheets API: {'✓ PASS' if sheets_success else '✗ FAIL'} - {sheets_message}")
    
    if not drive_success:
        print("\n🔧 RECOMMENDED ACTIONS:")
        if "QUOTA_ISSUE" in drive_message:
            print("1. Check your Google Drive storage - you may need to clear space")
            print("2. Verify service account has Storage Admin role")
            print("3. Consider using a different Google account with more storage")
        elif "PERMISSION_ISSUE" in drive_message:
            print("1. Go to Google Cloud Console → IAM & Admin → Service Accounts")
            print("2. Find your service account and click on it")
            print("3. Add these roles: 'Editor' and 'Storage Admin'")
            print("4. Regenerate the service account key (JSON)")
            print("5. Update your .env file with new credentials")
        else:
            print("1. Regenerate your service account key")
            print("2. Ensure all required APIs are enabled:")
            print("   - Google Drive API")
            print("   - Google Sheets API")
            print("   - Google Docs API")
