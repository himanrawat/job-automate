"""
Job Search Preferences and Regional Configuration
"""

class JobPreferences:
    # Application Limits
    MAX_APPLICATIONS_PER_DAY = 100
    MAX_APPLICATIONS_PER_PORTAL = 20
    
    # Application Preferences
    COVER_LETTER_TONE = 'enthusiastic'
    RECRUITER_APPROACH = 'direct'
    
    # Regional Job Markets
    REGIONS = {
        'INDIA': {
            'keywords': 'Frontend Developer OR UI Developer OR React Developer OR JavaScript Developer OR Web Developer',
            'locations': ['Bangalore', 'Delhi', 'Noida', 'Gurugram', 'Gurgaon', 'Chennai', 'Hyderabad', 'Mumbai', 'Remote'],
            'min_salary': '₹12,00,000',
            'visa_required': False,
            'priority_focus': 'startups_and_good_companies'
        },
        'USA': {
            'keywords': 'Frontend Developer OR UI Developer OR React Developer OR JavaScript Developer OR Web Developer',
            'locations': ['Remote', 'San Francisco', 'New York', 'Austin', 'Seattle', 'Boston', 'Los Angeles'],
            'min_salary': '$60,000',
            'visa_required': True,
            'priority_focus': 'startups_and_remote'
        },
        'AUSTRALIA': {
            'keywords': 'Frontend Developer OR UI Developer OR React Developer OR JavaScript Developer OR Web Developer',
            'locations': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Remote'],
            'min_salary': 'AU$60,000',
            'visa_required': True,
            'priority_focus': 'established_companies'
        },
        'UNITED_KINGDOM': {
            'keywords': 'Frontend Developer OR UI Developer OR React Developer OR JavaScript Developer OR Web Developer',
            'locations': ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Leeds', 'Remote'],
            'min_salary': '£35,000',
            'visa_required': True,
            'priority_focus': 'startups_and_good_companies'
        },
        'EUROPE': {
            'keywords': 'Frontend Developer OR UI Developer OR React Developer OR JavaScript Developer OR Web Developer',
            'locations': ['Berlin', 'Amsterdam', 'Zurich', 'Dublin', 'Barcelona', 'Remote'],
            'min_salary': '€40,000',
            'visa_required': True,
            'priority_focus': 'startups_and_remote'
        }
    }
    
    # Company Priority Lists
    TOP_STARTUPS = [
        'razorpay', 'swiggy', 'zomato', 'paytm', 'phonepe', 'cred', 'meesho', 
        'unacademy', 'byju', 'zerodha', 'groww', 'urban company', 'lenskart',
        'stripe', 'airbnb', 'uber', 'spotify', 'netflix', 'discord', 'figma'
    ]
    
    ESTABLISHED_GOOD_COMPANIES = [
        'google', 'microsoft', 'apple', 'adobe', 'salesforce', 'atlassian',
        'slack', 'dropbox', 'shopify', 'github', 'gitlab', 'linkedin'
    ]