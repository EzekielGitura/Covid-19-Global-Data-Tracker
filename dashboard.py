from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).with_name("owid-covid-data.csv")

DEFAULT_COUNTRIES = [
    "Kenya",
    "United States",
    "India",
    "Brazil",
    "South Africa",
]

BASE_COLUMNS = [
    "iso_code",
    "continent",
    "location",
    "date",
]

NUMERIC_COLUMNS = [
    "population",
    "total_cases",
    "new_cases",
    "new_cases_smoothed",
    "total_deaths",
    "new_deaths",
    "new_deaths_smoothed",
    "total_cases_per_million",
    "new_cases_per_million",
    "new_cases_smoothed_per_million",
    "total_deaths_per_million",
    "new_deaths_per_million",
    "new_deaths_smoothed_per_million",
    "people_vaccinated",
    "people_fully_vaccinated",
    "total_boosters",
    "total_vaccinations",
    "people_vaccinated_per_hundred",
    "people_fully_vaccinated_per_hundred",
    "total_boosters_per_hundred",
    "reproduction_rate",
    "icu_patients_per_million",
    "hosp_patients_per_million",
    "positive_rate",
    "stringency_index",
]

REQUIRED_COLUMNS = BASE_COLUMNS + NUMERIC_COLUMNS

MAP_METRICS = {
    "Cases per million": "total_cases_per_million",
    "Deaths per million": "total_deaths_per_million",
    "Fully vaccinated (%)": "people_fully_vaccinated_per_hundred",
    "Recent new cases per million": "new_cases_smoothed_per_million",
}

COLOR_SEQUENCE = [
    "#0f766e",
    "#e4572e",
    "#4c956c",
    "#2f4b7c",
    "#f2c14e",
    "#7b2cbf",
    "#bc5090",
    "#58508d",
]


