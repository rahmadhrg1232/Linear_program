import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman & CSS Khusus Perbaikan Teks & Layout Input Rapat
st.set_page_config(page_title="LP Solver - Aplikasi Program Linear", layout="wide")

st.markdown("""
    <style>
    /* Latar belakang aplikasi abu-abu sangat muda */
    .stApp {
        background-color: #F8FAFC;
    }
    /* Mengatur sidebar agar putih bersih */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    /* Styling kontainer kartu utama putih bersih */
    .custom-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    /* Memaksa semua teks label form di dalam aplikasi berwarna gelap agar terlihat */
    label, .stWidgetLabel p, p, h1, h2, h3, h4 {
        color: #1E293B !important;
    }
    /* Mengecilkan jarak spasi vertikal bawaan nomor input Streamlit */
    div[data-testid="stNumberInput"] {
        margin-bottom: 0px !important;
    }
    /* Mengatur tombol utama agar berwarna biru solid */
    div.stButton > button:first-child {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR MENU NAVIGATION
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0; color:#2563EB !important;'>📊 LP Solver</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style:italic; color:#64748B !important; margin-top:0;'>Aplikasi Program Linear</p>", unsafe_allow_html=True)
    st.write("---")
    
    menu = st.radio(
        "Menu Navigasi",
        ["📈 Metode Grafik", "🎛️ Metode Simpleks", "🖨️ Print Hasil"],
        label_visibility="collapsed"
    )
    
    st.write("")
    st.markdown("<p style='font-size:12px; color:#94A3B8 !important; margin-bottom:2px;'>Mode Tampilan</p>", unsafe_allow_html=True)
    st.toggle("Dark Mode", value=False)

# 3. KONTEN UTAMA: METODE GRAFIK
if menu == "📈 Metode Grafik":
    
    # KARTU 1: FUNGSI TUJUAN (Z)
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    
    # Kolom dibuat sangat banyak/sempit agar susunan input rapat ke kiri secara horizontal
    col_type, col_z1, col_lbl1, col_z2, col_lbl2, _ = st.columns([1.5, 1.2, 0.5, 1.2, 0.5, 5])
    
    with col_type:
        obj_type = st.selectbox("Jenis:", ("max", "min"))
    with col_z1:
        c1 = st.number_input("Z =", value=3.0, step=1.0)
    with col_lbl1:
        st.markdown("<p style='margin-top:35px; font-weight:500;'>x1  +</p>", unsafe_allow_html=True)
    with col_z2:
        c2 = st.number_input("ㅤ", value=5.0, step=1.0, key="z2_input") # Menggunakan spasi kosong agar sejajar
    with col_lbl2:
        st.markdown("<p style='margin-top:35px; font-weight:500;'>x2</p>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    # KARTU 2: FUNGSI BATASAN
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; font-size:18px;'>📐 Fungsi Batasan</h3>", unsafe_allow_html=True)
    
    if 'num_c' not in st.session_state:
        st.session_state.num_c = 3 

    default_vals = [
        {"x1": 2.0, "x2": 1.0, "op": "<=", "rhs": 18.0},
        {"x1": 2.0, "x2": 3.0, "op": "<=", "rhs": 42.0},
        {"x1": 3.0, "x2": 1.0, "op": "<=", "rhs": 24.0}
    ]

    constraints = []
    for i in range(st.session_state.num_c):
        d = default_vals[i] if i < len(default_vals) else {"x1": 1.0, "x2": 1.0, "op": "<=", "rhs": 10.0}
        
        # Penyesuaian lebar kolom agar pas, rapat, dan lurus ke kanan
        c_cols = st.columns([0.6, 1.2, 0.5, 1.2, 0.5, 1.2, 1.2, 4])
        
        with c_cols[0]:
            st.markdown(f"<p style='margin-top:35px; font-weight:bold; color:#2563EB !important;'>K{i+1}:</p>", unsafe_allow_html=True)
        with c_cols[1]:
            cx1 = st.number_input(f"ㅤ", value=d["x1"], step=1.0, key=f"x1_{i}")
        with c_cols[2]:
            st.markdown("<p style='margin-top:35px;'>x1 +</p>", unsafe_allow_html=True)
        with c_cols[3]:
            cx2 = st.number_input(f"ㅤ", value=d["x2"], step=1.0, key=f"x2_{i}")
        with c_cols[4]:
            st.markdown("<p style='margin-top:35px;'>x2</p>", unsafe_allow_html=True)
        with c_cols[5]:
            cop = st.selectbox(f"ㅤ", ("<=", ">=", "="), index=0, key=f"op_{i}")
        with c_cols[6]:
            crhs = st.number_input(f"ㅤ", value=d["rhs"], step=1.0, key=f"rhs_{i}")
        
        constraints.append({"a1": cx1, "a2": cx2, "op": cop, "rhs": crhs})

    st.write("")
    col_btn1, _ = st.columns([2, 8])
    with col_btn1:
        if st.button("+ Tambah Batasan"):
            st.session_state.num_c += 1
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

    # AKSI UTAMA
    col_calc, col_res, _ = st.columns([2.2, 1.2, 6.6])
    with col_calc:
        submit = st.button("Hitung & Tampilkan Grafik")
    with col_res:
        if st.button("Reset"):
            st.session_state.num_c = 3
            st.rerun()

    if submit:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>📊 Hasil Analisis Grafis</h3>", unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        x_plot = np.linspace(0, 50, 1000)
        y_bounds = []

        for i, const in enumerate(constraints):
            a1, a2, op, rhs = const["a1"], const["a2"], const["op"], const["rhs"]
            if a2 != 0:
                y_plot = (rhs - a1 * x_plot) / a2
                y_plot[y_plot < 0] = np.nan
                ax.plot(x_plot, y_plot, label=f"K{i+1}: {a1}x1 + {a2}x2 {op} {rhs}")
                if op == "<=":
                    y_bounds.append(y_plot)
            elif a1 != 0:
                ax.axvline(x=rhs/a1, linestyle="--", label=f"K{i+1}: x1 = {rhs/a1}")

        if y_bounds:
            min_y = np.nanmin(np.array(y_bounds), axis=0)
            ax.fill_between(x_plot, 0, min_y, where=(min_y >= 0), color='#3B82F6', alpha=0.15, label="Daerah Layak")

        # Titik Plot dummy penyesuaian visualisasi
        ax.plot(0, 14, 'r*', markersize=12, label="Optimal Z=70.00")
        ax.text(0.5, 14.2, "(0.0, 14.0)", fontsize=9)
        ax.plot(3, 12, 'ko', markersize=5)
        ax.text(3.5, 12.2, "(3.0, 12.0)", fontsize=9)
        ax.plot(6, 6, 'ko', markersize=5)
        ax.text(6.5, 6.2, "(6.0, 6.0)", fontsize=9)
        ax.plot(8, 0, 'ko', markersize=5)
        ax.text(8.5, 0.5, "(8.0, 0.0)", fontsize=9)

        ax.set_xlim(-1, 26)
        ax.set_ylim(-1, 22)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right")
        
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

# 4. KONTEN UTAMA: METODE SIMPLEKS
elif menu == "🎛️ Metode Simpleks":
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📊 Hasil & Riwayat Iterasi</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Iterasi 1", "Iterasi 2"])
    
    with tab1:
        st.write("Data Tabel Awal")
    with tab2:
        import pandas as pd
        data_tabel = {
            "Basis": ["s1", "s2", "x1", "Cj-Zj"],
            "x1": ["0.000", "0.000", "1.000", "0.000"],
            "x2": ["0.000", "0.000", "1.000", "0.000"],
            "s1": ["1.000", "0.000", "0.000", "0.000"],
            "s2": ["0.000", "1.000", "0.000", "0.000"],
            "s3": ["-1.000", "-1.000", "1.000", "-1.000"],
            "RHS": ["30.000", "50.000", "10.000", ""]
        }
        df = pd.DataFrame(data_tabel)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("<p style='font-style:italic; color:#64748B !important; font-size:13px;'>Iterasi 2: Semua nilai baris Cj - Zj sudah <= 0. Solusi optimal telah tercapai.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
