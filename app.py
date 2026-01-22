import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Asia Military Expenditure Dashboard",
    layout="wide"
)

st.title("🪖 Military Expenditure Dashboard — Asia")
st.caption("SIPRI & World Bank | Constant 2023 USD")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("df_asia_final.csv") 
#python -m streamlit run app.py

df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("🎛️ Filter Data")

years = sorted(df['Year'].unique())
countries = sorted(df['Country_clean'].unique())

year_range = st.sidebar.slider(
    "Rentang Tahun",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

selected_countries = st.sidebar.multiselect(
    "Pilih Negara (kosongkan untuk semua)",
    options=countries,
    default=[]
)

# =========================
# APPLY FILTER (LOGIC FIX)
# =========================
df_filtered = df[
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# Jika user memilih negara → filter
if selected_countries:
    df_filtered = df_filtered[df_filtered['Country_clean'].isin(selected_countries)]

# =========================
# KPI METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Jumlah Negara", df_filtered['Country_clean'].nunique())

col2.metric(
    "Total Belanja Militer",
    f"${df_filtered['Military_Expenditure_USD'].sum():,.0f}"
)

col3.metric(
    "Rata-rata Growth YoY",
    f"{df_filtered['Military_Expenditure_YoY'].mean():.2f}%"
)

col4.metric(
    "Rata-rata Political Stability",
    f"{df_filtered['Political_Stability_Index'].mean():.2f}"
)

st.divider()

# =========================
# 1️⃣ LINE — BELANJA MILITER
# =========================
st.subheader("📈 Tren Belanja Militer (USD)")

fig_exp = px.line(
    df_filtered,
    x="Year",
    y="Military_Expenditure_USD",
    color="Country_clean",
    markers=True,
    labels={"Military_Expenditure_USD": "USD"}
)

fig_exp.update_layout(height=500)
st.plotly_chart(fig_exp, use_container_width=True)

# =========================
# 2️⃣ LINE — YoY GROWTH
# =========================
st.subheader("📊 Growth Rate YoY (%)")

fig_yoy = px.line(
    df_filtered,
    x="Year",
    y="Military_Expenditure_YoY",
    color="Country_clean",
    labels={"Military_Expenditure_YoY": "Growth (%)"}
)

fig_yoy.update_layout(height=500)
st.plotly_chart(fig_yoy, use_container_width=True)

# =========================
# 3️⃣ SCATTER — BUDGET vs GROWTH
# =========================
st.subheader("🫧 Anggaran vs Growth (Log Scale)")

fig_scatter = px.scatter(
    df_filtered,
    x="Military_Expenditure_USD",
    y="Military_Expenditure_YoY",
    size="Military_Expenditure_USD",
    color="Country_clean",
    hover_name="Country_clean",
    log_x=True,   # 🔑 INI KUNCI UTAMA
    labels={
        "Military_Expenditure_USD": "Military Expenditure (USD, log scale)",
        "Military_Expenditure_YoY": "Growth YoY (%)"
    }
)

fig_scatter.update_traces(
    marker=dict(
        sizemode="area",
        sizeref=df_filtered["Military_Expenditure_USD"].max() / 40**2,
        sizemin=6,
        opacity=0.65,        # 🔑 bubble transparan
        line=dict(width=0.5, color="black")
    )
)

fig_scatter.update_layout(height=600)
st.plotly_chart(fig_scatter, use_container_width=True)


# =========================
# 4️⃣ RANKING — TOTAL SCORE
# =========================
st.subheader("🏆 Ranking Negara Asia (Total Score)")

ranking = (
    df_filtered
    .groupby("Country_clean")["Total_Score"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig_rank = px.bar(
    ranking,
    x="Total_Score",
    y="Country_clean",
    orientation="h",
    color="Total_Score",
    color_continuous_scale="Blues"
)

fig_rank.update_layout(
    height=700,
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig_rank, use_container_width=True)

# =========================
# 5️⃣ HEATMAP — SCORE per TAHUN
# =========================
st.subheader("🔥 Heatmap Total Score per Tahun")

heatmap_data = df_filtered.pivot_table(
    index="Country_clean",
    columns="Year",
    values="Total_Score",
    aggfunc="mean"
)

fig_heatmap = px.imshow(
    heatmap_data,
    color_continuous_scale="YlGnBu",
    aspect="auto"
)

fig_heatmap.update_layout(height=700)
st.plotly_chart(fig_heatmap, use_container_width=True)

# =========================
# DATA TABLE
# =========================
st.subheader("📋 Data Detail (Filtered)")
st.dataframe(df_filtered, use_container_width=True)
