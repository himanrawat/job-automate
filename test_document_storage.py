#!/usr/bin/env python3
"""
Test script for Document Storage System
Tests AWS S3 + GitHub Gist hybrid storage
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_document_storage():
    """Test the document storage system"""
    print("🧪 Testing Document Storage System")
    print("=" * 50)
    
    try:
        from utils.document_manager import DocumentManager
        
        # Initialize document manager
        print("🔧 Initializing Document Manager...")
        doc_manager = DocumentManager()
        
        # Check storage setup
        print(f"📍 Environment Detection:")
        print(f"   AWS Environment: {doc_manager.is_aws_environment}")
        print(f"   GitHub Token: {'✓' if doc_manager.github_token else '✗ Missing'}")
        
        if hasattr(doc_manager, 's3_client'):
            print(f"   S3 Client: ✓")
            print(f"   S3 Bucket: {doc_manager.bucket_name}")
        else:
            print(f"   S3 Client: ✗ Not available")
        
        # Test data
        test_job = {
            'title': 'Senior Frontend Developer',
            'company': 'Microsoft',
            'description': 'Join our team to build amazing user interfaces with React.js and modern web technologies.'
        }
        
        test_resume = """
HIMANSHU RAWAT
Frontend Developer

EXPERIENCE:
• 3.5+ years of frontend development experience
• React.js, JavaScript, HTML5, CSS3 expertise
• Improved website responsiveness by 40%
• Built ERP system UI from scratch

SKILLS:
• React.js, JavaScript, TypeScript
• HTML5, CSS3, SASS
• Performance optimization
• User experience design

CONTACT:
• Email: officialhimanshurawat@gmail.com
• Portfolio: https://www.himanshurawat.in
        """.strip()
        
        test_cover_letter = """
Dear Microsoft Team,

I am excited to apply for the Senior Frontend Developer position. With 3.5+ years of experience in React.js and modern web development, I am passionate about creating exceptional user experiences.

At my current role, I improved website responsiveness by 40% and built an ERP system UI from scratch. I specialize in React.js, JavaScript, and performance optimization.

I would love to contribute to Microsoft's innovative frontend projects and help build products that users love.

Best regards,
Himanshu Rawat
        """.strip()
        
        print("\n📄 Testing Resume Storage...")
        resume_link = doc_manager.create_resume_document(test_resume, test_job)
        print(f"   Resume Link: {resume_link}")
        
        print("\n📝 Testing Cover Letter Storage...")
        cover_letter_link = doc_manager.create_cover_letter_document(test_cover_letter, test_job)
        print(f"   Cover Letter Link: {cover_letter_link}")
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        if "failed" not in resume_link.lower() and "failed" not in cover_letter_link.lower():
            print("✅ Document storage working!")
            print("✅ Ready for job automation!")
            if doc_manager.github_token:
                print("✅ GitHub Gist integration active")
            if doc_manager.is_aws_environment:
                print("✅ AWS S3 integration ready")
        else:
            print("⚠️  Document storage has issues")
            print("💡 Check your GitHub token setup")
        
        print(f"\n🔗 Your documents will appear as clickable links in Google Sheets!")
        print(f"📱 Accessible from anywhere, anytime!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

if __name__ == "__main__":
    test_document_storage()
