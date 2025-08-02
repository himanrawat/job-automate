"""
AI-powered content generation for resumes and cover letters
"""

import openai
import logging
from config.api_keys import APIKeys
from config.user_profile import HimanshuProfile

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self):
        openai.api_key = APIKeys.OPENAI_API_KEY
    
    def tailor_resume_for_frontend(self, job_details, region):
        """Generate tailored resume for frontend positions"""
        try:
            regional_tips = {
                'USA': "Emphasize impact with metrics, highlight React.js expertise, mention performance optimization",
                'INDIA': "Focus on UI/UX skills, mention responsive design, highlight modern frameworks",
                'AUSTRALIA': "Emphasize user experience focus, mention accessibility, highlight collaboration",
                'UNITED_KINGDOM': "Professional tone, mention component architecture, highlight best practices",
                'EUROPE': "Mention international perspective, highlight technical skills, modern development"
            }
            
            prompt = f"""
            Tailor this frontend developer resume for a {region} job market:
            
            Job Title: {job_details['title']}
            Company: {job_details['company']}
            Region: {region}
            Job Description: {job_details['description'][:2000]}
            
            Regional considerations: {regional_tips.get(region, '')}
            
            Base Resume: {HimanshuProfile.BASE_RESUME}
            
            Key points to emphasize:
            - 3.5+ years frontend development experience
            - React.js, JavaScript, HTML5, CSS3 expertise
            - 40% responsiveness improvement achievement
            - Modern UI/UX practices and component-based architecture
            - Performance optimization and user experience focus
            
            Avoid mentioning: {', '.join(HimanshuProfile.AVOID_KEYWORDS)}
            
            Return a tailored resume optimized for ATS systems and this specific frontend role.
            Keep the same structure but emphasize most relevant experiences and skills.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error tailoring resume: {e}")
            return HimanshuProfile.BASE_RESUME
    
    def generate_enthusiastic_cover_letter(self, job_details, region, priority_level):
        """Generate enthusiastic cover letter for frontend positions"""
        try:
            cultural_notes = {
                'USA': "Direct, achievement-focused, confident tone, mention innovation and user impact",
                'INDIA': "Respectful, emphasize technical growth and passion for frontend development",
                'AUSTRALIA': "Friendly but professional, mention teamwork and user-centered design",
                'UNITED_KINGDOM': "Polite, structured, professional approach with technical depth",
                'EUROPE': "Formal but enthusiastic, mention international perspective and modern practices"
            }
            
            startup_focus = "🔥" in priority_level
            
            visa_note = ""
            from config.job_preferences import JobPreferences
            if JobPreferences.REGIONS[region]['visa_required']:
                visa_note = "I am currently based in India and open to visa sponsorship opportunities."
            
            startup_tone = """
            Special focus for startup environment:
            - Show enthusiasm for fast-paced, innovative environment
            - Mention adaptability and learning agility
            - Emphasize direct impact on product and user experience
            - Show passion for building products users love
            """ if startup_focus else ""
            
            prompt = f"""
            Write an enthusiastic cover letter for this {region} frontend developer position:
            
            Job Title: {job_details['title']}
            Company: {job_details['company']}
            Priority Level: {priority_level}
            Region: {region}
            Job Description: {job_details['description'][:1500]}
            
            Candidate Profile - Himanshu Rawat:
            - 3.5+ years frontend development experience
            - Passionate about creating products that users love to use
            - Improved website responsiveness by 40% at current role
            - Built ERP system UI from scratch
            - Expert in React.js, JavaScript, modern UI/UX practices
            - Strong focus on user experience and performance optimization
            - Portfolio: https://www.himanshurawat.in
            
            Cultural approach for {region}: {cultural_notes.get(region, '')}
            {startup_tone}
            {visa_note}
            
            Tone: Enthusiastic and passionate about frontend development
            Key themes: User experience, innovation, continuous improvement, modern web technologies
            Length: 250-300 words
            
            Make it specific to the role and show genuine excitement about frontend development opportunities.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return "Enthusiastic cover letter about frontend development passion and user-focused approach"
    
    def generate_direct_recruiter_message(self, job_details, region, priority_level):
        """Generate direct recruiter outreach message"""
        try:
            startup_focus = "🔥" in priority_level
            
            prompt = f"""
            Write a direct, professional message to reach out to a recruiter about this {region} frontend developer position:
            
            Job Title: {job_details['title']}
            Company: {job_details['company']}
            Priority: {priority_level}
            Region: {region}
            
            Candidate Profile - Himanshu Rawat:
            - Frontend Developer with 3.5+ years experience
            - React.js, JavaScript, modern UI/UX expert
            - Currently at MelpApp, improved responsiveness by 40%
            - Passionate about user experience and performance
            - Portfolio: https://www.himanshurawat.in
            
            Message should be:
            - Direct and to the point (60-80 words)
            - Professional but confident
            - Express genuine interest in frontend development
            - Mention key relevant experience briefly
            - Request brief conversation about the role
            
            {"Focus on startup enthusiasm and adaptability" if startup_focus else "Focus on professional growth and technical expertise"}
            
            Tone: Direct and professional with enthusiasm for frontend development
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating recruiter message: {e}")
            return "Hi! I'm interested in discussing the frontend developer role. I'm Himanshu, a React.js developer with 3.5+ years experience focusing on user experience and performance optimization. Would you be available for a brief conversation?"
