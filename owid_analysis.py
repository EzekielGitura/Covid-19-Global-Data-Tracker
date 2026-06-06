from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px


DEFAULT_COUNTRIES = ["Kenya", "United States", "India"]

REQUIRED_COLUMNS = [
    "iso_code",
    "continent",
    "location",
    "date",
    "population",
    "total_cases",
    "total_deaths",
    "total_cases_per_million",
    "total_deaths_per_million",
    "new_cases_smoothed_per_million",
    "people_fully_vaccinated_per_hundred",
]

COLOR_SEQUENCE = [
    "#0f766e",
    "#e4572e",
    "#4c956c",
    "#2f4b7c",
    "#f2c14e",
    "#7b2cbf",
]


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path, usecols=lambda column: column in REQUIRED_COLUMNS)
    missing = {"iso_code", "continent", "location", "date"} - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "location", "iso_code"])

    for column in REQUIRED_COLUMNS:
        if column not in {"iso_code", "continent", "location", "date"} and column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["continent"] = df["continent"].fillna("")
    df = df[df["continent"].ne("") & ~df["iso_code"].str.startswith("OWID")]
    return df.sort_values(["location", "date"]).reset_index(drop=True)


def latest_records_for_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    valid = df.dropna(subset=[metric]).sort_values("date")
    if valid.empty:
        return valid
    return valid.groupby("location", as_index=False).tail(1)


def create_country_snapshot(df: pd.DataFrame, countries: list[str]) -> pd.DataFrame:
    selected = df[df["location"].isin(countries)]
    latest_base = (
        selected.sort_values("date")
        .groupby("location", as_index=False)
        .tail(1)[["location", "continent", "population", "date"]]
        .rename(columns={"date": "latest_record"})
        .set_index("location")
    )

    metrics = [
        "total_cases",
        "total_deaths",
        "total_cases_per_million",
        "total_deaths_per_million",
        "new_cases_smoothed_per_million",
        "people_fully_vaccinated_per_hundred",
    ]
    snapshot = latest_base.copy()

    for metric in metrics:
        metric_rows = latest_records_for_metric(selected, metric)
        metric_rows = metric_rows[["location", "date", metric]].rename(
            columns={"date": f"{metric}_date"}
        )
        snapshot = snapshot.join(metric_rows.set_index("location"), how="left")

    snapshot["case_fatality_rate"] = (
        snapshot["total_deaths"] / snapshot["total_cases"] * 100
    )
    return snapshot.reset_index().rename(columns={"location": "country"})


def write_trend_chart(df: pd.DataFrame, output_path: Path) -> None:
    chart_data = df.dropna(subset=["new_cases_smoothed_per_million"])
    fig = px.line(
        chart_data,
        x="date",
        y="new_cases_smoothed_per_million",
        color="location",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "date": "Date",
            "new_cases_smoothed_per_million": "7-day smoothed cases per million",
            "location": "Country",
        },
        title="COVID-19 case waves by country",
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    fig.write_html(output_path)


def write_global_map(df: pd.DataFrame, output_path: Path) -> None:
    map_data = latest_records_for_metric(df, "total_cases_per_million")
    fig = px.choropleth(
        map_data,
        locations="iso_code",
        color="total_cases_per_million",
        hover_name="location",
        hover_data={
            "iso_code": False,
            "continent": True,
            "date": True,
            "total_cases_per_million": ":,.1f",
        },
        color_continuous_scale="Viridis",
        projection="natural earth",
        title="Confirmed COVID-19 cases per million, latest available country values",
    )
    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=60, b=0))
    fig.write_html(output_path)


def write_markdown_summary(
    df: pd.DataFrame,
    snapshot: pd.DataFrame,
    output_path: Path,
    countries: list[str],
) -> None:
    date_min = df["date"].min().strftime("%Y-%m-%d")
    date_max = df["date"].max().strftime("%Y-%m-%d")
    highest_case_burden = snapshot.sort_values(
        "total_cases_per_million", ascending=False
    ).iloc[0]
    highest_death_burden = snapshot.sort_values(
        "total_deaths_per_million", ascending=False
    ).iloc[0]

    summary = f"""# COVID-19 Analysis Summary

Data source file: `owid-covid-data.csv`

Coverage: {len(df):,} country-level records from {date_min} to {date_max}.

Countries analyzed: {", ".join(countries)}

## Snapshot Findings

- Highest confirmed case burden in the selected set: {highest_case_burden["country"]} at {highest_case_burden["total_cases_per_million"]:,.1f} cases per million.
- Highest confirmed death burden in the selected set: {highest_death_burden["country"]} at {highest_death_burden["total_deaths_per_million"]:,.1f} deaths per million.
- The dashboard uses latest non-null values per metric because OWID metrics can stop updating on different dates.

## Generated Artifacts

- `country_snapshot.csv`: latest comparable country metrics.
- `case_trends.html`: interactive case-wave trend chart.
- `global_case_map.html`: interactive country choropleth.
"""
    output_path.write_text(summary, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate static COVID-19 analysis artifacts from OWID data."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("owid-covid-data.csv"),
        help="Path to the OWID COVID-19 CSV file.",
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=DEFAULT_COUNTRIES,
        help="Country names to include in the focused comparison.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs"),
        help="Directory where generated artifacts should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(args.data)

    available = set(df["location"].unique())
    missing_countries = [country for country in args.countries if country not in available]
    if missing_countries:
        missing = ", ".join(missing_countries)
        raise ValueError(f"Country names not found in dataset: {missing}")

    selected_df = df[df["location"].isin(args.countries)]
    snapshot = create_country_snapshot(df, args.countries)

    args.output.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(args.output / "country_snapshot.csv", index=False)
    write_trend_chart(selected_df, args.output / "case_trends.html")
    write_global_map(df, args.output / "global_case_map.html")
    write_markdown_summary(
        df,
        snapshot,
        args.output / "summary.md",
        args.countries,
    )

    print(f"Generated analysis artifacts in {args.output.resolve()}")


if __name__ == "__main__":
    main()
