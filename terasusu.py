import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Terasusu AI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS MASTERPIECE (DARK THEME TRAILER PELUNCURAN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Global App Background */
    .stApp {
        background-color: #0F0909;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(122, 28, 28, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, rgba(209, 90, 90, 0.1) 0%, transparent 50%);
        color: #F0F0F0;
    }
    
    /* Typography Overrides */
    html, body, [class*="css"], .stMarkdown p { font-family: 'Outfit', sans-serif !important; color: #F0F0F0; }
    h1, h2, h3, h4, h5, h6, span, div { font-family: 'Outfit', sans-serif; }
    
    /* Sidebar */
    div[data-testid="stSidebar"] { 
        background-color: rgba(15, 9, 9, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-3px); border-color: rgba(209, 90, 90, 0.5); }
    
    /* Current Weather Big Card */
    .weather-main { text-align: left; padding: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.2) 100%); }
    .wm-temp { font-size: 84px; font-weight: 800; line-height: 1; margin-bottom: 5px; background: -webkit-linear-gradient(#fff, #999); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .wm-desc { font-size: 22px; font-weight: 600; color: #fff; margin-bottom: 5px; text-transform: capitalize;}
    .wm-feels { font-size: 15px; color: #aaa; margin-bottom: 25px;}
    
    .wm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .wm-item { background: rgba(0,0,0,0.3); padding: 12px; border-radius: 16px; text-align: center; border: 1px solid rgba(255,255,255,0.02);}
    .wm-i-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;}
    .wm-i-val { font-size: 15px; font-weight: 700; color: #ddd; margin-top: 4px;}
    
    /* Hourly Weather Row */
    .weather-row { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 10px; }
    .weather-row::-webkit-scrollbar { height: 6px; }
    .weather-row::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
    
    .wh-card {
        flex: 0 0 auto; min-width: 85px;
        background: rgba(0,0,0,0.3);
        border-radius: 18px; padding: 15px 10px; text-align: center;
        border: 1px solid rgba(255,255,255,0.02);
    }
    .wh-time { font-size: 13px; color: #aaa; font-weight: 600; margin-bottom: 8px;}
    .wh-icon { font-size: 28px; margin-bottom: 8px;}
    .wh-temp { font-size: 18px; font-weight: 700; color: #fff;}
    .wh-desc { font-size: 11px; color: #888; text-transform: capitalize; margin-top: 4px;}
    
    /* Metrics */
    .metric-title { color: #aaa; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 8px; }
    .metric-value { color: #fff; font-size: 34px; font-weight: 800; margin-bottom: 4px; line-height: 1.1; }
    .metric-value.highlight { color: #D15A5A; }
    .metric-sub { color: #777; font-size: 13px; font-weight: 500; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid rgba(255,255,255,0.1); gap: 30px;}
    .stTabs [data-baseweb="tab"] { padding-top: 15px; padding-bottom: 15px; }
    .stTabs [aria-selected="true"] { color: #D15A5A !important; border-bottom: 3px solid #D15A5A !important; font-weight: 700 !important; background: transparent !important; }
    
    /* Empty State */
    .empty-state { text-align: center; padding: 80px 20px; background: rgba(255,255,255,0.02); border: 2px dashed rgba(255,255,255,0.15); border-radius: 20px; margin: 20px 0;}
    .empty-state h3 { color: #D15A5A; font-weight: 800; font-size: 28px; margin-bottom: 10px; }
    .empty-state p { color: #aaa; font-size: 16px; max-width: 600px; margin: 0 auto; line-height: 1.6; }
    
    /* Hero Section */
    .hero { padding: 10px 0 20px 0; display: flex; flex-direction: column; justify-content: center; height: 100%;}
    .hero-title { font-size: 46px; font-weight: 800; color: #fff; margin-bottom: 5px; letter-spacing: -1px;}
    .hero-title span { color: #D15A5A; }
    .hero-subtitle { font-size: 18px; color: #aaa; font-weight: 400;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CACHED API FETCH ---
@st.cache_data(ttl=3600)
def get_weather_forecast(api_key, kota):
    url_api = f"http://api.openweathermap.org/data/2.5/forecast?q={kota}&appid={api_key}&units=metric&lang=id"
    try:
        respon = requests.get(url_api, timeout=10)
        return respon.status_code, respon.json()
    except Exception:
        return 500, {}

def get_weather_icon(condition):
    cond = condition.lower()
    if "rain" in cond or "drizzle" in cond: return "🌧️"
    if "thunderstorm" in cond: return "⛈️"
    if "cloud" in cond: return "☁️"
    if "clear" in cond: return "☀️"
    return "🌤️"

# --- 4. HERO SECTION (LOGO & GREETING) ---
col_hero1, col_hero2 = st.columns([5, 1])
with col_hero1:
    st.markdown("""
    <div class="hero">
        <div class="hero-title">Halo, Tim <span>Terasusu!</span> 👋</div>
        <div class="hero-subtitle">Sistem pintar AI buat bantu atur target produksi harian & analisa cuan penjualanmu.</div>
    </div>
    """, unsafe_allow_html=True)
with col_hero2:
    try:
        st.image("588078540_17887586781397154_4932475826654423039_n.jpg", use_container_width=True)
    except:
        pass

# --- 5. GLOBAL LOCK: WAJIB UPLOAD EXCEL ---
st.markdown("<br>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Mulai dengan unggah file Excel 'Keuangan REVISI(1).xlsx' kesini ya...", type=["xlsx"])

df_hist = None
if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file, header=None)
        if df_raw.shape[0] > 65:
            row_66 = df_raw.iloc[65, 1:9].tolist()
            vals_6_bulan_terakhir = [int(float(x)) for x in row_66[2:8]]
            df_hist = pd.DataFrame([
                {"Bulan": f"Bulan {i+3}", "Profit Bersih": val} for i, val in enumerate(vals_6_bulan_terakhir)
            ])
    except Exception as e:
        st.error(f"Waduh, gagal memproses Excel-nya nih. Coba cek lagi formatnya ya! Error: {e}")

# Jika Excel belum ada, JANGAN tampilkan apapun selain layar terkunci
if df_hist is None:
    st.markdown("""
    <div class="empty-state">
        <h3 style="font-family:'Outfit'">🔐 Sistem Menunggu Data...</h3>
        <p style="font-family:'Outfit'">Sistem analitik cerdas kita belum bisa menyala. Yuk, <b>upload dulu file Excel laporan keuangannya</b> di atas supaya AI bisa mulai menghitung ramalan operasional, membaca cuaca, dan membongkar tren profit penjualanmu!</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- 6. SIDEBAR (HANYA MUNCUL JIKA SUDAH UNLOCK) ---
    st.sidebar.markdown("<h2 style='color:#fff; text-align:center; font-weight:800; letter-spacing: 1px; margin-bottom: 30px;'>TERASUSU.</h2>", unsafe_allow_html=True)

    st.sidebar.markdown("<span style='font-size:12px; color:#aaa; text-transform:uppercase; letter-spacing:1px; font-weight:600;'>KONTROL OPERASIONAL</span>", unsafe_allow_html=True)
    tanggal_pilihan = st.sidebar.date_input("Pilih Tanggal Prediksi", datetime.date.today())
    hari_indo = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu", "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"}[tanggal_pilihan.strftime("%A")]

    jam_operasional = st.sidebar.selectbox("Fokus Jualan Jam Berapa Nih?", ["Sore Santai (16:00 - 18:00)", "Puncak Rame (18:00 - 21:00)", "Jelang Tutup (21:00 - 22:30)"])
    status_kampus = st.sidebar.selectbox("Kondisi Kampus Besok?", ["Reguler (Biasa aja)", "Pekan Ujian (Sepi)", "Event/Wisuda (Rame Parah)"])

    st.sidebar.markdown("<br><span style='font-size:12px; color:#aaa; text-transform:uppercase; letter-spacing:1px; font-weight:600;'>INTEGRASI SISTEM</span>", unsafe_allow_html=True)
    gunakan_api = st.sidebar.toggle("Nyalakan AI Cuaca Satelit", value=True)

    cuaca_final = "Cerah / Berawan"
    log_api_status = "Mode Manual"
    hourly_forecast_data = []
    current_weather = None

    if gunakan_api:
        API_KEY = "12bcf3cddf876b0c4e9eb6251bd91f72" 
        KOTA = "Surabaya,id"
        
        status_code, data_cuaca = get_weather_forecast(API_KEY, KOTA)
        
        if status_code == 200 and str(data_cuaca.get('cod')) == "200":
            log_api_status = f"{status_code} OK (Tersambung)"
            tanggal_str = tanggal_pilihan.strftime("%Y-%m-%d")
            
            current_weather = data_cuaca['list'][0] # Cuaca real-time saat ini
            
            # Perbaikan Logika Cuaca Per Jam: Ambil 8 data (24 jam) berturut-turut agar widget selalu penuh
            future_forecasts = [item for item in data_cuaca['list'] if item['dt_txt'] >= f"{tanggal_str} 00:00:00"]
            forecast_widget_data = future_forecasts[:8] if future_forecasts else data_cuaca['list'][:8]
            
            for f in forecast_widget_data:
                utc_time = datetime.datetime.strptime(f['dt_txt'], "%Y-%m-%d %H:%M:%S")
                wib_time = utc_time + datetime.timedelta(hours=7)
                hourly_forecast_data.append({
                    "waktu": wib_time.strftime("%H:%M"),
                    "suhu": f['main']['temp'],
                    "kondisi": f['weather'][0]['main'],
                    "deskripsi": f['weather'][0]['description']
                })
                
            # Evaluasi Keputusan AI berdasarkan jam ops Terasusu (16, 19, 22 WIB)
            forecast_ops = [
                item for item in data_cuaca['list'] if item['dt_txt'].startswith(tanggal_str) and 
                any(t in item['dt_txt'] for t in ["09:00:00", "12:00:00", "15:00:00"])
            ]
            if len(forecast_ops) == 0:
                forecast_ops = future_forecasts[:3] if future_forecasts else data_cuaca['list'][:3]
                
            hujan_terdeteksi = False
            for f in forecast_ops:
                kondisi = f['weather'][0]['main'].lower()
                desc = f['weather'][0]['description'].lower()
                if 'rain' in kondisi or 'drizzle' in kondisi or 'thunderstorm' in kondisi:
                    hujan_terdeteksi = True
                    if 'light' in desc: cuaca_final = "Hujan Ringan"
                    else: cuaca_final = "Hujan Deras"
            
            if not hujan_terdeteksi: cuaca_final = "Cerah / Berawan"
        else:
            log_api_status = f"Error: Gagal ({status_code})"
            cuaca_final = st.sidebar.selectbox("Set Manual Cuaca", ["Cerah / Berawan", "Hujan Ringan", "Hujan Deras"])
    else:
        cuaca_final = st.sidebar.selectbox("Simulasi Cuaca", ["Cerah / Berawan", "Hujan Ringan", "Hujan Deras"])

    # Kalkulasi AI Engine
    mult_hari = 2.0 if hari_indo in ["Jumat", "Sabtu"] else (1.3 if hari_indo == "Kamis" else (1.2 if hari_indo == "Minggu" else 1.0))
    mult_cuaca = 1.0 if cuaca_final == "Cerah / Berawan" else (0.5 if cuaca_final == "Hujan Ringan" else 0.2)
    mult_event = 3.6 if "Wisuda" in status_kampus else (0.6 if "Ujian" in status_kampus else 1.0)
    total_prediksi_cup = int(round(25.0 * mult_hari * mult_cuaca * mult_event))

    # --- 7. TABS DASHBOARD ---
    tab_forecast, tab_history = st.tabs(["⚡ AI Operasional Harian", "📊 AI Analisis Keuangan"])

    with tab_forecast:
        
        # MASTERPIECE WEATHER WIDGET
        if current_weather and hourly_forecast_data:
            c_temp = current_weather['main']['temp']
            c_feels = current_weather['main']['feels_like']
            c_desc = current_weather['weather'][0]['description']
            c_wind = current_weather['wind']['speed']
            c_hum = current_weather['main']['humidity']
            c_pres = current_weather['main']['pressure']
            c_vis = current_weather.get('visibility', 10000) / 1000
            c_icon = get_weather_icon(current_weather['weather'][0]['main'])
            
            cw1, cw2 = st.columns([1, 2])
            
            with cw1:
                left_html = f"""
                <div class="glass-card weather-main">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div class="wm-temp">{c_temp:.0f}&deg;</div>
                            <div class="wm-desc">{c_desc}</div>
                            <div class="wm-feels">Feels like {c_feels:.0f}&deg;</div>
                        </div>
                        <div style="font-size: 64px; line-height:1; filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.5));">{c_icon}</div>
                    </div>
                    <div class="wm-grid">
                        <div class="wm-item"><div class="wm-i-title">💨 Angin</div><div class="wm-i-val">{c_wind} m/s</div></div>
                        <div class="wm-item"><div class="wm-i-title">💧 Lembap</div><div class="wm-i-val">{c_hum}%</div></div>
                        <div class="wm-item"><div class="wm-i-title">⏱️ Tekanan</div><div class="wm-i-val">{c_pres} hPa</div></div>
                        <div class="wm-item"><div class="wm-i-title">👁️ Jarak Pandang</div><div class="wm-i-val">{c_vis:.1f} km</div></div>
                    </div>
                </div>
                """
                st.markdown(left_html, unsafe_allow_html=True)
                
            with cw2:
                st.markdown('<div class="glass-card" style="padding: 20px 24px; height: 350px;">', unsafe_allow_html=True)
                st.markdown('<h4 style="margin-top:0; color:#eee; font-weight:700;">Prakiraan 24 Jam Kedepan</h4>', unsafe_allow_html=True)
                
                df_hour = pd.DataFrame(hourly_forecast_data)
                fig_hour = px.line(df_hour, x="waktu", y="suhu", markers=True)
                fig_hour.update_traces(line=dict(color='#D15A5A', width=3, shape='spline'), marker=dict(size=8, color='#0F0909', line=dict(color='#D15A5A', width=2)))
                fig_hour.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=False, visible=False),
                    margin=dict(l=0, r=0, t=10, b=0), height=130, hovermode="x unified"
                )
                st.plotly_chart(fig_hour, use_container_width=True, config={'displayModeBar': False})
                
                w_cards = '<div class="weather-row">'
                for w in hourly_forecast_data:
                    w_cards += f'<div class="wh-card"><div class="wh-time">{w["waktu"]}</div><div class="wh-icon">{get_weather_icon(w["kondisi"])}</div><div class="wh-temp">{w["suhu"]:.0f}&deg;</div><div class="wh-desc">{w["deskripsi"]}</div></div>'
                w_cards += '</div>'
                st.markdown(w_cards, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Rekomendasi Box
        if "Hujan" in cuaca_final:
            if cuaca_final == "Hujan Deras":
                st.error(f"🚨 **MITIGASI CUACA BURUK:** Waduh, terdeteksi prediksi **Hujan Deras** nih. Rencana produksi dipotong aja ke **{total_prediksi_cup} cup**. **TINDAKAN:** Tahan dulu manasin susu segarnya, jangan sampai sisa banyak!", icon="⚠️")
            elif cuaca_final == "Hujan Ringan":
                st.warning(f"⚠️ **PERINGATAN CUACA:** Bakal ada **Hujan Ringan**. **TINDAKAN:** Jangan pajang terlalu banyak, fokus tawarin promo *takeaway* atau bungkus aja.", icon="🌦️")
        else:
            st.success("✨ **KONDISI OPTIMAL:** Asik! Cuacanya Cerah / Berawan. Ayo siapkan operasional penuh dan maksimalkan penjualan hari ini!", icon="✅")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrik Utama
        total_omset = total_prediksi_cup * 12400
        total_profit = total_prediksi_cup * 7820
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="glass-card"><div class="metric-title">Target Penjualan</div><div class="metric-value highlight">{total_prediksi_cup} <span style="font-size:16px;">Cup</span></div><div class="metric-sub">{hari_indo}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><div class="metric-title">Susu yang Dibutuhkan</div><div class="metric-value">{round(total_prediksi_cup/4, 1)} <span style="font-size:16px;">Liter</span></div><div class="metric-sub">Bahan Murni Segar</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="metric-title">Estimasi Omset</div><div class="metric-value" style="font-size:26px;">Rp {total_omset:,}</div><div class="metric-sub">Kas Kasar (Gross)</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="glass-card"><div class="metric-title">Prediksi Keuntungan</div><div class="metric-value highlight" style="font-size:26px;">Rp {total_profit:,}</div><div class="metric-sub">Margin Bersih (Net)</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns([1, 1.2])
        
        with col_g1:
            data_produk_master = [
                {"Produk": "Susu Coklat", "Profit Bersih": 8460},
                {"Produk": "Susu Caramel", "Profit Bersih": 8210},
                {"Produk": "Susu Taro", "Profit Bersih": 8210},
                {"Produk": "Susu Tiramisu", "Profit Bersih": 8210},
                {"Produk": "Susu Original", "Profit Bersih": 6055}
            ]
            df_margin = pd.DataFrame(data_produk_master).sort_values(by="Profit Bersih", ascending=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_margin = px.bar(df_margin, x="Profit Bersih", y="Produk", orientation='h', text="Profit Bersih")
            
            fig_margin.update_traces(
                texttemplate='Rp %{text:,}', textposition='inside', 
                insidetextfont=dict(color='#ffffff', family='Outfit', size=14, weight='bold'),
                marker_color='#D15A5A', marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Profit Bersih: Rp %{x:,}<extra></extra>"
            )
            fig_margin.update_layout(
                title=dict(text="Cuan Tertinggi per Produk (Margin)", font=dict(family="Outfit", size=18, color="#fff")),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="", yaxis_title="", showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(tickfont=dict(color="#ddd", size=14)),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(fig_margin, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_g2:
            df_trend = pd.DataFrame({
                "Tanggal": [(tanggal_pilihan + datetime.timedelta(days=i)).strftime("%d %b") for i in range(7)], 
                "Volume": [int(round(25.0 * (2.0 if (tanggal_pilihan + datetime.timedelta(days=i)).strftime("%A") in ["Friday", "Saturday"] else 1.0) * mult_cuaca * mult_event)) for i in range(7)]
            })
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            fig_trend = px.area(df_trend, x="Tanggal", y="Volume")
            fig_trend.update_layout(
                title=dict(text="Simulasi Tren Jualan 7 Hari ke Depan", font=dict(family="Outfit", size=18, color="#fff")), 
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Estimasi Volume (Cup)",
                xaxis=dict(tickfont=dict(color="#ddd")),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color="#ddd")), 
                margin=dict(l=0, r=0, t=50, b=0)
            )
            fig_trend.update_traces(
                fillcolor='rgba(209, 90, 90, 0.15)', line=dict(color='#D15A5A', width=3, shape='spline'), 
                hovertemplate="<b>%{x}</b><br>Prediksi: %{y} Cup<extra></extra>"
            ) 
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_history:
        st.markdown("<br><h3 style='font-size:22px; font-weight:700; color:#fff;'>Ringkasan Performa Bersih 6 Bulan Terakhir</h3>", unsafe_allow_html=True)
        
        total_profit_akumulasi = df_hist["Profit Bersih"].sum()
        rata_rata_profit = df_hist["Profit Bersih"].mean()
        bulan_tertinggi = df_hist.loc[df_hist["Profit Bersih"].idxmax(), "Bulan"]
        
        last_month = df_hist.iloc[-1]["Profit Bersih"]
        prev_month = df_hist.iloc[-2]["Profit Bersih"]
        mom_nom = last_month - prev_month
        mom_pct = (mom_nom / prev_month) * 100 if prev_month != 0 else 0
        
        box_color = "rgba(76, 175, 80, 0.15)" if mom_nom >= 0 else "rgba(244, 67, 54, 0.15)"
        border_color = "#4CAF50" if mom_nom >= 0 else "#F44336"
        text_color = "#4CAF50" if mom_nom >= 0 else "#F44336"
        icon = "🚀" if mom_nom >= 0 else "📉"
        
        st.markdown(f'''
        <div style="background-color: {box_color}; padding: 20px 24px; border-left: 6px solid {border_color}; border-radius: 16px; margin-bottom: 25px; display:flex; align-items:center; gap: 20px; backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.05); border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size:38px; filter: drop-shadow(0px 2px 5px rgba(0,0,0,0.5));">{icon}</div>
            <div>
                <div style="color: {text_color}; font-weight: 800; font-size: 16px; margin-bottom: 4px; letter-spacing: 0.5px;">PERTUMBUHAN MARGIN (MoM)</div>
                <div style="color: #ddd; font-size: 15px; font-weight:400;">Bulan ini naik sebesar <b style="color: {text_color}; font-size:18px;">{mom_pct:+.1f}%</b> (Rp {mom_nom:+,.0f}) dibanding bulan lalu.</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1: st.markdown(f'<div class="glass-card" style="border-top: 4px solid #D15A5A;"><div class="metric-title">Total Cuan Terkumpul</div><div class="metric-value">Rp {int(total_profit_akumulasi):,}</div></div>', unsafe_allow_html=True)
        with col_h2: st.markdown(f'<div class="glass-card" style="border-top: 4px solid #D15A5A;"><div class="metric-title">Rata-rata Cuan Bulanan</div><div class="metric-value">Rp {int(rata_rata_profit):,}</div></div>', unsafe_allow_html=True)
        with col_h3: st.markdown(f'<div class="glass-card" style="border-top: 4px solid #D15A5A;"><div class="metric-title">Bulan Paling Ramai</div><div class="metric-value" style="color:#D15A5A;">{bulan_tertinggi}</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_hist_chart = px.bar(df_hist, x="Bulan", y="Profit Bersih")
        
        colors = ['rgba(209, 90, 90, 0.3)'] * len(df_hist)
        max_idx = df_hist['Profit Bersih'].idxmax()
        colors[max_idx] = '#D15A5A'
        
        fig_hist_chart.update_traces(
            texttemplate='Rp %{y:,.0f}', textposition='outside', 
            textfont=dict(family="Outfit", size=14, color="#F0F0F0", weight="bold"),
            marker_color=colors, marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Profit Bersih: Rp %{y:,.0f}<extra></extra>"
        )
        fig_hist_chart.update_layout(
            title=dict(text="Tren Pertumbuhan Profit Bersih", font=dict(family="Outfit", size=18, color="#fff")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", yaxis_title="Profit (IDR)",
            xaxis=dict(tickfont=dict(color="#ddd")),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[0, df_hist['Profit Bersih'].max() * 1.3], tickfont=dict(color="#ddd")),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        st.plotly_chart(fig_hist_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
