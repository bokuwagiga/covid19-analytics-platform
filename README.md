# COVID-19 Mortality Analysis

A data analysis project that combines COVID-19 data from Snowflake with all-cause mortality data from Kaggle to analyze the pandemic's impact across different countries.

## Features

- Connects to Snowflake to retrieve COVID-19 mortality data
- Incorporates Kaggle's world mortality dataset for comprehensive analysis
- Calculates counterfactual scenarios (mortality without COVID)
- Visualizes trends with interactive plots
- Provides web dashboard for exploring data by country

## Project Structure

- `app.py` - Main application entry point
- `api.py` - API endpoints for data retrieval
- `utils.py` - Utility functions for data processing
- `components/` - Reusable UI components
- `pages/` - Dashboard page definitions
- `config/` - Configuration files (e.g., environment variables)
- `sql/` - SQL scripts for database setup
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `config/.env.example` to `config/.env` and configure your Snowflake credentials
6. Run the SQL setup file: `sql/setup.sql`
7. Go to Snowflake and search "COVID-19 Epidemiological Data" click "Get" on a COVID-19 provider dataset and enter database name (same as from .env) (e.g., DB_COVID)
8. Create mongoDB account, set up a database user and put MongoURI in `config/.env` as well

## Usage
Start the api services:

```
python api.py
```
Start the application:

```
python app.py
```


Access the dashboard at http://localhost:8050

## Dependencies

* snowflake-connector-python
* pandas
* dotenv
* kagglehub
* pymongo
* flask
* dash
* dash_bootstrap_components
* plotly
* pandas
* pymongo