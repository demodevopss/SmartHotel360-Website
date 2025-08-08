# SmartHotel360 Selenium Test Suite

Automated end-to-end tests for the SmartHotel360 web application using Selenium WebDriver and pytest.

## Features

- **Comprehensive Test Coverage**: Tests for home page, search functionality, pets feature, and navigation
- **Multiple Browser Support**: Chrome and Firefox
- **Selenium Grid Integration**: Run tests on distributed Selenium Grid
- **Flexible Execution**: Local drivers or remote Grid execution
- **CI/CD Ready**: Designed for integration with Jenkins and other CI systems
- **Detailed Reporting**: HTML and JUnit XML reports

## Test Suites

### 🏠 Home Page Tests (`test_home.py`)
- Page loading and title verification
- Hero section elements and app download links
- Navigation menu presence
- Search component availability
- Smart experience features
- Responsive design basic checks

### 🔍 Search Functionality Tests (`test_search.py`)
- Search tabs (Smart Room vs Conference Room)
- Location search with suggestions
- Date picker functionality
- Guest and room selection
- Pet selection integration
- Find a Room button behavior
- End-to-end search workflow

### 🐕 Pets Feature Tests (`test_pets.py`)
- Pets page navigation
- File upload form presence
- Pet name input functionality
- Approval status checking
- API integration indicators
- Basic accessibility checks

### 🧭 Navigation Tests (`test_navigation.py`)
- Home page accessibility
- Logo navigation functionality
- Route accessibility (/Pets, /SearchRooms, /RoomDetail)
- Browser navigation controls (back/forward)
- SPA routing behavior
- Responsive navigation

## Quick Start

### Prerequisites

- Python 3.7+
- Docker and Docker Compose (for Selenium Grid)
- Modern web browser (Chrome/Firefox)

### Installation

```bash
# Clone and navigate to tests directory
cd selenium-tests

# Install dependencies
make install

# Or manually with pip
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Tests

#### Basic Test Execution

```bash
# Run all tests (default: local Chrome, headless)
make test

# Run with specific application URL
make test APP_URL=http://192.168.1.137:30080

# Run specific test file
make test-home
make test-search
make test-pets
make test-navigation

# Run in headed mode for debugging
make test-local HEADLESS=false
```

#### Using Selenium Grid

```bash
# Start Selenium Grid
make start-grid

# Run tests with Grid
make test-grid

# Stop Grid when done
make stop-grid
```

#### Advanced Test Execution

```bash
# Run with Python script directly
python run_tests.py --app-url http://localhost:30080 --browser chrome --headless

# Run specific test pattern
python run_tests.py --test-pattern "test_search or test_home"

# Run with custom Selenium Hub
python run_tests.py --selenium-hub http://selenium-hub:4444/wd/hub

# Run in parallel (requires pytest-xdist)
python run_tests.py --parallel 2

# Run with additional pytest options
python run_tests.py --pytest-args "-v --tb=short"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_BASE_URL` | `http://localhost:30080` | Base URL of the application |
| `SELENIUM_HUB_URL` | `http://localhost:4444/wd/hub` | Selenium Grid hub URL |
| `BROWSER` | `chrome` | Browser choice (`chrome` or `firefox`) |
| `HEADLESS` | `true` | Run browser in headless mode |

### Pytest Configuration

Tests are configured via `pytest.ini`:

```ini
[tool:pytest]
addopts = -v --html=reports/report.html --self-contained-html
testpaths = .
markers =
    smoke: Quick smoke tests
    regression: Full regression tests
    ui: User interface tests
```

## CI/CD Integration

### Jenkins Pipeline Integration

The test suite is designed to integrate with Jenkins pipelines. Add this stage to your Jenkinsfile:

```groovy
stage('Selenium Tests') {
    steps {
        script {
            // Start Selenium Grid
            sh 'cd selenium-tests && make start-grid'
            
            try {
                // Run tests
                sh '''
                cd selenium-tests
                make ci-test APP_URL=http://smarthotel-website-service:80 SELENIUM_HUB=http://selenium-hub:4444/wd/hub
                '''
            } finally {
                // Stop Grid and collect reports
                sh 'cd selenium-tests && make stop-grid'
                
                // Archive test reports
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'selenium-tests/reports',
                    reportFiles: 'report.html',
                    reportName: 'Selenium Test Report'
                ])
                
                // Publish JUnit results
                junit 'selenium-tests/reports/junit.xml'
            }
        }
    }
}
```

### Docker Integration

Run tests in Docker container:

```bash
# Build test container
docker build -t smarthotel-tests .

# Run tests
docker run --rm \
  -e APP_BASE_URL=http://host.docker.internal:30080 \
  -e SELENIUM_HUB_URL=http://selenium-hub:4444/wd/hub \
  -v $(pwd)/reports:/app/reports \
  smarthotel-tests
```

## Test Reports

Tests generate detailed HTML and XML reports:

- **HTML Report**: `reports/report.html` - Detailed test results with screenshots
- **JUnit XML**: `reports/junit.xml` - CI/CD compatible test results

View reports:

```bash
make reports  # Opens HTML report in browser
```

## Development

### Adding New Tests

1. Create test file following the naming convention `test_*.py`
2. Use the provided fixtures (`driver`, `home_page`)
3. Follow the existing test patterns and assertions
4. Add appropriate markers for test categorization

Example test structure:

```python
import pytest
from selenium.webdriver.common.by import By

class TestNewFeature:
    def test_feature_functionality(self, home_page):
        """Test description"""
        # Test implementation
        element = home_page.find_element(By.CLASS_NAME, "feature-class")
        assert element.is_displayed()
        print("✓ Feature test passed")
```

### Running Tests During Development

```bash
# Quick development test
make dev-quick

# Test specific browser
make dev-chrome
make dev-firefox

# Watch mode (requires pytest-watch)
ptw . --runner "python run_tests.py --test-pattern test_home"
```

## Troubleshooting

### Common Issues

1. **Application not available**
   ```bash
   # Check if app is running
   curl http://localhost:30080
   
   # Skip app availability check
   python run_tests.py --skip-app-check
   ```

2. **Selenium Grid not responding**
   ```bash
   # Check Grid status
   curl http://localhost:4444/status
   
   # Restart Grid
   make stop-grid && make start-grid
   
   # Use local drivers instead
   python run_tests.py --selenium-hub local
   ```

3. **Browser driver issues**
   ```bash
   # Install/update ChromeDriver
   pip install --upgrade webdriver-manager
   
   # Use Firefox instead
   python run_tests.py --browser firefox
   ```

4. **Tests failing due to timing**
   ```bash
   # Run with longer waits
   python run_tests.py --pytest-args "--timeout=30"
   
   # Run in headed mode to debug
   python run_tests.py --headless false
   ```

### Debug Mode

Run tests in debug mode:

```bash
# Headed browser for visual debugging
python run_tests.py --headless false --browser chrome

# Verbose output
python run_tests.py --pytest-args "-v -s"

# Stop on first failure
python run_tests.py --pytest-args "-x"
```

## Architecture

```
selenium-tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_home.py            # Home page tests
├── test_search.py          # Search functionality tests
├── test_pets.py            # Pets feature tests
├── test_navigation.py      # Navigation and routing tests
├── run_tests.py            # Test runner script
├── pytest.ini             # Pytest configuration
├── requirements.txt        # Python dependencies
├── Makefile               # Build and test automation
├── docker-compose.selenium.yml  # Selenium Grid setup
└── reports/               # Generated test reports
```

## Contributing

1. Follow existing code patterns and naming conventions
2. Add appropriate docstrings and comments
3. Include both positive and negative test cases
4. Update documentation for new features
5. Ensure tests are stable and not flaky

## License

This test suite is part of the SmartHotel360 project and follows the same license terms.
