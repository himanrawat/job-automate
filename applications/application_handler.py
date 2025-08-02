"""
Job application handling and form filling
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.user_profile import HimanshuProfile

logger = logging.getLogger(__name__)

class ApplicationHandler:
    def __init__(self, driver):
        self.driver = driver
        self.personal_info = HimanshuProfile.PERSONAL_INFO
    
    def apply_to_job(self, job_details, cover_letter):
        """Main application method - tries Easy Apply then external"""
        portal = job_details['portal'].lower()
        
        try:
            if 'linkedin' in portal:
                return self.apply_linkedin_job(job_details, cover_letter)
            elif 'indeed' in portal:
                return self.apply_indeed_job(job_details, cover_letter)
            elif 'naukri' in portal:
                return self.apply_naukri_job(job_details, cover_letter)
            else:
                return self.try_external_application(job_details, cover_letter)
                
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return {
                'status': 'failed',
                'method': 'automation_error',
                'failure_reason': f'Automation error: {str(e)}',
                'suggested_approach': 'Manual application required - automation failed',
                'estimated_time': '10-15 minutes'
            }
    
    def apply_linkedin_job(self, job_details, cover_letter):
        """Apply to LinkedIn job using Easy Apply"""
        try:
            self.driver.get(job_details['url'])
            time.sleep(3)
            
            # Look for Easy Apply button
            apply_button_selectors = [
                ".jobs-apply-button",
                "[data-control-name='jobdetails_topcard_inapply']",
                ".jobs-s-apply"
            ]
            
            for selector in apply_button_selectors:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if "Easy Apply" in button.text or "apply" in button.text.lower():
                        button.click()
                        time.sleep(2)
                        
                        # Handle multi-step application
                        result = self.fill_linkedin_easy_apply(cover_letter)
                        if result['status'] == 'success':
                            return {
                                'status': 'success',
                                'method': 'easy_apply',
                                'failure_reason': '',
                                'suggested_approach': '',
                                'estimated_time': ''
                            }
                        else:
                            return result
            
            # If no Easy Apply found, it's external
            return {
                'status': 'manual_required',
                'method': 'external_apply',
                'failure_reason': 'External application required',
                'suggested_approach': 'Click "Apply" button and fill company form - use provided resume and cover letter',
                'estimated_time': '10-15 minutes'
            }
            
        except Exception as e:
            logger.error(f"Error with LinkedIn application: {e}")
            return {
                'status': 'manual_required',
                'method': 'linkedin_error',
                'failure_reason': f'LinkedIn application error: {str(e)}',
                'suggested_approach': 'Apply manually through LinkedIn - copy provided documents',
                'estimated_time': '5-10 minutes'
            }
    
    def fill_linkedin_easy_apply(self, cover_letter):
        """Fill LinkedIn Easy Apply multi-step form"""
        try:
            max_steps = 10
            current_step = 0
            
            while current_step < max_steps:
                current_step += 1
                
                # Fill text areas
                text_areas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in text_areas:
                    if textarea.is_displayed() and textarea.is_enabled():
                        textarea.clear()
                        textarea.send_keys(cover_letter[:500])
                
                # Answer common questions
                self.answer_frontend_questions()
                
                # Look for next/submit buttons
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[aria-label='Continue to next step'], [aria-label='Submit application']")
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label='Submit application']")
                
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)
                    return {'status': 'success'}
                elif next_buttons:
                    next_buttons[0].click()
                    time.sleep(2)
                else:
                    break
            
            return {
                'status': 'manual_required',
                'method': 'complex_form',
                'failure_reason': 'Complex multi-step form',
                'suggested_approach': 'Complete LinkedIn Easy Apply manually - form too complex for automation',
                'estimated_time': '5-8 minutes'
            }
            
        except Exception as e:
            return {
                'status': 'manual_required',
                'method': 'form_error',
                'failure_reason': f'Form filling error: {str(e)}',
                'suggested_approach': 'Complete LinkedIn Easy Apply manually',
                'estimated_time': '5-10 minutes'
            }
    
    def answer_frontend_questions(self):
        """Answer common frontend developer application questions"""
        try:
            # Handle dropdowns
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")
            for dropdown in dropdowns:
                if dropdown.is_displayed():
                    options = dropdown.find_elements(By.TAG_NAME, "option")
                    # Select appropriate options for frontend developer
                    for option in options[1:]:
                        option_text = option.text.lower()
                        if any(keyword in option_text for keyword in ['yes', '3', '4', '5', 'bachelor', 'master', 'react', 'javascript']):
                            option.click()
                            break
            
            # Handle radio buttons
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            for radio in radio_buttons:
                if radio.is_displayed():
                    try:
                        label = radio.find_element(By.XPATH, "following-sibling::label | preceding-sibling::label")
                        label_text = label.text.lower()
                        # Answer appropriately for frontend developer
                        if any(keyword in label_text for keyword in ['yes', 'authorized', 'eligible', 'available', 'frontend', 'ui']):
                            radio.click()
                    except:
                        continue
                        
            # Handle text inputs
            text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number']")
            for input_field in text_inputs:
                if input_field.is_displayed() and input_field.is_enabled():
                    placeholder = (input_field.get_attribute("placeholder") or "").lower()
                    if "salary" in placeholder:
                        input_field.send_keys("negotiable")
                    elif "experience" in placeholder:
                        input_field.send_keys("3.5")
                    elif "phone" in placeholder:
                        input_field.send_keys(self.personal_info['phone'])
                    elif "years" in placeholder:
                        input_field.send_keys("3")
                        
        except Exception as e:
            logger.error(f"Error answering questions: {e}")
    
    def try_external_application(self, job_details, cover_letter):
        """Try to handle external company website applications"""
        try:
            self.driver.get(job_details['url'])
            time.sleep(5)
            
            # Look for external application links
            external_selectors = [
                "a[href*='apply']",
                "a[href*='careers']",
                "a[href*='jobs']",
                ".apply-button",
                ".btn-apply"
            ]
            
            for selector in external_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if any(keyword in element.text.lower() for keyword in ['apply', 'submit application']):
                        external_url = element.get_attribute("href")
                        
                        # Try to fill external form
                        result = self.handle_external_form(external_url, cover_letter)
                        return result
            
            # No external application found
            return {
                'status': 'manual_required',
                'method': 'no_application_found',
                'failure_reason': 'No application method found',
                'suggested_approach': 'Search for company careers page manually and apply',
                'estimated_time': '15-20 minutes'
            }
            
        except Exception as e:
            return {
                'status': 'manual_required',
                'method': 'external_error',
                'failure_reason': f'External application error: {str(e)}',
                'suggested_approach': 'Apply manually through company website',
                'estimated_time': '10-15 minutes'
            }
    
    def handle_external_form(self, form_url, cover_letter):
        """Handle external company application forms"""
        try:
            self.driver.get(form_url)
            time.sleep(5)
            
            # Check for common ATS systems
            page_source = self.driver.page_source.lower()
            
            if 'workday' in page_source:
                return self.handle_workday_form(cover_letter)
            elif 'greenhouse' in page_source:
                return self.handle_greenhouse_form(cover_letter)
            elif 'lever' in page_source:
                return self.handle_lever_form(cover_letter)
            else:
                return self.handle_generic_form(cover_letter, form_url)
                
        except Exception as e:
            return {
                'status': 'manual_required',
                'method': 'external_form_error',
                'failure_reason': f'External form error: {str(e)}',
                'suggested_approach': 'Fill external application form manually',
                'estimated_time': '10-15 minutes'
            }
    
    def handle_generic_form(self, cover_letter, form_url):
        """Handle generic application forms"""
        try:
            # Try to fill common form fields
            filled_fields = 0
            
            # Fill name fields
            name_selectors = ["input[name*='name']", "input[placeholder*='name' i]"]
            for selector in name_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(self.personal_info['name'])
                        filled_fields += 1
                        break
            
            # Fill email fields
            email_selectors = ["input[type='email']", "input[name*='email']"]
            for selector in email_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(self.personal_info['email'])
                        filled_fields += 1
                        break
            
            # Fill phone fields
            phone_selectors = ["input[type='tel']", "input[name*='phone']"]
            for selector in phone_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(self.personal_info['phone'])
                        filled_fields += 1
                        break
            
            # Fill cover letter
            text_areas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for textarea in text_areas:
                if textarea.is_displayed() and textarea.is_enabled():
                    textarea.clear()
                    textarea.send_keys(cover_letter)
                    filled_fields += 1
                    break
            
            if filled_fields >= 3:
                # Try to submit
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "input[type='submit'], button[type='submit'], .submit-btn, .apply-btn")
                for button in submit_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(3)
                        return {'status': 'success'}
                
                return {
                    'status': 'manual_required',
                    'method': 'form_partially_filled',
                    'failure_reason': 'Form partially filled but could not submit',
                    'suggested_approach': 'Complete and submit the form manually - most fields are already filled',
                    'estimated_time': '3-5 minutes'
                }
            else:
                return {
                    'status': 'manual_required',
                    'method': 'complex_external_form',
                    'failure_reason': 'Complex form structure',
                    'suggested_approach': 'Fill the external application form manually using provided documents',
                    'estimated_time': '10-15 minutes'
                }
                
        except Exception as e:
            return {
                'status': 'manual_required',
                'method': 'generic_form_error',
                'failure_reason': f'Form handling error: {str(e)}',
                'suggested_approach': 'Complete external application manually',
                'estimated_time': '10-15 minutes'
            }
    
    def handle_workday_form(self, cover_letter):
        """Handle Workday ATS forms"""
        return {
            'status': 'manual_required',
            'method': 'workday_ats',
            'failure_reason': 'Workday ATS system detected',
            'suggested_approach': 'Create Workday account if needed, then fill application using provided documents',
            'estimated_time': '15-20 minutes'
        }
    
    def handle_greenhouse_form(self, cover_letter):
        """Handle Greenhouse ATS forms"""
        return {
            'status': 'manual_required',
            'method': 'greenhouse_ats',
            'failure_reason': 'Greenhouse ATS system detected',
            'suggested_approach': 'Fill Greenhouse application form manually - upload resume and paste cover letter',
            'estimated_time': '10-15 minutes'
        }
    
    def handle_lever_form(self, cover_letter):
        """Handle Lever ATS forms"""
        return {
            'status': 'manual_required',
            'method': 'lever_ats',
            'failure_reason': 'Lever ATS system detected',
            'suggested_approach': 'Complete Lever application form manually using provided documents',
            'estimated_time': '10-15 minutes'
        }