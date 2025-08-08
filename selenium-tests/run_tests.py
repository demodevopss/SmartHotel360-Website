#!/usr/bin/env python3
"""
SmartHotel360 Selenium Test Runner
Runs automated tests against the SmartHotel360 web application
"""

import os
import sys
import subprocess
import argparse
import time
import requests
from typing import Optional


def check_app_availability(base_url: str, timeout: int = 60) -> bool:
    """Check if the application is available at the given URL"""
    print(f"Checking application availability at {base_url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(base_url, timeout=10)
            if response.status_code == 200:
                print(f"✓ Application is available at {base_url}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for application... ({int(time.time() - start_time)}s)")
        time.sleep(5)
    
    print(f"✗ Application not available at {base_url} after {timeout}s")
    return False


def check_selenium_grid(selenium_hub_url: str) -> bool:
    """Check if Selenium Grid is available"""
    try:
        grid_status_url = f"{selenium_hub_url}/status"
        response = requests.get(grid_status_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ready = data.get('value', {}).get('ready', False)
            if ready:
                print(f"✓ Selenium Grid is ready at {selenium_hub_url}")
                return True
            else:
                print(f"⚠ Selenium Grid not ready at {selenium_hub_url}")
                return False
    except Exception as e:
        print(f"⚠ Selenium Grid not available at {selenium_hub_url}: {e}")
        return False


def setup_environment(args):
    """Setup environment variables for tests"""
    env_vars = {
        'APP_BASE_URL': args.app_url,
        'SELENIUM_HUB_URL': args.selenium_hub,
        'BROWSER': args.browser,
        'HEADLESS': str(args.headless).lower()
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")


def run_tests(args) -> int:
    """Run the test suite"""
    
    # Setup environment
    setup_environment(args)
    
    # Check application availability
    if not args.skip_app_check:
        if not check_app_availability(args.app_url, args.app_timeout):
            print("✗ Application is not available. Exiting.")
            return 1
    
    # Check Selenium Grid (if not using local)
    if args.selenium_hub != 'local' and not args.skip_grid_check:
        if not check_selenium_grid(args.selenium_hub):
            print("⚠ Selenium Grid not available, will try to fall back to local drivers")
    
    # Prepare pytest command
    pytest_cmd = ['python', '-m', 'pytest']
    
    # Add test selection
    if args.test_file:
        pytest_cmd.append(args.test_file)
    elif args.test_pattern:
        pytest_cmd.extend(['-k', args.test_pattern])
    
    # Add markers
    if args.markers:
        pytest_cmd.extend(['-m', args.markers])
    
    # Add parallel execution
    if args.parallel and args.parallel > 1:
        pytest_cmd.extend(['-n', str(args.parallel)])
    
    # Add custom pytest options
    if args.pytest_args:
        pytest_cmd.extend(args.pytest_args.split())
    
    # Ensure reports directory exists
    os.makedirs('reports', exist_ok=True)
    
    print(f"Running command: {' '.join(pytest_cmd)}")
    print("=" * 50)
    
    # Run tests
    try:
        result = subprocess.run(pytest_cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
        return result.returncode
    except KeyboardInterrupt:
        print("\n✗ Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Run SmartHotel360 Selenium tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with default settings
  python run_tests.py
  
  # Run tests against specific URL with Chrome
  python run_tests.py --app-url http://192.168.1.137:30080 --browser chrome
  
  # Run only home page tests
  python run_tests.py --test-file test_home.py
  
  # Run tests in headless mode with custom Selenium Grid
  python run_tests.py --headless --selenium-hub http://selenium-hub:4444/wd/hub
  
  # Run specific test pattern
  python run_tests.py --test-pattern "test_search or test_navigation"
  
  # Run tests in parallel
  python run_tests.py --parallel 2
        """
    )
    
    # Application settings
    parser.add_argument('--app-url', 
                       default=os.getenv('APP_BASE_URL', 'http://localhost:30080'),
                       help='Base URL of the application to test')
    
    parser.add_argument('--app-timeout', type=int, default=60,
                       help='Timeout in seconds to wait for app availability')
    
    parser.add_argument('--skip-app-check', action='store_true',
                       help='Skip checking if application is available')
    
    # Selenium settings
    parser.add_argument('--selenium-hub', 
                       default=os.getenv('SELENIUM_HUB_URL', 'http://localhost:4444/wd/hub'),
                       help='Selenium Grid hub URL (use "local" for local drivers)')
    
    parser.add_argument('--skip-grid-check', action='store_true',
                       help='Skip checking if Selenium Grid is available')
    
    parser.add_argument('--browser', 
                       choices=['chrome', 'firefox'], 
                       default=os.getenv('BROWSER', 'chrome'),
                       help='Browser to use for tests')
    
    parser.add_argument('--headless', action='store_true',
                       default=os.getenv('HEADLESS', 'true').lower() == 'true',
                       help='Run browser in headless mode')
    
    # Test selection
    parser.add_argument('--test-file', 
                       help='Run specific test file (e.g., test_home.py)')
    
    parser.add_argument('--test-pattern', 
                       help='Run tests matching pattern (e.g., "test_search or test_home")')
    
    parser.add_argument('--markers', 
                       help='Run tests with specific markers (e.g., "smoke")')
    
    # Execution settings
    parser.add_argument('--parallel', type=int,
                       help='Run tests in parallel (requires pytest-xdist)')
    
    parser.add_argument('--pytest-args', 
                       help='Additional pytest arguments (as string)')
    
    args = parser.parse_args()
    
    print("SmartHotel360 Selenium Test Runner")
    print("=" * 40)
    print(f"Application URL: {args.app_url}")
    print(f"Selenium Hub: {args.selenium_hub}")
    print(f"Browser: {args.browser} ({'headless' if args.headless else 'headed'})")
    print("=" * 40)
    
    exit_code = run_tests(args)
    
    if exit_code == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
