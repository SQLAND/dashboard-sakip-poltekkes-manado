import streamlit as st
import plotly.graph_objects as go

from utils.loader import load_terakhir_update


def render_component_page(
    title,
    caption,
    color,
    nilai,
    bobot,
    sub_komponen,
    kriteria,
    pic,
    dokumen,
    tindak_lanjut,
    sidebar_title,
    sidebar_page_path,
    sidebar_icon,
    inovasi=None
):
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
            sidebar_page_path,
            label=sidebar_title,
            icon=sidebar_icon
        )

        st.divider()

        st.markdown(
            f"📅 **Terakhir Update**  \n{load_terakhir_update()}"
        )

    # =========================
    # HEADER
    # =========================
    st.title(title)
    st.caption(caption)

    persen = nilai / bobot * 100 if bobot else 0

    # =========================
    # TOP LAYOUT
    # =========================
    left, center, right = st.columns([1.1, 1.8, 1.1])

    with left:
        with st.container(border=True):
            st.subheader(f"Capaian {title.title()}")

            fig = go.Figure(go.Pie(
                values=[nilai, max(bobot - nilai, 0)],
                labels=["Nilai Diperoleh", "Sisa"],
                hole=0.65,
                marker=dict(colors=[color, "#E5ECF5"]),
                textinfo="none"
            ))

            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=10),
                annotations=[
                    dict(
                        text=f"<b>{nilai:.2f}</b><br>{persen:.2f}%<br>Capaian",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                        font=dict(size=18, color="#0B2C5F")
                    )
                ],
                showlegend=False,
                paper_bgcolor="white",
                plot_bgcolor="white"
            )

            st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)
            c1.metric("Nilai Diperoleh", f"{nilai:.2f}")
            c2.metric("Bobot Maksimal", f"{bobot:.2f}")

    with center:
        with st.container(border=True):
            st.subheader("Sub Komponen")

            st.dataframe(
                sub_komponen,
                use_container_width=True,
                hide_index=True
            )

    with right:
        with st.container(border=True):
            st.subheader("Status Kriteria")

            total = len(kriteria)
            selesai = len(kriteria[kriteria["Status"] == "Selesai"])
            proses = len(kriteria[kriteria["Status"] == "Proses"])
            belum = len(kriteria[kriteria["Status"] == "Belum Lengkap"])

            st.caption(f"Total {total} Kriteria")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("🟢 Selesai", selesai)

            with c2:
                st.metric("🟡 Proses", proses)

            with c3:
                st.metric("🔴 Belum", belum)

        with st.container(border=True):
            st.subheader("Tindak Lanjut Prioritas")

            st.dataframe(
                tindak_lanjut,
                use_container_width=True,
                hide_index=True
            )

    st.divider()

    # =========================
    # BOTTOM LAYOUT
    # =========================
    main, side = st.columns([2.2, 1])

    with main:
        with st.container(border=True):
            st.subheader(f"Kriteria {title.title()}")

            if "Sub Komponen" in kriteria.columns:
                for sub in kriteria["Sub Komponen"].dropna().unique():
                    data_sub = kriteria[kriteria["Sub Komponen"] == sub]

                    with st.expander(sub, expanded=False):
                        st.dataframe(
                            data_sub,
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.dataframe(
                    kriteria,
                    use_container_width=True,
                    hide_index=True
                )

        # =========================
        # INOVASI
        # =========================
        if inovasi is not None and not inovasi.empty:
            with st.container(border=True):
                st.subheader(f"💡 Inovasi {title.title()}")
                st.caption(
                    "Menampilkan upaya inovatif yang terkait dengan sub komponen."
                )

                for _, row in inovasi.iterrows():
                    st.markdown(
                        f"""
                        <div class="inovasi-card">
                            <div class="inovasi-title">💡 {row["Inovasi"]}</div>
                            <div class="inovasi-meta"><b>Sub Komponen:</b> {row["Sub Komponen"]}</div>
                            <div class="inovasi-meta"><b>PIC:</b> {row["PIC"]}</div>
                            <div class="inovasi-meta"><b>Catatan:</b> {row["Catatan"]}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    with side:
        with st.container(border=True):
            st.subheader("PIC Terlibat")

            st.dataframe(
                pic,
                use_container_width=True,
                hide_index=True
            )

        with st.container(border=True):
            st.subheader(f"Dokumen Pendukung {title.title()}")

            st.dataframe(
                dokumen,
                use_container_width=True,
                hide_index=True
            )

            st.button(
                f"Lihat Detail Dokumen {title.title()} →",
                use_container_width=True
            )