import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from utils.styles import load_css
from utils.loader import load_trend_nilai
from utils.loader import load_dashboard_sakip
from utils.loader import load_terakhir_update


st.set_page_config(
    page_title="Dashboard SAKIP 2025",
    page_icon="📊",
    layout="wide"
)

# =========================
# CSS + FIX OVERFLOW
# =========================
try:
    df_dash = load_dashboard_sakip()
    df_dash.columns = [str(c).strip() for c in df_dash.columns]

    col_text = "Komponen/Sub Komponen/Kriteria"
    col_status = "Unnamed: 9"

    komponen_map = {
        "PERENCANAAN KINERJA": {
            "nama": "Perencanaan Kinerja",
            "bobot": 30,
            "nilai": 27.60,
            "warna": "#1565F9"
        },
        "PENGUKURAN KINERJA": {
            "nama": "Pengukuran Kinerja",
            "bobot": 30,
            "nilai": 27.60,
            "warna": "#10A85C"
        },
        "PELAPORAN KINERJA": {
            "nama": "Pelaporan Kinerja",
            "bobot": 15,
            "nilai": 13.80,
            "warna": "#FF8A00"
        },
        "EVALUASI AKUNTABILITAS KINERJA INTERNAL": {
            "nama": "Evaluasi Akuntabilitas Kinerja Internal",
            "bobot": 25,
            "nilai": 23.00,
            "warna": "#6F42C1"
        },
    }

    rows = []
    current_component = None
    summary = {
        key: {
            "Jumlah Kriteria": 0,
            "Selesai": 0,
            "Proses": 0,
            "Belum Lengkap": 0
        }
        for key in komponen_map
    }

    for _, r in df_dash.iterrows():
        teks = str(r.get(col_text, "")).strip()
        status = str(r.get(col_status, "")).strip().lower()

        if teks.upper() in komponen_map:
            current_component = teks.upper()
            continue

        if current_component is None:
            continue

        no_value = str(r.get("No", "")).strip()

        if no_value.isdigit():
            summary[current_component]["Jumlah Kriteria"] += 1

            if status in ["ok", "selesai", "sesuai"]:
                summary[current_component]["Selesai"] += 1
            elif "belum" in status:
                summary[current_component]["Belum Lengkap"] += 1
            else:
                summary[current_component]["Proses"] += 1

    for key, meta in komponen_map.items():
        rows.append({
            "Komponen": meta["nama"],
            "Bobot": meta["bobot"],
            "Nilai": meta["nilai"],
            "Jumlah Kriteria": summary[key]["Jumlah Kriteria"],
            "Selesai": summary[key]["Selesai"],
            "Proses": summary[key]["Proses"],
            "Belum Lengkap": summary[key]["Belum Lengkap"],
            "Warna": meta["warna"]
        })

    komponen = pd.DataFrame(rows)

except Exception as e:
    st.warning(f"Data Dashboard_SAKIP gagal dibaca. Menggunakan data sementara. Error: {e}")

    komponen = pd.DataFrame({
        "Komponen": [
            "Perencanaan Kinerja",
            "Pengukuran Kinerja",
            "Pelaporan Kinerja",
            "Evaluasi Akuntabilitas Kinerja Internal",
        ],
        "Bobot": [30, 30, 15, 25],
        "Nilai": [27.60, 27.60, 13.80, 23.00],
        "Jumlah Kriteria": [25, 20, 22, 13],
        "Selesai": [15, 18, 21, 13],
        "Proses": [8, 2, 1, 0],
        "Belum Lengkap": [1, 0, 0, 0],
        "Warna": ["#1565F9", "#10A85C", "#FF8A00", "#6F42C1"]
    })
st.markdown(load_css(), unsafe_allow_html=True)

st.markdown("""
<style>
.block-container {
    max-width: 100% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}
div[data-testid="column"] {
    padding: 0 0.4rem !important;
}
</style>
""", unsafe_allow_html=True)




# =========================
# DATA REAL TREND DARI GOOGLE SHEET
# =========================
try:
    trend = load_trend_nilai()
    trend.columns = [str(c).strip() for c in trend.columns]

    trend = trend[["Tahun", "Nilai"]].dropna()
    trend["Tahun"] = trend["Tahun"].astype(str)
    trend["Nilai"] = pd.to_numeric(trend["Nilai"], errors="coerce")
    trend = trend.dropna()

except Exception as e:
    st.warning(f"Data Trend_Nilai gagal dibaca dari Google Sheet. Menggunakan data sementara. Error: {e}")

    trend = pd.DataFrame({
        "Tahun": [2020, 2021, 2022, 2023, 2024],
        "Nilai": [94.97, 90.30, 91.10, 90.25, 89.25]
    })

# =========================
# DATA SEMENTARA TINDAK LANJUT
# =========================
tindak_lanjut = pd.DataFrame({
    "Kriteria": [
        "Dokumen Anggaran",
        "Pengukuran TW II",
        "Dokumen Aktivitas",
        "Pengukuran Berjenjang",
        "Notulensi Rapat"
    ],
    "Sub Komponen": ["1.c", "2.c", "1.b", "2.b", "4.a"],
    "Komponen": ["Perencanaan", "Pengukuran", "Perencanaan", "Pengukuran", "Evaluasi"],
    "Bobot Sub": [15, 15, 9, 9, 6],
    "PIC": ["Sebastian", "Debora", "Feybe", "Debora", "Erick"],
    "Status": ["Belum Lengkap", "Proses", "Belum Lengkap", "Proses", "Proses"],
    "Catatan": [
        "RKA-KL belum lengkap",
        "Data TW II belum ada",
        "RAK tunggu revisi NKA",
        "Bukti upload belum lengkap",
        "Notulensi belum diunggah"
    ]
})

