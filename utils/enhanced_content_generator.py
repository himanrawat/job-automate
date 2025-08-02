"""
Enhanced AI-powered content generation for Apify job data
Includes contact extraction, tailored resume/cover letter generation, and improved formatting
"""

import re
import logging
from openai import OpenAI
from typing import Dict, List, Optional, Tuple
from config.api_keys import APIKeys
from config.user_profile import HimanshuProfile

logger = logging.getLogger(__name__)

class EnhancedContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=APIKeys.OPENAI_API_KEY)
    
    def extract_contact_details(self, job_data: Dict) -> Dict[str, str]:
        """
        Extract contact details from job description and company information
        Returns dict with email, phone, recruiter_name, contact_info, etc.
        """
        try:
            description = job_data.get('description', '')
            company = job_data.get('company', '')
            
            # Common email patterns
            email_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b',
            ]
            
            # Phone patterns (US, India, international)
            phone_patterns = [
                r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US
                r'\+91[-.\s]?[0-9]{10}',  # India
                r'\+[0-9]{1,3}[-.\s]?[0-9]{4,14}',  # International
                r'\b[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'  # Basic US
            ]
            
            # Contact person patterns
            contact_patterns = [
                r'contact[:\s]+([A-Za-z\s]+)',
                r'recruiter[:\s]+([A-Za-z\s]+)',
                r'hiring\s+manager[:\s]+([A-Za-z\s]+)',
                r'reach\s+out\s+to[:\s]+([A-Za-z\s]+)',
                r'questions\?[:\s]+([A-Za-z\s]+)'
            ]
            
            extracted = {
                'emails': [],
                'phones': [],
                'contact_names': [],
                'contact_instructions': '',
                'company_domain': '',
                'linkedin_company': '',
                'apply_instructions': ''
            }
            
            # Extract emails
            for pattern in email_patterns:
                emails = re.findall(pattern, description, re.IGNORECASE)
                extracted['emails'].extend(emails)
            
            # Extract phones
            for pattern in phone_patterns:
                phones = re.findall(pattern, description, re.IGNORECASE)
                extracted['phones'].extend(phones)
            
            # Extract contact names
            for pattern in contact_patterns:
                names = re.findall(pattern, description, re.IGNORECASE)
                extracted['contact_names'].extend([name.strip() for name in names])
            
            # Extract company domain for potential contact
            if company:
                # Common company domain patterns
                domain_patterns = [
                    company.lower().replace(' ', '').replace(',', '').replace('.', '') + '.com',
                    company.lower().replace(' ', '').replace(',', '').replace('.', '') + '.co',
                    company.lower().replace(' ', '').replace(',', '').replace('.', '') + '.org'
                ]
                extracted['company_domain'] = domain_patterns[0] if domain_patterns else ''
            
            # Extract LinkedIn company page
            linkedin_matches = re.findall(r'linkedin\.com/company/([^/\s]+)', description, re.IGNORECASE)
            if linkedin_matches:
                extracted['linkedin_company'] = f"linkedin.com/company/{linkedin_matches[0]}"
            
            # Extract application instructions
            apply_patterns = [
                r'apply[^.]*?(?:email|send|contact)[^.]*?\.',
                r'to\s+apply[^.]*?\.',
                r'interested\s+candidates[^.]*?\.',
                r'submit[^.]*?(?:resume|application)[^.]*?\.'
            ]
            
            for pattern in apply_patterns:
                matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
                if matches:
                    extracted['apply_instructions'] = matches[0].strip()
                    break
            
            # Remove duplicates
            extracted['emails'] = list(set(extracted['emails']))
            extracted['phones'] = list(set(extracted['phones']))
            extracted['contact_names'] = list(set(extracted['contact_names']))
            
            logger.info(f"Extracted contact details: {len(extracted['emails'])} emails, {len(extracted['phones'])} phones")
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting contact details: {e}")
            return {'emails': [], 'phones': [], 'contact_names': [], 'contact_instructions': '', 'company_domain': '', 'linkedin_company': '', 'apply_instructions': ''}
    
    def generate_tailored_resume(self, job_data: Dict, contact_details: Dict) -> str:
        """
        Generate a tailored resume based on detailed job description from Apify data
        """
        try:
            # Extract key information from Apify job data
            title = job_data.get('title', '')
            company = job_data.get('company', '')
            description = job_data.get('description', '')
            salary = job_data.get('salary', '')
            platform = job_data.get('platform', 'unknown')
            location = job_data.get('location', '')
            
            # Analyze job requirements from description
            prompt = f'''
            Generate a tailored resume for Himanshu Rawat based on this detailed job posting:
            
            === JOB DETAILS ===
            Title: {title}
            Company: {company}
            Location: {location}
            Platform: {platform}
            Salary: {salary}
            
            === JOB DESCRIPTION ===
            {description[:3000]}  # Limit for token efficiency
            
            === CANDIDATE PROFILE ===
            {HimanshuProfile.BASE_RESUME}
            
            === CONTACT DETAILS FOUND ===
            Emails: {', '.join(contact_details.get('emails', []))}
            Contact Names: {', '.join(contact_details.get('contact_names', []))}
            
            === INSTRUCTIONS ===
            1. Analyze the job description to identify key requirements, skills, and technologies
            2. Tailor the resume to emphasize relevant experience and skills
            3. Use keywords from the job description for ATS optimization
            4. Maintain professional formatting with clear sections
            5. Highlight specific achievements that match job requirements
            6. Ensure the resume feels authentic to Himanshu's actual experience
            7. Optimize for both human readability and ATS parsing
            
            === RESUME SECTIONS TO INCLUDE ===
            - Professional Summary (2-3 lines highlighting relevant experience)
            - Technical Skills (emphasizing technologies mentioned in job)
            - Professional Experience (tailored bullet points)
            - Projects (if relevant to job requirements)
            - Education
            - Additional sections if relevant
            
            Return a well-formatted resume that specifically targets this {title} role at {company}.
            '''
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            tailored_resume = response.choices[0].message.content.strip()
            logger.info(f"Generated tailored resume for {title} at {company}")
            return tailored_resume
            
        except Exception as e:
            logger.error(f"Error generating tailored resume: {e}")
            return HimanshuProfile.BASE_RESUME
    
    def generate_personalized_cover_letter(self, job_data: Dict, contact_details: Dict) -> str:
        """
        Generate a personalized cover letter with contact details and specific job insights
        """
        try:
            # Extract key information
            title = job_data.get('title', '')
            company = job_data.get('company', '')
            description = job_data.get('description', '')
            salary = job_data.get('salary', '')
            location = job_data.get('location', '')
            platform = job_data.get('platform', 'unknown')
            
            # Determine addressing
            contact_name = contact_details.get('contact_names', [])
            greeting = f"Dear {contact_name[0]}," if contact_name else "Dear Hiring Manager,"
            
            # Check for visa requirements
            location_parts = location.split(',')
            country = location_parts[-1].strip() if location_parts else ''
            visa_note = ""
            if country.upper() in ['US', 'USA', 'UNITED STATES', 'AUSTRALIA', 'CANADA', 'UK', 'UNITED KINGDOM']:
                visa_note = "I am currently based in India and open to visa sponsorship opportunities."
            
            prompt = f'''
            Write a compelling, personalized cover letter for this job application:
            
            === JOB DETAILS ===
            Title: {title}
            Company: {company}
            Location: {location}
            Salary: {salary}
            Platform: {platform}
            
            === JOB DESCRIPTION (Key Points) ===
            {description[:2500]}
            
            === CONTACT INFORMATION ===
            Greeting: {greeting}
            Contact Names: {', '.join(contact_details.get('contact_names', []))}
            Emails Found: {', '.join(contact_details.get('emails', []))}
            Application Instructions: {contact_details.get('apply_instructions', '')}
            
            === CANDIDATE PROFILE - Himanshu Rawat ===
            - 3.5+ years frontend development experience
            - React.js, JavaScript, TypeScript, Node.js expertise
            - Currently working at MelpApp, improved website responsiveness by 40%
            - Built ERP system UI from scratch, focusing on user experience
            - Strong background in modern UI/UX practices and component architecture
            - Passionate about creating products that users love
            - Portfolio: https://www.himanshurawat.in
            
            === SPECIAL NOTES ===
            {visa_note}
            
            === COVER LETTER REQUIREMENTS ===
            1. Use the appropriate greeting based on contact information
            2. Show specific knowledge of the company and role
            3. Connect Himanshu's experience directly to job requirements
            4. Demonstrate genuine enthusiasm for the specific opportunity
            5. Include relevant technical skills and achievements
            6. Mention specific projects or accomplishments that align
            7. Professional but enthusiastic tone
            8. 250-350 words maximum
            9. Include call to action for next steps
            10. If contact details found, reference willingness to discuss further
            
            Write a cover letter that feels personal and specifically crafted for this {title} role at {company}.
            '''
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.8
            )
            
            cover_letter = response.choices[0].message.content.strip()
            logger.info(f"Generated personalized cover letter for {title} at {company}")
            return cover_letter
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return f"Dear Hiring Manager,\\n\\nI am writing to express my strong interest in the {title} position at {company}..."
    
    def generate_linkedin_message(self, job_data: Dict, contact_details: Dict) -> str:
        """
        Generate a LinkedIn outreach message for recruiters/hiring managers
        """
        try:
            title = job_data.get('title', '')
            company = job_data.get('company', '')
            description = job_data.get('description', '')
            
            prompt = f'''
            Write a professional LinkedIn message to reach out about this job opportunity:
            
            Job: {title} at {company}
            
            Key Requirements (from description):
            {description[:1000]}
            
            Himanshu's Profile:
            - Frontend Developer with 3.5+ years experience
            - React.js, JavaScript, modern UI/UX expert
            - 40% performance improvement at current role
            - Portfolio: https://www.himanshurawat.in
            
            Requirements:
            1. Professional and concise (80-120 words)
            2. Show specific interest in the role
            3. Highlight most relevant experience
            4. Request brief conversation
            5. Include portfolio link naturally
            
            Write a LinkedIn message that would get a positive response from a recruiter.
            '''
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.8
            )
            
            linkedin_message = response.choices[0].message.content.strip()
            logger.info(f"Generated LinkedIn message for {title} at {company}")
            return linkedin_message
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {e}")
            return f"Hi! I'm interested in the {title} role at {company}. I'm a frontend developer with 3.5+ years of React.js experience..."
    
    def format_application_package(self, job_data: Dict, contact_details: Dict, 
                                  resume: str, cover_letter: str, linkedin_message: str) -> Dict:
        """
        Format the complete application package with improved presentation
        """
        try:
            title = job_data.get('title', '')
            company = job_data.get('company', '')
            salary = job_data.get('salary', '')
            location = job_data.get('location', '')
            url = job_data.get('url', '')
            platform = job_data.get('platform', '')
            priority_score = job_data.get('priority_score', 0)
            
            # Create formatted package
            package = {
                'job_info': {
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'platform': platform.title(),
                    'priority_score': priority_score,
                    'job_url': url
                },
                'contact_details': contact_details,
                'documents': {
                    'tailored_resume': resume,
                    'cover_letter': cover_letter,
                    'linkedin_message': linkedin_message
                },
                'application_strategy': self._generate_application_strategy(job_data, contact_details),
                'next_steps': self._generate_next_steps(job_data, contact_details)
            }
            
            logger.info(f"Formatted application package for {title} at {company}")
            return package
            
        except Exception as e:
            logger.error(f"Error formatting application package: {e}")
            return {}
    
    def _generate_application_strategy(self, job_data: Dict, contact_details: Dict) -> str:
        """Generate application strategy based on available contact information"""
        try:
            emails = contact_details.get('emails', [])
            phones = contact_details.get('phones', [])
            contact_names = contact_details.get('contact_names', [])
            apply_instructions = contact_details.get('apply_instructions', '')
            
            strategy = []
            
            if emails:
                strategy.append(f"📧 Direct Email: Send tailored resume and cover letter to {emails[0]}")
            
            if contact_names:
                strategy.append(f"👤 Personal Contact: Reach out to {contact_names[0]} via LinkedIn")
            
            if apply_instructions:
                strategy.append(f"📝 Follow Instructions: {apply_instructions}")
            
            if job_data.get('platform') == 'linkedin':
                strategy.append("🔗 LinkedIn Apply: Use platform's application system")
            elif job_data.get('platform') == 'indeed':
                strategy.append("📄 Indeed Apply: Submit through Indeed's application process")
            
            strategy.append("🌐 Company Website: Check careers page for additional opportunities")
            strategy.append("📱 Follow Up: Send LinkedIn connection request to hiring manager")
            
            return "\\n".join([f"{i+1}. {item}" for i, item in enumerate(strategy)])
            
        except Exception as e:
            logger.error(f"Error generating application strategy: {e}")
            return "1. Submit application through job posting\\n2. Follow up via LinkedIn"
    
    def _generate_next_steps(self, job_data: Dict, contact_details: Dict) -> List[str]:
        """Generate specific next steps for this application"""
        try:
            steps = [
                "Review and customize resume for this specific role",
                "Personalize cover letter with company research",
                "Submit application through primary channel",
                "Connect with hiring manager on LinkedIn",
                "Follow up within 1 week if no response",
                "Research company culture and recent news",
                "Prepare for potential screening call"
            ]
            
            # Add specific steps based on contact details
            if contact_details.get('emails'):
                steps.insert(2, f"Send direct email to {contact_details['emails'][0]}")
            
            if contact_details.get('contact_names'):
                steps.insert(3, f"Reach out to {contact_details['contact_names'][0]} personally")
            
            return steps
            
        except Exception as e:
            logger.error(f"Error generating next steps: {e}")
            return ["Submit application", "Follow up via LinkedIn"]

# Usage example and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample job data
    sample_job = {
        'title': 'Frontend Developer',
        'company': 'TechCorp Inc.',
        'description': 'We are looking for a React.js developer... Contact Jane Smith at jane@techcorp.com',
        'location': 'San Francisco, CA',
        'salary': '$100k-120k',
        'platform': 'indeed',
        'url': 'https://example.com/job/123'
    }
    
    generator = EnhancedContentGenerator()
    contact_details = generator.extract_contact_details(sample_job)
    print("Contact details:", contact_details)
