# api.py
import os
import traceback
from datetime import datetime
import io

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
import gridfs

# functions from utils
from utils import (
    load_kaggle_mortality_data,
    preprocess_mortality_data,
    fetch_data_from_snowflake
)
from config.config import EXCESS_MORTALITY_PAGE, VACCINATION_PAGE, INFECTION_DEATHS_PAGE, INFECTION_CASES_PAGE

# load environment variables
load_dotenv('config/.env')

# flask app
app = Flask(__name__)

# mongodb setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["covid_db"]
comments_col = db["comments"]

# file storage
fs = gridfs.GridFS(db)

# preload mortality data from kaggle
df_mortality_raw = load_kaggle_mortality_data()
df_mortality = preprocess_mortality_data(df_mortality_raw)


# --- api endpoints ---

@app.route("/countries", methods=["GET"])
def get_countries():
    """
    return list of distinct countries from a given table
    """
    table_name = request.args.get("table", "ECDC_GLOBAL")
    try:
        # Ensure table_name is validated to prevent SQL injection
        allowed_tables = ["ECDC_GLOBAL", "ECDC_GLOBAL_WEEKLY", "OWID_VACCINATIONS"]
        if table_name not in allowed_tables:
            return jsonify({"error": f"Invalid table name: {table_name}"}), 400

        query = f"SELECT DISTINCT COUNTRY_REGION FROM {table_name}"
        countries = fetch_data_from_snowflake(query, return_df=False)
        snowflake_countries = [country[0] for country in countries]

        # find common countries with mortality dataset
        common_countries = set(df_mortality['country_name']).intersection(set(snowflake_countries))
        common_countries_list = sorted(list(common_countries))
    except Exception:
        common_countries_list = []
        traceback.print_exc()

    return jsonify(common_countries_list), 200



@app.route(f"/{EXCESS_MORTALITY_PAGE}", methods=["GET"])
def get_covid_data():
    """
    return merged covid + mortality data for a given country
    """
    country = request.args.get("country")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    query = """
        SELECT COUNTRY_REGION, DEATHS, DATE
        FROM ECDC_GLOBAL
        WHERE UPPER(COUNTRY_REGION) = %s
    """
    df_covid_raw = fetch_data_from_snowflake(query, return_df=True, params=(country.upper(),))

    # Convert daily covid deaths to monthly totals
    df_temp = df_covid_raw[['COUNTRY_REGION', 'DEATHS', 'DATE']].copy()
    df_temp["year"] = pd.to_datetime(df_temp['DATE']).dt.year
    df_temp["month"] = pd.to_datetime(df_temp['DATE']).dt.month

    # group by month and sum deaths
    df_covid_monthly = (
        df_temp.groupby(['COUNTRY_REGION', 'year', 'month'])['DEATHS']
        .sum()
        .reset_index()
        .rename(columns={
            'COUNTRY_REGION': 'country_name',
            'DEATHS': 'deaths_covid'
        })
    )
    # rename columns for consistency
    df_merged = pd.merge(
        df_mortality, df_covid_monthly,
        on=['country_name', 'year', 'month'],
        how='inner'
    )
    # fill NaN values in deaths_covid with 0
    df_merged['deaths_covid'] = df_merged['deaths_covid'].fillna(0)

    # calculate deaths without covid
    df_merged['deaths_without_covid'] = df_merged['deaths_allcause'] - df_merged['deaths_covid']

    # create date column
    df_merged["date"] = pd.to_datetime(
        df_merged["year"].astype(str) + "-" + df_merged["month"].astype(str) + "-01"
    )

    return jsonify(df_merged.to_dict(orient="records")), 200


