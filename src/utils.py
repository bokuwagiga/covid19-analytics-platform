# app.py

import os
import traceback
import kagglehub
import matplotlib.pyplot as plt
import pandas as pd
import requests
import snowflake.connector

from config.config import API_BASE


# Environment & Connection


def get_snowflake_connection(initial: bool = False):
    """
    Connect to Snowflake using env vars
    if initial=True use only account, user, password
    otherwise include warehouse, database, and schema
    """
    if initial:
        args = {
            'user': os.getenv("SNOWFLAKE_USER"),
            'password': os.getenv("SNOWFLAKE_PASSWORD"),
            'account': os.getenv("SNOWFLAKE_ACCOUNT")
        }
    else:
        args = {
            'user': os.getenv("SNOWFLAKE_USER"),
            'password': os.getenv("SNOWFLAKE_PASSWORD"),
            'account': os.getenv("SNOWFLAKE_ACCOUNT"),
            'warehouse': os.getenv("SNOWFLAKE_WAREHOUSE"),
            'database': os.getenv("SNOWFLAKE_DATABASE"),
            'schema': os.getenv("SNOWFLAKE_SCHEMA")
        }
    return snowflake.connector.connect(**args)


# Data Fetching

def fetch_data_from_snowflake(query: str, return_df: bool = True, params=None):
    """
    Run a query on Snowflake
    return dataframe if return_df=True else raw tuples
    """
    conn = None
    cursor = None
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if return_df:
            return pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
        else:
            return cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        traceback.print_exc()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def load_kaggle_mortality_data() -> pd.DataFrame:
    """
    Download and load Kaggle world mortality dataset
    returns dataframe with mortality data
    """
    path = kagglehub.dataset_download("konradb/world-mortality-dataset")
    file_path = os.path.join(path, "world_mortality.csv")
    df = pd.read_csv(file_path)
    return df


# Preprocessing

def preprocess_mortality_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert weekly deaths to monthly totals
    """
    df_weekly = df[df['time_unit'] == 'weekly'].copy()

    # convert year+week to datetime
    df_weekly["date"] = pd.to_datetime(
        df_weekly["year"].astype(str) + df_weekly["time"].astype(str) + '1',
        format="%Y%W%w"
    )
    df_weekly["month"] = df_weekly["date"].dt.month

    # group by month
    df_monthly = (
        df_weekly.groupby(["country_name", "year", "month"])["deaths"]
        .sum()
        .reset_index()
        .rename(columns={"deaths": "deaths_allcause"})
    )
    return df_monthly


# Visualization

def plot_mortality(df: pd.DataFrame, country: str) -> None:
    """
    Plot observed vs counterfactual vs covid deaths
    for a given country
    """
    df_country = df[df['country_name'].str.upper() == country.upper()].copy()
    df_country = df_country.sort_values(['year', 'month'])
    df_country['date'] = pd.to_datetime(
        df_country['year'].astype(str) + '-' + df_country['month'].astype(str) + '-01'
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # observed vs counterfactual
    ax1.plot(df_country['date'], df_country['deaths_allcause'],
             label='Observed all-cause deaths', color='black')
    ax1.plot(df_country['date'], df_country['deaths_without_covid'],
             label='Counterfactual (no COVID)', linestyle='--', color='blue')
    ax1.set_title(f"Mortality in {country}: Observed vs Counterfactual")
    ax1.set_ylabel("Deaths")
    ax1.legend()
    ax1.grid(True)

    # reported covid deaths
    ax2.plot(df_country['date'], df_country['deaths_covid'],
             label='Reported COVID deaths', linestyle=':', color='red')
    ax2.set_ylabel("COVID deaths")
    ax2.legend()
    ax2.grid(True)

    plt.xlabel("Date")
    plt.tight_layout()
    plt.show()

# utility function to get available countries

def get_country_list(table="ECDC_GLOBAL",include_world=False):
    """
    Fetch the list of countries from the API
    adds 'World' option on top of the list
    """
    try:
        resp = requests.get(f"{API_BASE}/countries",params={"table": table})
        if resp.status_code == 200:
            countries = resp.json()
            if include_world:
                return ["World"] + countries
            else:
                return countries
    except:
        return []
    return []