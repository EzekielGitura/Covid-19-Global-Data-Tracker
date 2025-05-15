import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
from matplotlib.backends.backend_pdf import PdfPages
import os

# Load Data Function
@st.cache_data
def load_data(filepath):
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Filter Data by User Input
def filter_data(df, countries, start_date, end_date):
    df_filtered = df[(df['location'].isin(countries)) & (df['date'] >= start_date) & (df['date'] <= end_date)]
    return df_filtered

# Visualization Functions
def plot_total_cases(df, countries):
    plt.figure(figsize=(10, 6))
    for country in countries:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_cases'], label=country)
    plt.title("Total Cases Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Cases")
    plt.legend()
    st.pyplot(plt)

def plot_total_deaths(df, countries):
    plt.figure(figsize=(10, 6))
    for country in countries:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_deaths'], label=country)
    plt.title("Total Deaths Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Deaths")
    plt.legend()
    st.pyplot(plt)

def plot_vaccination_progress(df, countries):
    plt.figure(figsize=(10, 6))
    for country in countries:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_vaccinations'], label=country)
    plt.title("Vaccination Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Vaccinations")
    plt.legend()
    st.pyplot(plt)

# Choropleth Map
def generate_choropleth_map(df):
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date]
    fig = px.choropleth(latest_data,
                        locations="iso_code",
                        color="total_cases",
                        hover_name="location",
                        title=f"Global COVID-19 Cases as of {latest_date}",
                        color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig)

# Dashboard with Streamlit
def run_dashboard():
    st.title("COVID-19 Global Data Tracker Dashboard")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload COVID-19 Dataset (owid-covid-data.csv)", type="csv")
    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success("Data loaded successfully!")
            
            # User Input: Country and Date Range
            countries = st.multiselect("Select Countries", df['location'].unique())
            start_date = st.date_input("Start Date", value=df['date'].min())
            end_date = st.date_input("End Date", value=df['date'].max())
            
            if countries and start_date and end_date:
                df_filtered = filter_data(df, countries, start_date, end_date)
                
                # Visualizations
                st.subheader("Total Cases Over Time")
                plot_total_cases(df_filtered, countries)
                
                st.subheader("Total Deaths Over Time")
                plot_total_deaths(df_filtered, countries)
                
                st.subheader("Vaccination Progress Over Time")
                plot_vaccination_progress(df_filtered, countries)
                
                st.subheader("Choropleth Map")
                generate_choropleth_map(df_filtered)
                
                # Optional: Hospitalization or ICU Data
                if 'hosp_patients' in df.columns and 'icu_patients' in df.columns:
                    st.subheader("Hospitalization and ICU Data")
                    for country in countries:
                        country_df = df_filtered[df_filtered['location'] == country]
                        st.write(f"Hospitalization data for {country}")
                        st.line_chart(country_df[['date', 'hosp_patients', 'icu_patients']].set_index('date'))
    else:
        st.warning("Please upload a dataset to proceed.")

# Main Function
if __name__ == "__main__":
    run_dashboard()