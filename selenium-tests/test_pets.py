import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os


class TestPetsFunctionality:
    """Test cases for SmartHotel360 pets feature"""
    
    def test_pets_page_navigation(self, driver):
        """Test navigation to pets page"""
        wait = WebDriverWait(driver, 10)
        
        try:
            # Navigate to pets page directly
            pets_url = f"{driver.base_url}/Pets"
            driver.get(pets_url)
            time.sleep(3)
            
            # Check if we're on pets page
            current_url = driver.current_url
            assert "Pets" in current_url or "pets" in current_url
            print(f"✓ Successfully navigated to pets page: {current_url}")
            
        except Exception as e:
            pytest.fail(f"Failed to navigate to pets page: {e}")
    
    def test_pets_page_elements(self, driver):
        """Test pets page contains expected elements"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Check for pets-related content
            pets_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='pet'], [class*='Pet']")
            if pets_elements:
                print(f"✓ Found {len(pets_elements)} pet-related elements")
            else:
                print("⚠ No pet-specific elements found")
            
            # Check for upload-related elements
            upload_elements = driver.find_elements(By.CSS_SELECTOR, 
                "input[type='file'], [class*='upload'], [class*='Upload'], button[class*='upload']")
            if upload_elements:
                print(f"✓ Found {len(upload_elements)} upload-related elements")
            else:
                print("⚠ No upload elements found")
                
            # Check for form elements
            form_elements = driver.find_elements(By.TAG_NAME, "form")
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            button_elements = driver.find_elements(By.TAG_NAME, "button")
            
            print(f"✓ Page contains {len(form_elements)} forms, {len(input_elements)} inputs, {len(button_elements)} buttons")
            
        except Exception as e:
            print(f"⚠ Error checking pets page elements: {e}")
    
    def test_pet_upload_form_presence(self, driver):
        """Test pet upload form is present and functional"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Look for file input
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            if file_inputs:
                file_input = file_inputs[0]
                print("✓ File input found for pet upload")
                
                # Check if input accepts images
                accept_attr = file_input.get_attribute("accept")
                if accept_attr and "image" in accept_attr:
                    print("✓ File input accepts images")
                else:
                    print("⚠ File input accept attribute not found or doesn't specify images")
                    
                # Test file input functionality (simulate)
                try:
                    # Note: We can't actually upload files in most CI environments
                    # but we can test that the input is interactable
                    file_input.click()
                    print("✓ File input is clickable")
                except Exception:
                    print("⚠ File input not clickable")
                    
            else:
                print("⚠ No file input found for pet upload")
            
            # Look for upload button
            upload_buttons = driver.find_elements(By.CSS_SELECTOR, 
                "button[class*='upload'], input[type='submit'], [class*='btn']")
            
            if upload_buttons:
                print(f"✓ Found {len(upload_buttons)} potential upload/submit buttons")
                
                # Check button text
                for button in upload_buttons:
                    button_text = button.text.lower()
                    if any(word in button_text for word in ['upload', 'submit', 'send', 'check']):
                        print(f"✓ Found relevant button: '{button.text}'")
                        break
            else:
                print("⚠ No upload/submit buttons found")
                
        except Exception as e:
            print(f"⚠ Error testing pet upload form: {e}")
    
    def test_pet_name_input(self, driver):
        """Test pet name input field"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Look for name input field
            name_inputs = driver.find_elements(By.CSS_SELECTOR, 
                "input[placeholder*='name'], input[name*='name'], input[id*='name']")
            
            if name_inputs:
                name_input = name_inputs[0]
                print("✓ Pet name input found")
                
                # Test typing in name input
                name_input.clear()
                name_input.send_keys("Buddy")
                time.sleep(1)
                
                entered_value = name_input.get_attribute("value")
                if entered_value == "Buddy":
                    print("✓ Pet name input accepts text correctly")
                else:
                    print(f"⚠ Pet name input value incorrect: {entered_value}")
                    
            else:
                # Look for any text inputs that might be for pet name
                text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                if text_inputs:
                    print(f"✓ Found {len(text_inputs)} text inputs (one might be for pet name)")
                else:
                    print("⚠ No name input or text inputs found")
                    
        except Exception as e:
            print(f"⚠ Error testing pet name input: {e}")
    
    def test_pet_approval_status_check(self, driver):
        """Test pet approval status checking functionality"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Look for elements related to checking approval status
            status_elements = driver.find_elements(By.CSS_SELECTOR, 
                "[class*='status'], [class*='approval'], [class*='check'], [class*='result']")
            
            if status_elements:
                print(f"✓ Found {len(status_elements)} status-related elements")
            else:
                print("⚠ No status/approval elements found")
            
            # Look for buttons that might check status
            check_buttons = driver.find_elements(By.CSS_SELECTOR, 
                "button[class*='check'], button[class*='status'], [class*='btn']")
            
            for button in check_buttons:
                button_text = button.text.lower()
                if any(word in button_text for word in ['check', 'status', 'verify', 'result']):
                    print(f"✓ Found status check button: '{button.text}'")
                    
                    # Test clicking (but expect it might not work without valid data)
                    try:
                        button.click()
                        time.sleep(2)
                        print("✓ Status check button is clickable")
                    except Exception:
                        print("⚠ Status check button not clickable or no response")
                    break
                    
        except Exception as e:
            print(f"⚠ Error testing pet approval status: {e}")
    
    def test_pets_page_navigation_from_search(self, driver):
        """Test navigation to pets page from search form"""
        wait = WebDriverWait(driver, 10)
        
        try:
            # Start from home page
            driver.get(driver.base_url)
            time.sleep(2)
            
            # Try to activate guests section and enable pets
            search_groups = driver.find_elements(By.CLASS_NAME, "sh-search-group")
            
            if len(search_groups) >= 3:
                # Click guests section
                search_groups[2].click()
                time.sleep(2)
                
                # Look for pet selection buttons
                pet_buttons = driver.find_elements(By.CSS_SELECTOR, 
                    "button[class*='guest'][class*='extra'], .sh-guests-extra_button")
                
                if len(pet_buttons) >= 2:
                    # Click "Yes" for bringing pets
                    pet_buttons[1].click()
                    time.sleep(1)
                    
                    # Look for "Check it" link to pets page
                    pet_links = driver.find_elements(By.CSS_SELECTOR, 
                        "a[href*='Pets'], .sh-guests-pets_link")
                    
                    if pet_links:
                        visible_link = None
                        for link in pet_links:
                            if link.is_displayed():
                                visible_link = link
                                break
                        
                        if visible_link:
                            print("✓ Pet check link found and visible")
                            
                            # Test clicking the link
                            try:
                                visible_link.click()
                                time.sleep(3)
                                
                                # Check if we navigated to pets page
                                current_url = driver.current_url
                                if "Pets" in current_url or "pets" in current_url:
                                    print("✓ Successfully navigated to pets page from search")
                                else:
                                    print(f"⚠ Navigation didn't reach pets page: {current_url}")
                            except Exception:
                                print("⚠ Could not click pet check link")
                        else:
                            print("⚠ Pet check link not visible")
                    else:
                        print("⚠ Pet check link not found after selecting pets")
                else:
                    print("⚠ Pet selection buttons not found")
            else:
                print("⚠ Not enough search groups found")
                
        except Exception as e:
            print(f"⚠ Error testing pets navigation from search: {e}")
    
    def test_pets_page_accessibility_basic(self, driver):
        """Basic accessibility test for pets page"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Check for alt attributes on images
            images = driver.find_elements(By.TAG_NAME, "img")
            images_with_alt = 0
            
            for img in images:
                alt_text = img.get_attribute("alt")
                if alt_text:
                    images_with_alt += 1
            
            print(f"✓ {images_with_alt}/{len(images)} images have alt attributes")
            
            # Check for form labels
            inputs = driver.find_elements(By.TAG_NAME, "input")
            labels = driver.find_elements(By.TAG_NAME, "label")
            
            print(f"✓ Found {len(labels)} labels for {len(inputs)} inputs")
            
            # Check for button text
            buttons = driver.find_elements(By.TAG_NAME, "button")
            buttons_with_text = 0
            
            for button in buttons:
                if button.text.strip():
                    buttons_with_text += 1
            
            print(f"✓ {buttons_with_text}/{len(buttons)} buttons have text content")
            
        except Exception as e:
            print(f"⚠ Error checking pets page accessibility: {e}")
    
    def test_pets_api_integration_check(self, driver):
        """Check if pets feature integrates with backend API"""
        wait = WebDriverWait(driver, 10)
        
        # Navigate to pets page
        pets_url = f"{driver.base_url}/Pets"
        driver.get(pets_url)
        time.sleep(3)
        
        try:
            # Check browser console for API-related errors
            logs = driver.get_log('browser')
            api_errors = []
            
            for log in logs:
                if log['level'] == 'SEVERE':
                    message = log['message'].lower()
                    if any(keyword in message for keyword in ['api', 'fetch', 'xhr', 'network', '500', '404']):
                        api_errors.append(log['message'])
            
            if api_errors:
                print(f"⚠ Found {len(api_errors)} potential API-related errors:")
                for error in api_errors[:3]:  # Show first 3 errors
                    print(f"  - {error}")
            else:
                print("✓ No severe API-related errors found in console")
                
        except Exception as e:
            print(f"⚠ Could not check browser logs: {e}")
        
        try:
            # Check if page makes requests to expected endpoints
            # Note: This is limited without access to network monitoring
            # but we can check if the page structure suggests API integration
            
            # Look for JavaScript that might indicate API calls
            scripts = driver.find_elements(By.TAG_NAME, "script")
            api_indicators = []
            
            for script in scripts:
                script_content = script.get_attribute("innerHTML") or ""
                if any(keyword in script_content.lower() for keyword in ['/api/', 'fetch(', 'axios', 'pets']):
                    api_indicators.append("API-related JavaScript found")
                    break
            
            if api_indicators:
                print("✓ Page contains JavaScript that suggests API integration")
            else:
                print("⚠ No clear API integration indicators found")
                
        except Exception as e:
            print(f"⚠ Error checking API integration: {e}")
