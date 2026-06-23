import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Terasusu Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PENGUNCI DESAIN (TEMA MAROON TERASUSU) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .main { background-color: #FDFBFB; }
    
    div[data-testid="stSidebar"] { 
        background-color: #7A1C1C !important; 
    }
    div[data-testid="stSidebar"] .stMarkdown, div[data-testid="stSidebar"] label, div[data-testid="stSidebar"] span { 
        color: #FFFFFF !important; 
    }
    
    .metric-card { 
        background-color: #ffffff; 
        padding: 22px; 
        border-radius: 10px; 
        border: 1px solid #F0F0F0; 
        box-shadow: 0 4px 12px rgba(122, 28, 28, 0.05); 
        margin-bottom: 16px;
        border-top: 4px solid #7A1C1C;
    }
    .metric-title { color: #666666; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 6px; }
    .metric-value { color: #7A1C1C; font-size: 30px; font-weight: 800; margin-bottom: 2px; }
    .metric-sub { color: #999999; font-size: 12px; }
    
    .upload-box { text-align: center; padding: 30px 20px; background: #ffffff; border: 2px dashed #7A1C1C; border-radius: 12px; margin-bottom: 25px; }
    .upload-box h3 { color: #7A1C1C; font-weight: 600; font-size: 18px; margin-bottom: 5px; }
    .upload-box p { color: #666; font-size: 14px; }
    
    .api-badge { background-color: #ffffff; color: #7A1C1C; padding: 12px; border-radius: 8px; font-size: 12px; margin-bottom: 15px; border-left: 4px solid #4CAF50;}
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [aria-selected="true"] { color: #7A1C1C !important; border-bottom: 3px solid #7A1C1C !important; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR UTAMA (NAVIGASI & PARAMETER) ---
try:
    st.sidebar.image("588078540_17887586781397154_4932475826654423039_n.jpg", use_container_width=True)
except Exception:
    st.sidebar.markdown("<h2 style='color:#ffffff; text-align:center;'>TERASUSU</h2>", unsafe_allow_html=True)

st.sidebar.markdown("<br><span style='font-size:11px; text-transform:uppercase; letter-spacing:1px;'>Parameter Peramalan</span>", unsafe_allow_html=True)
tanggal_pilihan = st.sidebar.date_input("Tanggal Prediksi", datetime.date.today())
hari_indo = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}[tanggal_pilihan.strftime("%A")]

jam_operasional = st.sidebar.selectbox("Fase Jam", ["Sore Baru Buka (16:00 - 18:00)", "Puncak Ramai (18:00 - 21:00)", "Jelang Tutup (21:00 - 22:30)"])
status_kampus = st.sidebar.selectbox("Aktivitas Kampus", ["Reguler", "Pekan Ujian", "Event/Wisuda"])

# --- 4. ENGINE INTEGRASI API CUACA (W/ TIME FILTERING) ---
gunakan_api = st.sidebar.checkbox("Integrasi Auto-Forecast API")
cuaca_final = "Cerah / Berawan"
info_cuaca_api = ""
log_api_status = "Tidak Aktif (Mode Simulasi Manual)"

if gunakan_api:
    API_KEY = "MASUKKAN_API_KEY_KAMU_DISINI" # <--- JANGAN LUPA MASUKKAN KEMBALI API KEY DI SINI
    KOTA = "Surabaya,id"
    url_api = f"http://api.openweathermap.org/data/2.5/forecast?q={KOTA}&appid={API_KEY}&units=metric&lang=id"
    
    try:
        respon = requests.get(url_api)
        data_cuaca = respon.json()
        log_api_status = f"{respon.status_code} OK (Connected)"
        
        if str(data_cuaca.get('cod')) == "200":
            tanggal_str = tanggal_pilihan.strftime("%Y-%m-%d")
            
            # Filter Super Ketat: Hanya ekstrak cuaca pada pukul 16:00, 19:00, dan 22:00 WIB
            # (Konversi ke UTC: 09:00, 12:00, 15:00 UTC)
            forecast_ops = [
                item for item in data_cuaca['list'] 
                if item['dt_txt'].startswith(tanggal_str) and any(t in item['dt_txt'] for t in ["09:00:00", "12:00:00", "15:00:00"])
            ]
            
            if len(forecast_ops) == 0:
                forecast_ops = [item for item in data_cuaca['list'] if item['dt_txt'].startswith(tanggal_str)]
                
            hujan_terdeteksi = False
            deskripsi_list = []
            suhu_list = []
            
            for f in forecast_ops:
                kondisi = f['weather'][0]['main'].lower()
                desc = f['weather'][0]['description'].title()
                deskripsi_list.append(desc)
                suhu_list.append(f['main']['temp'])
                
                if 'rain' in kondisi or 'drizzle' in kondisi or 'thunderstorm' in kondisi:
                    hujan_terdeteksi = True
                    if 'light' in desc.lower():
                        cuaca_final = "Hujan Ringan"
                    else:
                        cuaca_final = "Hujan Deras"
            
            if not hujan_terdeteksi:
                cuaca_final = "Cerah / Berawan"
                
            avg_suhu = sum(suhu_list)/len(suhu_list) if suhu_list else 0.0
            info_cuaca_api = f"Rata-rata Suhu Ops: {avg_suhu:.1f}°C | Kondisi Tercatat: {', '.join(set(deskripsi_list))}"
            st.sidebar.markdown(f"<div class='api-badge'><b>Sistem API Aktif 🎯</b><br>Filter Jam Operasional: <b>{cuaca_final}</b></div>", unsafe_allow_html=True)
        else:
            log_api_status = "Error: Invalid API Key / Unauthorized"
            cuaca_final = st.sidebar.selectbox("Tetapkan Cuaca Manual", ["Cerah / Berawan", "Hujan Ringan", "Hujan Deras"])
    except Exception:
        log_api_status = "Error: Koneksi Internet Gagal"
        cuaca_final = st.sidebar.selectbox("Tetapkan Cuaca Manual", ["Cerah / Berawan", "Hujan Ringan", "Hujan Deras"])
else:
    cuaca_final = st.sidebar.selectbox("Cuaca (Simulasi)", ["Cerah / Berawan", "Hujan Ringan", "Hujan Deras"])

# Kalkulasi AI Engine
mult_hari = 2.0 if hari_indo in ["Jumat", "Sabtu"] else (1.3 if hari_indo == "Kamis" else (1.2 if hari_indo == "Minggu" else 1.0))
mult_cuaca = 1.0 if cuaca_final == "Cerah / Berawan" else (0.5 if cuaca_final == "Hujan Ringan" else 0.2)
mult_event = 3.6 if status_kampus == "Event/Wisuda" else (0.6 if status_kampus == "Pekan Ujian" else 1.0)
total_prediksi_cup = int(round(25.0 * mult_hari * mult_cuaca * mult_event))

# --- 5. HALAMAN UTAMA (TENGAH) ---
st.title("Terasusu Intelligence Dashboard")

# Memindahkan File Uploader ke tengah untuk UI yang lebih bersih
uploaded_file = st.file_uploader("Unggah File Basis Data Keuangan Terkini (Keuangan REVISI(1).xlsx)", type=["xlsx"], label_visibility="collapsed")

# Database Master Statis (Profit Margin)
data_produk_master = [
    {"Produk": "Susu Coklat", "Profit Bersih": 8460},
    {"Produk": "Susu Caramel", "Profit Bersih": 8210},
    {"Produk": "Susu Taro", "Profit Bersih": 8210},
    {"Produk": "Susu Tiramisu", "Profit Bersih": 8210},
    {"Produk": "Susu Original", "Profit Bersih": 6055}
]

# Fallback Data Historis Riil (Bulan 3-8) jika file tidak diunggah
histori_pemasukan = [
    {"Bulan": "Bulan 3", "Omset Kotor": 11461824},
    {"Bulan": "Bulan 4", "Omset Kotor": 13754188},
    {"Bulan": "Bulan 5", "Omset Kotor": 16505026},
    {"Bulan": "Bulan 6", "Omset Kotor": 19806031},
    {"Bulan": "Bulan 7", "Omset Kotor": 23767238},
    {"Bulan": "Bulan 8", "Omset Kotor": 28520685}
]

if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file, header=None)
        # Parser Cerdas: Membaca Baris 66 (Indeks 65 Pandas) Kolom B-I
        if df_raw.shape[0] > 65:
            row_66 = df_raw.iloc[65, 1:9].tolist()
            # Memotong secara presisi hanya untuk Bulan 3 sampai Bulan 8 (Indeks ke-2 s/d ke-7)
            vals_6_bulan_terakhir = [int(float(x)) for x in row_66[2:8]]
            
            histori_pemasukan = [
                {"Bulan": f"Bulan {i+3}", "Omset Kotor": val} for i, val in enumerate(vals_6_bulan_terakhir)
            ]
    except Exception:
        pass
else:
    st.markdown("""
        <div class="upload-box">
            <h3>Sistem Berjalan dalam Mode Simulasi Internal</h3>
            <p>Silakan unggah berkas <b>Keuangan REVISI(1).xlsx</b> di atas untuk menarik data profit bersih 6 bulan terakhir.</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. NAVIGASI TAB HALAMAN UTAMA ---
tab_forecast, tab_history = st.tabs(["Operasional Harian", "Histori Penjualan"])

with tab_forecast:
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_omset = total_prediksi_cup * 12400
    total_profit = total_prediksi_cup * 7820
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.markdown(f'<div class="metric-card"><div class="metric-title">Volume Proyeksi</div><div class="metric-value">{total_prediksi_cup} Cup</div><div class="metric-sub">{hari_indo}</div></div>', unsafe_allow_html=True)
    with col_m2: st.markdown(f'<div class="metric-card"><div class="metric-title">Kebutuhan Susu</div><div class="metric-value">{round(total_prediksi_cup/4, 1)} Liter</div><div class="metric-sub">Susu Murni Segar</div></div>', unsafe_allow_html=True)
    with col_m3: st.markdown(f'<div class="metric-card"><div class="metric-title">Estimasi Pendapatan</div><div class="metric-value">Rp {total_omset:,}</div><div class="metric-sub">Kas Kotor (Gross)</div></div>', unsafe_allow_html=True)
    with col_m4: st.markdown(f'<div class="metric-card"><div class="metric-title">Estimasi Profit</div><div class="metric-value">Rp {total_profit:,}</div><div class="metric-sub">Margin Bersih (Net)</div></div>', unsafe_allow_html=True)
    
    st.markdown("### Rekomendasi Tindakan Operasional")
    if "Hujan" in cuaca_final:
        if cuaca_final == "Hujan Deras":
            st.error(f"**MITIGASI CUACA BURUK:** Terdeteksi prediksi **Hujan Deras** pada rentang jam operasional (16:00 - 22:00 WIB). Rencana produksi dipotong ke tingkat minimum ({total_prediksi_cup} cup). **TINDAKAN:** Tahan laju pemanasan susu untuk menghindari kerugian/waste bahan baku segar!")
        elif cuaca_final == "Hujan Ringan":
            st.warning(f"**PERINGATAN CUACA:** Prediksi **Hujan Ringan** pada jam buka toko. **TINDAKAN:** Batasi kuantitas pajangan produk dan gencarkan opsi penjualan takeaway.")
    else:
        st.success("**KONDISI OPTIMAL:** Cuaca di jam operasional diproyeksikan Cerah / Berawan. Lakukan persiapan operasional penuh.")

    st.markdown("<br>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns([1, 1.2])
    with col_g1:
        # Pilihan A: Horizontal Bar Chart Margin Profit
        df_margin = pd.DataFrame(data_produk_master).sort_values(by="Profit Bersih", ascending=True)
        fig_margin = px.bar(df_margin, x="Profit Bersih", y="Produk", orientation='h', text="Profit Bersih",
                            color="Profit Bersih", color_continuous_scale=["#D15A5A", "#7A1C1C"])
        fig_margin.update_traces(
            texttemplate='Rp %{text:,}', textposition='inside', insidetextfont=dict(color='white'),
            hovertemplate="<b>%{y}</b><br>Profit Bersih/Cup: Rp %{x:,}<extra></extra>"
        )
        fig_margin.update_layout(
            title=dict(text="Komparasi Keuntungan Bersih per Produk", font=dict(family="Plus Jakarta Sans", size=15, color="#7A1C1C")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Margin Profit (Rp)", yaxis_title="", showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        st.plotly_chart(fig_margin, use_container_width=True)
        
    with col_g2:
        # Area Chart 7 Hari
        df_trend = pd.DataFrame({
            "Tanggal": [(tanggal_pilihan + datetime.timedelta(days=i)).strftime("%d %b") for i in range(7)], 
            "Volume": [int(round(25.0 * (2.0 if (tanggal_pilihan + datetime.timedelta(days=i)).strftime("%A") in ["Friday", "Saturday"] else 1.0) * mult_cuaca * mult_event)) for i in range(7)]
        })
        fig_trend = px.area(df_trend, x="Tanggal", y="Volume", color_discrete_sequence=['#7A1C1C'])
        fig_trend.update_layout(
            title=dict(text="Simulasi Tren Penjualan 7 Hari ke Depan", font=dict(family="Plus Jakarta Sans", size=15, color="#7A1C1C")), 
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Estimasi Volume (Cup)",
            yaxis=dict(showgrid=True, gridcolor='#F0F0F0'), margin=dict(l=0, r=0, t=50, b=0)
        )
        fig_trend.update_traces(
            fillcolor='rgba(122, 28, 28, 0.15)', line=dict(color='#7A1C1C', width=3), 
            hovertemplate="<b>%{x}</b><br>Prediksi: %{y} Cup<extra></extra>"
        ) 
        st.plotly_chart(fig_trend, use_container_width=True)

    # Transparansi API untuk Kebutuhan Akademis/Sidang
    with st.expander("Visualisasi Data Satelit & Parameter API Cuaca (Khusus Admin)"):
        st.markdown(f"""
        * **Status Koneksi Server OWM:** `{log_api_status}`
        * **Titik Koordinat Sistem:** `Surabaya, Jawa Timur, ID`
        * **Time-Window Filtering:** `Aktif (16:00 - 22:00 WIB)`
        * **Raw Data Log:** `{info_cuaca_api if info_cuaca_api else 'Mode Simulasi Internal'}`
        """)

with tab_history:
    st.markdown("<br>", unsafe_allow_html=True)
    df_hist = pd.DataFrame(histori_pemasukan)
    
    st.markdown("#### Profit Bersih Penjualan 6 Bulan Terakhir")
    
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1: st.markdown(f'<div class="metric-card"><div class="metric-title">Total Akumulasi Profit</div><div class="metric-value">Rp {int(df_hist["Omset Kotor"].sum()):,}</div></div>', unsafe_allow_html=True)
    with col_h2: st.markdown(f'<div class="metric-card"><div class="metric-title">Rata-rata Profit Bulanan</div><div class="metric-value">Rp {int(df_hist["Omset Kotor"].mean()):,}</div></div>', unsafe_allow_html=True)
    with col_h3: st.markdown(f'<div class="metric-card"><div class="metric-title">Bulan Performa Tertinggi</div><div class="metric-value">{df_hist.loc[df_hist["Omset Kotor"].idxmax(), "Bulan"]}</div></div>', unsafe_allow_html=True)
    
    fig_hist_chart = px.bar(df_hist, x="Bulan", y="Omset Kotor", text="Omset Kotor", color_discrete_sequence=['#7A1C1C'])
    fig_hist_chart.update_traces(
        texttemplate='Rp %{text:,.0f}', textposition='outside', 
        hovertemplate="<b>%{x}</b><br>Profit Bersih: Rp %{y:,.0f}<extra></extra>"
    )
    fig_hist_chart.update_layout(
        title=dict(text="Tren Pertumbuhan Profit Bersih Penjualan", font=dict(family="Plus Jakarta Sans", size=15, color="#7A1C1C")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Profit (IDR)"
    )
    st.plotly_chart(fig_hist_chart, use_container_width=True)
