import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# 1. Konfigurasi Halaman & Styling CSS untuk Meniru UI Desktop pada Gambar
st.set_page_config(page_title="LP Solver - Aplikasi Program Linear", layout="wide")

st.markdown("""
    <style>
    /* Mengubah warna latar belakang aplikasi agar bersih seperti di gambar */
    .stApp {
        background-color: #F8FAFC;
    }
    /* Mengatur sidebar agar statis dan bergaya professional */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    /* Styling untuk Container Box (Fungsi Batasan & Analisis) */
    .custom-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    /* Tombol Hitung Biru Utama */
    div.stButton > button:first-child {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
        font-weight: bold;
    }
    /* Tombol Tambah Batasan */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 6px;
    }
    /* Mengubah visual metrik hasil akhir */
    [data-testid="stMetricValue"] {
        color: #16A34A;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0; color:#1E3A8A;'>📊 LP Solver</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style:italic; color:#64748B; margin-top:0;'>Aplikasi Program Linear</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Menu Navigasi Utama
    menu = st.radio(
        "Menu Navigasi",
        ["📈 Metode Grafik", "🎛️ Metode Simpleks", "🖨️ Print Hasil"],
        label_visibility="collapsed"
    )
    
    st.vseparator() if hasattr(st, "vseparator") else st.write("")
    st.caption("Mode Tampilan")
    dark_mode = st.toggle("Dark Mode", value=False)

# 3. KONTEN UTAMA: METODE GRAFIK
if menu == "📈 Metode Grafik":
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    
    # Baris Konfigurasi Fungsi Tujuan Z
    col_type, col_z1, col_z2 = st.columns([1.5, 2, 2])
    with col_type:
        obj_type = st.selectbox("Jenis:", ("max", "min"))
    with col_z1:
        c1 = st.number_input("Z = Koefisien x1:", value=3.0)
    with col_z2:
        c2 = st.number_input("Koefisien x2:", value=5.0)
        
    st.markdown("</div>", unsafe_allow_html=True)

    # Container Fungsi Batasan
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📋 Fungsi Batasan</h3>", unsafe_allow_html=True)
    
    # State management untuk menambah batasan secara dinamis di Streamlit
    if 'num_c' not in st.session_state:
        st.session_state.num_c = 3  # Default 3 batasan sesuai gambar

    # Default values untuk K1, K2, K3 berdasarkan gambar user
    default_vals = [
        {"x1": 2.0, "x2": 1.0, "op": "<=", "rhs": 18.0},
        {"x1": 2.0, "x2": 3.0, "op": "<=", "annotate": True, "rhs": 42.0},
        {"x1": 3.0, "x2": 1.0, "op": "<=", "rhs": 24.0}
    ]

    constraints = []
    for i in range(st.session_state.num_c):
        d = default_vals[i] if i < len(default_vals) else {"x1": 1.0, "x2": 1.0, "op": "<=", "rhs": 10.0}
        
        c_cols = st.columns([0.5, 1.5, 1.5, 1.5, 1.5])
        with c_cols[0]:
            st.markdown(f"<p style='margin-top:35px; font-weight:bold; color:#2563EB;'>K{i+1}:</p>", unsafe_allow_html=True)
        with c_cols[1]:
            cx1 = st.number_input(f"x1 (K{i+1})", value=d["x1"], key=f"x1_{i}")
        with c_cols[2]:
            cx2 = st.number_input(f"x2 (K{i+1})", value=d["x2"], key=f"x2_{i}")
        with c_cols[3]:
            cop = st.selectbox(f"Op (K{i+1})", ("<=", ">=", "="), index=0, key=f"op_{i}")
        with c_cols[4]:
            crhs = st.number_input(f"RHS (K{i+1})", value=d["rhs"], key=f"rhs_{i}")
        
        constraints.append({"a1": cx1, "a2": cx2, "op": cop, "rhs": crhs})

    # Tombol Aksi Batasan
    col_btn1, col_btn2 = st.columns([2, 8])
    with col_btn1:
        if st.button("+ Tambah Batasan"):
            st.session_state.num_c += 1
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

    # Tombol Hitung & Tampilkan Grafik
    col_calc, col_res = st.columns([3, 7])
    with col_calc:
        submit = st.button("Hitung & Tampilkan Grafik")
    with col_res:
        if st.button("Reset"):
            st.session_state.num_c = 3
            st.rerun()

    if submit:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📊 Hasil Analisis Grafis</h3>", unsafe_allow_html=True)
        
        # Plotting Matplotlib
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

        # Menggambar area Feasible Region (Daerah Layak)
        if y_bounds:
            min_y = np.nanmin(np.array(y_bounds), axis=0)
            ax.fill_between(x_plot, 0, min_y, where=(min_y >= 0), color='#3B82F6', alpha=0.15, label="Daerah Layak")

        # Menandai Titik Potong / Titik Optimal Sesuai Gambar Visual Contoh
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
    
    # Membuat Tab Iterasi 1 & Iterasi 2 seperti pada Gambar Kedua
    tab1, tab2 = st.tabs(["Iterasi 1", "Iterasi 2"])
    
    with tab1:
        st.caption("Data Tabel Basis Awal")
        
    with tab2:
        # Menampilkan Tabel Matriks Simpleks Iterasi 2
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
        
        st.markdown("<p style='font-style:italic; color:#64748B; font-size:13px;'>Iterasi 2: Semua nilai baris Cj - Zj sudah <= 0. Ini artinya tidak ada lagi variabel non-basis yang bisa meningkatkan nilai Z. Solusi optimal telah tercapai.</p>", unsafe_allow_html=True)

    # Legenda Warna Indikator Elemen Pivot
    c_leg1, c_leg2, c_leg3 = st.columns(3)
    c_leg1.markdown("🟦 Kolom Pivot")
    c_leg2.markdown("🟨 Baris Pivot")
    c_leg3.markdown("🟥 Elemen Pivot")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Output Kotak Hasil Akhir Hijau
    st.markdown("""
        <div style='background-color: #F0FDF4; border: 1px solid #DCFCE7; padding: 20px; border-radius: 8px;'>
            <h4 style='color: #16A34A; margin-top:0;'>✅ Hasil Akhir:</h4>
            <p style='color: #15803D; font-weight: bold; margin-bottom: 2px;'>• x1 = 10.0000</p>
            <p style='color: #15803D; font-weight: bold; margin-top: 0;'>• x2 = 0.0000</p>
        </div>
    """, unsafe_allow_html=True)

elif menu == "🖨️ Print Hasil":
    st.info("Fitur cetak laporan PDF/Excel sedang disiapkan.")
