"""
Apify Job Scraper Integration
Professional-grade job scraping using Apify's infrastructure for LinkedIn, Indeed, and other platforms
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from apify_client import ApifyClient
from config.api_keys import APIKeys
from config.job_preferences import JobPreferences
from utils.priority_calculator import PriorityCalculator

logger = logging.getLogger(__name__)

class ApifyJobScraper:
    """
    Apify-powered job scraper supporting multiple platforms (LinkedIn, Indeed, German Federal Employment Agency)
    with advanced filtering and rate limiting
    """
    
    def __init__(self):
        """Initialize Apify client and configuration"""
        self.client = ApifyClient(APIKeys.APIFY_API_TOKEN)
        
        # Actor IDs for different job platforms
        self.actors = {
            'linkedin': "bebity~linkedin-jobs-scraper",  # LinkedIn Jobs Scraper
            'indeed': "hMvNSpz3JnHgl5jkh",               # Indeed Jobs Scraper
            'german_jobs': "xtech~bundesagentur-fur-arbeit-job-scraper",  # German Federal Employment Agency
            # Add more actors as needed
        }
        
        self.priority_calculator = PriorityCalculator()
        self.job_preferences = JobPreferences()
        
        # Rate limiting and cost management
        self.daily_requests = 0
        self.max_daily_requests = 15  # Increased for multiple platforms
        self.last_request_date = datetime.now().date()
        
        logger.info("ApifyJobScraper initialized successfully with multi-platform support")
    
    def search_jobs(self, 
                   keywords: Optional[List[str]] = None,
                   locations: Optional[List[str]] = None,
                   companies: Optional[List[str]] = None,
                   experience_levels: Optional[List[str]] = None,
                   max_jobs: int = 50,
                   published_days_ago: int = 1,  # Default to 24 hours
                   platform: str = 'linkedin',
                   work_types: Optional[List[str]] = None,
                   visa_sponsorship_required: bool = False) -> List[Dict[str, Any]]:
        """
        Search for jobs using Apify scrapers with enhanced filtering
        
        Args:
            keywords: Job titles/keywords to search for (UI Developer, Frontend Developer, etc.)
            locations: Geographic locations
            companies: Specific companies to target
            experience_levels: Experience levels (entry, mid, senior)
            max_jobs: Maximum number of jobs to fetch
            published_days_ago: How recent jobs should be (1 = 24 hours)
            platform: Platform to search ('linkedin', 'indeed')
            work_types: Work arrangement preferences (remote, onsite, hybrid)
            visa_sponsorship_required: Whether visa sponsorship is needed
        
        Returns:
            List of job dictionaries with standardized format
        """
        try:
            # Use enhanced defaults for your preferences
            if not keywords:
                keywords = [
                    "UI Developer", 
                    "UI/UX Developer", 
                    "Frontend Developer", 
                    "Design Engineer",
                    "User Interface Developer",
                    "Front End Developer",
                    "React Developer"
                ]
            
            # Default to recent jobs (24 hours)
            if published_days_ago is None:
                published_days_ago = 1
            
            # Check rate limits
            if not self._check_rate_limits():
                logger.warning("Daily rate limit exceeded for Apify requests")
                return []
            
            # Get the appropriate actor ID
            actor_id = self.actors.get(platform)
            if not actor_id:
                logger.error(f"Unsupported platform: {platform}")
                return []
            
            # Prepare search parameters based on platform
            if platform == 'linkedin':
                run_input = self._prepare_linkedin_search_input(
                    keywords, locations, companies, experience_levels, max_jobs, published_days_ago,
                    work_types, visa_sponsorship_required
                )
            elif platform == 'indeed':
                run_input = self._prepare_indeed_search_input(
                    keywords, locations, companies, experience_levels, max_jobs, published_days_ago,
                    work_types, visa_sponsorship_required
                )
            elif platform == 'german_jobs':
                run_input = self._prepare_german_search_input(
                    keywords, locations, companies, experience_levels, max_jobs, published_days_ago,
                    work_types, visa_sponsorship_required
                )
            else:
                logger.error(f"No input preparation method for platform: {platform}")
                return []
            
            logger.info(f"Starting Apify {platform} job search with parameters: {run_input}")
            
            # Run the Actor and wait for completion
            run = self.client.actor(actor_id).call(run_input=run_input)
            
            # Track usage
            self._update_rate_limits()
            
            # Fetch results
            jobs = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                job = self._normalize_job_data(item, platform)
                if job:
                    jobs.append(job)
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from Apify {platform}")
            
            # Calculate priorities and filter
            prioritized_jobs = self._prioritize_jobs(jobs)
            
            return prioritized_jobs
            
        except Exception as e:
            logger.error(f"Error in Apify {platform} job search: {e}")
            return []
    
    def _prepare_linkedin_search_input(self, 
                                      keywords: Optional[List[str]] = None,
                                      locations: Optional[List[str]] = None,
                                      companies: Optional[List[str]] = None,
                                      experience_levels: Optional[List[str]] = None,
                                      max_jobs: int = 50,
                                      published_days_ago: int = 1,
                                      work_types: Optional[List[str]] = None,
                                      visa_sponsorship_required: bool = False) -> Dict[str, Any]:
        """Prepare enhanced input parameters for LinkedIn Apify Actor with your specific filters"""
        
        # Use enhanced job preferences for UI/Frontend roles
        if not keywords:
            keywords = [
                "UI Developer", 
                "UI/UX Developer", 
                "Frontend Developer", 
                "Design Engineer",
                "User Interface Developer",
                "Front End Developer"
            ]
        
        if not locations:
            locations = self.job_preferences.locations
        
        # Enhanced search title for UI/Frontend roles
        search_title = " OR ".join([f'"{keyword}"' for keyword in keywords])
        
        # Default experience levels for less than 4 years
        if not experience_levels:
            experience_levels = ["entry", "associate", "mid"]  # Exclude senior and executive
        
        # Map experience levels to LinkedIn API format (numeric strings)
        experience_level_mapping = {
            "internship": "1",
            "entry": "2", 
            "associate": "3",
            "mid": "3",
            "senior": "4",
            "director": "5",
            "executive": "5"
        }
        
        # Convert experience levels to LinkedIn format
        mapped_experience_levels = []
        for level in experience_levels:
            if level in experience_level_mapping:
                mapped_value = experience_level_mapping[level]
                if mapped_value not in mapped_experience_levels:
                    mapped_experience_levels.append(mapped_value)
        
        # Determine work arrangement based on location and visa requirements
        work_arrangement = self._determine_work_arrangement(locations, visa_sponsorship_required, work_types)
        
        # Calculate published date filter - Default to 24 hours
        published_date = "r86400"  # 24 hours by default
        if published_days_ago:
            if published_days_ago <= 1:
                published_date = "r86400"  # 24 hours
            elif published_days_ago <= 7:
                published_date = "r604800"  # 7 days
            elif published_days_ago <= 30:
                published_date = "r2592000"  # 30 days
            else:
                published_date = ""  # All time
        
        # Enhanced run input with your specific requirements
        run_input = {
            "title": search_title,
            "location": locations[0] if locations else "United States",
            "companyName": companies or [],
            "companyId": [],
            "publishedAt": published_date,  # Default to 24 hours
            "rows": min(max_jobs, 100),
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            },
            # Enhanced filters for your requirements
            "experienceLevel": ",".join(mapped_experience_levels) if mapped_experience_levels else "2,3",
            "jobType": work_arrangement["job_types"],
            "remote": work_arrangement["remote_allowed"],
            # Additional LinkedIn-specific filters
            "sortBy": "DD",  # Sort by date (most recent first)
            "onSiteRemote": work_arrangement["on_site_remote"],
        }
        
        logger.info(f"LinkedIn search configured for: {search_title} in {locations}")
        logger.info(f"Work arrangement: {work_arrangement}")
        logger.info(f"Experience levels: {experience_levels}")
        logger.info(f"Published within: {published_date}")
        
        return run_input
    
    def _determine_work_arrangement(self, locations, visa_sponsorship_required, work_types):
        """
        Determine work arrangement based on location and visa requirements
        
        Rules:
        - India applications: onsite, remote, hybrid all work
        - Worldwide remote: if visa sponsorship available, hybrid and onsite work too
        - Otherwise: prefer remote for international applications
        """
        # Default arrangement
        arrangement = {
            "job_types": ["full-time", "contract"],
            "remote_allowed": True,
            "on_site_remote": ["remote", "hybrid"]  # LinkedIn filter values
        }
        
        if not locations:
            return arrangement
        
        # Check if applying for India-based positions
        india_locations = any(
            any(keyword in loc.upper() for keyword in ['INDIA', 'DELHI', 'MUMBAI', 'BANGALORE', 'BENGALURU', 'HYDERABAD', 'CHENNAI', 'PUNE', 'GURGAON', 'NOIDA'])
            for loc in locations
        )
        
        # Check if applying for worldwide/remote positions
        worldwide_remote = any(
            any(keyword in loc.upper() for keyword in ['REMOTE', 'WORLDWIDE', 'GLOBAL', 'ANYWHERE'])
            for loc in locations
        )
        
        if india_locations:
            # For India: onsite, remote, hybrid all work
            arrangement.update({
                "remote_allowed": True,
                "on_site_remote": ["remote", "hybrid", "onsite"]
            })
            logger.info("India applications: onsite, remote, hybrid all enabled")
            
        elif worldwide_remote and visa_sponsorship_required:
            # For worldwide remote with visa sponsorship: hybrid and onsite also work
            arrangement.update({
                "remote_allowed": True,
                "on_site_remote": ["remote", "hybrid", "onsite"]
            })
            logger.info("Worldwide remote with visa sponsorship: all work arrangements enabled")
            
        else:
            # For other international: prefer remote and hybrid
            arrangement.update({
                "remote_allowed": True,
                "on_site_remote": ["remote", "hybrid"]
            })
            logger.info("International applications: remote and hybrid preferred")
        
        return arrangement

    def _prepare_indeed_search_input(self, 
                                   keywords: Optional[List[str]] = None,
                                   locations: Optional[List[str]] = None,
                                   companies: Optional[List[str]] = None,
                                   experience_levels: Optional[List[str]] = None,
                                   max_jobs: int = 50,
                                   published_days_ago: int = 1,
                                   work_types: Optional[List[str]] = None,
                                   visa_sponsorship_required: bool = False) -> Dict[str, Any]:
        """Prepare enhanced input parameters for Indeed Apify Actor with your specific filters"""
        
        # Use enhanced job preferences for UI/Frontend roles
        if not keywords:
            keywords = [
                "UI Developer", 
                "UI/UX Developer", 
                "Frontend Developer", 
                "Design Engineer",
                "User Interface Developer",
                "Front End Developer"
            ]
        
        if not locations:
            locations = self.job_preferences.locations
        
        # Enhanced search query with quotes for exact matches
        position = " OR ".join([f'"{keyword}"' for keyword in keywords])
        
        # Get primary location or default to US
        primary_location = locations[0] if locations else "United States"
        
        # Map experience levels to standardized format for Indeed
        indeed_experience_mapping = {
            "entry": "entry_level",
            "associate": "mid_level", 
            "mid": "mid_level",
            "senior": "senior_level",
            "director": "senior_level",
            "executive": "senior_level"
        }
        
        # Convert experience levels to Indeed format
        mapped_indeed_levels = []
        if experience_levels:
            for level in experience_levels:
                if level in indeed_experience_mapping:
                    mapped_value = indeed_experience_mapping[level]
                    if mapped_value not in mapped_indeed_levels:
                        mapped_indeed_levels.append(mapped_value)
        
        # Enhanced Indeed actor input with your filters
        run_input = {
            "position": position,
            "country": "US",  # Can be made configurable based on location
            "location": primary_location,
            "maxItems": min(max_jobs, 100),
            "parseCompanyDetails": False,
            "saveOnlyUniqueItems": True,
            "followApplyRedirects": False,
            # Add experience level filter if supported
            "experienceLevel": ",".join(mapped_indeed_levels) if mapped_indeed_levels else "entry_level,mid_level",
            # Add date filter - Indeed might use different format
            "datePosted": "1" if published_days_ago <= 1 else str(published_days_ago),
        }
        
        # Add company filter if specified
        if companies:
            run_input["position"] = f"{position} {companies[0]}"
        
        logger.info(f"Indeed search configured for: {position} in {primary_location}")
        
        return run_input
    
    def _prepare_german_search_input(self, 
                                   keywords: Optional[List[str]] = None,
                                   locations: Optional[List[str]] = None,
                                   companies: Optional[List[str]] = None,
                                   experience_levels: Optional[List[str]] = None,
                                   max_jobs: int = 50,
                                   published_days_ago: int = 1,
                                   work_types: Optional[List[str]] = None,
                                   visa_sponsorship_required: bool = False) -> Dict[str, Any]:
        """Prepare enhanced input parameters for German Federal Employment Agency Apify Actor"""
        
        # German translations for UI/Frontend roles
        if not keywords:
            keywords = [
                "Frontend Entwickler", 
                "UI Entwickler", 
                "UX Developer",
                "Softwareentwickler Frontend",
                "Web Developer",
                "JavaScript Entwickler",
                "React Entwickler"
            ]
        
        # Default German locations if not specified
        german_locations = [
            "Berlin", "München", "Hamburg", "Köln", "Frankfurt", 
            "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"
        ]
        
        if not locations or not any('germany' in loc.lower() or 'deutschland' in loc.lower() for loc in locations):
            locations = german_locations
        
        # Use first keyword as primary search term
        search_term = keywords[0] if keywords else "Frontend Entwickler"
        
        # Enhanced German job search input
        run_input = {
            "searchTerm": search_term,
            "location": locations[0] if locations else "Berlin",
            "maxResults": min(max_jobs, 100),
            "sortBy": "date",  # Sort by publication date
            "workingTime": "VOLLZEIT",  # Full-time preference, can be made configurable
        }
        
        # Add additional search parameters if supported by the actor
        if companies:
            # Note: This might need adjustment based on actual actor capabilities
            run_input["company"] = companies[0]
        
        # Add experience level mapping for German market
        if experience_levels:
            german_experience_map = {
                "entry": "Berufseinsteiger",
                "associate": "Junior",
                "mid": "Professional", 
                "senior": "Senior",
                "executive": "Führungsposition"
            }
            # Add experience level to search term if supported
            if experience_levels[0] in german_experience_map:
                run_input["searchTerm"] += f" {german_experience_map[experience_levels[0]]}"
        
        logger.info(f"German job search configured for: {search_term} in {locations[0] if locations else 'Berlin'}")
        
        return run_input
    
    def _normalize_job_data(self, raw_job: Dict[str, Any], platform: str = 'linkedin') -> Optional[Dict[str, Any]]:
        """
        Normalize Apify job data to match your system's format
        Supports different platforms with different data structures
        """
        try:
            if platform == 'linkedin':
                # LinkedIn-specific data extraction
                job = {
                    'title': raw_job.get('title', '').strip(),
                    'company': raw_job.get('companyName', '').strip(),
                    'location': raw_job.get('location', '').strip(),
                    'description': raw_job.get('description', '').strip(),
                    'url': raw_job.get('url', ''),
                    'job_id': raw_job.get('jobId', ''),
                    'posted_date': raw_job.get('publishedAt', ''),
                    'salary': raw_job.get('salary', ''),
                    'experience_level': raw_job.get('experienceLevel', ''),
                    'job_type': raw_job.get('jobType', ''),
                    'company_url': raw_job.get('companyUrl', ''),
                    'company_logo': raw_job.get('companyLogo', ''),
                    'benefits': raw_job.get('benefits', []),
                    'skills': raw_job.get('skills', []),
                    'source': 'apify_linkedin',
                    'platform': 'linkedin',
                    'scraped_at': datetime.now().isoformat(),
                    'raw_data': raw_job,
                }
            elif platform == 'indeed':
                # Indeed-specific data extraction
                job = {
                    'title': raw_job.get('positionName', raw_job.get('title', '')).strip(),
                    'company': raw_job.get('company', '').strip(),
                    'location': raw_job.get('location', '').strip(),
                    'description': raw_job.get('description', '').strip(),
                    'url': raw_job.get('url', ''),
                    'job_id': raw_job.get('id', ''),
                    'posted_date': raw_job.get('postedAt', ''),
                    'salary': raw_job.get('salary', ''),
                    'experience_level': '',  # Indeed might not have this field
                    'job_type': raw_job.get('jobType', ''),
                    'company_url': '',
                    'company_logo': '',
                    'benefits': [],
                    'skills': [],
                    'source': 'apify_indeed',
                    'platform': 'indeed',
                    'scraped_at': datetime.now().isoformat(),
                    'raw_data': raw_job,
                }
            elif platform == 'german_jobs':
                # German Federal Employment Agency data extraction
                raw_data = raw_job
                arbeitsort = raw_data.get('arbeitsort', {})
                
                job = {
                    'title': raw_data.get('titel', '').strip(),
                    'company': raw_data.get('arbeitgeber', '').strip(),
                    'location': f"{arbeitsort.get('ort', '')}, {arbeitsort.get('region', '')}".strip(', '),
                    'description': raw_data.get('beschreibung', raw_data.get('beruf', '')).strip(),
                    'url': raw_data.get('externeUrl', raw_data.get('url', '')),
                    'job_id': raw_data.get('refnr', ''),
                    'posted_date': raw_data.get('aktuelleVeroeffentlichungsdatum', ''),
                    'salary': raw_data.get('gehalt', raw_data.get('salary', '')),
                    'experience_level': '',  # German agency doesn't typically provide this
                    'job_type': 'VOLLZEIT' if raw_data.get('arbeitszeit') == 'VOLLZEIT' else raw_data.get('arbeitszeit', ''),
                    'company_url': '',
                    'company_logo': '',
                    'benefits': [],
                    'skills': [raw_data.get('beruf', '')] if raw_data.get('beruf') else [],
                    'source': 'apify_german_jobs',
                    'platform': 'german_jobs',
                    'scraped_at': datetime.now().isoformat(),
                    'raw_data': raw_job,
                    # Additional German-specific fields
                    'postal_code': arbeitsort.get('plz', ''),
                    'state': arbeitsort.get('region', ''),
                    'country': arbeitsort.get('land', 'Deutschland'),
                    'start_date': raw_data.get('eintrittsdatum', ''),
                    'profession_category': raw_data.get('beruf', ''),
                }
            else:
                logger.error(f"Unsupported platform for data normalization: {platform}")
                return None
            
            # Validate required fields
            if not job['title'] or not job['company']:
                logger.warning(f"Skipping job with missing required fields: {job}")
                return None
            
            return job
            
        except Exception as e:
            logger.error(f"Error normalizing {platform} job data: {e}")
            return None
    
    def _prioritize_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate priority scores for jobs"""
        try:
            for job in jobs:
                # Create job_details dict in the format expected by priority calculator
                job_details = {
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'description': job['description'],
                    'salary': job.get('salary', ''),
                    'experience_level': job.get('experience_level', ''),
                    'skills': job.get('skills', [])
                }
                
                priority_score = self.priority_calculator.calculate_priority(job_details)
                job['priority_score'] = priority_score
            
            # Sort by priority (highest first)
            jobs.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error prioritizing jobs: {e}")
            return jobs
    
    def _check_rate_limits(self) -> bool:
        """Check if we can make another API request"""
        current_date = datetime.now().date()
        
        # Reset daily counter if it's a new day
        if current_date != self.last_request_date:
            self.daily_requests = 0
            self.last_request_date = current_date
        
        return self.daily_requests < self.max_daily_requests
    
    def _update_rate_limits(self):
        """Update rate limiting counters"""
        self.daily_requests += 1
        logger.info(f"Apify requests today: {self.daily_requests}/{self.max_daily_requests}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            'daily_requests': self.daily_requests,
            'max_daily_requests': self.max_daily_requests,
            'requests_remaining': self.max_daily_requests - self.daily_requests,
            'last_request_date': self.last_request_date.isoformat(),
        }
    
    def search_specific_companies(self, 
                                 company_names: List[str],
                                 keywords: Optional[List[str]] = None,
                                 max_jobs_per_company: int = 20) -> List[Dict[str, Any]]:
        """
        Search for jobs at specific companies
        
        Args:
            company_names: List of company names to search
            keywords: Optional job keywords
            max_jobs_per_company: Max jobs per company
        
        Returns:
            List of jobs from specified companies
        """
        all_jobs = []
        
        for company in company_names:
            logger.info(f"Searching jobs at {company}")
            
            # Check rate limits before each company search
            if not self._check_rate_limits():
                logger.warning("Rate limit reached, stopping company search")
                break
            
            company_jobs = self.search_jobs(
                keywords=keywords,
                companies=[company],
                max_jobs=max_jobs_per_company
            )
            
            all_jobs.extend(company_jobs)
            
            # Small delay between company searches
            time.sleep(2)
        
        return all_jobs
    
    def search_by_experience_level(self, 
                                  experience_level: str,
                                  keywords: Optional[List[str]] = None,
                                  max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Search jobs by specific experience level
        
        Args:
            experience_level: Entry level, Mid level, Senior level, etc.
            keywords: Job keywords
            max_jobs: Maximum jobs to return
        
        Returns:
            List of jobs matching experience level
        """
        return self.search_jobs(
            keywords=keywords,
            experience_levels=[experience_level],
            max_jobs=max_jobs
        )
    
    def search_multiple_platforms(self, 
                                 platforms: List[str] = ['linkedin'],
                                 keywords: Optional[List[str]] = None,
                                 locations: Optional[List[str]] = None,
                                 max_jobs_per_platform: int = 25) -> List[Dict[str, Any]]:
        """
        Search for jobs across multiple platforms
        
        Args:
            platforms: List of platforms to search ('linkedin', 'indeed', 'german_jobs')
            keywords: Job keywords
            locations: Geographic locations
            max_jobs_per_platform: Max jobs per platform
        
        Returns:
            Combined list of jobs from all platforms
        """
        all_jobs = []
        
        for platform in platforms:
            if not self._check_rate_limits():
                logger.warning("Rate limit reached, stopping multi-platform search")
                break
            
            logger.info(f"Searching jobs on {platform}")
            
            platform_jobs = self.search_jobs(
                keywords=keywords,
                locations=locations,
                max_jobs=max_jobs_per_platform,
                platform=platform
            )
            
            all_jobs.extend(platform_jobs)
            
            # Small delay between platform searches
            time.sleep(3)
        
        # Re-sort all jobs by priority
        all_jobs.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return all_jobs
    
    def search_german_jobs(self, 
                          keywords: Optional[List[str]] = None,
                          locations: Optional[List[str]] = None,
                          max_jobs: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs specifically in the German job market using Bundesagentur für Arbeit
        
        Args:
            keywords: German job keywords (defaults to Frontend/UI roles in German)
            locations: German cities (defaults to major German cities)
            max_jobs: Maximum number of jobs to return
        
        Returns:
            List of German job opportunities
        """
        return self.search_jobs(
            keywords=keywords,
            locations=locations,
            max_jobs=max_jobs,
            platform='german_jobs'
        )

# Backward compatibility alias
ApifyLinkedInScraper = ApifyJobScraper

# Usage example and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test the scraper
    scraper = ApifyJobScraper()
    
    # Test LinkedIn job search
    print("Testing LinkedIn job search...")
    linkedin_jobs = scraper.search_jobs(
        keywords=["Python Developer", "Software Engineer"],
        locations=["United States"],
        max_jobs=5,
        platform='linkedin'
    )
    
    print(f"Found {len(linkedin_jobs)} LinkedIn jobs")
    for job in linkedin_jobs[:2]:  # Print first 2 jobs
        print(f"- {job['title']} at {job['company']} (Priority: {job.get('priority_score', 'N/A')})")
    
    # Test multi-platform search
    print("\nTesting multi-platform search...")
    multi_jobs = scraper.search_multiple_platforms(
        platforms=['linkedin'],  # Add 'indeed' when available
        keywords=["Frontend Developer"],
        max_jobs_per_platform=3
    )
    
    print(f"Found {len(multi_jobs)} jobs across platforms")
    for job in multi_jobs[:2]:
        print(f"- {job['title']} at {job['company']} ({job['platform']}) - Priority: {job.get('priority_score', 'N/A')}")
    
    # Test German job search
    print("\nTesting German job search...")
    german_jobs = scraper.search_german_jobs(
        keywords=["Frontend Entwickler", "UI Entwickler"],
        locations=["Berlin", "München"],
        max_jobs=3
    )
    
    print(f"Found {len(german_jobs)} German jobs")
    for job in german_jobs[:2]:
        print(f"- {job['title']} at {job['company']} (German Market) - Priority: {job.get('priority_score', 'N/A')}")
