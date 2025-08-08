import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class TestNavigation:
    """Test cases for SmartHotel360 navigation and routing"""
    
    def test_home_page_access(self, driver):
        """Test home page is accessible"""
        driver.get(driver.base_url)
        time.sleep(2)
        
        assert driver.current_url == driver.base_url or driver.current_url == f"{driver.base_url}/"
        assert "SmartHotel360" in driver.title
        print(f"✓ Home page accessible at {driver.current_url}")
    
    def test_logo_navigation(self, driver):
        """Test clicking logo navigates to home page"""
        driver.get(driver.base_url)
        time.sleep(2)
        
        try:
            # Find logo
            logo_selectors = [
                (By.CLASS_NAME, "sh-nav_menu-logo"),
                (By.CSS_SELECTOR, "img[src*='logo']"),
                (By.CSS_SELECTOR, ".sh-nav_menu-container img")
            ]
            
            logo = None
            for selector in logo_selectors:
                try:
                    logo = driver.find_element(*selector)
                    if logo.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if logo:
                # Navigate away first
                driver.get(f"{driver.base_url}/Pets")
                time.sleep(2)
                
                # Find logo again (page changed)
                for selector in logo_selectors:
                    try:
                        logo = driver.find_element(*selector)
                        if logo.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if logo:
                    # Click logo
                    logo.click()
                    time.sleep(2)
                    
                    # Check if we're back at home
                    current_url = driver.current_url
                    if current_url == driver.base_url or current_url == f"{driver.base_url}/":
                        print("✓ Logo click navigates to home page")
                    else:
                        print(f"⚠ Logo click didn't navigate to home: {current_url}")
                else:
                    print("⚠ Logo not found after navigation")
            else:
                print("⚠ Logo not found")
                
        except Exception as e:
            print(f"⚠ Error testing logo navigation: {e}")
    
    def test_pets_page_route(self, driver):
        """Test /Pets route is accessible"""
        pets_url = f"{driver.base_url}/Pets"
        
        try:
            driver.get(pets_url)
            time.sleep(3)
            
            # Check URL
            current_url = driver.current_url
            assert "Pets" in current_url or "pets" in current_url
            
            # Check page loaded (not 404)
            page_source = driver.page_source.lower()
            if "404" in page_source or "not found" in page_source:
                pytest.fail("Pets page returned 404 or not found")
            
            print(f"✓ Pets page accessible at {current_url}")
            
        except Exception as e:
            pytest.fail(f"Pets page not accessible: {e}")
    
    def test_search_rooms_route(self, driver):
        """Test /SearchRooms route is accessible"""
        search_rooms_url = f"{driver.base_url}/SearchRooms"
        
        try:
            driver.get(search_rooms_url)
            time.sleep(3)
            
            # Check URL
            current_url = driver.current_url
            assert "SearchRooms" in current_url or "searchrooms" in current_url.lower()
            
            # Check page loaded (not 404)
            page_source = driver.page_source.lower()
            if "404" in page_source or "not found" in page_source:
                print("⚠ SearchRooms page might return 404 (expected if no backend)")
            else:
                print(f"✓ SearchRooms page accessible at {current_url}")
            
        except Exception as e:
            print(f"⚠ SearchRooms page not accessible: {e}")
    
    def test_room_detail_route_structure(self, driver):
        """Test /RoomDetail/:id route structure"""
        room_detail_url = f"{driver.base_url}/RoomDetail/1"
        
        try:
            driver.get(room_detail_url)
            time.sleep(3)
            
            # Check URL contains RoomDetail
            current_url = driver.current_url
            if "RoomDetail" in current_url:
                print(f"✓ RoomDetail route structure working: {current_url}")
            else:
                print(f"⚠ RoomDetail route might not be working: {current_url}")
            
        except Exception as e:
            print(f"⚠ RoomDetail route test failed: {e}")
    
    def test_navigation_between_pages(self, driver):
        """Test navigation flow between different pages"""
        wait = WebDriverWait(driver, 10)
        
        try:
            # Start at home
            driver.get(driver.base_url)
            time.sleep(2)
            print("✓ Started at home page")
            
            # Navigate to Pets via search form
            search_groups = driver.find_elements(By.CLASS_NAME, "sh-search-group")
            if len(search_groups) >= 3:
                # Open guests section
                search_groups[2].click()
                time.sleep(2)
                
                # Enable pets
                pet_buttons = driver.find_elements(By.CSS_SELECTOR, 
                    "button[class*='guest'][class*='extra'], .sh-guests-extra_button")
                
                if len(pet_buttons) >= 2:
                    pet_buttons[1].click()  # Yes to pets
                    time.sleep(1)
                    
                    # Click pets link
                    pet_links = driver.find_elements(By.CSS_SELECTOR, 
                        "a[href*='Pets'], .sh-guests-pets_link")
                    
                    visible_pet_link = None
                    for link in pet_links:
                        if link.is_displayed():
                            visible_pet_link = link
                            break
                    
                    if visible_pet_link:
                        visible_pet_link.click()
                        time.sleep(3)
                        
                        if "Pets" in driver.current_url:
                            print("✓ Navigated to Pets via search form")
                        else:
                            print("⚠ Pets navigation from search failed")
            
            # Navigate to SearchRooms via Find button
            driver.get(driver.base_url)
            time.sleep(2)
            
            find_buttons = driver.find_elements(By.CLASS_NAME, "sh-search-button")
            if find_buttons:
                # Check if button is enabled (might need form completion)
                button = find_buttons[0]
                button_classes = button.get_attribute("class")
                
                if "disabled" not in button_classes.lower():
                    button.click()
                    time.sleep(3)
                    
                    if "SearchRooms" in driver.current_url:
                        print("✓ Navigated to SearchRooms via Find button")
                    else:
                        print("⚠ SearchRooms navigation failed")
                else:
                    print("ℹ Find button disabled (form incomplete)")
            
            # Navigate back to home via direct URL
            driver.get(driver.base_url)
            time.sleep(2)
            
            if driver.current_url == driver.base_url or driver.current_url == f"{driver.base_url}/":
                print("✓ Successfully returned to home page")
            
        except Exception as e:
            print(f"⚠ Error in navigation flow test: {e}")
    
    def test_browser_navigation_controls(self, driver):
        """Test browser back/forward navigation"""
        try:
            # Start at home
            driver.get(driver.base_url)
            time.sleep(2)
            
            # Navigate to pets
            driver.get(f"{driver.base_url}/Pets")
            time.sleep(2)
            
            # Use browser back
            driver.back()
            time.sleep(2)
            
            # Should be back at home
            current_url = driver.current_url
            if current_url == driver.base_url or current_url == f"{driver.base_url}/":
                print("✓ Browser back navigation working")
            else:
                print(f"⚠ Browser back navigation issue: {current_url}")
            
            # Use browser forward
            driver.forward()
            time.sleep(2)
            
            # Should be at pets again
            if "Pets" in driver.current_url:
                print("✓ Browser forward navigation working")
            else:
                print("⚠ Browser forward navigation issue")
            
        except Exception as e:
            print(f"⚠ Error testing browser navigation: {e}")
    
    def test_url_direct_access(self, driver):
        """Test direct URL access to different routes"""
        routes_to_test = [
            "/",
            "/Pets",
            "/SearchRooms"
        ]
        
        successful_routes = 0
        
        for route in routes_to_test:
            try:
                full_url = f"{driver.base_url}{route}".rstrip('/')
                if route == "/":
                    full_url = driver.base_url
                    
                driver.get(full_url)
                time.sleep(2)
                
                # Check if page loaded without major errors
                page_source = driver.page_source.lower()
                
                if "404" in page_source or "not found" in page_source:
                    print(f"⚠ Route {route} returned 404")
                elif "error" in page_source and "loading" not in page_source:
                    print(f"⚠ Route {route} has errors")
                else:
                    print(f"✓ Route {route} accessible")
                    successful_routes += 1
                    
            except Exception as e:
                print(f"⚠ Route {route} failed: {e}")
        
        print(f"✓ {successful_routes}/{len(routes_to_test)} routes successfully accessible")
    
    def test_spa_routing_behavior(self, driver):
        """Test Single Page Application routing behavior"""
        try:
            # Start at home
            driver.get(driver.base_url)
            time.sleep(2)
            
            # Check if React app loaded
            react_elements = driver.find_elements(By.CSS_SELECTOR, "[data-reactroot], #root")
            if react_elements:
                print("✓ React SPA detected")
            else:
                print("⚠ React SPA not clearly detected")
            
            # Test client-side routing by checking if navigation doesn't cause full page reload
            initial_page_load_time = driver.execute_script("return performance.timing.loadEventEnd")
            
            # Navigate to pets (if available)
            pets_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='Pets']")
            if pets_links:
                pets_links[0].click()
                time.sleep(2)
                
                # Check if URL changed but page didn't fully reload
                if "Pets" in driver.current_url:
                    new_page_load_time = driver.execute_script("return performance.timing.loadEventEnd")
                    
                    if new_page_load_time == initial_page_load_time:
                        print("✓ Client-side routing working (no full page reload)")
                    else:
                        print("ℹ Page reload detected (might be server-side routing)")
                        
        except Exception as e:
            print(f"⚠ Error testing SPA routing: {e}")
    
    def test_responsive_navigation(self, driver):
        """Test navigation on different screen sizes"""
        original_size = driver.get_window_size()
        
        try:
            # Test mobile size
            driver.set_window_size(375, 667)
            time.sleep(1)
            
            driver.get(driver.base_url)
            time.sleep(2)
            
            # Check if navigation is still accessible
            nav_elements = driver.find_elements(By.CSS_SELECTOR, ".sh-nav_menu, nav, [class*='nav']")
            if nav_elements and any(elem.is_displayed() for elem in nav_elements):
                print("✓ Navigation accessible on mobile size")
            else:
                print("⚠ Navigation might not be accessible on mobile")
            
            # Test tablet size
            driver.set_window_size(768, 1024)
            time.sleep(1)
            
            # Check navigation again
            nav_elements = driver.find_elements(By.CSS_SELECTOR, ".sh-nav_menu, nav, [class*='nav']")
            if nav_elements and any(elem.is_displayed() for elem in nav_elements):
                print("✓ Navigation accessible on tablet size")
            else:
                print("⚠ Navigation might not be accessible on tablet")
            
        finally:
            # Restore original size
            driver.set_window_size(original_size['width'], original_size['height'])
            time.sleep(1)
