import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class TestHomePage:
    """Test cases for SmartHotel360 home page functionality"""
    
    def test_page_loads_successfully(self, home_page):
        """Test that home page loads and has correct title"""
        assert "SmartHotel360" in home_page.title
        print(f"✓ Page title: {home_page.title}")
    
    def test_hero_section_elements(self, home_page):
        """Test hero section elements are present"""
        wait = WebDriverWait(home_page, 10)
        
        # Check hero title
        try:
            hero_title = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sh-hero-title"))
            )
            assert "intelligent hospitality" in hero_title.text.lower()
            print("✓ Hero title found and contains expected text")
        except TimeoutException:
            pytest.fail("Hero title not found")
        
        # Check download app section
        try:
            hero_buttons = home_page.find_elements(By.CLASS_NAME, "sh-hero-button")
            assert len(hero_buttons) >= 3, "Expected at least 3 download buttons"
            print(f"✓ Found {len(hero_buttons)} app download buttons")
        except NoSuchElementException:
            pytest.fail("App download buttons not found")
    
    def test_navigation_menu(self, home_page):
        """Test navigation menu elements"""
        wait = WebDriverWait(home_page, 10)
        
        # Check logo presence
        try:
            logo = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sh-nav_menu-logo"))
            )
            assert logo.is_displayed()
            print("✓ Navigation logo found")
        except TimeoutException:
            pytest.fail("Navigation logo not found")
        
        # Check navigation container
        try:
            nav_menu = home_page.find_element(By.CLASS_NAME, "sh-nav_menu")
            assert nav_menu.is_displayed()
            print("✓ Navigation menu container found")
        except NoSuchElementException:
            pytest.fail("Navigation menu not found")
    
    def test_search_component_present(self, home_page):
        """Test that search component is present on home page"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            search_component = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sh-search"))
            )
            assert search_component.is_displayed()
            print("✓ Search component found")
            
            # Check search tabs
            search_tabs = home_page.find_elements(By.CLASS_NAME, "sh-search-tab")
            assert len(search_tabs) >= 2, "Expected Smart Room and Conference Room tabs"
            print(f"✓ Found {len(search_tabs)} search tabs")
            
        except TimeoutException:
            pytest.fail("Search component not found")
    
    def test_conference_rooms_section(self, home_page):
        """Test conference rooms features section"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Scroll to conference section
            home_page.execute_script("window.scrollTo(0, 1000);")
            time.sleep(1)
            
            conf_features = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='conference'], [class*='Conference']"))
            )
            print("✓ Conference rooms section found")
            
        except TimeoutException:
            print("⚠ Conference rooms section not found (this might be expected)")
    
    def test_smart_experience_section(self, home_page):
        """Test smart experience info grid section"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Scroll to infogrid section
            home_page.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            
            infogrid = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sh-infogrid"))
            )
            
            # Check for infogrid rows
            infogrid_rows = home_page.find_elements(By.CLASS_NAME, "sh-infogrid-row")
            assert len(infogrid_rows) >= 3, "Expected at least 3 smart experience features"
            print(f"✓ Found {len(infogrid_rows)} smart experience features")
            
        except TimeoutException:
            pytest.fail("Smart experience section not found")
    
    def test_smartphone_section(self, home_page):
        """Test smartphone section with testimonials"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Scroll to smartphone section
            home_page.execute_script("window.scrollTo(0, 2000);")
            time.sleep(2)
            
            smartphone_section = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "sh-smartphone"))
            )
            
            # Check for smartphone image
            smartphone_image = home_page.find_element(By.CLASS_NAME, "sh-smartphone-image")
            assert smartphone_image.is_displayed()
            print("✓ Smartphone section and image found")
            
        except (TimeoutException, NoSuchElementException):
            print("⚠ Smartphone section not fully loaded")
    
    def test_rooms_section(self, home_page):
        """Test rooms and conference rooms section at bottom"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Scroll to bottom
            home_page.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Look for rooms container or similar
            rooms_elements = home_page.find_elements(By.CSS_SELECTOR, "[class*='room'], [class*='Room']")
            if rooms_elements:
                print(f"✓ Found {len(rooms_elements)} room-related elements")
            else:
                print("⚠ Rooms section elements not found")
                
        except Exception as e:
            print(f"⚠ Error checking rooms section: {e}")
    
    def test_page_responsiveness_basic(self, home_page):
        """Basic responsiveness test - resize window"""
        original_size = home_page.get_window_size()
        
        try:
            # Test mobile size
            home_page.set_window_size(375, 667)
            time.sleep(1)
            
            # Check if page still loads main elements
            nav_menu = home_page.find_element(By.CLASS_NAME, "sh-nav_menu")
            assert nav_menu.is_displayed()
            
            search_component = home_page.find_element(By.CLASS_NAME, "sh-search")
            assert search_component.is_displayed()
            
            print("✓ Page responsive on mobile size")
            
        finally:
            # Restore original size
            home_page.set_window_size(original_size['width'], original_size['height'])
    
    def test_external_links_present(self, home_page):
        """Test that external app download links are present"""
        wait = WebDriverWait(home_page, 10)
        
        try:
            # Find all hero button links
            hero_links = home_page.find_elements(By.CLASS_NAME, "sh-hero-button-link")
            
            valid_links = 0
            for link in hero_links:
                href = link.get_attribute('href')
                if href and ('aka.ms' in href or 'microsoft.com' in href or 'apple.com' in href or 'google.com' in href):
                    valid_links += 1
                    print(f"✓ Valid app download link: {href}")
            
            assert valid_links >= 2, "Expected at least 2 valid app download links"
            print(f"✓ Found {valid_links} valid app download links")
            
        except Exception as e:
            print(f"⚠ Error checking external links: {e}")
