# shared/config/config.py
import os

API_BASE_EXTERNAL = os.getenv("API_BASE_EXTERNAL", "http://localhost:5000")

EXCESS_MORTALITY_PAGE = "excess-mortality"
VACCINATION_PAGE = "vaccinations"
INFECTION_CASES_PAGE = "infection-cases"
INFECTION_DEATHS_PAGE = "infection-deaths"

DASHBOARDS_LIST = [
    EXCESS_MORTALITY_PAGE,
    VACCINATION_PAGE,
    INFECTION_CASES_PAGE,
    INFECTION_DEATHS_PAGE,
]

MORTALITY_FORECAST_PAGE = "mortality-forecast"
CLUSTERING_PAGE = "clustering"
EDA_PAGE = "eda"
PATTERNS_PAGE = "patterns"

ANALYTICS_LIST = [EDA_PAGE, MORTALITY_FORECAST_PAGE, CLUSTERING_PAGE, PATTERNS_PAGE]

# Default to Docker service name if not overridden
API_BASE = os.getenv("API_BASE", "http://api:5000")
