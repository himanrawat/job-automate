"""
Himanshu Rawat's Personal Profile Configuration
"""

class HimanshuProfile:
    # Personal Information
    PERSONAL_INFO = {
        'name': 'Himanshu Rawat',
        'email': 'iam@himanshurawat.in',
        'phone': '+91-9910978079',
        'linkedin': 'https://www.linkedin.com/in/rawat-himanshu/',
        'github': 'https://github.com/himanrawat',
        'portfolio': 'https://www.himanshurawat.in'
    }
    
    # Resume Content
    BASE_RESUME = """
HIMANSHU RAWAT
Frontend Developer | Ghaziabad, IN | +91-9910978079 | iam@himanshurawat.in
LinkedIn: https://www.linkedin.com/in/rawat-himanshu/ | GitHub: https://github.com/himanrawat
Portfolio: https://www.himanshurawat.in

PROFESSIONAL SUMMARY
Frontend Developer with 3.5+ years of experience designing and building responsive, high-performance web applications. Skilled in React.js, JavaScript, and modern UI/UX practices. Proven ability to collaborate cross-functionally and deliver scalable, user-focused solutions. Passionate about creating products that users love to use and driving innovation through continuous improvement.

EXPERIENCE

MelpApp | Frontend Developer | 2025 – Present
• Redeveloped entire website based on designer-provided UI/UX, improving responsiveness by 40%
• Modernized legacy codebase without disrupting platform compatibility
• Enhanced overall user experience and reduced bounce rate by implementing lazy loading and optimized assets
• Collaborated with backend teams to ensure seamless API integration

Webiosis Systems | UI Developer | 2024 – 2025
• Designed and built a school ERP system from scratch
• Gathered requirements and planned a modular system architecture
• Implemented asynchronous data fetching to reduce system delays
• Collaborated with stakeholders to ensure the system met user needs

Yetticate Solutions Pvt. Ltd. | Web Developer | 2022 – 2024
• Redesigned the client onboarding process to streamline operations
• Worked with backend developers to integrate a faster API
• Simplified user registration steps for a smoother experience
• Conducted thorough testing to verify improvements in the workflow

Adaan Digital Solutions Pvt. Ltd. | Web Designer | 2022
• Revamped legacy websites by migrating them to CMS platforms (Duda, WordPress)
• Conducted user research to guide design updates
• Tested prototypes to improve usability while maintaining the familiar look
• Coordinated with the content team to ensure smooth integration of the new design

EDUCATION
Master of Science in Computer Applications – 2022
Swami Vivekanand Subharti University, Meerut, IN

Bachelor of Commerce – 2019
Sam Higginbottom University of Agriculture, Technology and Sciences, Allahabad, IN

PROJECTS
I Am Art – Photography Portfolio
• A responsive portfolio showcasing photographic work
• Implemented smooth animations using GSAP and Locomotive Scroll
• Built custom image galleries with lazy loading and slider functionality
Stack: HTML5, CSS3, JavaScript, GSAP, Locomotive Scroll, Shery.js

Last3Feet Marketing Solutions Portfolio
• React-based portfolio website for a retail advertisement and marketing services company
• Dark/Light mode support, responsive design, Navigation using React Router
Stack: React 18.3, Vite 6.0, Tailwind CSS 3.4, React Router DOM 7.1, ESLint 9.17

TECHNICAL SKILLS
Languages & Frameworks: JavaScript, HTML5, CSS3, React.js, Next.js, Tailwind CSS
Tooling & Utilities: Git, Vite, Webpack, ESLint, VS Code
API & Backend: REST APIs, Axios, Fetch
Design & UI Tools: Figma, Adobe XD

CORE COMPETENCIES
UI Development • Component-Based Architecture • Responsive Web Design • Accessibility (WCAG/ADA) • Cross-Functional Collaboration • Agile & Scrum Methodologies • Clean Code Practices • Performance Optimization • Version Control (Git) • Feature Enhancement • Technical Requirement Analysis • Code Review & Refactoring
    """
    
    # Technical Skills
    TECHNICAL_SKILLS = [
        'JavaScript', 'HTML5', 'CSS3', 'React.js', 'Next.js', 'Tailwind CSS',
        'Git', 'Vite', 'Webpack', 'ESLint', 'VS Code', 'REST APIs', 'Axios', 
        'Fetch', 'Figma', 'Adobe XD', 'Responsive Design', 'UI/UX Design',
        'Component-Based Architecture', 'Performance Optimization', 'GSAP',
        'Locomotive Scroll', 'React Router', 'CSS Grid', 'Flexbox'
    ]
    
    # Keywords to avoid in job descriptions
    AVOID_KEYWORDS = ['vue', 'angular', 'Vue.js', 'Angular', 'AngularJS', 'docker', 'kubernetes', 'devops', 'backend', 'server', 'database administration']
    
    # Target job roles
    TARGET_ROLES = [
        'Frontend Developer', 'UI Developer', 'UI/UX Developer', 
        'Web Developer', 'React Developer', 'JavaScript Developer',
        'Frontend Engineer', 'UI Engineer', 'Web UI Developer'
    ]
