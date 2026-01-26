import streamlit as st
import pandas as pd
import numpy as np
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

df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("🎛️ Filter Data")

years = sorted(df["Year"].unique())
countries = sorted(df["Country_clean"].unique())

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
# APPLY FILTER
# =========================
df_filtered = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

if selected_countries:
    df_filtered = df_filtered[df_filtered["Country_clean"].isin(selected_countries)]

# =========================
# KPI METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Jumlah Negara", df_filtered["Country_clean"].nunique())
col2.metric("Total Belanja Militer", f"${df_filtered['Military_Expenditure_USD'].sum():,.0f}")
col3.metric("Rata-rata Growth YoY", f"{df_filtered['Military_Expenditure_YoY'].mean():.2f}%")
col4.metric("Rata-rata Political Stability", f"{df_filtered['Political_Stability_Index'].mean():.2f}")

st.divider()

# =========================
# 1️⃣ LINE — BELANJA MILITER
# =========================
st.subheader("📈 Tren Belanja Militer (USD)")

# 🔑 Ambil tahun terbaru
latest_year = df_filtered["Year"].max()

# 🔑 Hitung nilai belanja terbaru per negara
legend_order = (
    df_filtered[df_filtered["Year"] == latest_year]
    .sort_values("Military_Expenditure_USD", ascending=False)
    ["Country_clean"]
    .tolist()
)

# 🔑 Plot dengan category_orders
fig_exp = px.line(
    df_filtered,
    x="Year",
    y="Military_Expenditure_USD",
    color="Country_clean",
    markers=True,
    labels={"Military_Expenditure_USD": "USD"},
    category_orders={"Country_clean": legend_order}
)

fig_exp.update_layout(
    height=500,
    legend_title_text="Negara (Belanja Terbesar → Terkecil)"
)

st.plotly_chart(fig_exp, use_container_width=True)

st.caption(
    "Urutan legenda merepresentasikan besarnya belanja militer terbaru, sehingga pengguna dapat "
    "langsung mengidentifikasi negara dengan kapasitas pengadaan terbesar. "
    "Pendekatan ini memperkuat analisis potensi pasar avionik dengan menonjolkan aktor utama "
    "tanpa bergantung pada urutan alfabet."
)


# =========================
# URUTKAN LEGEND BERDASARKAN RATA-RATA YoY
# =========================
st.subheader("📈Tren Growth Rate Belanja Militer Negara Asia (YoY)")
legend_order = (
    df_filtered
    .groupby("Country_clean")["Military_Expenditure_YoY"]
    .mean()
    .sort_values(ascending=False)
    .index
    .tolist()
)

fig_yoy = px.line(
    df_filtered,
    x="Year",
    y="Military_Expenditure_YoY",
    color="Country_clean",
    labels={"Military_Expenditure_YoY": "Growth (%)"},
    category_orders={"Country_clean": legend_order}
)

fig_yoy.update_layout(height=500)
st.plotly_chart(fig_yoy, use_container_width=True)

st.caption(
    "Pertumbuhan YoY yang moderat dan konsisten menunjukkan sistem pengadaan yang matang dan dapat diprediksi. "
    "Sebaliknya, fluktuasi ekstrem menandakan ketergantungan pada faktor situasional yang meningkatkan risiko pasar."
)

# =========================
# 🔑 1. Tentukan urutan negara berdasarkan nilai penting
# (rata-rata Military Expenditure)
# =========================
legend_order = (
    df_filtered
    .groupby("Country_clean")["Military_Expenditure_USD"]
    .mean()
    .sort_values(ascending=False)
    .index
    .tolist()
)

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
    log_x=True,
    category_orders={"Country_clean": legend_order},  # 🔥 KUNCI UTAMA
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
        opacity=0.65,
        line=dict(width=0.5, color="black")
    )
)

fig_scatter.update_layout(height=600)
st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "Negara dengan belanja besar dan pertumbuhan stabil merupakan target pasar avionik yang paling strategis. "
    "Sementara pertumbuhan ekstrem pada anggaran kecil cenderung mencerminkan proyek temporer atau kebutuhan reaktif."
)

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

st.caption(
    "Total Score berfungsi sebagai alat screening pasar untuk mengidentifikasi negara dengan kombinasi "
    "kapasitas belanja, stabilitas, dan konsistensi yang relevan bagi strategi masuk pasar avionik."
)

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

st.caption(
    "Heatmap menyoroti konsistensi performa belanja militer antarwaktu. "
    "Negara dengan pola warna stabil lebih menarik bagi produk avionik "
    "karena mencerminkan kesinambungan anggaran dan potensi kontrak berulang."
)

# =========================
# DATA TABLE
# =========================
st.subheader("📋 Data Detail (Filtered)")
st.dataframe(df_filtered, use_container_width=True)


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Avionics Trade Analysis (SIPRI)",
    layout="wide"
)

