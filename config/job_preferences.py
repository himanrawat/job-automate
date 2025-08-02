"""
Job Search Preferences and Regional Configuration
Enhanced for Apify LinkedIn Jobs Scraper integration
"""

class JobPreferences:
    # Application Limits
    MAX_APPLICATIONS_PER_DAY = 100
    MAX_APPLICATIONS_PER_PORTAL = 20
    
    # Apify Specific Settings
    APIFY_MAX_JOBS_PER_SEARCH = 50
    APIFY_DAILY_SEARCH_LIMIT = 10
    APIFY_PUBLISHED_DAYS_AGO = 7
    
    # Application Preferences
    COVER_LETTER_TONE = 'enthusiastic'
    RECRUITER_APPROACH = 'direct'
    
    # Core Job Titles for Search - Enhanced for UI/Frontend focus
    job_titles = [
        'UI Developer',
        'UI/UX Developer', 
        'Frontend Developer',
        'Design Engineer',
        'User Interface Developer',
        'Front End Developer',
        'React Developer',
        'JavaScript Developer'
    ]
    
    # Primary locations with work arrangement preferences
    locations = [
        'India',           # Onsite, remote, hybrid all work
        'Remote, United States',  # Visa considerations apply
        'Remote, Worldwide',      # Prefer remote/hybrid
        'United Kingdom',
        'Germany',
        'Canada',
        'Australia'
    ]
    
    # Experience levels for less than 4 years
    experience_levels = [
        'Entry level',
        'Associate', 
        'Mid-Senior level'  # Excluding senior and executive levels
    ]
    
    # Job types
    job_types = [
        'full-time',
        'contract',
        'part-time'
    ]
    
    # Regional Job Markets - Enhanced with UI/Frontend focus
    REGIONS = {
        'INDIA': {
            'keywords': 'UI Developer OR UI/UX Developer OR Frontend Developer OR Design Engineer OR React Developer',
            'locations': ['Bangalore', 'Delhi', 'Noida', 'Gurugram', 'Chennai', 'Hyderabad', 'Mumbai', 'Remote'],
            'min_salary': '₹12,00,000',
            'visa_required': False,
            'work_arrangements': ['onsite', 'remote', 'hybrid'],
            'priority_focus': 'startups_and_good_companies'
        },
        'USA': {
            'keywords': 'UI Developer OR UI/UX Developer OR Frontend Developer OR Design Engineer OR React Developer',
            'locations': ['Remote', 'San Francisco', 'New York', 'Austin', 'Seattle', 'Boston', 'Los Angeles'],
            'min_salary': '$70,000',
            'visa_required': True,
            'work_arrangements': ['remote', 'hybrid', 'onsite'],  # All if visa sponsorship
            'priority_focus': 'startups_and_remote'
        },
        'AUSTRALIA': {
            'keywords': 'UI Developer OR UI/UX Developer OR Frontend Developer OR Design Engineer OR React Developer',
            'locations': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Remote'],
            'min_salary': 'AU$65,000',
            'visa_required': True,
            'work_arrangements': ['remote', 'hybrid'],
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
        },
        'GERMANY': {
            'keywords': 'Frontend Entwickler OR UI Entwickler OR React Entwickler OR JavaScript Entwickler OR Web Developer',
            'locations': ['Berlin', 'München', 'Hamburg', 'Köln', 'Frankfurt', 'Stuttgart', 'Düsseldorf', 'Remote'],
            'min_salary': '€45,000',
            'visa_required': True,
            'work_arrangements': ['remote', 'hybrid', 'onsite'],
            'priority_focus': 'tech_companies_and_startups',
            'platform': 'german_jobs',  # Use German Federal Employment Agency
            'search_terms_german': [
                'Frontend Entwickler',
                'UI Entwickler', 
                'UX Developer',
                'Softwareentwickler Frontend',
                'Web Developer',
                'JavaScript Entwickler',
                'React Entwickler'
            ]
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