"""Interfaz Streamlit para tiempos y grado de consolidación (RS2).

Esta capa es SOLO presentación: toda la numérica vive en ``core`` (módulos
puros, sin Streamlit), de modo que la interfaz puede portarse a JavaScript sin
tocar los cálculos. No se usa ningún recurso externo: los datos de ejemplo los
genera ``core.datos_sinteticos``.
"""

from __future__ import annotations

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from core import datos_sinteticos as ds
from core import io_datos, metodos

st.set_page_config(page_title="Consolidación RS2", layout="wide")

COLORES = {
    "Casagrande": "#1f77b4",
    "Taylor": "#2ca02c",
    "Inflexion": "#d62728",
    "PWP": "#9467bd",
}


# --------------------------------------------------------------------------- #
# Entrada de datos.                                                            #
# --------------------------------------------------------------------------- #
def _sidebar_entrada():
    st.sidebar.header("1 · Datos de entrada")
    modo = st.sidebar.radio(
        "Modo de entrada",
        ("Cargar ejemplo (sintético)", "Subir CSV / Excel", "Entrada manual / pegar"),
    )

    df = None
    es_ejemplo = False

    if modo == "Cargar ejemplo (sintético)":
        if st.sidebar.button("Generar datos de ejemplo", type="primary"):
            st.session_state["df"] = ds.generar_ejemplo()
            st.session_state["es_ejemplo"] = True
        df = st.session_state.get("df")
        es_ejemplo = st.session_state.get("es_ejemplo", False)

    elif modo == "Subir CSV / Excel":
        archivo = st.sidebar.file_uploader("Archivo", type=["csv", "xlsx", "xls", "xlsm"])
        if archivo is not None:
            hojas = io_datos.listar_hojas(archivo)
            hoja = st.sidebar.selectbox("Hoja", hojas) if hojas else None
            crudo = io_datos.leer_archivo(archivo, hoja=hoja)
            df = _mapear_columnas(crudo)

    else:  # entrada manual / pegar
        st.sidebar.caption("Pega una tabla (coma o tabulador) con encabezados t, s, u")
        texto = st.sidebar.text_area("Tabla", height=150,
                                     placeholder="t,s,u\n0,0,100\n10,1.2,88\n...")
        if texto.strip():
            try:
                crudo = io_datos.desde_texto_pegado(texto)
                df = _mapear_columnas(crudo)
            except Exception as exc:
                st.sidebar.error(f"No se pudo leer la tabla: {exc}")

    return df, es_ejemplo


def _mapear_columnas(crudo: pd.DataFrame) -> pd.DataFrame:
    """Autodetecta y, si falla, permite mapear columnas manualmente."""
    mapa = io_datos.detectar_columnas(crudo.columns)
    st.sidebar.markdown("**Mapeo de columnas**")
    opciones = ["(ninguna)"] + list(crudo.columns)

    def _sel(label, clave):
        idx = opciones.index(mapa[clave]) if clave in mapa else 0
        val = st.sidebar.selectbox(label, opciones, index=idx, key=f"map_{clave}")
        return None if val == "(ninguna)" else val

    col_t = _sel("Tiempo (t)", "t")
    col_s = _sel("Asentamiento (s)", "s")
    col_u = _sel("Exceso PWP (u)", "u")

    if col_t is None:
        st.sidebar.warning("Selecciona al menos la columna de tiempo.")
        return None
    if col_s is None and col_u is None:
        st.sidebar.warning("Selecciona asentamiento y/o presión de poro.")
        return None
    return io_datos.preparar(crudo, col_t, col_s, col_u)


