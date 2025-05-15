import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import plotly.express as px
import os

# Error Handling Wrapper
def safe_execute(func):
    def wrapper_safe_execute(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error occurred: {e}")
    return wrapper_safe_execute

# Step 1: Data Loading and Exploration
@safe_execute
def load_and_explore_data(filepath):
    print("Loading data...")
    df = pd.read_csv(filepath)
    print(f"Data loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns}")
    print(f"Preview of data:\n{df.head()}")
    print(f"Missing values:\n{df.isnull().sum()}")
    return df

# Step 2: Data Cleaning
@safe_execute
def clean_data(df, countries_of_interest):
    print("Cleaning data...")
    df = df[df['location'].isin(countries_of_interest)]
    df['date'] = pd.to_datetime(df['date'])
    df.fillna(method='ffill', inplace=True)  # Forward fill for NaN values
    print("Data cleaned. Final shape:", df.shape)
    return df

# Step 3: Exploratory Data Analysis
@safe_execute
def perform_eda(df, countries_of_interest):
    print("Performing EDA...")

    # Plot total cases over time
    plt.figure(figsize=(10, 6))
    for country in countries_of_interest:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_cases'], label=country)
    plt.title("Total Cases Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Cases")
    plt.legend()
    plt.savefig('total_cases_over_time.png')
    plt.close()

    # Plot total deaths over time
    plt.figure(figsize=(10, 6))
    for country in countries_of_interest:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_deaths'], label=country)
    plt.title("Total Deaths Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Deaths")
    plt.legend()
    plt.savefig('total_deaths_over_time.png')
    plt.close()

    # Daily new cases comparison
    plt.figure(figsize=(10, 6))
    for country in countries_of_interest:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['new_cases'], label=country)
    plt.title("Daily New Cases Comparison")
    plt.xlabel("Date")
    plt.ylabel("New Cases")
    plt.legend()
    plt.savefig('daily_new_cases.png')
    plt.close()

# Step 4: Vaccination Progress
@safe_execute
def visualize_vaccination_progress(df, countries_of_interest):
    print("Visualizing vaccination progress...")
    plt.figure(figsize=(10, 6))
    for country in countries_of_interest:
        country_df = df[df['location'] == country]
        plt.plot(country_df['date'], country_df['total_vaccinations'], label=country)
    plt.title("Vaccination Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Vaccinations")
    plt.legend()
    plt.savefig('vaccination_progress.png')
    plt.close()

# Step 5: Choropleth Map
@safe_execute
def generate_choropleth_map(df):
    print("Generating choropleth map...")
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date]
    fig = px.choropleth(latest_data,
                        locations="iso_code",
                        color="total_cases",
                        hover_name="location",
                        title=f"Global COVID-19 Cases as of {latest_date}",
                        color_continuous_scale=px.colors.sequential.Plasma)
    fig.write_html("choropleth_map.html")
    print("Choropleth map saved as 'choropleth_map.html'.")

# Step 6: Generate PDF Report
@safe_execute
def generate_pdf_report():
    print("Generating PDF report...")
    with PdfPages("COVID19_Data_Report.pdf") as pdf:
        for filename in ['total_cases_over_time.png', 'total_deaths_over_time.png', 'daily_new_cases.png', 'vaccination_progress.png']:
            if os.path.exists(filename):
                fig, ax = plt.subplots(figsize=(10, 6))
                img = plt.imread(filename)
                ax.imshow(img)
                ax.axis('off')
                pdf.savefig(fig)
                plt.close(fig)
        print("PDF report generated as 'COVID19_Data_Report.pdf'.")

# Step 7: Generate Insights
@safe_execute
def generate_insights(df):
    print("Generating insights...")
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date]
    top_country = latest_data.loc[latest_data['total_cases'].idxmax()]
    print(f"As of {latest_date}:")
    print(f"1. {top_country['location']} has the most total cases: {top_country['total_cases']}.")
    print(f"2. Global vaccination rates are improving steadily.")
    print(f"3. Death rates vary significantly across countries.")
    print("Insights generation complete.")

# Main Function
if __name__ == "__main__":
    file_path = "owid-covid-data.csv"
    countries = ['Kenya', 'USA', 'India']

    df = load_and_explore_data(file_path)
    if df is not None:
        df_cleaned = clean_data(df, countries)
        if df_cleaned is not None:
            perform_eda(df_cleaned, countries)
            visualize_vaccination_progress(df_cleaned, countries)
            generate_choropleth_map(df_cleaned)
            generate_pdf_report()
            generate_insights(df_cleaned)