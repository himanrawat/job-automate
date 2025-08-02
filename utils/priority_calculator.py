"""
Priority Calculation for Job Applications
"""

import re
from config.job_preferences import JobPreferences

class PriorityCalculator:
    def __init__(self):
        self.top_startups = JobPreferences.TOP_STARTUPS
        self.good_companies = JobPreferences.ESTABLISHED_GOOD_COMPANIES
    
    def calculate_priority(self, job_details, company_info=None):
        """Calculate priority score for job application"""
        try:
            score = 0
            company_name = job_details.get('company', '').lower()
            job_description = job_details.get('description', '').lower()
            job_title = job_details.get('title', '').lower()
            
            # Company type analysis (50% weight)
            if self.is_startup(company_name, job_description):
                score += 40
                logger.info(f"Startup detected: {company_name}")
            elif self.has_good_reviews(company_name):
                score += 35
                logger.info(f"Good company detected: {company_name}")
            elif company_name in [c.lower() for c in self.good_companies]:
                score += 30
            else:
                score += 15
            
            # Job match analysis (25% weight)
            match_percentage = self.calculate_skill_match(job_description)
            score += (match_percentage / 100) * 25
            
            # Work culture/flexibility (15% weight)
            if any(keyword in job_description for keyword in ['remote', 'work from home', 'hybrid']):
                score += 10
            if any(keyword in job_description for keyword in ['flexible', 'startup culture', 'fast-paced']):
                score += 5
            
            # Modern tech stack (10% weight)
            if self.uses_modern_frontend_stack(job_description):
                score += 10
            
            # Return priority level
            if score >= 65:
                return "High 🔥"
            elif score >= 45:
                return "Medium 🟡"
            else:
                return "Low 🔵"
                
        except Exception as e:
            logger.error(f"Error calculating priority: {e}")
            return "Medium 🟡"
    
    def is_startup(self, company_name, job_description):
        """Detect if company is a startup"""
        startup_indicators = [
            'startup', 'scale-up', 'founded in 20', 'series a', 'series b', 'series c',
            'seed funding', 'venture capital', 'equity', 'stock options',
            'fast-growing', 'rapidly expanding', 'early stage'
        ]
        
        # Check company name against known startups
        if company_name in [s.lower() for s in self.top_startups]:
            return True
            
        # Check job description for startup keywords
        return any(keyword in job_description for keyword in startup_indicators)
    
    def has_good_reviews(self, company_name):
        """Check if company has good reviews (simplified)"""
        # This is a simplified version - in production, you'd integrate with Glassdoor API
        good_review_indicators = [
            'great place to work', 'best company', 'top employer',
            'employee satisfaction', 'work-life balance', 'learning culture'
        ]
        return company_name in [c.lower() for c in self.good_companies]
    
    def calculate_skill_match(self, job_description):
        """Calculate how well job matches Himanshu's frontend skills"""
        try:
            from config.user_profile import HimanshuProfile
            
            job_keywords = set(re.findall(r'\b[a-zA-Z]+\b', job_description.lower()))
            skill_keywords = set(skill.lower() for skill in HimanshuProfile.TECHNICAL_SKILLS)
            
            # Frontend-specific keywords get higher weight
            frontend_keywords = {'react', 'javascript', 'html', 'css', 'frontend', 'ui', 'ux', 'responsive'}
            frontend_matches = job_keywords.intersection(frontend_keywords)
            
            total_matches = job_keywords.intersection(skill_keywords)
            
            # Calculate score with frontend bonus
            base_score = (len(total_matches) / len(skill_keywords)) * 100 if skill_keywords else 0
            frontend_bonus = len(frontend_matches) * 5  # 5% bonus per frontend keyword
            
            final_score = min(base_score + frontend_bonus, 100)
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating skill match: {e}")
            return 50
    
    def uses_modern_frontend_stack(self, job_description):
        """Check if job uses modern frontend technologies"""
        modern_stack = [
            'react', 'next.js', 'typescript', 'tailwind', 'vite', 'webpack',
            'es6', 'modern javascript', 'component-based', 'spa', 'responsive design'
        ]
        return any(tech in job_description for tech in modern_stack)