# --------------------------------------------------------------------------- #
# Gráficas de verificación.                                                    #
# --------------------------------------------------------------------------- #
def _fig_casagrande(c):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(10 ** c["logt"], c["s"], "o-", ms=3, color="#444", label="s(t)")
    L = np.linspace(c["logt"].min(), np.log10(c["t100"]) + 0.3, 50)
    tp = c["tangente_primaria"]
    ax.plot(10 ** L, tp["s0"] + tp["m"] * (L - tp["L0"]), "--",
            color=COLORES["Casagrande"], label="tangente primaria")
    sec = c["tangente_secundaria"]
    ax.plot(10 ** L, sec["b"] * L + sec["a"], ":",
            color="#ff7f0e", label="tangente secundaria")
    ax.axhline(c["s0"], color="gray", lw=0.8, ls="-.", label="s0")
    ax.axhline(c["s100"], color="green", lw=0.8, ls="-.", label="s100")
    ax.plot(c["t100"], c["s100"], "k*", ms=12, label="t100")
    ax.set_xlabel("log t"); ax.set_ylabel("asentamiento s")
    ax.set_title("Casagrande (s vs log t)"); ax.legend(fontsize=7); ax.grid(True, which="both", alpha=.3)
    return fig


def _fig_taylor(c):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(c["sqt"], c["s"], "o-", ms=3, color="#444", label="s(√t)")
    x = np.linspace(0, c["sqt"].max(), 50)
    ax.plot(x, c["s0"] + c["b_init"] * x, "--",
            color=COLORES["Taylor"], label="recta inicial")
    ax.plot(x, c["s0"] + c["m_taylor"] * x, ":",
            color="#ff7f0e", label="recta 1.15")
    if np.isfinite(c["sq90"]):
        ax.plot(c["sq90"], c["s90"], "k*", ms=12, label="t90")
    ax.set_xlabel("√t"); ax.set_ylabel("asentamiento s")
    ax.set_title("Taylor (s vs √t)"); ax.legend(fontsize=7); ax.grid(True, alpha=.3)
    return fig


def _fig_inflexion(c):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(c["t_mid"], c["D"], "o-", ms=3, color=COLORES["Inflexion"],
                label="ds/d(ln t)")
    ax.axvline(c["t70"], color="k", ls="--", label="t70 (pico)")
    ax.plot(c["t_mid"][c["k"]], c["D"][c["k"]], "k*", ms=12)
    ax.set_xlabel("log t"); ax.set_ylabel("ds/d(ln t)")
    ax.set_title("Punto de inflexión"); ax.legend(fontsize=7); ax.grid(True, which="both", alpha=.3)
    return fig


def _fig_pwp(c, tiempos):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.semilogx(c["t"], c["U"], "o-", ms=3, color=COLORES["PWP"], label="U(t)=1-u/u0")
    for et, lab in (("t50", "50%"), ("t70", "70.15%"), ("t90", "90%"), ("t100", "99%")):
        tv = tiempos.get(et)
        if tv is not None and np.isfinite(tv):
            ax.axvline(tv, color="gray", lw=0.8, ls=":")
            ax.text(tv, 0.05, lab, rotation=90, fontsize=7, va="bottom")
    ax.set_xlabel("log t"); ax.set_ylabel("grado de consolidación U")
    ax.set_title("Disipación de PWP"); ax.legend(fontsize=7); ax.grid(True, which="both", alpha=.3)
    ax.set_ylim(0, 1.02)
    return fig


