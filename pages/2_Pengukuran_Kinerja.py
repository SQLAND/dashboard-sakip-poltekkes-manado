import pandas as pd
import streamlit as st

from utils.styles import load_css
from utils.loader import load_dashboard_sakip
from utils.component_page import render_component_page

st.set_page_config(
    page_title="Pengukuran Kinerja",
    page_icon="📗",
    layout="wide"
)

st.markdown(load_css(), unsafe_allow_html=True)


def normalisasi_status(status):
    status = str(status).strip().lower()

    if status in ["selesai", "sesuai", "ok"]:
        return "Selesai"

    if "belum" in status:
        return "Belum Lengkap"

    if status in ["none", "nan", "-", ""]:
        return "Proses"

    return "Proses"


def to_number(value):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return 0.0


try:
    df = load_dashboard_sakip()
    df.columns = [str(c).strip() for c in df.columns]

    col_no = "No"
    col_text = "Komponen/Sub Komponen/Kriteria"
    col_bobot = "Bobot"
    col_nilai = "Unnamed: 4"
    col_evidence = "Daftar Evidence"
    col_link = "Link Dokumen"
    col_pic = "Penanggungjawab"
    col_catatan = "Unnamed: 9"
    col_status = "Unnamed: 10"
    col_target = "Unnamed: 11"

    current_component = None
    current_sub = None

    sub_rows = []
    kriteria_rows = []
    inovasi_rows = []

    for _, row in df.iterrows():
        teks = str(row.get(col_text, "")).strip()
        teks_upper = teks.upper()
        no_value = str(row.get(col_no, "")).strip()

        if teks_upper == "PENGUKURAN KINERJA":
            current_component = "PENGUKURAN KINERJA"
            current_sub = None
            continue

        if teks_upper in [
            "PERENCANAAN KINERJA",
            "PELAPORAN KINERJA",
            "EVALUASI AKUNTABILITAS KINERJA INTERNAL"
        ]:
            current_component = teks_upper
            current_sub = None
            continue

        if current_component != "PENGUKURAN KINERJA":
            continue

        if no_value.lower() in ["2.a", "2.b", "2.c"]:
            current_sub = f"{no_value} {teks}"

            bobot_sub = to_number(row.get(col_bobot, 0))
            nilai_sub = to_number(row.get(col_nilai, 0))
            capaian = (nilai_sub / bobot_sub * 100) if bobot_sub else 0

            sub_rows.append({
                "Sub Komponen": current_sub,
                "Bobot": bobot_sub,
                "Nilai": nilai_sub,
                "Capaian": f"{capaian:.2f}%"
            })

            continue

        if "upaya inovatif" in teks.lower() and current_sub is not None:
            inovasi_rows.append({
                "Sub Komponen": current_sub,
                "Inovasi": teks,
                "Dokumen / Evidence": row.get(col_evidence, "-"),
                "PIC": row.get(col_pic, "-"),
                "Link Dokumen": row.get(col_link, "-"),
                "Catatan": row.get(col_catatan, "-")
            })

            continue

        if no_value.isdigit() and current_sub is not None:
            status_asli = row.get(col_status, "")

            if pd.isna(status_asli) or str(status_asli).strip() == "":
                status_asli = row.get(col_catatan, "")

            kriteria_rows.append({
                "Sub Komponen": current_sub,
                "Kriteria": teks,
                "Dokumen / Evidence": row.get(col_evidence, "-"),
                "PIC": row.get(col_pic, "-"),
                "Status": normalisasi_status(status_asli),
                "Target Penyelesaian": row.get(col_target, "-"),
                "Link Dokumen": row.get(col_link, "-"),
                "Catatan": row.get(col_catatan, "-")
            })

    sub_komponen = pd.DataFrame(sub_rows)
    kriteria = pd.DataFrame(kriteria_rows)
    inovasi = pd.DataFrame(inovasi_rows)

    if sub_komponen.empty:
        st.error("Data sub komponen Pengukuran tidak ditemukan. Cek baris 2.a, 2.b, 2.c di Google Sheet.")
        st.stop()

    nilai = pd.to_numeric(sub_komponen["Nilai"], errors="coerce").fillna(0).sum()
    bobot = pd.to_numeric(sub_komponen["Bobot"], errors="coerce").fillna(0).sum()

    pic_rows = []

    for _, row in kriteria.iterrows():
        raw_pic = str(row["PIC"]).replace("/", ",").replace(";", ",")

        for pic_name in raw_pic.split(","):
            pic_name = pic_name.strip()

            if pic_name and pic_name != "-":
                pic_rows.append({
                    "PIC": pic_name,
                    "Status": row["Status"]
                })

    df_pic = pd.DataFrame(pic_rows)

    if df_pic.empty:
        pic = pd.DataFrame(columns=["PIC", "Jumlah Kriteria", "Selesai", "Proses", "Belum Lengkap"])
    else:
        pic = (
            df_pic.groupby("PIC")
            .agg(
                Jumlah_Kriteria=("Status", "count"),
                Selesai=("Status", lambda x: (x == "Selesai").sum()),
                Proses=("Status", lambda x: (x == "Proses").sum()),
                Belum_Lengkap=("Status", lambda x: (x == "Belum Lengkap").sum())
            )
            .reset_index()
            .rename(columns={
                "Jumlah_Kriteria": "Jumlah Kriteria",
                "Belum_Lengkap": "Belum Lengkap"
            })
        )

    dokumen = kriteria[
        ["Dokumen / Evidence", "Link Dokumen", "Status"]
    ].rename(columns={
        "Dokumen / Evidence": "Dokumen"
    })

    tindak_lanjut = kriteria[
        kriteria["Status"] != "Selesai"
    ][
        ["Kriteria", "PIC", "Status", "Target Penyelesaian", "Catatan"]
    ]

except Exception as e:
    st.error(f"Gagal membaca data Pengukuran dari Google Sheet: {e}")
    st.stop()


render_component_page(
    title="PENGUKURAN KINERJA",
    caption="Detail Komponen SAKIP",
    color="#10A85C",
    nilai=nilai,
    bobot=bobot,
    sub_komponen=sub_komponen,
    kriteria=kriteria,
    pic=pic,
    dokumen=dokumen,
    tindak_lanjut=tindak_lanjut,
    sidebar_title="Pengukuran Kinerja",
    sidebar_page_path="pages/2_Pengukuran_Kinerja.py",
    sidebar_icon="📗",
    inovasi=inovasi
)