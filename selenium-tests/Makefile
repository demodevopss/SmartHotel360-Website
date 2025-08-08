# SmartHotel360 Selenium Tests Makefile

# Default settings
APP_URL ?= http://localhost:30080
SELENIUM_HUB ?= http://localhost:4444/wd/hub
BROWSER ?= chrome
HEADLESS ?= true

# Virtual environment
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

.PHONY: help install install-dev setup-venv clean test test-local test-smoke test-headless test-grid start-grid stop-grid reports

help:
	@echo "SmartHotel360 Selenium Test Suite"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  install-dev    - Install dev dependencies"
	@echo "  setup-venv     - Set up virtual environment"
	@echo "  clean          - Clean up generated files"
	@echo ""
	@echo "Test targets:"
	@echo "  test           - Run all tests"
	@echo "  test-local     - Run tests with local browser"
	@echo "  test-smoke     - Run smoke tests only"
	@echo "  test-headless  - Run tests in headless mode"
	@echo "  test-grid      - Run tests with Selenium Grid"
	@echo ""
	@echo "Selenium Grid:"
	@echo "  start-grid     - Start Selenium Grid with Docker Compose"
	@echo "  stop-grid      - Stop Selenium Grid"
	@echo ""
	@echo "Utilities:"
	@echo "  reports        - Open test reports in browser"
	@echo ""
	@echo "Environment variables:"
	@echo "  APP_URL        - Application URL (default: $(APP_URL))"
	@echo "  SELENIUM_HUB   - Selenium Hub URL (default: $(SELENIUM_HUB))"
	@echo "  BROWSER        - Browser choice (default: $(BROWSER))"
	@echo "  HEADLESS       - Headless mode (default: $(HEADLESS))"

setup-venv:
	@echo "Setting up virtual environment..."
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip setuptools wheel

install: setup-venv
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

install-dev: install
	@echo "Installing development dependencies..."
	$(PIP) install pytest-xdist pytest-cov black flake8

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# Test targets
test: install
	@echo "Running all tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --selenium-hub $(SELENIUM_HUB) --browser $(BROWSER)

test-local: install
	@echo "Running tests with local browser..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --selenium-hub local --browser $(BROWSER)

test-smoke: install
	@echo "Running smoke tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --markers smoke --browser $(BROWSER)

test-headless: install
	@echo "Running tests in headless mode..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --headless --browser $(BROWSER)

test-grid: install
	@echo "Running tests with Selenium Grid..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --selenium-hub $(SELENIUM_HUB) --browser $(BROWSER)

test-home: install
	@echo "Running home page tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --test-file test_home.py --browser $(BROWSER)

test-search: install
	@echo "Running search tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --test-file test_search.py --browser $(BROWSER)

test-pets: install
	@echo "Running pets tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --test-file test_pets.py --browser $(BROWSER)

test-navigation: install
	@echo "Running navigation tests..."
	$(PYTHON) run_tests.py --app-url $(APP_URL) --test-file test_navigation.py --browser $(BROWSER)

# Selenium Grid management
start-grid:
	@echo "Starting Selenium Grid..."
	docker-compose -f docker-compose.selenium.yml up -d
	@echo "Waiting for Grid to be ready..."
	sleep 10
	@echo "Grid should be available at http://localhost:4444"

stop-grid:
	@echo "Stopping Selenium Grid..."
	docker-compose -f docker-compose.selenium.yml down

# Utilities
reports:
	@echo "Opening test reports..."
	@if [ -f "reports/report.html" ]; then \
		open reports/report.html 2>/dev/null || xdg-open reports/report.html 2>/dev/null || echo "Please open reports/report.html manually"; \
	else \
		echo "No test reports found. Run tests first."; \
	fi

# CI/CD targets
ci-test: install
	@echo "Running tests for CI/CD..."
	mkdir -p reports
	$(PYTHON) run_tests.py \
		--app-url $(APP_URL) \
		--selenium-hub $(SELENIUM_HUB) \
		--browser $(BROWSER) \
		--headless \
		--pytest-args "--html=reports/report.html --self-contained-html --junitxml=reports/junit.xml"

# Quick development targets
dev-chrome: install
	$(PYTHON) run_tests.py --app-url $(APP_URL) --browser chrome --selenium-hub local

dev-firefox: install
	$(PYTHON) run_tests.py --app-url $(APP_URL) --browser firefox --selenium-hub local

dev-quick: install
	$(PYTHON) run_tests.py --app-url $(APP_URL) --test-pattern "test_home_page or test_pets_page" --selenium-hub local
