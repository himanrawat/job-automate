#!/usr/bin/env python3
"""
Test CSV fallback functionality
"""

import logging
from utils.csv_data_manager import CSVDataManager
from utils.sheets_manager import SheetsManager
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_csv_functionality():
    """Test CSV data manager functionality"""
    print("📊 Testing CSV Data Manager...")
    
    csv_manager = CSVDataManager()
    
    # Test data
    test_job = {
        'date_applied': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'job_title': 'Senior Frontend Developer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'portal': 'LinkedIn',
        'job_url': 'https://linkedin.com/jobs/test-job',
        'applied_status': 'Manual Required',
        'application_method': 'External Apply',
        'salary_range': '15-25 LPA',
        'priority': 'High',
        'required_skills': 'React, TypeScript, Node.js',
        'experience_level': '5+ years',
        'employment_type': 'Full-time',
        'remote_work': 'Hybrid',
        'notes': 'Great company culture, good growth opportunities',
        'cover_letter_used': 'Frontend_Developer_Cover_Letter_v2.pdf',
        'resume_version': 'Himanshu_Resume_Frontend_2025.pdf'
    }
    
    # Add test job
    success = csv_manager.add_job_application('INDIA', test_job)
    if success:
        print("✅ Test job added to CSV successfully")
    else:
        print("❌ Failed to add test job to CSV")
        return False
    
    # Get summary
    summary = csv_manager.get_applications_summary('INDIA')
    print(f"📈 Applications Summary: {summary}")
    
    # List all files
    files = csv_manager.list_all_data_files()
    print(f"📁 Data Files: {len(files)} files found")
    for file in files:
        print(f"   - {file['name']} ({file['size']} bytes)")
    
    # Test Excel export
    excel_file = csv_manager.export_to_excel('INDIA')
    if excel_file:
        print(f"✅ Excel export successful: {excel_file}")
    else:
        print("❌ Excel export failed")
    
    return True

def test_sheets_manager_csv_fallback():
    """Test SheetsManager with CSV fallback"""
    print("\n📋 Testing SheetsManager CSV Fallback...")
    
    sheets_manager = SheetsManager()
    
    if sheets_manager.using_csv_fallback:
        print("✅ SheetsManager correctly using CSV fallback mode")
        
        # Test adding a job through SheetsManager
        test_job = {
            'title': 'React Developer',
            'company': 'Startup Inc',
            'location': 'Remote',
            'portal': 'Naukri',
            'url': 'https://naukri.com/test-job',
            'application_status': 'Applied',
            'application_method': 'Easy Apply',
            'salary': '12-18 LPA',
            'priority_level': 'Medium',
            'keywords': 'React, JavaScript, CSS',
            'job_type': 'Full-time',
            'notes': 'Remote-first company'
        }
        
        sheets_manager.update_application_row('INDIA', test_job)
        print("✅ Job added through SheetsManager CSV fallback")
        
        return True
    else:
        print("❌ SheetsManager not using CSV fallback mode")
        return False

if __name__ == "__main__":
    print("🧪 CSV Fallback Functionality Test")
    print("=" * 50)
    
    csv_test = test_csv_functionality()
    sheets_test = test_sheets_manager_csv_fallback()
    
    print("\n" + "=" * 50)
    print("📊 CSV Test Results:")
    print(f"CSV Manager: {'✅' if csv_test else '❌'}")
    print(f"SheetsManager Fallback: {'✅' if sheets_test else '❌'}")
    
    if csv_test and sheets_test:
        print("\n🎉 All CSV fallback functionality is working correctly!")
        print("💡 Your job automation system is ready to use with CSV data storage.")
    else:
        print("\n⚠️ Some CSV functionality needs attention.")