nilai_total = komponen["Nilai"].sum()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.image(
        "assets/icons/single/logo.png",
        width=180
    )

    st.divider()

    st.markdown("### MENU")

    st.page_link(
        "app.py",
        label="Dashboard",
        icon="🏠"
    )

    st.page_link(
        "pages/1_Perencanaan_Kinerja.py",
        label="Perencanaan Kinerja",
        icon="📘"
    )

    st.page_link(
        "pages/2_Pengukuran_Kinerja.py",
        label="Pengukuran Kinerja",
        icon="📗"
    )

    st.page_link(
        "pages/3_Pelaporan_Kinerja.py",
        label="Pelaporan Kinerja",
        icon="📙"
    )

    st.page_link(
        "pages/4_Evaluasi_Akuntabilitas_Kinerja_Internal.py",
        label="Evaluasi Akuntabilitas Kinerja Internal",
        icon="📕"
    )

    st.divider()

    st.page_link(
        "pages/5_PIC_Monitoring.py",
        label="PIC Monitoring",
        icon="👥"
    )

    st.divider()

    st.markdown(
        st.markdown(
    f"📅 **Terakhir Update**  \n{load_terakhir_update()}"
)

# =========================
# HEADER
# =========================
st.title("Dashboard SAKIP 2025")
st.caption("Poltekkes Kemenkes Manado")

# =========================
# BARIS ATAS
# =========================
col1, col2, col3 = st.columns([1.2, 0.8, 1.4])

with col1:
    with st.container(border=True):
        st.subheader("Pembagian Bobot Komponen")

        fig_bobot = go.Figure(go.Pie(
            labels=komponen["Komponen"],
            values=komponen["Bobot"],
            hole=0.55,
            textinfo="percent",
            marker=dict(colors=komponen["Warna"])
        ))

        fig_bobot.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#0B2C5F"),
            showlegend=True
        )

        st.plotly_chart(fig_bobot, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Nilai Total SAKIP")
        st.metric("Nilai", f"{nilai_total:.2f} / 100")
        st.success("Predikat AA")
        st.caption("Sangat Memuaskan")

with col3:
    with st.container(border=True):
        st.subheader("Trend Nilai SAKIP 5 Tahun")

        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=trend["Tahun"],
            y=trend["Nilai"],
            mode="lines+markers+text",
            text=trend["Nilai"],
            textposition="top center",
            line=dict(color="#1565F9", width=3),
            marker=dict(size=9)
        ))

        fig_trend.update_layout(
            height=320,
            yaxis=dict(range=[0, 100]),
            margin=dict(l=0, r=0, t=20, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#0B2C5F"),
            showlegend=False
        )

        st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# =========================
# CARD KOMPONEN
# =========================
# =========================
# CARD KOMPONEN
# =========================
detail_pages = {
    "Perencanaan Kinerja": "pages/1_Perencanaan_Kinerja.py",
    "Pengukuran Kinerja": "pages/2_Pengukuran_Kinerja.py",
    "Pelaporan Kinerja": "pages/3_Pelaporan_Kinerja.py",
    "Evaluasi Akuntabilitas Kinerja Internal":
        "pages/4_Evaluasi_Akuntabilitas_Kinerja_Internal.py",
}

card_cols = st.columns(4)

for i, row in komponen.iterrows():
    persen = row["Nilai"] / row["Bobot"] * 100

    with card_cols[i]:
        with st.container(border=True):
            st.markdown(f"### {row['Komponen']}")

            st.metric(
                "Nilai",
                f"{row['Nilai']:.2f} / {row['Bobot']}",
                f"{persen:.2f}%"
            )

            st.write(f"Jumlah Kriteria: **{row['Jumlah Kriteria']}**")
            st.write(f"🟢 Selesai: **{row['Selesai']}**")
            st.write(f"🟡 Proses: **{row['Proses']}**")
            st.write(f"🔴 Belum Lengkap: **{row['Belum Lengkap']}**")

            if st.button(
                "Lihat Detail",
                key=f"detail_{i}",
                use_container_width=True
            ):
                st.switch_page(detail_pages[row["Komponen"]])

st.divider()

# =========================
# STATUS DAN PIC MONITORING
# =========================
b1, b2 = st.columns([0.8, 1.6])

with b1:
    with st.container(border=True):

        total = int(komponen["Jumlah Kriteria"].sum())
        selesai = int(komponen["Selesai"].sum())
        proses = int(komponen["Proses"].sum())
        belum = int(komponen["Belum Lengkap"].sum())

        st.subheader("Status Kriteria SAKIP")

        r1c1, r1c2 = st.columns(2)

        with r1c1:
            st.metric(
                label="🟢 Selesai",
                value=selesai
            )

        with r1c2:
            st.metric(
                label="🟡 Proses",
                value=proses
            )

        r2c1, r2c2 = st.columns(2)

        with r2c1:
            st.metric(
                label="🔴 Belum Lengkap",
                value=belum
            )

        with r2c2:
            st.metric(
                label="🔵 Total",
                value=total
            )

        st.divider()

        progress = selesai / total if total > 0 else 0

        st.caption(
            f"Progress Penyelesaian {progress*100:.2f}%"
        )

        st.progress(progress)

with b2:
    with st.container(border=True):
        st.subheader("Tindak Lanjut Prioritas")
        st.caption(
            "Menampilkan status bukan Selesai, "
            "diurutkan berdasarkan bobot sub komponen terbesar."
        )

        st.dataframe(
            tindak_lanjut,
            use_container_width=True,
            hide_index=True
        )