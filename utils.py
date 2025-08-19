#app.py

import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import kagglehub
import matplotlib.pyplot as plt



# Environment & Connection


def load_env() -> None:
    """
    Load environment variables from .env file.
    Required vars:
        SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT,
        SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
    """
    load_dotenv('config/.env')


def get_snowflake_connection(initial: bool = False):
    """
    Connect to Snowflake using environment variables.

    If initial=True, connect only with account, user, password (used for setup).
    Otherwise include warehouse, database, and schema (used for main operations).
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


def fetch_covid_data(country: str, table: str = "ECDC_GLOBAL") -> pd.DataFrame:
    """
    Fetch COVID-19 death data from Snowflake for a given country.

    Args:
        country: Country name (case-insensitive).
        table: Source table name (default = ECDC_GLOBAL).

    Returns:
        DataFrame with columns [COUNTRY_REGION, DEATHS, DATE].
    """
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT COUNTRY_REGION, DEATHS, DATE
        FROM {table}
        WHERE UPPER(COUNTRY_REGION) = %s
    """
    cursor.execute(query, (country.upper(),))
    df = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])

    cursor.close()
    conn.close()
    return df

def fetch_covid_data_countries(table: str = "ECDC_GLOBAL") -> pd.DataFrame:
    """
    Fetch countries with COVID-19 death data from Snowflake.

    Args:
        table: Source table name (default = ECDC_GLOBAL).
    Returns:
        DataFrame with columns [COUNTRY_REGION, DEATHS, DATE].
    """
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    query = f"""
        SELECT DISTINCT COUNTRY_REGION
        FROM {table}
    """
    cursor.execute(query)
    countries = cursor.fetchall()
    cursor.close()
    conn.close()
    return countries


def load_kaggle_mortality_data() -> pd.DataFrame:
    """
    Download and load Kaggle's world mortality dataset.

    Returns:
        DataFrame with columns [iso3c, country_name, year, time, time_unit, deaths].
    """
    path = kagglehub.dataset_download("konradb/world-mortality-dataset")
    file_path = os.path.join(path, "world_mortality.csv")
    df = pd.read_csv(file_path)
    return df



# Preprocessing


def preprocess_mortality_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert weekly all-cause deaths to monthly totals.

    Args:
        df: Raw Kaggle mortality dataset.

    Returns:
        DataFrame with [country_name, year, month, deaths_allcause].
    """
    df_weekly = df[df['time_unit'] == 'weekly'].copy()
    # Convert year+week to datetime
    df_weekly["date"] = pd.to_datetime(
        df_weekly["year"].astype(str) + df_weekly["time"].astype(str) + '1',
        format="%Y%W%w"
    )
    df_weekly["month"] = df_weekly["date"].dt.month

    # Aggregate weekly → monthly deaths
    df_monthly = (
        df_weekly.groupby(["country_name", "year", "month"])["deaths"]
        .sum()
        .reset_index()
        .rename(columns={"deaths": "deaths_allcause"})
    )
    return df_monthly


def preprocess_covid_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert daily COVID deaths to monthly totals.

    Args:
        df: Raw Snowflake COVID dataset.

    Returns:
        DataFrame with [country_name, year, month, deaths_covid].
    """
    df_temp = df[['COUNTRY_REGION', 'DEATHS', 'DATE']].copy()
    df_temp["year"] = pd.to_datetime(df_temp['DATE']).dt.year
    df_temp["month"] = pd.to_datetime(df_temp['DATE']).dt.month

    df_monthly = (
        df_temp.groupby(['COUNTRY_REGION', 'year', 'month'])['DEATHS']
        .sum()
        .reset_index()
        .rename(columns={
            'COUNTRY_REGION': 'country_name',
            'DEATHS': 'deaths_covid'
        })
    )
    return df_monthly



# Analysis


def merge_country_datasets(df_mortality: pd.DataFrame, df_covid: pd.DataFrame) -> pd.DataFrame:
    """
    Merge all-cause mortality with COVID deaths.

    Args:
        df_mortality: Monthly all-cause mortality.
        df_covid: Monthly COVID deaths.

    Returns:
        list of countries.
    """
    df_merged = pd.merge(
        df_mortality, df_covid,
        on='country_name',
        how='inner'
    )
    return df_merged


def merge_datasets(df_mortality: pd.DataFrame, df_covid: pd.DataFrame) -> pd.DataFrame:
    """
    Merge all-cause mortality with COVID deaths.

    Args:
        df_mortality: Monthly all-cause mortality.
        df_covid: Monthly COVID deaths.

    Returns:
        DataFrame with [country_name, year, month, deaths_allcause, deaths_covid].
    """
    df_merged = pd.merge(
        df_mortality, df_covid,
        on=['country_name', 'year', 'month'],
        how='inner'
    )
    df_merged['deaths_covid'] = df_merged['deaths_covid'].fillna(0)
    return df_merged


def calculate_counterfactual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate counterfactual deaths = all-cause - COVID.

    Args:
        df: Merged mortality + COVID dataset.

    Returns:
        Same DataFrame with added column `deaths_without_covid`.
    """
    df['deaths_without_covid'] = df['deaths_allcause'] - df['deaths_covid']
    return df



# Visualization


def plot_mortality(df: pd.DataFrame, country: str) -> None:
    """
    Plot observed vs counterfactual vs COVID deaths for a given country.

    Args:
        df: Merged dataset with counterfactual column.
        country: Country name.
    """
    df_country = df[df['country_name'].str.upper() == country.upper()].copy()
    df_country = df_country.sort_values(['year', 'month'])
    df_country['date'] = pd.to_datetime(
        df_country['year'].astype(str) + '-' + df_country['month'].astype(str) + '-01'
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot observed vs counterfactual
    ax1.plot(df_country['date'], df_country['deaths_allcause'],
             label='Observed all-cause deaths', color='black')
    ax1.plot(df_country['date'], df_country['deaths_without_covid'],
             label='Counterfactual (no COVID)', linestyle='--', color='blue')
    ax1.set_title(f"Mortality in {country}: Observed vs Counterfactual")
    ax1.set_ylabel("Deaths")
    ax1.legend()
    ax1.grid(True)

    # Plot reported COVID deaths
    ax2.plot(df_country['date'], df_country['deaths_covid'],
             label='Reported COVID deaths', linestyle=':', color='red')
    ax2.set_ylabel("COVID deaths")
    ax2.legend()
    ax2.grid(True)

    plt.xlabel("Date")
    plt.tight_layout()
    plt.show()



# Main Workflow


def main(country: str = "Lithuania") -> None:
    """
    Full workflow:
    1. Load env vars & connect to Snowflake.
    2. Fetch COVID data for given country.
    3. Load and preprocess Kaggle mortality dataset.
    4. Preprocess COVID data.
    5. Merge + calculate counterfactual.
    6. Visualize.
    """
    load_env()
    df_covid_raw = fetch_covid_data(country)
    df_mortality_raw = load_kaggle_mortality_data()

    df_mortality = preprocess_mortality_data(df_mortality_raw)
    df_covid = preprocess_covid_data(df_covid_raw)

    df_merged = merge_datasets(df_mortality, df_covid)
    df_final = calculate_counterfactual(df_merged)

    plot_mortality(df_final, country)


if __name__ == "__main__":
    main("Lithuania")
