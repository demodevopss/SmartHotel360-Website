import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@pytest.fixture(scope="session")
def driver_init(request):
    """Initialize WebDriver with Selenium Grid or local browser"""
    
    # Get test configuration from environment variables
    base_url = os.getenv('APP_BASE_URL', 'http://192.168.1.137:30080')  # NodePort URL
    selenium_hub = os.getenv('SELENIUM_HUB_URL', 'http://localhost:4444/wd/hub')
    browser = os.getenv('BROWSER', 'chrome').lower()
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    
    print(f"Starting {browser} browser for testing {base_url}")
    print(f"Using Selenium Hub: {selenium_hub}")
    
    if browser == 'chrome':
        chrome_options = ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Try Selenium Grid first, fallback to local
        try:
            driver = webdriver.Remote(
                command_executor=selenium_hub,
                options=chrome_options
            )
        except Exception as e:
            print(f"Selenium Grid not available: {e}")
            print("Falling back to local ChromeDriver")
            driver = webdriver.Chrome(options=chrome_options)
            
    elif browser == 'firefox':
        firefox_options = FirefoxOptions()
        if headless:
            firefox_options.add_argument("--headless")
        
        try:
            driver = webdriver.Remote(
                command_executor=selenium_hub,
                options=firefox_options
            )
        except Exception as e:
            print(f"Selenium Grid not available: {e}")
            print("Falling back to local GeckoDriver")
            driver = webdriver.Firefox(options=firefox_options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    driver.maximize_window()
    driver.implicitly_wait(10)
    
    # Store base URL in driver for tests to use
    driver.base_url = base_url
    
    yield driver
    
    # Teardown
    driver.quit()


@pytest.fixture
def driver(driver_init):
    """Provide clean driver instance for each test"""
    yield driver_init


@pytest.fixture
def home_page(driver):
    """Navigate to home page before test"""
    driver.get(driver.base_url)
    return driver
