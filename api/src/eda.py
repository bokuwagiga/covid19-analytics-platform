# api/src/eda.py
import pandas as pd
import os

def _make_json_safe(obj):
    """Convert Pandas/numpy objects to JSON-safe types recursively"""
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_safe(v) for v in obj]
    elif isinstance(obj, (pd.Series, pd.Index)):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif hasattr(obj, "item"):
        return obj.item()
    return obj


def run_basic_eda(df: pd.DataFrame, name: str = "dataset") -> dict:
    """Run a simple EDA on a pandas DataFrame."""
    results = {}
    results["shape"] = (int(df.shape[0]), int(df.shape[1]))
    results["columns"] = {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
    results["missing_values"] = df.isnull().sum().astype(int).to_dict()
    results["summary_stats"] = _make_json_safe(df.describe(include="all").to_dict())
    results["correlations"] = _make_json_safe(df.corr(numeric_only=True).to_dict())

    # Save preview
    preview_path = f"eda_{name}_preview.csv"
    df.head(50).to_csv(preview_path, index=False)
    results["preview_file"] = preview_path
    return results

def run_detailed_eda(df: pd.DataFrame, name: str = "dataset"):
    """
    Generate a detailed HTML profiling report if ydata-profiling is installed.
    Returns the absolute path of the report file.
    """
    try:
        from ydata_profiling import ProfileReport
    except ImportError:
        print("⚠️ ydata-profiling not installed. Skipping detailed EDA.")
        return None

    # Ensure reports directory exists
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    safe_name = name.replace(".", "_").replace(" ", "_")
    out_file = os.path.join(reports_dir, f"eda_{safe_name}_report.html")

    profile = ProfileReport(df, title=f"EDA Report for {name}", explorative=True)
    profile.to_file(out_file)
    print(f"Detailed EDA report saved: {out_file}")

    return out_file
