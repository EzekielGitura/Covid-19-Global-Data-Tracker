# 🌍 COVID-19 Global Data Tracker Dashboard

### 🚀 Project Overview
Welcome to the **COVID-19 Global Data Tracker Dashboard**! This interactive project allows you to explore and visualize global COVID-19 data in a fun and engaging way. Whether you're analyzing vaccination rollouts, observing country-specific trends, or creating choropleth maps of cases worldwide, this dashboard has you covered. 

With just a few clicks, you can dive deep into the pandemic's data, customize your analysis, and generate insights that matter to you.

---

### 🔥 Features
✔️ **Interactive Dashboard:**  
Easily choose countries and date ranges for analysis.  

✔️ **Visualizations Galore:**  
Beautiful line charts, choropleth maps, and more to help you understand trends.  

✔️ **Vaccination & Hospitalization Analysis:**  
Track vaccination progress and, if available, hospitalization and ICU data.  

✔️ **Easy Insights Generation:**  
Generate insights and observations based on the latest data.  

✔️ **PDF Reports & Visuals:**  
Export your visualizations and insights for presentations or research reports.

---

### 🎛️ How It Works
1. Upload the dataset (`owid-covid-data.csv`) directly in the dashboard.
2. Select countries and date ranges to filter the data.
3. View and interact with:
   - Total cases and deaths over time.
   - Vaccination progress.
   - Daily new cases comparison.
   - A choropleth map for global cases.
4. (Optional) Dive into hospitalization and ICU trends.
5. Share your insights with the PDF report feature!  

---

### 🛠️ Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/EzekielGitura/covid19-global-data-tracker.git
   cd covid19-global-data-tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard app:**
   ```bash
   streamlit run covid19_data_analysis_dashboard.py
   ```

4. **Open your browser** and navigate to the Streamlit URL provided (it looks something like `http://localhost:8501`).

---

### 📂 File Structure
```
📦 covid19-global-data-tracker
 ┣ 📜 covid19_data_analysis_dashboard.py
 ┣ 📜 requirements.txt
 ┣ 📜 README.md
 ┗ 📄 owid-covid-data.csv (you need to add this file manually)
```

---

### 💡 Example Use Cases
- **Understand Vaccination Progress:** Want to know how different countries are rolling out vaccines? We've got you covered!  
- **Compare COVID-19 Trends:** Choose countries like the USA, India, and Kenya to see how their cases, deaths, and vaccinations compare.  
- **Global Perspective:** Use the interactive choropleth map to visualize global cases.  

---

### ⚙️ Dependencies
- **pandas**: For data manipulation and cleaning.  
- **matplotlib**: For creating static visualizations.  
- **seaborn**: For enhancing visualization aesthetics.  
- **plotly**: For creating interactive maps and charts.  
- **streamlit**: For building the interactive dashboard.

---

### 🏆 Stretch Goals (Optional Features)
✨ Add user input for specific insights.  
✨ Build an even more detailed dashboard with hospitalization data.  
✨ Include ICU trends for deeper pandemic analysis.  

---

### 🎉 Have Fun Exploring!
COVID-19 data is complex, but this dashboard makes it intuitive, insightful, and interactive. Whether you're a data enthusiast, researcher, or just curious, we hope this project adds value to your exploration.

---

### ⚠️ Disclaimer
This project uses real-world data from "Our World in Data". Data accuracy depends on the dataset provided and might have limitations or discrepancies. Always cross-check data for critical use cases.

---