# --------------------------------------------------------------------------- #
# App.                                                                         #
# --------------------------------------------------------------------------- #
def main():
    st.title("Tiempos y grado de consolidación — RS2")
    st.caption("Curvas asentamiento–tiempo y disipación de presión de poro · "
               "cuatro métodos (Casagrande, Taylor, inflexión, PWP). "
               "La numérica vive en `core/` (pura y testeable).")

    df, es_ejemplo = _sidebar_entrada()

    st.sidebar.header("2 · Parámetros de ajuste")
    t1 = st.sidebar.number_input("Casagrande · t1 (0 = auto)", value=0.0, min_value=0.0)
    ventana_sec = st.sidebar.number_input("Casagrande · ventana tangente secundaria (0 = auto)",
                                          value=0, min_value=0, step=1)
    n_init = st.sidebar.number_input("Taylor · n_init", value=4, min_value=2, step=1)

    st.sidebar.header("3 · cv (opcional)")
    calc_cv = st.sidebar.checkbox("Calcular cv")
    espesor = st.sidebar.number_input("Espesor del estrato H", value=1.0, min_value=0.0)
    drenaje = st.sidebar.radio("Drenaje", ("Doble", "Simple"), horizontal=True)

    if df is None or df.empty:
        st.info("Elige un modo de entrada en la barra lateral. "
                "Puedes empezar con **Cargar ejemplo (sintético)**.")
        return

    if es_ejemplo:
        st.success("Mostrando **datos de ejemplo** generados por las fórmulas de Terzaghi "
                   "(s_ult=10 mm, u0=100 kPa, t=2000·Tv).")

    st.subheader("Datos")
    st.dataframe(df, use_container_width=True, height=220)

    tiene_s = "s" in df.columns
    tiene_u = "u" in df.columns

    resultados = metodos.aplicar_todos(
        t=df["t"].to_numpy(),
        s=df["s"].to_numpy() if tiene_s else None,
        u=df["u"].to_numpy() if tiene_u else None,
        t1=t1 or None,
        ventana_sec=int(ventana_sec) or None,
        n_init=int(n_init),
    )

    # --- tabla de resultados (todos los métodos juntos) --------------------- #
    st.subheader("Resultados: t50 / t70 / t90 / t100")
    st.caption("Tiempos en la misma unidad del archivo. Se muestran todos los "
               "métodos; nunca se colapsa a un solo número sin exponer las diferencias.")
    tabla = metodos.tabla_resultados(resultados)
    df_tabla = pd.DataFrame(tabla).T[list(metodos.ETIQUETAS)]
    st.dataframe(df_tabla.style.format("{:.3f}"), use_container_width=True)

    for metodo, data in resultados.items():
        if "error" in data:
            st.warning(f"{metodo}: {data['error']}")

    # --- cv opcional -------------------------------------------------------- #
    if calc_cv and espesor > 0:
        H_dr = espesor / 2.0 if drenaje == "Doble" else espesor
        st.subheader(f"cv = Tv·H_dr²/t  (H_dr = {H_dr:g})")
        cv_rows = {m: metodos.calcular_cv(t, H_dr)
                   for m, t in tabla.items()}
        df_cv = pd.DataFrame(cv_rows).T[list(metodos.ETIQUETAS)]
        st.dataframe(df_cv.style.format("{:.4g}"), use_container_width=True)

    # --- exportación -------------------------------------------------------- #
    st.subheader("Exportar resultados")
    col1, col2 = st.columns(2)
    csv = df_tabla.to_csv().encode("utf-8")
    col1.download_button("Descargar CSV", csv, "resultados_consolidacion.csv", "text/csv")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        df_tabla.to_excel(xw, sheet_name="tiempos")
        df.to_excel(xw, sheet_name="datos", index=False)
    col2.download_button("Descargar Excel", buf.getvalue(),
                         "resultados_consolidacion.xlsx",
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # --- gráficas de verificación ------------------------------------------- #
    st.subheader("Gráficas de verificación (parte del método)")
    figs = []
    if "Casagrande" in resultados and "construccion" in resultados["Casagrande"]:
        figs.append(_fig_casagrande(resultados["Casagrande"]["construccion"]))
    if "Taylor" in resultados and "construccion" in resultados["Taylor"]:
        figs.append(_fig_taylor(resultados["Taylor"]["construccion"]))
    if "Inflexion" in resultados and "construccion" in resultados["Inflexion"]:
        figs.append(_fig_inflexion(resultados["Inflexion"]["construccion"]))
    if "PWP" in resultados and "construccion" in resultados["PWP"]:
        figs.append(_fig_pwp(resultados["PWP"]["construccion"],
                             resultados["PWP"]["tiempos"]))

    cols = st.columns(2)
    for i, fig in enumerate(figs):
        cols[i % 2].pyplot(fig)


if __name__ == "__main__":
    main()
