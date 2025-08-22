#api/src/clustering.py
import pandas as pd
from sklearn.cluster import KMeans

def run_clustering(df: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    """
    Compute clusters based on Covid-19 deaths + cases per 100k.
    Vaccination is optional (if available).
    """
    features = []
    for country, grp in df.groupby("COUNTRY_REGION"):
        pop = grp["POPULATION"].max() or None
        if not pop or pop == 0:
            continue
        rec = {"country": country}

        for year in [2020, 2021, 2022]:
            deaths = grp.loc[grp["YEAR"] == year, "TOTAL_DEATHS"].sum()
            cases = grp.loc[grp["YEAR"] == year, "TOTAL_CASES"].sum()
            rec[f"deaths_{year}_per100k"] = (deaths / pop) * 100000 if deaths else 0
            rec[f"cases_{year}_per100k"] = (cases / pop) * 100000 if cases else 0

        features.append(rec)

    df_feat = pd.DataFrame(features).dropna()
    if df_feat.empty:
        return pd.DataFrame()

    # Normalize features
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    X = df_feat.drop(columns=["country"]).values
    X_scaled = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(X_scaled)
    df_feat["cluster"] = km.labels_.astype(int)

    return df_feat
