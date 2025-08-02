"""
Pre-flight Check - Verify all systems before running main.py
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'APIFY_API_TOKEN', 
        'GOOGLE_PROJECT_ID',
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_PRIVATE_KEY',
        'GITHUB_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📋 Please set these in your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_imports():
    """Check if all required modules can be imported"""
    print("\n🔍 Checking Import Dependencies...")
    
    try:
        import logging
        print("✅ logging module")
        
        from dotenv import load_dotenv
        print("✅ dotenv module")
        
        from apify_client import ApifyClient
        print("✅ apify_client module")
        
        import openai
        print("✅ openai module") 
        
        import gspread
        print("✅ gspread module")
        
        from selenium import webdriver
        print("✅ selenium module")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📋 Please install missing dependencies with: pip install -r requirements.txt")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n🔍 Checking File Structure...")
    
    required_files = [
        'config/api_keys.py',
        'config/job_preferences.py',
        'config/user_profile.py',
        'scrapers/apify_linkedin_scraper.py',
        'utils/enhanced_application_processor.py',
        'utils/enhanced_content_generator.py',
        'utils/sheets_manager.py',
        'utils/document_manager.py',
        'applications/application_handler.py',
        'main.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_api_connections():
    """Test API connections"""
    print("\n🔍 Testing API Connections...")
    
    try:
        # Test Apify connection
        from config.api_keys import APIKeys
        from apify_client import ApifyClient
        
        if APIKeys.APIFY_API_TOKEN:
            client = ApifyClient(APIKeys.APIFY_API_TOKEN)
            print("✅ Apify client initialized")
        else:
            print("⚠️ Apify API token not found")
        
        # Test OpenAI connection (basic check)
        if APIKeys.OPENAI_API_KEY:
            print("✅ OpenAI API key present")
        else:
            print("❌ OpenAI API key missing")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def check_german_integration():
    """Check German job market integration"""
    print("\n🇩🇪 Checking German Job Market Integration...")
    
    try:
        from scrapers.apify_linkedin_scraper import ApifyJobScraper
        from config.job_preferences import JobPreferences
        
        scraper = ApifyJobScraper()
        
        # Check if German actor is available
        if 'german_jobs' in scraper.actors:
            print("✅ German job scraper actor configured")
        else:
            print("❌ German job scraper actor missing")
            return False
        
        # Check German preferences
        if 'GERMANY' in JobPreferences.REGIONS:
            print("✅ German job preferences configured")
        else:
            print("❌ German job preferences missing")
            return False
        
        # Test German search parameters
        test_params = scraper._prepare_german_search_input(
            keywords=["Frontend Entwickler"], 
            locations=["Berlin"]
        )
        
        if test_params and test_params.get('searchTerm'):
            print("✅ German search parameters working")
        else:
            print("❌ German search parameters not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ German integration error: {e}")
        return False

def main():
    """Run all pre-flight checks"""
    print("🚀 Pre-flight Check for Himanshu's Job Automation")
    print("=" * 60)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    checks = [
        ("Environment Variables", check_environment),
        ("Python Dependencies", check_imports), 
        ("File Structure", check_file_structure),
        ("API Connections", check_api_connections),
        ("German Integration", check_german_integration)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready to run main.py!")
        print("\n🚀 You can now run: python main.py")
        print("\n📋 Expected platforms: LinkedIn, Indeed, German Jobs")
        print("🎯 Enhanced content generation: Enabled")
        print("📊 Google Sheets tracking: Enabled")
        print("🇩🇪 German job market: Enabled")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print("\n📋 After fixing issues, run this check again")
        print("🔧 Then you can run: python main.py")
    
    return all_passed

if __name__ == "__main__":
    main()
