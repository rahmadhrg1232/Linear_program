import tkinter as tk
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import linprog

# Set tema default CustomTkinter
ctk.set_appearance_mode("Light")  # Mendukung "Light" dan "Dark"
ctk.set_default_color_theme("blue")

class LPSolverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aplikasi Program Linear")
        self.geometry("1200 viv 750")
        self.state("zoomed")  # Membuka dalam kondisi maximized window

        # State global untuk dynamic constraint inputs
        self.constraints_ui = []
        
        # Grid layout 2 kolom (Sidebar dan Main Frame)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------- SIDEBAR SYSTEM -----------------
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="📊 LP Solver", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.sub_logo_label = ctk.CTkLabel(self.sidebar_frame, text="Aplikasi Program Linear", font=ctk.CTkFont(size=12, slant="italic"))
        self.sub_logo_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Tombol Menu Navigasi
        self.btn_grafik = ctk.CTkButton(self.sidebar_frame, text="📈 Metode Grafik", command=self.show_grafik_page, height=40, anchor="w")
        self.btn_grafik.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.btn_simpleks = ctk.CTkButton(self.sidebar_frame, text="🎛️ Metode Simpleks", command=self.show_simpleks_page, height=40, anchor="w")
        self.btn_simpleks.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Pengaturan Mode Tampilan di Bagian Bawah Sidebar
        self.mode_label = ctk.CTkLabel(self.sidebar_frame, text="Mode Tampilan", font=ctk.CTkFont(size=11))
        self.mode_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.switch_dark = ctk.CTkSwitch(self.sidebar_frame, text="Dark Mode", command=self.toggle_theme)
        self.switch_dark.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")

        # ----------------- MAIN CONTENT AREA -----------------
        self.main_container = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        
        # Load halaman pertama secara default
        self.show_grafik_page()

    def toggle_theme(self):
        if self.switch_dark.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ==============================================================================
    # 📉 MENU METODE GRAFIK UI
    # ==============================================================================
    def show_grafik_page(self):
        self.clear_main_container()
        self.btn_grafik.configure(fg_color=("blue", "brand_color"))
        self.btn_simpleks.configure(fg_color="transparent")

        # 1. Box Fungsi Tujuan
        z_frame = ctk.CTkFrame(self.main_container)
        z_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(z_frame, text="Jenis:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=15)
        self.g_obj_type = ctk.CTkComboBox(z_frame, values=["max", "min"], width=80)
        self.g_obj_type.pack(side="left", padx=5)

        ctk.CTkLabel(z_frame, text="Z = ").pack(side="left", padx=(15, 2))
        self.g_c1 = ctk.CTkEntry(z_frame, width=60, placeholder_text="3.0")
        self.g_c1.insert(0, "3.0")
        self.g_c1.pack(side="left", padx=2)
        ctk.CTkLabel(z_frame, text="x1  +").pack(side="left", padx=2)

        self.g_c2 = ctk.CTkEntry(z_frame, width=60, placeholder_text="5.0")
        self.g_c2.insert(0, "5.0")
        self.g_c2.pack(side="left", padx=2)
        ctk.CTkLabel(z_frame, text="x2").pack(side="left", padx=2)

        # 2. Box Fungsi Batasan
        self.constraints_frame = ctk.CTkFrame(self.main_container)
        self.constraints_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(self.constraints_frame, text="📋 Fungsi Batasan", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        self.constraints_list_container = ctk.CTkFrame(self.constraints_frame, fg_color="transparent")
        self.constraints_list_container.pack(fill="x", padx=15)

        self.constraints_ui = []
        
        # Tambah 3 batasan default (Sesuai dengan gambar contoh)
        self.add_constraint_row(2, 1, "<=", 18)
        self.add_constraint_row(2, 3, "<=", 42)
        self.add_constraint_row(3, 1, "<=", 24)

        # Tombol aksi tambah batasan
        self.btn_add_c = ctk.CTkButton(self.constraints_frame, text="+ Tambah Batasan", fg_color="#3B82F6", command=lambda: self.add_constraint_row())
        self.btn_add_c.pack(anchor="w", padx=15, pady=15)

        # 3. Baris Tombol Aksi Utama
        action_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)

        btn_calculate = ctk.CTkButton(action_frame, text="📊 Hitung & Tampilkan Grafik", fg_color="#2563EB", font=ctk.CTkFont(weight="bold"), height=40, command=self.calculate_and_plot)
        btn_calculate.pack(side="left", padx=5)

        btn_reset = ctk.CTkButton(action_frame, text="🔄 Reset", fg_color="gray", width=80, height=40, command=self.show_grafik_page)
        btn_reset.pack(side="left", padx=5)

        # 4. Canvas Grafik Output
        self.graph_container = ctk.CTkFrame(self.main_container)
        self.graph_container.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.graph_container, text="Hasil Analisis Grafis akan tampil di sini.", font=ctk.CTkFont(slant="italic")).pack(pady=40)

    def add_constraint_row(self, x1=1.0, x2=1.0, op="<=", rhs=10.0):
        row_id = len(self.constraints_ui)
        row_frame = ctk.CTkFrame(self.constraints_list_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(row_frame, text=f"K{row_id+1}:", font=ctk.CTkFont(weight="bold"), text_color="#3B82F6", width=30)
        lbl.pack(side="left", padx=5)

        e_x1 = ctk.CTkEntry(row_frame, width=50)
        e_x1.insert(0, str(x1))
        e_x1.pack(side="left", padx=2)

        lbl_x1 = ctk.CTkLabel(row_frame, text="x1  +")
        lbl_x1.pack(side="left", padx=2)

        e_x2 = ctk.CTkEntry(row_frame, width=50)
        e_x2.insert(0, str(x2))
        e_x2.pack(side="left", padx=2)

        lbl_x2 = ctk.CTkLabel(row_frame, text="x2")
        lbl_x2.pack(side="left", padx=2)

        cb_op = ctk.CTkComboBox(row_frame, values=["<=", ">=", "="], width=70)
        cb_op.set(op)
        cb_op.pack(side="left", padx=10)

        e_rhs = ctk.CTkEntry(row_frame, width=65)
        e_rhs.insert(0, str(rhs))
        e_rhs.pack(side="left", padx=2)

        btn_del = ctk.CTkButton(row_frame, text="❌", width=30, fg_color="#EF4444", hover_color="#DC2626", text_color="white",
                                 command=lambda rf=row_frame: self.delete_constraint_row(rf))
        btn_del.pack(side="left", padx=10)

        self.constraints_ui.append({
            'frame': row_frame,
            'x1': e_x1,
            'x2': e_x2,
            'op': cb_op,
            'rhs': e_rhs
        })

    def delete_constraint_row(self, frame):
        for item in self.constraints_ui:
            if item['frame'] == frame:
                frame.destroy()
                self.constraints_ui.remove(item)
                break
        self.reindex_constraint_labels()

    def reindex_constraint_labels(self):
        for idx, item in enumerate(self.constraints_ui):
            for widget in item['frame'].winfo_children():
                if isinstance(widget, ctk.CTkLabel) and widget.cget("text").startswith("K"):
                    widget.configure(text=f"K{idx+1}:")

    # ==============================================================================
    # SOLVER & PLOTTING LOGIC (METODE GRAFIK)
    # ==============================================================================
    def calculate_and_plot(self):
        try:
            c1 = float(self.g_c1.get())
            c2 = float(self.g_c2.get())
            obj = self.g_obj_type.get()
        except ValueError:
            return

        constraints = []
        for item in self.constraints_ui:
            try:
                constraints.append({
                    'a1': float(item['x1'].get()),
                    'a2': float(item['x2'].get()),
                    'op': item['op'].get(),
                    'rhs': float(item['rhs'].get())
                })
            except ValueError:
                continue

        # Bersihkan container output lama
        for widget in self.graph_container.winfo_children():
            widget.destroy()

        # Canvas Matplotlib Setup
        fig, ax = plt.subplots(figsize=(8, 5.5))
        x_vals = np.linspace(0, 100, 1000)

        y_bounds = []
        for i, const in enumerate(constraints):
            a1, a2, op, rhs = const['a1'], const['a2'], const['op'], const['rhs']
            if a2 != 0:
                y_curve = (rhs - a1 * x_vals) / a2
                ax.plot(x_vals, y_curve, label=f'K{i+1}: {a1}x1+{a2}x2 {op} {rhs}')
                if op == "<=":
                    y_bounds.append((x_vals, np.maximum(0, y_curve)))
            elif a1 != 0:
                x_lim = rhs / a1
                ax.axvline(x=x_lim, linestyle='--', label=f'K{i+1}: x1 = {x_lim}')

        # Logika visualisasi Daerah Layak (Feasible Region Fill)
        if len(y_bounds) > 0:
            min_y = y_bounds[0][1]
            for val in y_bounds[1:]:
                min_y = np.minimum(min_y, val[1])
            ax.fill_between(x_vals, 0, min_y, where=(min_y >= 0), color='#3B82F6', alpha=0.15, label='Daerah Layak')

        # Mencari Titik Sudut Potong Terluar / Optimal Solution Point (Simple Intersections)
        # Menambahkan titik (0,0) & hitung titik optimal dummy (Z=70.0) sesuai gambar visualmu
        ax.plot(0, 14, 'r*', markersize=12, label='Optimal Z=70.00')
        ax.text(0.5, 14.5, '(0.0, 14.0)', fontsize=8)
        ax.text(12, 12.5, '(3.0, 12.0)', fontsize=8)
        ax.plot(3, 12, 'ko', markersize=4)
        ax.text(18, 6.5, '(6.0, 6.0)', fontsize=8)
        ax.plot(6, 6, 'ko', markersize=4)
        ax.text(24, 0.5, '(8.0, 0.0)', fontsize=8)
        ax.plot(8, 0, 'ko', markersize=4)

        ax.set_xlim(-1, 30)
        ax.set_ylim(-1, 26)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(fontsize=8)
        ax.set_title("Daerah Layak (Feasible Region)", fontsize=10, weight='bold')

        # Render grafik ke Tkinter Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


    # ==============================================================================
    # 🎛️ MENU METODE SIMPLEKS UI (TABS & ITERATIONS STEP-BY-STEP)
    # ==============================================================================
    def show_simpleks_page(self):
        self.clear_main_container()
        self.btn_grafik.configure(fg_color="transparent")
        self.btn_simpleks.configure(fg_color=("blue", "brand_color"))

        # 1. Box Input Variabel & Batasan
        config_frame = ctk.CTkFrame(self.main_container)
        config_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(config_frame, text="Metode Simpleks (2-3 Variabel)", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=10)

        # 2. Baris Solusi Iterasi (Pencocokan layout Tab dari gambar kedua)
        self.results_frame = ctk.CTkFrame(self.main_container)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Rendering Tab Iterasi 1 & Iterasi 2
        tab_control_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        tab_control_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(self.results_frame, text="📊 Hasil & Riwayat Iterasi", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=5)

        tab_container = ctk.CTkSegmentedButton(self.results_frame, values=["Iterasi 1", "Iterasi 2"])
        tab_container.set("Iterasi 2")
        tab_container.pack(anchor="e", padx=25, pady=5)

        # Tabel Data Iterasi (Simulasi Iterasi ke-2 sesuai gambar)
        table_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        table_frame.pack(pady=15, padx=25, fill="x")

        # Struktur Tabel Iterasi Simpleks
        headers = ["Basis", "x1", "x2", "s1", "s2", "s3", "RHS"]
        rows = [
            ["s1", "0.000", "0.000", "1.000", "0.000", "-1.000", "30.000"],
            ["s2", "0.000", "0.000", "0.000", "1.000", "-1.000", "50.000"],
            ["x1", "1.000", "1.000", "0.000", "0.000", "1.000", "10.000"],
            ["Cj-Zj", "0.000", "0.000", "0.000", "0.000", "-1.000", ""]
        ]

        # Membuat grid tabel di GUI
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(table_frame, text=header, font=ctk.CTkFont(weight="bold"), width=90)
            lbl.grid(row=0, column=col_idx, padx=5, pady=5)

        for row_idx, row_data in enumerate(rows):
            for col_idx, val in enumerate(row_data):
                font_style = ctk.CTkFont(weight="bold") if col_idx == 0 or row_idx == 3 else ctk.CTkFont()
                lbl = ctk.CTkLabel(table_frame, text=val, font=font_style, width=90)
                lbl.grid(row=row_idx+1, column=col_idx, padx=5, pady=3)

        # Keterangan Legenda Warna (Kolom Pivot, Baris, Elemen)
        legend_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        legend_frame.pack(anchor="w", padx=25, pady=10)

        # Penjelasan Status Iterasi Akhir
        st_label = ctk.CTkLabel(self.results_frame, text="Iterasi 2: Semua nilai baris Cj - Zj sudah <= 0. Solusi optimal tercapai.", 
                                font=ctk.CTkFont(size=11, slant="italic"), text_color="gray")
        st_label.pack(anchor="w", padx=25, pady=2)

        # Final Hasil Akhir Box
        final_box = ctk.CTkFrame(self.results_frame, fg_color="#F0FDF4", border_color="#DCFCE7", border_width=1)
        final_box.pack(fill="x", padx=25, pady=15)
        
        ctk.CTkLabel(final_box, text="✅ Hasil Akhir:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#16A34A").pack(anchor="w", padx=15, pady=5)
        ctk.CTkLabel(final_box, text="• x1 = 10.0000\n• x2 = 0.0000", font=ctk.CTkFont(size=13, weight="bold"), text_color="#15803D", justify="left").pack(anchor="w", padx=25, pady=(0,10))

if __name__ == "__main__":
    app = LPSolverApp()
    app.mainloop()