st.set_page_config(
    page_title="COVID-19 Global Data Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_data(file_bytes: bytes | None = None) -> pd.DataFrame:
    source = BytesIO(file_bytes) if file_bytes else DATA_PATH

    if not file_bytes and not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {DATA_PATH.name}")

    df = pd.read_csv(source, usecols=lambda column: column in REQUIRED_COLUMNS)
    missing_columns = set(BASE_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"The dataset is missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "location", "iso_code"])

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["continent"] = df["continent"].fillna("")
    df["is_country"] = df["continent"].ne("") & ~df["iso_code"].str.startswith("OWID")

    return df.sort_values(["location", "date"]).reset_index(drop=True)


def format_compact(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"

    value = float(value)
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def format_percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.1f}%"


def format_date(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return pd.Timestamp(value).strftime("%b %d, %Y")


def latest_records_for_metric(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    if metric not in df.columns:
        return pd.DataFrame(columns=df.columns)

    valid = df.dropna(subset=[metric]).sort_values("date")
    if valid.empty:
        return valid
    return valid.groupby("location", as_index=False).tail(1)


def country_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    latest_base = (
        df.sort_values("date")
        .groupby("location", as_index=False)
        .tail(1)[["location", "iso_code", "continent", "population", "date"]]
        .rename(columns={"date": "latest_record"})
        .set_index("location")
    )

    metrics = [
        "total_cases",
        "total_deaths",
        "total_cases_per_million",
        "total_deaths_per_million",
        "new_cases_smoothed_per_million",
        "people_fully_vaccinated",
        "people_fully_vaccinated_per_hundred",
    ]

    snapshot = latest_base.copy()
    for metric in metrics:
        metric_rows = latest_records_for_metric(df, metric)
        if metric_rows.empty:
            snapshot[metric] = pd.NA
            snapshot[f"{metric}_date"] = pd.NaT
            continue

        metric_rows = metric_rows[["location", "date", metric]].rename(
            columns={"date": f"{metric}_date"}
        )
        snapshot = snapshot.join(metric_rows.set_index("location"), how="left")

    snapshot = snapshot.reset_index()
    snapshot["case_fatality_rate"] = (
        snapshot["total_deaths"] / snapshot["total_cases"] * 100
    )
    return snapshot


def aggregate_kpis(snapshot: pd.DataFrame) -> dict[str, float | None]:
    cases = snapshot["total_cases"].sum(min_count=1)
    deaths = snapshot["total_deaths"].sum(min_count=1)
    fully_vaccinated = snapshot["people_fully_vaccinated"].sum(min_count=1)
    population = snapshot["population"].sum(min_count=1)

    cfr = deaths / cases * 100 if pd.notna(cases) and cases else None
    vaccination_rate = (
        fully_vaccinated / population * 100
        if pd.notna(fully_vaccinated) and pd.notna(population) and population
        else None
    )

    return {
        "cases": cases,
        "deaths": deaths,
        "case_fatality_rate": cfr,
        "vaccination_rate": vaccination_rate,
    }


def apply_page_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.9rem 1rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        }
        div[data-testid="stMetricLabel"] p {
            color: #475569;
            font-size: 0.88rem;
        }
        div[data-testid="stMetricValue"] {
            color: #0f172a;
        }
        .source-note {
            color: #475569;
            font-size: 0.92rem;
            margin-top: -0.4rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_line_chart(
    df: pd.DataFrame,
    metric: str,
    title: str,
    y_axis_title: str,
    log_scale: bool = False,
):
    chart_data = df.dropna(subset=[metric])
    if chart_data.empty:
        return None

    fig = px.line(
        chart_data,
        x="date",
        y=metric,
        color="location",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"date": "Date", metric: y_axis_title, "location": "Country"},
        title=title,
    )
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="",
        margin=dict(l=10, r=10, t=55, b=10),
    )
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log")
    return fig


def build_choropleth(
    df: pd.DataFrame,
    metric_label: str,
    metric: str,
):
    map_data = latest_records_for_metric(df, metric)
    map_data = map_data[map_data["is_country"]].dropna(subset=["iso_code", metric])
    if map_data.empty:
        return None

    latest_metric_date = map_data["date"].max()
    fig = px.choropleth(
        map_data,
        locations="iso_code",
        color=metric,
        hover_name="location",
        hover_data={
            "iso_code": False,
            "continent": True,
            "date": True,
            metric: ":,.1f",
        },
        color_continuous_scale="Viridis",
        projection="natural earth",
        title=f"{metric_label} by country, latest available through {format_date(latest_metric_date)}",
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=55, b=0),
        coloraxis_colorbar_title=metric_label,
    )
    return fig


def build_top_country_chart(df: pd.DataFrame, metric_label: str, metric: str):
    ranking = latest_records_for_metric(df, metric)
    ranking = ranking[ranking["is_country"]].dropna(subset=[metric])
    if ranking.empty:
        return None

    ranking = ranking.sort_values(metric, ascending=False).head(20)
    fig = px.bar(
        ranking.sort_values(metric),
        x=metric,
        y="location",
        color="continent",
        orientation="h",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={metric: metric_label, "location": "", "continent": "Region"},
        title=f"Top countries by {metric_label.lower()}",
    )
    fig.update_layout(
        template="plotly_white",
        legend_title_text="",
        margin=dict(l=10, r=10, t=55, b=10),
    )
    return fig


def main() -> None:
    apply_page_styles()

    uploaded_file = st.sidebar.file_uploader(
        "Optional replacement CSV",
        type="csv",
        help="Use a newer Our World in Data CSV without changing the repository file.",
    )

    try:
        df = load_data(uploaded_file.getvalue() if uploaded_file else None)
    except Exception as exc:
        st.error(f"Could not load the COVID-19 dataset. {exc}")
        st.stop()

    country_df = df[df["is_country"]].copy()
    source_name = uploaded_file.name if uploaded_file else DATA_PATH.name
    min_date = country_df["date"].min().date()
    max_date = country_df["date"].max().date()

    st.title("COVID-19 Global Data Tracker")
    st.markdown(
        f"<div class='source-note'>Source: {source_name} | "
        f"{len(country_df):,} country-level records | "
        f"{format_date(pd.Timestamp(min_date))} to {format_date(pd.Timestamp(max_date))}</div>",
        unsafe_allow_html=True,
    )

    continents = sorted(country_df["continent"].dropna().unique())
    selected_continents = st.sidebar.multiselect(
        "Regions",
        continents,
        default=continents,
    )

    scoped_countries = country_df[country_df["continent"].isin(selected_continents)]
    country_options = sorted(scoped_countries["location"].dropna().unique())
    default_countries = [country for country in DEFAULT_COUNTRIES if country in country_options]
    if not default_countries and country_options:
        default_countries = country_options[: min(5, len(country_options))]

    selected_countries = st.sidebar.multiselect(
        "Countries",
        country_options,
        default=default_countries,
    )

    selected_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if not isinstance(selected_range, tuple) or len(selected_range) != 2:
        st.info("Select a start and end date to render the dashboard.")
        st.stop()

    start_date, end_date = selected_range
    if start_date > end_date:
        st.error("The start date must be before the end date.")
        st.stop()

    map_metric_label = st.sidebar.selectbox(
        "Map and ranking metric",
        list(MAP_METRICS.keys()),
        index=0,
    )
    map_metric = MAP_METRICS[map_metric_label]
    log_scale = st.sidebar.toggle("Log scale cumulative charts", value=False)

    date_mask = country_df["date"].between(
        pd.Timestamp(start_date), pd.Timestamp(end_date)
    )
    comparison_scope = country_df[
        country_df["continent"].isin(selected_continents) & date_mask
    ]
    filtered = country_df[
        country_df["location"].isin(selected_countries) & date_mask
    ]

    if not selected_countries:
        st.warning("Select at least one country to compare.")
        st.stop()
    if filtered.empty:
        st.warning("No records match the selected filters.")
        st.stop()

    snapshot = country_snapshot(filtered)
    kpis = aggregate_kpis(snapshot)

    st.caption(
        f"Current view: {len(selected_countries)} countries from "
        f"{format_date(pd.Timestamp(start_date))} to {format_date(pd.Timestamp(end_date))}. "
        "Cumulative totals use the latest non-null country value inside the selected range."
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Confirmed cases", format_compact(kpis["cases"]))
    metric_cols[1].metric("Confirmed deaths", format_compact(kpis["deaths"]))
    metric_cols[2].metric(
        "Case fatality ratio",
        format_percent(kpis["case_fatality_rate"]),
    )
    metric_cols[3].metric(
        "Fully vaccinated",
        format_percent(kpis["vaccination_rate"]),
    )

    trends_tab, map_tab, comparison_tab, data_tab = st.tabs(
        ["Trends", "Global map", "Country comparison", "Data"]
    )

    with trends_tab:
        left, right = st.columns(2)
        with left:
            fig = build_line_chart(
                filtered,
                "total_cases_per_million",
                "Cumulative confirmed cases",
                "Cases per million",
                log_scale=log_scale,
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cumulative case data is available for this selection.")

        with right:
            fig = build_line_chart(
                filtered,
                "new_cases_smoothed_per_million",
                "Recent confirmed cases",
                "7-day smoothed cases per million",
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent case data is available for this selection.")

        left, right = st.columns(2)
        with left:
            fig = build_line_chart(
                filtered,
                "total_deaths_per_million",
                "Cumulative confirmed deaths",
                "Deaths per million",
                log_scale=log_scale,
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cumulative death data is available for this selection.")

        with right:
            fig = build_line_chart(
                filtered,
                "people_fully_vaccinated_per_hundred",
                "Vaccination coverage",
                "Fully vaccinated (% of population)",
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No vaccination coverage data is available for this selection.")

    with map_tab:
        fig = build_choropleth(comparison_scope, map_metric_label, map_metric)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No map data is available for this metric and date range.")

    with comparison_tab:
        fig = build_top_country_chart(comparison_scope, map_metric_label, map_metric)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No ranking data is available for this metric and date range.")

        display = snapshot[
            [
                "location",
                "continent",
                "total_cases",
                "total_deaths",
                "case_fatality_rate",
                "total_cases_per_million",
                "total_deaths_per_million",
                "people_fully_vaccinated_per_hundred",
            ]
        ].rename(
            columns={
                "location": "Country",
                "continent": "Region",
                "total_cases": "Confirmed cases",
                "total_deaths": "Confirmed deaths",
                "case_fatality_rate": "Case fatality ratio (%)",
                "total_cases_per_million": "Cases per million",
                "total_deaths_per_million": "Deaths per million",
                "people_fully_vaccinated_per_hundred": "Fully vaccinated (%)",
            }
        )
        display = display.sort_values("Confirmed cases", ascending=False)
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Confirmed cases": st.column_config.NumberColumn(format="%d"),
                "Confirmed deaths": st.column_config.NumberColumn(format="%d"),
                "Case fatality ratio (%)": st.column_config.NumberColumn(format="%.2f"),
                "Cases per million": st.column_config.NumberColumn(format="%.1f"),
                "Deaths per million": st.column_config.NumberColumn(format="%.1f"),
                "Fully vaccinated (%)": st.column_config.NumberColumn(format="%.1f"),
            },
        )

    with data_tab:
        availability_columns = list(MAP_METRICS.values())
        completeness = (
            filtered.groupby("location")[availability_columns]
            .apply(lambda frame: frame.notna().mean() * 100)
            .reset_index()
            .rename(columns={"location": "Country"})
        )
        completeness = completeness.rename(
            columns={column: label for label, column in MAP_METRICS.items()}
        )
        st.subheader("Metric availability in the current view")
        st.dataframe(
            completeness,
            hide_index=True,
            use_container_width=True,
            column_config={
                label: st.column_config.ProgressColumn(
                    label,
                    format="%.0f%%",
                    min_value=0,
                    max_value=100,
                )
                for label in MAP_METRICS
            },
        )

        st.download_button(
            "Download filtered data",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="covid19_filtered_data.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