st.title("Analisis Perdagangan Senjata Avionik Global (SIPRI)")
st.caption("Data-driven insight untuk identifikasi tren, supplier, importir, dan potensi market modernisasi")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df_trade = pd.read_csv(
        "trade-register-edited.csv",
        encoding="latin1",
        sep=None,
        engine="python"
    )

    # Normalisasi kolom
    df_trade.columns = (
        df_trade.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    df_trade.replace(["?", "-", "n/a", "N/A", ""], np.nan, inplace=True)

    numeric_cols = [
        "year_of_order",
        "number_ordered",
        "number_delivered",
        "years_of_delivery",
        "sipri_tiv_per_unit",
        "sipri_tiv_for_total_order",
        "sipri_tiv_of_delivered_weapons"
    ]

    df_trade[numeric_cols] = df_trade[numeric_cols].apply(
        lambda x: pd.to_numeric(x, errors="coerce")
    )

    df_trade["year_of_order"] = df_trade["year_of_order"].round().astype("Int64")

    for col in numeric_cols:
        df_trade.loc[df_trade[col] < 0, col] = np.nan

    df_trade = df_trade.drop_duplicates()

    # Load avionics reference
    df_av_ref = pd.read_csv("avionik_weapon_sipri.csv", sep=";")

    avionics_whitelist = set(
        df_av_ref[df_av_ref["avionik"] == True]["weapon_description"]
        .str.strip()
        .str.lower()
    )

    df_trade["weapon_desc_norm"] = (
        df_trade["weapon_description"]
        .str.strip()
        .str.lower()
    )

    df_av = df_trade[
        df_trade["weapon_desc_norm"].isin(avionics_whitelist)
    ].copy()

    df_av.drop(columns=["weapon_desc_norm"], inplace=True)

    # Cleaning lanjutan
    num_cols = [
        "number_ordered",
        "number_delivered",
        "sipri_tiv_per_unit",
        "sipri_tiv_for_total_order",
        "sipri_tiv_of_delivered_weapons"
    ]

    df_av[num_cols] = df_av[num_cols].fillna(0)

    text_cols = [
        "recipient", "supplier", "weapon_designation",
        "weapon_description", "status"
    ]

    for col in text_cols:
        df_av[col] = (
            df_av[col].fillna("unknown")
            .str.lower()
            .str.strip()
        )

    df_av["comments"] = df_av["comments"].fillna("-")

    df_av["delivery_gap"] = df_av["number_ordered"] - df_av["number_delivered"]
    df_av["delivery_status"] = df_av["delivery_gap"].apply(
        lambda x: "completed" if x == 0 else "partial"
    )

    # Hitung usia alat
    CURRENT_YEAR = 2026
    df_av["weapon_age"] = CURRENT_YEAR - df_av["years_of_delivery"]

    df_av = df_av[
        (df_av["weapon_age"] >= 0) &
        (df_av["weapon_age"] <= 60)
    ]

    return df_av

df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("Filter Data")

year_range = st.sidebar.slider(
    "Tahun Pemesanan",
    int(df["year_of_order"].min()),
    int(df["year_of_order"].max()),
    (
        int(df["year_of_order"].min()),
        int(df["year_of_order"].max())
    )
)

selected_recipient = st.sidebar.multiselect(
    "Negara Penerima",
    sorted(df["recipient"].unique())
)

# Filter utama
filtered_df = df[
    (df["year_of_order"] >= year_range[0]) &
    (df["year_of_order"] <= year_range[1])
]

if selected_recipient:
    filtered_df = filtered_df[
        filtered_df["recipient"].isin(selected_recipient)
    ]

# =========================
# METRICS
# =========================
st.subheader("Ringkasan Utama")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transaksi", f"{filtered_df.shape[0]:,}")
col2.metric("Total Importir", filtered_df["recipient"].nunique())
col3.metric("Total Supplier", filtered_df["supplier"].nunique())
col4.metric("Total SIPRI TIV", f"{filtered_df['sipri_tiv_of_delivered_weapons'].sum():,.0f}")

# =========================
# TREND TRANSAKSI INTERAKTIF
# =========================
st.subheader("Tren Perdagangan Avionik")
yearly_trades = filtered_df.groupby("year_of_order").size().reset_index(name="transactions")
fig = px.line(
    yearly_trades,
    x="year_of_order",
    y="transactions",
    markers=True,
    title="Trend Transaksi Avionik",
    labels={"year_of_order": "Tahun", "transactions": "Jumlah Transaksi"}
)
fig.update_layout(hovermode="x unified", template="plotly_white")
st.plotly_chart(fig, use_container_width=True)
st.caption('''Line chart tren transaksi per tahun menunjukkan volume transaksi avionik global.

Insight:
1. Negara atau periode dengan tren naik menandakan permintaan meningkat → pasar lebih aktif → peluang masuk lebih besar.
2. Tren turun → kemungkinan pasar jenuh atau ada hambatan regulasi.
Strategi: fokus negara dengan pertumbuhan transaksi positif, terutama jika didukung oleh modernisasi angkatan udara.
''')
# =========================
# TREND NILAI SIPRI TIV INTERAKTIF
# =========================
st.subheader("Total Nilai SIPRI TIV Avionik per Tahun")
tiv_yearly = filtered_df.groupby("year_of_order")["sipri_tiv_of_delivered_weapons"].sum().reset_index()
fig = px.line(
    tiv_yearly,
    x="year_of_order",
    y="sipri_tiv_of_delivered_weapons",
    markers=True,
    title="Total Nilai SIPRI TIV Avionik per Tahun",
    labels={"year_of_order": "Tahun", "sipri_tiv_of_delivered_weapons": "Total TIV (USD, konstan)"}
)
fig.update_layout(template="plotly_white", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Total nilai SIPRI TIV avionik per tahun menggambarkan dinamika volume transfer dan akuisisi sistem avionik "
    "di tingkat global/regional. Tren yang meningkat secara konsisten mencerminkan permintaan berkelanjutan "
    "terhadap teknologi avionik, serta peluang pasar yang relevan bagi strategi masuk dan ekspansi produk."
)


# =========================
# TOP IMPORTER & SUPPLIER
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌍 Top Importir Avionik")
    top_importers = (
        filtered_df["recipient"]
        .value_counts()
        .reset_index()
    )
    top_importers.columns = ["recipient", "transactions"]

    fig = px.bar(
        top_importers,
        x="transactions",
        y="recipient",
        orientation="h",
        title="Top Importir Avionik",
        labels={"transactions": "Jumlah Transaksi", "recipient": "Negara"}
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏭 Top Supplier Avionik")
    top_suppliers = (
        filtered_df["supplier"]
        .value_counts()
        .reset_index()
    )
    top_suppliers.columns = ["supplier", "transactions"]

    fig = px.bar(
        top_suppliers,
        x="transactions",
        y="supplier",
        orientation="h",
        title="Top Supplier Avionik",
        labels={"transactions": "Jumlah Transaksi", "supplier": "Supplier"}
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

st.caption('''Bar chart top importir (negara) menunjukkan negara mana yang paling banyak membeli avionik.

Bar chart top supplier menunjukkan kompetitor utama.

Insight:
1. Negara dengan volume pembelian tinggi tapi usia alat rata-rata tinggi → pasar potensial untuk upgrade/retrofit.
2. Supplier dominan → perlu strategi differentiation, misal fitur unik atau harga kompetitif.

Strategi: target negara top importir, tetapi perhatikan peluang jika mereka masih menggunakan sistem lama.
''')

# =========================
# SEMUA JENIS SENJATA AVIONIK
# =========================
st.subheader("💥 Semua Jenis Senjata Avionik")

weapons_all = (
    filtered_df["weapon_description"]
    .value_counts()
    .reset_index()  # ambil semua, jangan dibatasi 10
)
weapons_all.columns = ["weapon_description", "transactions"]

# Plotly bar
fig = px.bar(
    weapons_all,
    x="transactions",
    y="weapon_description",
    orientation="h",
    title="Semua Jenis Senjata Avionik yang Diperdagangkan",
    labels={"transactions": "Jumlah Transaksi", "weapon_description": "Jenis Avionik"}
)
fig.update_layout(yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Distribusi semua jenis senjata avionik menunjukkan struktur permintaan pasar berdasarkan kategori sistem. "
    "Dominasi kategori tertentu mengindikasikan peluang pemasaran yang lebih kuat, "
    "khususnya untuk strategi diferensiasi produk dan fokus portofolio avionik."
)


# =========================
# USIA PER JENIS AVIONIK
# =========================
# Hitung rata-rata usia per jenis avionik
age_by_weapon = (
    filtered_df.groupby("weapon_description")["weapon_age"]
    .mean()
    .sort_values()
    .reset_index()
)

st.subheader("🕒 Jenis Avionik dengan Usia Operasional")

# Plotly bar untuk usia
fig = px.bar(
    age_by_weapon,
    x="weapon_age",
    y="weapon_description",
    orientation="h",
    title="Jenis Avionik dengan Usia Operasional",
    labels={"weapon_age": "Rata-rata Usia (Tahun)", "weapon_description": "Jenis Avionik"}
)
fig.update_layout(yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig, use_container_width=True)
st.caption(
    "Visualisasi jenis avionik berdasarkan usia operasional menunjukkan distribusi siklus hidup sistem yang masih aktif digunakan. "
    "Avionik dengan usia operasional tinggi mengindikasikan potensi kebutuhan upgrade, retrofit, atau penggantian sistem, "
    "yang relevan bagi strategi pemasaran avionik berbasis modernisasi dan sustainment."
)

# =========================
# ORDER VS DELIVERY
# =========================
st.subheader("📦 Konsistensi Order vs Pengiriman")

fig = px.scatter(
    filtered_df,
    x="number_ordered",
    y="number_delivered",
    color="delivery_status",
    hover_data=[
        "recipient",
        "supplier",
        "weapon_description",
        "year_of_order"
    ],
    labels={
        "number_ordered": "Jumlah Dipesan",
        "number_delivered": "Jumlah Dikirim"
    }
)

max_val = filtered_df["number_ordered"].max()
fig.add_shape(
    type="line",
    x0=0, y0=0,
    x1=max_val, y1=max_val,
    line=dict(dash="dash")
)

st.plotly_chart(fig, use_container_width=True)

st.caption('''Scatter plot order vs delivery menunjukkan konsistensi pemenuhan kontrak.

Insight:
1. Negara dengan delivery gap besar → peluang untuk menawarkan solusi lebih andal atau layanan after-sales.
2. Negara dengan delivery = order → pasar stabil, kompetisi tinggi, mungkin butuh diferensiasi.
Strategi: masuk ke pasar yang memiliki gap pengiriman, bisa menekankan keandalan dan layanan cepat.
''')

# =========================
# ANALISIS ORDER VS DELIVERY
# =========================
table_df = filtered_df.copy()

table_df["delivery_gap"] = (
    table_df["number_delivered"] - table_df["number_ordered"]
)

table_df["consistency_flag"] = table_df["delivery_gap"].apply(
    lambda x: "✅ Konsisten"
    if x == 0 else
    ("⚠️ Kurang Kirim" if x < 0 else "📈 Over Delivery")
)

result_table = table_df[[
    "recipient",
    "supplier",
    "weapon_description",
    "year_of_order",
    "number_ordered",
    "number_delivered",
    "delivery_gap",
    "consistency_flag",
    "delivery_status"
]].sort_values("delivery_gap")

st.caption(f"""
🔍 **Ringkasan Cepat**  
• Total transaksi: **{len(result_table)}**  
• Konsisten (Order = Delivery): **{(result_table['delivery_gap'] == 0).sum()}**  
• Kurang kirim: **{(result_table['delivery_gap'] < 0).sum()}**  
• Over delivery: **{(result_table['delivery_gap'] > 0).sum()}**
""")


st.subheader("📊 Tabel Evaluasi Konsistensi Order vs Pengiriman")

st.dataframe(
    result_table,
    use_container_width=True
)


# =========================
# USIA AVIONIK
# =========================
st.subheader("🕰️ Analisis Usia Operasional Avionik")

fig = px.histogram(
    filtered_df,
    x="weapon_age",
    nbins=20,
    marginal="box",
    labels={"weapon_age": "Usia Alat (Tahun)"}
)
st.plotly_chart(fig, use_container_width=True)

st.caption('''Histogram usia alat menunjukkan rata-rata usia sistem avionik di berbagai negara.

Insight:
1. Usia tinggi → kemungkinan ada kebutuhan modernisasi.
2. Usia rendah → pasar modern, tetapi bisa menawarkan upgrade teknologi terbaru.

Strategi: negara dengan usia rata-rata >20 tahun → fokus untuk retrofit & modernisasi.
''')

# =========================
# MODERNIZATION MARKET
# =========================
st.subheader("🚀 Identifikasi Market Modernisasi")

# Hitung rata-rata usia per negara
age_by_country = (
    filtered_df
    .groupby("recipient")["weapon_age"]
    .mean()
    .sort_values()
    .reset_index()
)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        age_by_country.sort_values("weapon_age", ascending=True),
        x="weapon_age",
        y="recipient",
        orientation="h",
        title="Avionik Termuda (Modern Fleet)",
        height=600
    )
    fig1.update_layout(
        yaxis=dict(categoryorder="total descending")
    )
    st.plotly_chart(fig1, use_container_width=True)


with col2:
    fig2 = px.bar(
        age_by_country.sort_values("weapon_age", ascending=False),
        x="weapon_age",
        y="recipient",
        orientation="h",
        title="Avionik Tertua (Upgrade Market)",
        height=600
    )
    fig2.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig2, use_container_width=True)

st.caption('''Bar chart “Avionik tertua / termuda” per negara.

Insight:
1. Negara dengan avionik tertua = peluang pasar modernisasi.
2. Negara dengan avionik termuda = pasar lebih sulit ditembus, tapi bisa menawarkan teknologi canggih.

Strategi:
1. Masuk pasar upgrade/retrofit untuk negara dengan alat lama.
2. Masuk pasar high-end untuk negara dengan armada modern (diferensiasi & fitur premium).
''')



























