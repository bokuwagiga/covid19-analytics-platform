# src/config/config.py
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

# Default to Docker service name if not overridden
API_BASE = os.getenv("API_BASE", "http://api:5000")
