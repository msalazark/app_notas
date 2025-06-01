import pandas as pd
import streamlit as st

REMOTE_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/1XwIduZvxpaHb6bZ9zzBZJOZdKeqkJ0O8TRRbgAmX6qc/export?format=csv&gid=0"
)

@st.cache_data(ttl=300, show_spinner=False)
def load_data(url):
    dtypes = {"curso": str, "nrc": str, "codigo_alumno": str, "nota": float}
    try:
        # Motor C (rápido). Fallará si hay filas mal formateadas.
        return pd.read_csv(url, dtype=dtypes)
    except pd.errors.ParserError:
        st.warning(
            "Se detectaron filas con número irregular de columnas; "
            "se cargarán omitiendo las problemáticas."
        )
        # Motor Python, más tolerante: omite las filas corruptas.
        return pd.read_csv(
            url,
            dtype=dtypes,
            engine="python",
            on_bad_lines="skip"  # usa "warn" si quieres ver cuáles se omiten
        )

df = load_data(REMOTE_CSV_URL)

st.set_page_config(page_title="Consulta de notas", page_icon="🎓", layout="centered")
st.title("Consulta de Nota de participación")

# --- Dropdown dependientes ---
curso_sel = st.selectbox("Curso", sorted(df["curso"].unique()))
nrc_sel   = st.selectbox(
    "NRC",
    sorted(df.loc[df["curso"] == curso_sel, "nrc"].unique())
)
codigo = st.text_input("Código del alumno")

if st.button("Obtener nota"):
    fila = df.query(
        "curso == @curso_sel and nrc == @nrc_sel and codigo_alumno == @codigo.strip()"
    )
    if fila.empty:
        st.error("⚠️ No se encontró la nota ")
    else:
        nota = float(fila.iloc[0]["nota"])

        notas_seccion = df.loc[
            (df["curso"] == curso_sel) & (df["nrc"] == nrc_sel), "nota"
        ]
        q1, q2, q3 = notas_seccion.quantile([0.25, 0.5, 0.75])

        cuartil = (
            "Q1 (≤25 %)"  if nota <= q1 else
            "Q2 (25-50 %)" if nota <= q2 else
            "Q3 (50-75 %)" if nota <= q3 else
            "Q4 (75-100 %)"
        )

        st.success(f"🎉 Tu nota es **{nota:.2f}**")
        st.info(f"📊 Perteneces al **{cuartil}** de tu sección")

        with st.expander("Distribución de notas del grupo"):
            st.write(
                f"- Q1: {q1:.2f}\n"
                f"- Q2 (mediana): {q2:.2f}\n"
                f"- Q3: {q3:.2f}"
            )
