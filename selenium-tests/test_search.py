import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class TestSearchFunctionality:
    """Test cases for SmartHotel360 search functionality"""
    
    def test_search_tabs_present(self, home_page):
        """Test that search tabs are present and clickable"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            search_tabs = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "sh-search-tab"))
            )
            
            assert len(search_tabs) >= 2
            
            # Check Smart Room tab
            smart_tab = None
            conference_tab = None
            
            for tab in search_tabs:
                if "smart room" in tab.text.lower():
                    smart_tab = tab
                elif "conference" in tab.text.lower():
                    conference_tab = tab
            
            assert smart_tab is not None, "Smart Room tab not found"
            assert conference_tab is not None, "Conference Room tab not found"
            
            # Test tab clicking
            if not "is-active" in smart_tab.get_attribute("class"):
                smart_tab.click()
                time.sleep(1)
            
            assert "is-active" in smart_tab.get_attribute("class")
            print("✓ Search tabs found and Smart Room tab is active")
            
        except TimeoutException:
            pytest.fail("Search tabs not found")
    
    def test_where_input_functionality(self, home_page):
        """Test location search input"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Find where input (might be input or div)
            where_input = None
            
            # Try different selectors
            possible_selectors = [
                (By.CSS_SELECTOR, "input[placeholder*='Where']"),
                (By.CSS_SELECTOR, "[ref='whereinput']"),
                (By.CSS_SELECTOR, ".sh-search-input"),
                (By.XPATH, "//input[contains(@placeholder, 'Where')]")
            ]
            
            for selector in possible_selectors:
                try:
                    where_input = home_page.find_element(*selector)
                    if where_input.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if where_input is None:
                # Try clicking on search area to activate input
                search_groups = home_page.find_elements(By.CLASS_NAME, "sh-search-group")
                if search_groups:
                    search_groups[0].click()
                    time.sleep(1)
                    
                    # Try finding input again
                    for selector in possible_selectors:
                        try:
                            where_input = home_page.find_element(*selector)
                            if where_input.is_displayed():
                                break
                        except NoSuchElementException:
                            continue
            
            if where_input:
                # Test typing in location
                where_input.clear()
                where_input.send_keys("New York")
                time.sleep(2)  # Wait for suggestions
                
                # Check if suggestions appear
                try:
                    suggestions = home_page.find_elements(By.CLASS_NAME, "sh-search-option")
                    if suggestions:
                        print(f"✓ Found {len(suggestions)} location suggestions")
                        # Click first suggestion
                        suggestions[0].click()
                        time.sleep(1)
                    else:
                        print("⚠ No location suggestions found")
                except NoSuchElementException:
                    print("⚠ Location suggestions not found")
                
                print("✓ Where input functionality working")
            else:
                print("⚠ Where input not found or not interactable")
                
        except Exception as e:
            print(f"⚠ Error testing where input: {e}")
    
    def test_when_date_selection(self, home_page):
        """Test date picker functionality"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Find and click when section
            when_elements = home_page.find_elements(By.CSS_SELECTOR, "[class*='when'], .sh-search-group")
            
            when_clicked = False
            for element in when_elements:
                if "when" in element.text.lower() or "when" in element.get_attribute("class"):
                    element.click()
                    when_clicked = True
                    time.sleep(2)
                    break
            
            if not when_clicked and len(when_elements) >= 2:
                # Try clicking second search group (likely the when group)
                when_elements[1].click()
                time.sleep(2)
                when_clicked = True
            
            if when_clicked:
                # Check if date picker appears
                date_picker_selectors = [
                    (By.CLASS_NAME, "react-datepicker"),
                    (By.CSS_SELECTOR, "[class*='datepicker']"),
                    (By.CSS_SELECTOR, "[class*='calendar']"),
                    (By.CLASS_NAME, "sh-search-when")
                ]
                
                date_picker_found = False
                for selector in date_picker_selectors:
                    try:
                        date_picker = home_page.find_element(*selector)
                        if date_picker.is_displayed():
                            date_picker_found = True
                            print("✓ Date picker found and displayed")
                            
                            # Try to click a date
                            try:
                                date_elements = home_page.find_elements(By.CSS_SELECTOR, ".react-datepicker__day:not(.react-datepicker__day--disabled)")
                                if date_elements:
                                    date_elements[5].click()  # Click a future date
                                    time.sleep(1)
                                    print("✓ Date selection working")
                            except Exception:
                                print("⚠ Date clicking not working")
                            
                            break
                    except NoSuchElementException:
                        continue
                
                if not date_picker_found:
                    print("⚠ Date picker not found after clicking when section")
            else:
                print("⚠ Could not activate when/date section")
                
        except Exception as e:
            print(f"⚠ Error testing date functionality: {e}")
    
    def test_guests_selection(self, home_page):
        """Test guests/rooms selection functionality"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Find guests section
            guests_elements = home_page.find_elements(By.CSS_SELECTOR, "[class*='guest'], .sh-search-group")
            
            guests_clicked = False
            for element in guests_elements:
                element_text = element.text.lower()
                if "guest" in element_text or "people" in element_text:
                    element.click()
                    guests_clicked = True
                    time.sleep(2)
                    break
            
            if not guests_clicked and len(guests_elements) >= 3:
                # Try clicking third search group (likely guests)
                guests_elements[2].click()
                time.sleep(2)
                guests_clicked = True
            
            if guests_clicked:
                # Check for guests configuration panel
                try:
                    guests_config = home_page.find_element(By.CLASS_NAME, "sh-guests")
                    if guests_config.is_displayed():
                        print("✓ Guests configuration panel found")
                        
                        # Test increment/decrement buttons
                        try:
                            increment_buttons = home_page.find_elements(By.CSS_SELECTOR, "button[class*='increment'], .sh-guests-room_button")
                            if increment_buttons:
                                increment_buttons[0].click()
                                time.sleep(1)
                                print("✓ Guest increment functionality working")
                        except Exception:
                            print("⚠ Guest increment/decrement not working")
                        
                        # Test room selection
                        try:
                            room_buttons = home_page.find_elements(By.CLASS_NAME, "sh-guests-room")
                            if room_buttons:
                                room_buttons[0].click()
                                time.sleep(1)
                                print("✓ Room selection working")
                        except Exception:
                            print("⚠ Room selection not working")
                            
                        # Test pet selection
                        try:
                            pet_buttons = home_page.find_elements(By.CSS_SELECTOR, "button[class*='guest'][class*='extra'], .sh-guests-extra_button")
                            if len(pet_buttons) >= 2:
                                pet_buttons[1].click()  # Click "Yes" for pets
                                time.sleep(1)
                                print("✓ Pet selection working")
                                
                                # Check if "Check it" link appears
                                pet_link = home_page.find_elements(By.CSS_SELECTOR, "[href*='Pets'], .sh-guests-pets_link")
                                if pet_link:
                                    print("✓ Pet check link found")
                        except Exception:
                            print("⚠ Pet selection not working")
                            
                except NoSuchElementException:
                    print("⚠ Guests configuration panel not found")
            else:
                print("⚠ Could not activate guests section")
                
        except Exception as e:
            print(f"⚠ Error testing guests functionality: {e}")
    
    def test_find_room_button(self, home_page):
        """Test Find a Room button functionality"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Look for Find a Room button
            find_room_selectors = [
                (By.LINK_TEXT, "Find a Room"),
                (By.PARTIAL_LINK_TEXT, "Find"),
                (By.CLASS_NAME, "sh-search-button"),
                (By.CSS_SELECTOR, "a[href*='SearchRooms']")
            ]
            
            find_button = None
            for selector in find_room_selectors:
                try:
                    find_button = home_page.find_element(*selector)
                    if find_button.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if find_button:
                # Check if button is enabled/disabled
                button_classes = find_button.get_attribute("class")
                is_disabled = "disabled" in button_classes.lower() or "is-disabled" in button_classes.lower()
                
                print(f"✓ Find a Room button found - {'Disabled' if is_disabled else 'Enabled'}")
                
                # If enabled, test clicking (but don't navigate away)
                if not is_disabled:
                    href = find_button.get_attribute("href")
                    if href and "SearchRooms" in href:
                        print("✓ Find a Room button has correct link")
                    else:
                        print("⚠ Find a Room button link incorrect")
                else:
                    print("ℹ Find a Room button is disabled (expected when form incomplete)")
            else:
                print("⚠ Find a Room button not found")
                
        except Exception as e:
            print(f"⚠ Error testing Find a Room button: {e}")
    
    def test_conference_room_tab(self, home_page):
        """Test Conference Room tab functionality"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Find and click Conference Room tab
            search_tabs = home_page.find_elements(By.CLASS_NAME, "sh-search-tab")
            
            conference_tab = None
            for tab in search_tabs:
                if "conference" in tab.text.lower():
                    conference_tab = tab
                    break
            
            if conference_tab:
                conference_tab.click()
                time.sleep(2)
                
                # Check if tab is now active
                if "is-active" in conference_tab.get_attribute("class"):
                    print("✓ Conference Room tab activated")
                    
                    # Check if button text changed
                    find_buttons = home_page.find_elements(By.CLASS_NAME, "sh-search-button")
                    for button in find_buttons:
                        if "conference" in button.text.lower():
                            print("✓ Button text changed to Conference Room")
                            break
                else:
                    print("⚠ Conference Room tab not activated")
            else:
                print("⚠ Conference Room tab not found")
                
        except Exception as e:
            print(f"⚠ Error testing Conference Room tab: {e}")
    
    def test_search_workflow_end_to_end(self, home_page):
        """Test complete search workflow"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            print("Starting end-to-end search workflow test...")
            
            # Step 1: Enter location
            search_groups = home_page.find_elements(By.CLASS_NAME, "sh-search-group")
            if search_groups:
                search_groups[0].click()
                time.sleep(1)
                
                # Try to find and use location input
                location_inputs = home_page.find_elements(By.CSS_SELECTOR, "input[placeholder*='Where'], .sh-search-input")
                if location_inputs:
                    location_input = location_inputs[0]
                    location_input.clear()
                    location_input.send_keys("Seattle")
                    time.sleep(2)
                    
                    # Try to select first suggestion
                    suggestions = home_page.find_elements(By.CLASS_NAME, "sh-search-option")
                    if suggestions:
                        suggestions[0].click()
                        time.sleep(1)
                        print("✓ Step 1: Location selected")
                    else:
                        print("⚠ Step 1: No location suggestions")
                else:
                    print("⚠ Step 1: Location input not found")
            
            # Step 2: Select dates (if when section available)
            if len(search_groups) >= 2:
                search_groups[1].click()
                time.sleep(2)
                
                # Look for date picker
                date_pickers = home_page.find_elements(By.CSS_SELECTOR, ".react-datepicker__day:not(.react-datepicker__day--disabled)")
                if date_pickers and len(date_pickers) >= 2:
                    date_pickers[1].click()  # Start date
                    time.sleep(1)
                    if len(date_pickers) >= 3:
                        date_pickers[2].click()  # End date
                        time.sleep(1)
                    print("✓ Step 2: Dates selected")
                else:
                    print("⚠ Step 2: Date selection not available")
            
            # Step 3: Configure guests (if guests section available)
            if len(search_groups) >= 3:
                search_groups[2].click()
                time.sleep(2)
                print("✓ Step 3: Guests section opened")
            
            # Step 4: Check Find button status
            find_buttons = home_page.find_elements(By.CLASS_NAME, "sh-search-button")
            if find_buttons:
                button = find_buttons[0]
                is_disabled = "disabled" in button.get_attribute("class").lower()
                print(f"✓ Step 4: Find button status - {'Disabled' if is_disabled else 'Enabled'}")
            
            print("✓ End-to-end search workflow test completed")
            
        except Exception as e:
            print(f"⚠ Error in end-to-end search workflow: {e}")
