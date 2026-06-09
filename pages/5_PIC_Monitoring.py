import streamlit as st
import pandas as pd

from utils.styles import load_css
from utils.loader import load_dashboard_sakip

st.set_page_config(
    page_title="PIC Monitoring",
    page_icon="👥",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)

# =========================
# CSS TAMBAHAN
# =========================
st.markdown("""
<style>
.metric-box {
    background: white;
    border: 1px solid #DDE6F2;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 6px 18px rgba(11, 44, 95, 0.08);
}

.metric-title {
    font-size: 13px;
    color: #64748B;
    font-weight: 700;
}

.metric-value {
    font-size: 30px;
    font-weight: 900;
    color: #0B2C5F;
}

.metric-green {
    border-left: 6px solid #10A85C;
}

.metric-yellow {
    border-left: 6px solid #F59E0B;
}

.metric-red {
    border-left: 6px solid #EF4444;
}

.metric-blue {
    border-left: 6px solid #1565F9;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA DARI GOOGLE SHEET
# =========================
try:
    df_dash = load_dashboard_sakip()
    df_dash.columns = [str(c).strip() for c in df_dash.columns]

    col_no = "No"
    col_kriteria = "Komponen/Sub Komponen/Kriteria"
    col_pic = "Penanggungjawab"
    col_catatan = "Unnamed: 9"
    col_status = "Unnamed: 10"
    col_target = "Unnamed: 11"
    col_link = "Link Dokumen"

    df_kriteria = df_dash[
        df_dash[col_no].astype(str).str.strip().str.isdigit()
    ].copy()

    df_kriteria["Kriteria"] = df_kriteria[col_kriteria].fillna("-")
    df_kriteria["PIC"] = df_kriteria[col_pic].fillna("-")
    df_kriteria["Catatan"] = df_kriteria[col_catatan].fillna("-")
    df_kriteria["Status Asli"] = df_kriteria[col_status].fillna("Proses")
    df_kriteria["Target Penyelesaian"] = df_kriteria[col_target].fillna("-")
    df_kriteria["Link Dokumen"] = df_kriteria[col_link].fillna("-")

    def normalisasi_status(status):
        status = str(status).strip().lower()

        if status in ["selesai", "sesuai", "ok"]:
            return "Selesai"

        if "belum" in status:
            return "Belum Lengkap"

        if status in ["none", "nan", "-", ""]:
            return "Proses"

        return "Proses"

    df_kriteria["Status"] = df_kriteria["Status Asli"].apply(normalisasi_status)

    komponen_keywords = [
        "PERENCANAAN KINERJA",
        "PENGUKURAN KINERJA",
        "PELAPORAN KINERJA",
        "EVALUASI AKUNTABILITAS KINERJA INTERNAL",
    ]

    current_component = None
    komponen_list = []

    for _, row in df_dash.iterrows():
        teks = str(row.get(col_kriteria, "")).strip()
        teks_upper = teks.upper()

        if teks_upper in komponen_keywords:
            current_component = teks.title()

        no_value = str(row.get(col_no, "")).strip()

        if no_value.isdigit():
            komponen_list.append(current_component)

    df_kriteria["Komponen"] = komponen_list[:len(df_kriteria)]

    detail_kriteria = df_kriteria[
        [
            "Komponen",
            "Kriteria",
            "PIC",
            "Status",
            "Target Penyelesaian",
            "Link Dokumen",
            "Catatan"
        ]
    ].copy()

    # Hapus header komponen yang ikut terbaca sebagai kriteria
    detail_kriteria = detail_kriteria[
        ~detail_kriteria["Kriteria"].astype(str).str.upper().isin(komponen_keywords)
    ]

    # Hapus baris tidak valid, misalnya hanya huruf "c"
    detail_kriteria = detail_kriteria[
        detail_kriteria["Kriteria"].astype(str).str.len() > 5
    ]

    # Pecah PIC jika satu kriteria punya lebih dari satu PIC
    pic_rows = []

    for _, row in detail_kriteria.iterrows():
        raw_pic = str(row["PIC"]).replace("/", ",").replace(";", ",")

        for pic in raw_pic.split(","):
            pic = pic.strip()

            if pic and pic != "-":
                pic_rows.append({
                    "PIC": pic,
                    "Status": row["Status"]
                })

    df_pic = pd.DataFrame(pic_rows)

    if df_pic.empty:
        daftar_pic = pd.DataFrame({
            "PIC": [],
            "Total Kriteria": [],
            "Selesai": [],
            "Proses": [],
            "Belum Lengkap": [],
            "Progress": []
        })
    else:
        daftar_pic = (
            df_pic.groupby("PIC")
            .agg(
                Total_Kriteria=("Status", "count"),
                Selesai=("Status", lambda x: (x == "Selesai").sum()),
                Proses=("Status", lambda x: (x == "Proses").sum()),
                Belum_Lengkap=("Status", lambda x: (x == "Belum Lengkap").sum()),
            )
            .reset_index()
        )

        daftar_pic["Progress"] = (
            daftar_pic["Selesai"] / daftar_pic["Total_Kriteria"] * 100
        ).round(2).astype(str) + "%"

        daftar_pic = daftar_pic.rename(columns={
            "Total_Kriteria": "Total Kriteria",
            "Belum_Lengkap": "Belum Lengkap"
        })

except Exception as e:
    st.warning(
        f"Data PIC Monitoring gagal dibaca dari Google Sheet. "
        f"Menggunakan data sementara. Error: {e}"
    )

    daftar_pic = pd.DataFrame({
        "PIC": ["Sebastian", "Debora", "Feybe", "Erick"],
        "Total Kriteria": [8, 10, 6, 5],
        "Selesai": [5, 7, 4, 3],
        "Proses": [2, 2, 1, 1],
        "Belum Lengkap": [1, 1, 1, 1],
        "Progress": ["62.5%", "70.0%", "66.7%", "60.0%"]
    })

    detail_kriteria = pd.DataFrame({
        "Komponen": [
            "Pengukuran Kinerja",
            "Pengukuran Kinerja",
            "Perencanaan Kinerja",
            "Pelaporan Kinerja"
        ],
        "Kriteria": [
            "Pengukuran Kinerja telah dimanfaatkan",
            "Pengukuran Kinerja telah berjenjang",
            "Dokumen Perjanjian Kinerja",
            "Tersedia laporan kinerja berkala"
        ],
        "PIC": ["Debora", "Debora", "Sebastian", "Debora"],
        "Status": ["Proses", "Proses", "Belum Lengkap", "Selesai"],
        "Target Penyelesaian": ["-", "-", "-", "-"],
        "Link Dokumen": ["Lihat", "Lihat", "Lihat", "Lihat"],
        "Catatan": ["-", "-", "-", "-"]
    })

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.image("assets/icons/single/logo.png", width=180)

    st.divider()

    st.page_link(
        "app.py",
        label="Dashboard",
        icon="🏠"
    )

    st.page_link(
        "pages/5_PIC_Monitoring.py",
        label="PIC Monitoring",
        icon="👥"
    )

    st.divider()

    st.markdown("📅 **Terakhir Update**  \n26 Mei 2025 10:30 WIB")

# =========================
# HEADER
# =========================
st.title("PIC Monitoring")
st.caption("Monitoring progres kriteria berdasarkan PIC")

# =========================
# KPI CARD ATAS
# =========================
total_pic = daftar_pic["PIC"].nunique()
total_kriteria = int(daftar_pic["Total Kriteria"].sum())
total_selesai = int(daftar_pic["Selesai"].sum())
total_proses = int(daftar_pic["Proses"].sum())
total_belum = int(daftar_pic["Belum Lengkap"].sum())

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-box metric-blue">
        <div class="metric-title">Total PIC</div>
        <div class="metric-value">{total_pic}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-box metric-blue">
        <div class="metric-title">Total Kriteria</div>
        <div class="metric-value">{total_kriteria}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-box metric-green">
        <div class="metric-title">Selesai</div>
        <div class="metric-value">{total_selesai}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-box metric-yellow">
        <div class="metric-title">Proses</div>
        <div class="metric-value">{total_proses}</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-box metric-red">
        <div class="metric-title">Belum Lengkap</div>
        <div class="metric-value">{total_belum}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# DAFTAR PIC
# =========================
with st.container(border=True):
    st.subheader("Daftar PIC")

    st.dataframe(
        daftar_pic,
        use_container_width=True,
        hide_index=True
    )

# =========================
# DAFTAR KRITERIA
# =========================
with st.container(border=True):
    st.subheader("Daftar Kriteria")

    f1, f2, f3, f4 = st.columns([1, 1, 1, 2])

    with f1:
        pilihan_pic = st.selectbox(
            "PIC",
            ["Semua PIC"] + sorted(daftar_pic["PIC"].dropna().unique().tolist())
        )

    with f2:
        pilihan_status = st.selectbox(
            "Status",
            ["Semua Status", "Selesai", "Proses", "Belum Lengkap"]
        )

    with f3:
        pilihan_komponen = st.selectbox(
            "Komponen",
            ["Semua Komponen"] + sorted(detail_kriteria["Komponen"].dropna().unique().tolist())
        )

    with f4:
        keyword = st.text_input(
            "Cari Kriteria",
            placeholder="Cari kriteria..."
        )

    data_filter = detail_kriteria.copy()

    if pilihan_pic != "Semua PIC":
        data_filter = data_filter[
            data_filter["PIC"].fillna("").str.contains(
                pilihan_pic,
                case=False,
                na=False
            )
        ]

    if pilihan_status != "Semua Status":
        data_filter = data_filter[
            data_filter["Status"] == pilihan_status
        ]

    if pilihan_komponen != "Semua Komponen":
        data_filter = data_filter[
            data_filter["Komponen"] == pilihan_komponen
        ]

    if keyword:
        data_filter = data_filter[
            data_filter["Kriteria"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

    def warna_status(val):
        if val == "Selesai":
            return "background-color: #DCFCE7; color: #166534; font-weight: 700;"
        if val == "Proses":
            return "background-color: #FEF3C7; color: #92400E; font-weight: 700;"
        if val == "Belum Lengkap":
            return "background-color: #FEE2E2; color: #991B1B; font-weight: 700;"
        return ""

    st.dataframe(
        data_filter.style.map(warna_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True
    )