#!/usr/bin/env python3
"""
Test script to validate setup and fix configuration issues
"""

import logging
import os
from config.api_keys import APIKeys
from utils.browser_setup import BrowserManager
from utils.sheets_manager import SheetsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_google_credentials():
    """Test Google credentials setup"""
    print("🔑 Testing Google Credentials...")
    try:
        creds = APIKeys.get_google_credentials()
        if not creds.get('project_id'):
            print("❌ Google Project ID missing")
            return False
        if not creds.get('private_key'):
            print("❌ Google Private Key missing")
            return False
        print("✅ Google credentials configured")
        return True
    except Exception as e:
        print(f"❌ Error with Google credentials: {e}")
        return False

def test_browser_setup():
    """Test browser setup"""
    print("\n🌐 Testing Browser Setup...")
    try:
        browser_manager = BrowserManager()
        driver = browser_manager.setup_browser()
        if driver:
            print("✅ Browser setup successful")
            browser_manager.close_browser()
            return True
        else:
            print("❌ Browser setup failed")
            return False
    except Exception as e:
        print(f"❌ Error with browser setup: {e}")
        return False

def test_sheets_connection():
    """Test Google Sheets connection"""
    print("\n📊 Testing Google Sheets Connection...")
    try:
        sheets_manager = SheetsManager()
        if hasattr(sheets_manager, 'spreadsheet') and sheets_manager.spreadsheet:
            print("✅ Google Sheets connection successful")
            return True
        else:
            print("❌ Google Sheets connection failed")
            return False
    except Exception as e:
        print(f"❌ Error with Google Sheets: {e}")
        return False

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n💡 Solutions for Common Issues:")
    print("=" * 50)
    
    print("\n1. Google Drive API Error (403):")
    print("   - Go to: https://console.developers.google.com/apis/api/drive.googleapis.com/overview")
    print("   - Select your project: job-automate-467805")
    print("   - Click 'Enable' for Google Drive API")
    print("   - Also enable Google Sheets API if not already enabled")
    
    print("\n2. ChromeDriver Issues:")
    print("   - Install latest Chrome browser")
    print("   - The script will auto-download compatible ChromeDriver")
    print("   - Ensure no antivirus blocking the download")
    
    print("\n3. Google Sheets Permissions:")
    print("   - Your service account email: job-automate-sheet@job-automate-467805.iam.gserviceaccount.com")
    print("   - Share your Google Sheet with this email")
    print("   - Give it 'Editor' permissions")
    
    print("\n4. Environment Variables:")
    print("   - Check .env file exists and has all required values")
    print("   - Private key should have proper newlines (\\n)")
    
if __name__ == "__main__":
    print("🚀 Job Automation Setup Test")
    print("=" * 50)
    
    # Run tests
    google_ok = test_google_credentials()
    browser_ok = test_browser_setup()
    sheets_ok = test_sheets_connection()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"Google Credentials: {'✅' if google_ok else '❌'}")
    print(f"Browser Setup: {'✅' if browser_ok else '❌'}")
    print(f"Google Sheets: {'✅' if sheets_ok else '❌'}")
    
    if not all([google_ok, browser_ok, sheets_ok]):
        provide_solutions()
    else:
        print("\n🎉 All tests passed! Your setup is ready.")
