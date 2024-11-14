# Makefile for Urban-Heat-Island project

# Define Python environment
PYTHON_ENV = uv

# Default city for heat map generation (Austin, Texas)
DEFAULT_CITY = "Austin"

# Targets

## Run main.py with a city name (interactive)
run_main_with_city:
	$(PYTHON_ENV) run src/main.py -c

## Run main.py with the default city (Austin)
run_main_default:
	$(PYTHON_ENV) run src/main.py

## Run Streamlit dashboard
run_dashboard:
	$(PYTHON_ENV) run streamlit run src/app.py

## Print help message with available commands
help:
	@echo "Available commands:"
	@echo "  make run_main_with_city   - Run main.py and enter a city name to generate a heat map."
	@echo "  make run_main_default     - Run main.py with the default city (Austin, Texas)."
	@echo "  make run_dashboard        - Run the Streamlit dashboard."
