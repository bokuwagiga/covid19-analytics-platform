# COVID-19 Mortality Analysis

An interactive analytics platform that integrates COVID-19 epidemiological data from Snowflake with all-cause mortality data from Kaggle to evaluate the pandemic’s impact across countries through dashboards, visualizations, and counterfactual analysis.
## Features

- Connects to Snowflake to retrieve COVID-19 mortality data 
- Incorporates Kaggle's world mortality dataset for comprehensive analysis 
- Calculates counterfactual scenarios (mortality without COVID)
- Visualizes trends with interactive plots 
- Provides web dashboard for exploring data by country 
- Allows users to leave comments on dashboards, including text and images for discussion

## Project Structure

- `src/app.py` - Main application entry point
- `src/api.py` - API endpoints for data retrieval
- `src/utils.py` - Utility functions for data processing
- `src/components/` - Reusable UI components
- `src/pages/` - Dashboard page definitions
- `src/config/` - Configuration files (e.g., environment variables)
- `src/sql/` - SQL scripts for database setup
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
8. Create MongoDB account, set up a database user and put MongoURI in `config/.env` as well

## Usage

Start the API service:

```bash
python src/api.py
````

Start the dashboard application:

```bash
python src/app.py
```

Access the dashboard at [http://localhost:8050](http://localhost:8050)

## Docker

You can also run the whole project with Docker Compose.

Build and start the services:

```bash
docker-compose up --build
```

Stop the containers:

```bash
docker-compose down
```

This will start both:

* The API service on **[http://localhost:5000](http://localhost:5000)**
* The Dashboard service on **[http://localhost:8050](http://localhost:8050)**

## Dependencies

* snowflake-connector-python
* pandas
* dotenv
* kagglehub
* pymongo
* flask
* dash
* dash\_bootstrap\_components
* plotly
* matplotlib
