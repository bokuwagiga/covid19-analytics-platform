import pandas as pd
from prophet import Prophet
from shared.utils import preprocess_mortality_data, load_kaggle_mortality_data

def build_forecast(country: str, horizon_months: int = 24):
    """
    Forecast expected deaths for 2020–2022 based on 2015–2019.
    Return observed (2015–<2023) and forecast (2020–2022).
    """
    df = load_kaggle_mortality_data()
    df_monthly = preprocess_mortality_data(df)

    if country.upper() == "WORLD":
        # Aggregate world deaths by month
        df_monthly = (
            df_monthly.groupby(["year", "month"])["deaths_allcause"]
            .sum()
            .reset_index()
        )
        df_monthly["country_name"] = "World"
    else:
        df_monthly = df_monthly[df_monthly["country_name"] == country]

    df_monthly["date"] = pd.to_datetime(
        df_monthly["year"].astype(str) + "-" + df_monthly["month"].astype(str) + "-01"
    )

    # training data: 2015–2019
    df_train = df_monthly[df_monthly["year"] < 2020][["date", "deaths_allcause"]]
    if df_train.empty:
        raise ValueError(f"No training data available for {country}")

    df_train = df_train.rename(columns={"date": "ds", "deaths_allcause": "y"})

    # fit Prophet
    model = Prophet(yearly_seasonality=True)
    model.fit(df_train)

    # forecast horizon = 2020–2022
    future = model.make_future_dataframe(periods=horizon_months, freq="M")
    forecast = model.predict(future)

    # normalize to first of month
    forecast["ds"] = pd.to_datetime(forecast["ds"]).dt.to_period("M").dt.to_timestamp()

    # keep forecast rows only for 2020–2022
    forecast_filtered = forecast[
        (forecast["ds"].dt.year >= 2020) & (forecast["ds"].dt.year <= 2022)
    ][["ds", "yhat"]].copy()
    forecast_filtered.rename(columns={"ds": "date", "yhat": "forecast"}, inplace=True)

    # observed deaths (2015–<2023 full history)
    df_obs = df_monthly[df_monthly["year"] < 2023][["date", "deaths_allcause"]]
    df_obs = df_obs.rename(columns={"deaths_allcause": "observed"})

    # merge observed + forecast
    df_out = pd.merge(df_obs, forecast_filtered, on="date", how="outer").sort_values("date")

    # fill missing with None for JSON safety
    df_out["observed"] = df_out["observed"].where(pd.notnull(df_out["observed"]), None)
    df_out["forecast"] = df_out["forecast"].where(pd.notnull(df_out["forecast"]), None)
    df_out["country_name"] = country

    # ---- cumulative totals (for 2020–2022 only) ----
    observed_total = df_out[
        (df_out["date"].dt.year >= 2020) & (df_out["date"].dt.year <= 2022) & (pd.notnull(df_out["observed"]))
    ]["observed"].sum()
    forecast_total = df_out[
        (df_out["date"].dt.year >= 2020) & (df_out["date"].dt.year <= 2022) & (pd.notnull(df_out["forecast"]))
    ]["forecast"].sum()

    df_out["observed_total"] = observed_total
    df_out["forecast_total"] = forecast_total

    return df_out
