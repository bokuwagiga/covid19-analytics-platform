# api.py (updated)
import os
import traceback
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient

# Import functions from app.py
from utils import (
    fetch_covid_data, load_kaggle_mortality_data,
    preprocess_mortality_data, preprocess_covid_data,
    merge_datasets, calculate_counterfactual, fetch_covid_data_countries
)

# Load env vars
load_dotenv('config/.env')

COVID_MORTALITY_COMPARISON = os.getenv('COVID_MORTALITY_COMPARISON')

# Flask app
app = Flask(__name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["covid_db"]
comments_col = db["comments"]

# Preload Kaggle mortality dataset
df_mortality_raw = load_kaggle_mortality_data()
df_mortality = preprocess_mortality_data(df_mortality_raw)

# --- API Endpoints ---

@app.route("/covid_mortality_comparison_countries", methods=["GET"])
def get_covid_data_countries():
    """
    Return countries for merged COVID + mortality data.
    """
    try:
        countries = fetch_covid_data_countries()
        snowflake_countries = [country[0] for country in countries]
        common_countries = set(df_mortality['country_name']).intersection(set(snowflake_countries))
        common_countries_list = sorted(list(common_countries))
    except:
        common_countries_list = []
        traceback.print_exc()
    return jsonify(common_countries_list), 200

@app.route(f"/{COVID_MORTALITY_COMPARISON}", methods=["GET"])
def get_covid_data():
    """
    Return merged COVID + mortality data for a given country.
    Example: /covid?country=Lithuania
    """
    country = request.args.get("country")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    df_covid_raw = fetch_covid_data(country)
    df_covid = preprocess_covid_data(df_covid_raw)

    df_merged = merge_datasets(df_mortality, df_covid)
    df_final = calculate_counterfactual(df_merged)

    df_final["date"] = pd.to_datetime(
        df_final["year"].astype(str) + "-" + df_final["month"].astype(str) + "-01"
    )
    # Convert to JSON serializable
    data = df_final.to_dict(orient="records")
    return jsonify(data), 200


@app.route("/comments", methods=["GET"])
def get_comments():
    country = request.args.get("country")
    date = request.args.get("date")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    query = {"country": country}
    if date:
        query["date"] = date

    comments = list(comments_col.find(query, {"_id": 0}))
    return jsonify(comments), 200


@app.route("/comments", methods=["POST"])
def add_comment():
    data = request.get_json()
    required = ["country", "date", "metric", "comment", "user"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    doc = {
        "country": data["country"],
        "date": data["date"],
        "metric": data["metric"],
        "comment": data["comment"],
        "user": data["user"],
        "tags": data.get("tags", []),
        "created_at": datetime.utcnow()
    }
    comments_col.insert_one(doc)
    return jsonify({"message": "Comment added"}), 201


if __name__ == "__main__":
    app.run(port=5000, debug=True)
