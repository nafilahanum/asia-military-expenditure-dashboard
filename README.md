# asia-military-expenditure-dashboard
Nafila Hanum Al Hasaniy Data Science Student

# 🪖 Asia Military Expenditure Dashboard

Interactive dashboard to analyze military expenditure trends across Asian countries using SIPRI and World Bank data.

## 📌 Features
- Interactive time-series of military expenditure (constant 2023 USD)
- Year-over-Year (YoY) growth analysis
- Budget vs Growth scatter (log scale)
- Country ranking based on composite score
- Heatmap of total score by year
- Dynamic filters (year range & country selection)

## 📊 Data Sources
- SIPRI Military Expenditure Database
- World Bank:
  - GDP (current USD)
  - GDP per capita
  - Political Stability Index

## 🧠 Methodology (Summary)
- Data cleaning & harmonization across sources
- Country name normalization using `pycountry`
- Focused analysis on Asian countries
- Composite score calculation:
  - 40% Military Expenditure
  - 30% YoY Growth
  - 20% Share of Government Spending
  - 10% Political Stability Index
- Min-Max normalization for scoring

## 🚀 Live Demo
👉 *(link will be added after deployment)*

## 🛠️ Tech Stack
- Python
- Streamlit
- Pandas, NumPy
- Plotly
- Scikit-learn

## ▶️ Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