@app.route("/comments", methods=["POST"])
def add_comment():
    """
    add new comment with optional image
    """
    # check if image file is uploaded
    if "image" in request.files:
        image = request.files["image"]
        file_id = fs.put(image, filename=image.filename, content_type=image.content_type)
    else:
        file_id = None

    data = request.form.to_dict() if "image" in request.files else request.get_json()

    # required fields
    required = ["comment", "user"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    # default country
    if not data.get("country"):
        data["country"] = "General"

    doc = {
        "country": data["country"],
        "comment": data["comment"],
        "user": data["user"],
        "page": data.get("page", "default"),
        "created_at": datetime.utcnow()
    }

    if file_id:
        doc["image_id"] = str(file_id)

    comments_col.insert_one(doc)
    return jsonify({"message": "Comment added"}), 201


@app.route("/comments/image/<file_id>", methods=["GET"])
def get_comment_image(file_id):
    """
    return image stored in gridfs by file_id
    """
    try:
        gridout = fs.get(ObjectId(file_id))
        mimetype = gridout.metadata.get("contentType") if gridout.metadata else None
        return send_file(
            io.BytesIO(gridout.read()),
            mimetype=mimetype or "application/octet-stream",
            download_name=gridout.filename
        )
    except Exception:
        return jsonify({"error": "Image not found"}), 404


@app.route("/comments", methods=["GET"])
def get_comments():
    """
    return list of comments (filtered by country or page if provided)
    """
    query = {}
    if "country" in request.args:
        query["country"] = request.args["country"]
    if "page" in request.args:
        query["page"] = request.args["page"]

    comments = list(comments_col.find(query, {"_id": 0}))
    for c in comments:
        if "image_id" in c:
            c["image_url"] = f"/comments/image/{c['image_id']}"

    return jsonify(comments), 200


@app.route(f"/{VACCINATION_PAGE}", methods=["GET"])
def get_vaccination_data():
    """
    return vaccination data for a given country or world
    """
    country = request.args.get("country")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    try:
        if country.upper() == "WORLD":
            # world-level aggregation
            # attach world population (single value) to each aggregated row
            query = """
            WITH pop AS (
                SELECT SUM(POPULATION) AS WORLD_POP
                FROM (
                    SELECT DISTINCT COUNTRY_REGION, POPULATION
                    FROM ECDC_GLOBAL
                )
            )
            SELECT v.DATE,
                   SUM(v.PEOPLE_VACCINATED) AS PEOPLE_VACCINATED,
                   SUM(v.PEOPLE_FULLY_VACCINATED) AS PEOPLE_FULLY_VACCINATED,
                   SUM(v.TOTAL_VACCINATIONS) AS TOTAL_VACCINATIONS,
                   p.WORLD_POP AS POPULATION
            FROM OWID_VACCINATIONS v
            CROSS JOIN pop p
            GROUP BY v.DATE, p.WORLD_POP
            ORDER BY v.DATE;
            """
            df_vax = fetch_data_from_snowflake(query, return_df=True)
        else:
            # country-level data
            query = """
                SELECT v.COUNTRY_REGION, v.DATE,
                       v.PEOPLE_VACCINATED, v.PEOPLE_FULLY_VACCINATED,
                       v.TOTAL_VACCINATIONS, p.POPULATION
                FROM OWID_VACCINATIONS v
                JOIN (
                    SELECT DISTINCT COUNTRY_REGION, POPULATION
                    FROM ECDC_GLOBAL
                ) p
                  ON UPPER(v.COUNTRY_REGION) = UPPER(p.COUNTRY_REGION)
                WHERE UPPER(v.COUNTRY_REGION) = %s
                  AND v.TOTAL_VACCINATIONS IS NOT NULL
                ORDER BY v.DATE
            """
            df_vax = fetch_data_from_snowflake(query, return_df=True, params=(country.upper(),))

        if df_vax.empty:
            return jsonify([]), 200

        df_vax["date"] = pd.to_datetime(df_vax["DATE"]).dt.strftime("%Y-%m-%d")
        return jsonify(df_vax.to_dict(orient="records")), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route(f"/{INFECTION_CASES_PAGE}", methods=["GET"])
def get_infection_cases():
    """
    return infection cases data for a given country or world
    """
    country = request.args.get("country")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    try:
        if country.upper() == "WORLD":
            # world-level aggregation
            query = """
                SELECT DATE,
                       SUM(CASES_WEEKLY) AS CASES_WEEKLY,
                       SUM(POPULATION) AS POPULATION
                FROM ECDC_GLOBAL_WEEKLY
                GROUP BY DATE
                ORDER BY DATE
            """
            df = fetch_data_from_snowflake(query, return_df=True)
        else:
            # country-level data
            query = """
                SELECT COUNTRY_REGION, DATE,
                       CASES_WEEKLY, POPULATION
                FROM ECDC_GLOBAL_WEEKLY
                WHERE UPPER(COUNTRY_REGION) = %s
                ORDER BY DATE
            """
            df = fetch_data_from_snowflake(query, return_df=True, params=(country.upper(),))

        if df.empty:
            return jsonify([]), 200

        df["date"] = pd.to_datetime(df["DATE"]).dt.strftime("%Y-%m-%d")
        return jsonify(df.to_dict(orient="records")), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route(f"/{INFECTION_DEATHS_PAGE}", methods=["GET"])
def get_infection_deaths():
    """
    return infection deaths data for a given country or world
    """
    country = request.args.get("country")
    if not country:
        return jsonify({"error": "country parameter required"}), 400

    try:
        if country.upper() == "WORLD":
            query = """
                SELECT DATE,
                       SUM(DEATHS_WEEKLY) AS DEATHS_WEEKLY,
                       SUM(POPULATION) AS POPULATION
                FROM ECDC_GLOBAL_WEEKLY
                GROUP BY DATE
                ORDER BY DATE
            """
            df = fetch_data_from_snowflake(query, return_df=True)
        else:
            query = """
                SELECT COUNTRY_REGION, DATE,
                       DEATHS_WEEKLY, POPULATION
                FROM ECDC_GLOBAL_WEEKLY
                WHERE UPPER(COUNTRY_REGION) = %s
                ORDER BY DATE
            """
            df = fetch_data_from_snowflake(query, return_df=True, params=(country.upper(),))

        if df.empty:
            return jsonify([]), 200

        df["date"] = pd.to_datetime(df["DATE"]).dt.strftime("%Y-%m-%d")
        return jsonify(df.to_dict(orient="records")), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
