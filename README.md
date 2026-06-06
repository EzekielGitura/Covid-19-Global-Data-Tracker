# COVID-19 Global Data Tracker

Interactive Streamlit dashboard for exploring country-level COVID-19 cases, deaths, and vaccination coverage from the Our World in Data dataset.

## Features

- Automatic loading of the bundled `owid-covid-data.csv`, with optional upload for a newer CSV.
- Country and date filters for focused comparisons.
- KPI cards for confirmed cases, confirmed deaths, case fatality ratio, and vaccination coverage.
- Population-normalized trend charts for fairer country comparison.
- Global choropleth map, country ranking chart, metric availability table, and filtered CSV download.

## Data

- Source: Our World in Data COVID-19 dataset
- Local file: `owid-covid-data.csv`
- Snapshot coverage: 2020-01-01 through 2024-08-14
- Dataset docs: https://docs.owid.io/projects/covid/en/latest/dataset.html
- Refresh CSV: https://covid.ourworldindata.org/data/owid-covid-data.csv

The dashboard uses the latest non-null value per metric because OWID fields can stop updating on different dates.

## Tech Stack

Python, pandas, Plotly, Streamlit

## Run Locally

Use Python 3.11 or 3.12.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard.py
```

Open the Streamlit URL shown in the terminal, usually `http://localhost:8501`.

## Static Analysis

Generate optional HTML and CSV artifacts:

```bash
python owid_analysis.py --countries Kenya "United States" India
```

Outputs are written to `outputs/`.

## Limitations

- The bundled dataset is a static snapshot, not a live feed.
- Confirmed metrics depend on country reporting practices and testing availability.
- Case fatality ratio is calculated as confirmed deaths divided by confirmed cases.
