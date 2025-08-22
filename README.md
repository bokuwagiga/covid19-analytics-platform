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

### Option 1: Local Setup (without Docker)
1. Clone the repository  
2. Create a virtual environment: `python -m venv .venv`  
3. Activate the environment:  
   - Windows: `.venv\Scripts\activate`  
   - Unix/MacOS: `source .venv/bin/activate`  
4. Install dependencies: `pip install -r requirements.txt`  
5. Copy `config/.env.example` to `config/.env` and configure your Snowflake credentials  
6. Run the SQL setup file: `sql/setup.sql`  
7. Go to Snowflake and search "COVID-19 Epidemiological Data" → click **Get** on a COVID-19 provider dataset and enter the database name (same as in `.env`, e.g., `DB_COVID`)  
8. Set up **MongoDB** (choose one of the options below):
   - **MongoDB via Docker Compose:**  
     - If you use the provided `docker-compose.yml`, MongoDB will be started as a service automatically  
     - Use `MONGO_URI=mongodb://mongodb:27017` in `.env`  
   
   - **Local MongoDB:**  
     - Install MongoDB locally or run with Docker:  
       ```bash
       docker run -d -p 27017:27017 --name mongodb mongo:6
       ```  
     - Use `MONGO_URI=mongodb://localhost:27017` in `.env`
   - **MongoDB Atlas (cloud, recommended):**  
     - Create a free cluster on [MongoDB Atlas](https://www.mongodb.com/atlas)  
     - Add a database user and whitelist your IP  
     - Copy the connection string (e.g., `mongodb+srv://<user>:<pass>@cluster0.mongodb.net/`)  
     - Add it to `.env` as `MONGO_URI`  
### Option 2: With Docker
1. Clone the repository  
2. Copy `config/.env.example` to `config/.env` and configure your Snowflake and MongoDB credentials  
3. Make sure Docker is installed and running  
4. Build and start the containers:  
   ```bash
   docker compose up --build
   ```

5. Access the dashboard at [http://localhost:8050](http://localhost:8050)

## Usage

Start the API service:

```bash
python src/api.py
```

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
