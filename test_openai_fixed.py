#!/usr/bin/env python3
"""
Updated OpenAI API Test - Compatible with OpenAI v1.0+
Tests for authentication, payment, rate limits, and response quality
"""

import sys
import os
import logging
import time
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from openai import OpenAI
    from config.api_keys import APIKeys
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Please install required packages: pip install openai")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenAITester:
    def __init__(self):
        self.api_key = APIKeys.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.test_results = {}
        
    def test_api_key_format(self):
        """Test if API key has correct format"""
        print("\n🔑 Testing API Key Format...")
        
        if not self.api_key:
            print("❌ No API key found in environment variables")
            return False
            
        if not self.api_key.startswith('sk-'):
            print("❌ API key doesn't start with 'sk-' (invalid format)")
            return False
            
        if len(self.api_key) < 40:
            print("❌ API key too short (likely invalid)")
            return False
            
        # Mask the key for security
        masked_key = f"{self.api_key[:8]}...{self.api_key[-8:]}"
        print(f"✅ API key format looks valid: {masked_key}")
        return True
    
    def test_basic_connection(self):
        """Test basic API connection"""
        print("\n🌐 Testing Basic API Connection...")
        
        try:
            # Simple test with minimal tokens
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for testing
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                temperature=0.1
            )
            
            if response and response.choices:
                print("✅ Basic API connection successful")
                print(f"   Response: {response.choices[0].message.content}")
                return True
            else:
                print("❌ API connected but no response received")
                return False
                
        except Exception as e:
            error_message = str(e).lower()
            
            if "authentication" in error_message or "unauthorized" in error_message:
                print(f"❌ Authentication Error: {e}")
                print("💡 Check if your API key is correct and active")
                return False
                
            elif "rate limit" in error_message or "quota" in error_message:
                print(f"❌ Rate Limit/Quota Error: {e}")
                print("💡 You've exceeded your rate limit or quota")
                return False
                
            elif "billing" in error_message or "insufficient" in error_message:
                print(f"❌ Billing Error: {e}")
                print("💡 Check your OpenAI billing and add credits")
                return False
                
            elif "timeout" in error_message:
                print(f"❌ Timeout Error: {e}")
                print("💡 Request timed out. Check your internet connection")
                return False
                
            else:
                print(f"❌ Unexpected Error: {e}")
                print(f"   Error type: {type(e).__name__}")
                return False
    
    def test_payment_status(self):
        """Test if account has sufficient credits"""
        print("\n💳 Testing Payment/Credit Status...")
        
        try:
            # Try a small request to check payment status
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            
            if response:
                print("✅ Payment status good - API calls working")
                return True
                
        except Exception as e:
            error_message = str(e).lower()
            
            if "quota" in error_message or "billing" in error_message or "insufficient" in error_message:
                print("❌ Payment Issue: Quota exceeded or billing problem")
                print("💡 Check your OpenAI billing dashboard")
                print("🔗 https://platform.openai.com/account/billing")
                return False
            elif "rate limit" in error_message:
                print("⚠️  Rate limit hit (but payment seems OK)")
                return True
            elif "authentication" in error_message:
                print("❌ Authentication failed - check API key")
                return False
            else:
                print(f"⚠️  Could not determine payment status: {e}")
                return None
    
    def test_gpt4o_model(self):
        """Test GPT-4o model specifically"""
        print("\n🤖 Testing GPT-4o Model...")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Say 'GPT-4o is working' in exactly 4 words"}],
                max_tokens=10,
                temperature=0.1
            )
            
            if response and response.choices:
                result = response.choices[0].message.content.strip()
                print(f"✅ GPT-4o is working! Response: '{result}'")
                return True
            else:
                print("❌ GPT-4o not responding")
                return False
                
        except Exception as e:
            error_message = str(e).lower()
            
            if "model" in error_message and ("not found" in error_message or "does not exist" in error_message):
                print("❌ GPT-4o model not available for your account")
                print("💡 You might need to upgrade your plan or request access")
                print("🔗 https://platform.openai.com/account/billing")
                return False
            elif "quota" in error_message or "billing" in error_message:
                print("❌ GPT-4o access requires payment - check billing")
                return False
            else:
                print(f"❌ Error testing GPT-4o: {e}")
                return False
    
    def test_job_automation_scenario(self):
        """Test a realistic job automation scenario"""
        print("\n💼 Testing Job Automation Scenario...")
        
        try:
            # Simulate resume tailoring request
            prompt = """
            Write a brief 2-sentence summary for a frontend developer resume:
            - 3+ years React.js experience
            - Focus on user experience
            """
            
            start_time = time.time()
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            end_time = time.time()
            
            if response and response.choices:
                result = response.choices[0].message.content.strip()
                response_time = end_time - start_time
                
                print(f"✅ Job automation test successful!")
                print(f"   Response time: {response_time:.2f} seconds")
                print(f"   Sample output: {result[:100]}...")
                
                # Check response quality
                if len(result) > 20 and ("react" in result.lower() or "frontend" in result.lower()):
                    print("✅ Response quality looks good")
                    return True
                else:
                    print("⚠️  Response quality seems low")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except Exception as e:
            print(f"❌ Job automation test failed: {e}")
            return False
    
    def test_content_generator_integration(self):
        """Test your actual ContentGenerator class"""
        print("\n🔧 Testing ContentGenerator Integration...")
        
        try:
            from utils.content_generator import ContentGenerator
            
            # Create a test ContentGenerator instance
            content_gen = ContentGenerator()
            
            # Test job details
            job_details = {
                'title': 'Frontend Developer',
                'company': 'Test Company',
                'description': 'We are looking for a skilled React developer with 3+ years of experience in building modern user interfaces.'
            }
            
            # Test resume generation
            start_time = time.time()
            resume = content_gen.tailor_resume_for_frontend(job_details, 'INDIA')
            end_time = time.time()
            
            if resume and len(resume) > 50:
                print(f"✅ Resume generation working!")
                print(f"   Generation time: {end_time - start_time:.2f} seconds")
                print(f"   Resume length: {len(resume)} characters")
                return True
            else:
                print("❌ Resume generation failed or too short")
                return False
                
        except Exception as e:
            print(f"❌ ContentGenerator test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide summary"""
        print("🧪 Starting Comprehensive OpenAI API Test")
        print("=" * 50)
        
        tests = [
            ("API Key Format", self.test_api_key_format),
            ("Basic Connection", self.test_basic_connection),
            ("Payment Status", self.test_payment_status),
            ("GPT-4o Model", self.test_gpt4o_model),
            ("Job Automation", self.test_job_automation_scenario),
            ("ContentGenerator", self.test_content_generator_integration)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            if result is True:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            elif result is False:
                print(f"❌ {test_name}: FAILED")
            else:
                print(f"⚠️  {test_name}: UNKNOWN")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if results.get("API Key Format") is False:
            print("🔧 Fix your API key in the .env file")
            
        if results.get("Basic Connection") is False:
            print("🔧 Check internet connection and API key validity")
            
        if results.get("Payment Status") is False:
            print("🔧 Add credits to your OpenAI account")
            print("🔗 https://platform.openai.com/account/billing")
            
        if results.get("GPT-4o Model") is False:
            print("🔧 Consider using GPT-3.5-turbo as fallback")
            print("🔧 Or upgrade your OpenAI plan for GPT-4o access")
            
        if results.get("ContentGenerator") is False:
            print("🔧 Check your ContentGenerator class implementation")
        
        if passed == total:
            print("🎉 All tests passed! Your ChatGPT integration is working perfectly!")
            print("🚀 Ready for job automation!")
        elif passed >= total * 0.6:
            print("⚠️  Most tests passed, but some issues need attention")
        else:
            print("🚨 Multiple issues detected - please fix before using job automation")
        
        return results

def main():
    """Main test execution"""
    try:
        tester = OpenAITester()
        results = tester.run_comprehensive_test()
        
        # Exit code based on results
        if all(r is True for r in results.values() if r is not None):
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Issues found
            
    except Exception as e:
        print(f"💥 Test script crashed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
