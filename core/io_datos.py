"""Lectura y normalización de datos de entrada (CSV / Excel / RS2 nativo).

Módulo puro (pandas/numpy). Autodetecta las columnas t, s, u por nombre con
sinónimos, trabaja con el asentamiento RELATIVO a la primera lectura y
auto-detecta el signo para que el asentamiento sea creciente.
"""

from __future__ import annotations

import io
import re
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

# Sinónimos de encabezados (en minúsculas). Los de un solo carácter se cotejan
# solo por igualdad exacta; el resto también por subcadena.
SINONIMOS: Dict[str, List[str]] = {
    "t": ["t", "tiempo", "time", "stage time"],
    "s": ["s", "sy", "asentamiento", "settlement", "vertical displacement"],
    "u": ["u", "pwp", "excess pore", "excess pwp", "exceso", "poro"],
}


def detectar_columnas(columnas) -> Dict[str, str]:
    """Mapea cada clave (t, s, u) a un nombre de columna del DataFrame."""
    mapa: Dict[str, str] = {}
    low = {c: str(c).strip().lower() for c in columnas}
    for clave, sinonimos in SINONIMOS.items():
        encontrado: Optional[object] = None
        # 1) coincidencia exacta
        for c, l in low.items():
            if l in sinonimos and c not in mapa.values():
                encontrado = c
                break
        # 2) coincidencia por subcadena (solo sinónimos de >1 carácter)
        if encontrado is None:
            for c, l in low.items():
                if c in mapa.values():
                    continue
                if any(len(sy) > 1 and sy in l for sy in sinonimos):
                    encontrado = c
                    break
        if encontrado is not None:
            mapa[clave] = encontrado
    return mapa


def leer_archivo(origen, hoja=None) -> pd.DataFrame:
    """Lee un CSV o Excel a DataFrame.

    ``origen`` puede ser una ruta o un buffer. Para Excel se usa ``hoja``
    (nombre o índice); por defecto la primera.
    """
    nombre = getattr(origen, "name", origen)
    nombre = str(nombre).lower()
    if nombre.endswith((".xlsx", ".xls", ".xlsm")):
        return pd.read_excel(origen, sheet_name=0 if hoja is None else hoja)
    return pd.read_csv(origen)


def listar_hojas(origen) -> List[str]:
    """Nombres de hoja de un Excel (lista vacía si no aplica)."""
    nombre = str(getattr(origen, "name", origen)).lower()
    if nombre.endswith((".xlsx", ".xls", ".xlsm")):
        return pd.ExcelFile(origen).sheet_names
    return []


def preparar(df: pd.DataFrame, col_t: str, col_s: Optional[str] = None,
             col_u: Optional[str] = None) -> pd.DataFrame:
    """Normaliza a columnas t, s, u.

    - ``s`` se vuelve relativo a la primera lectura y se auto-orienta a creciente.
    - Se conservan las unidades; solo se ordena por t y se eliminan filas sin t.
    """
    out = pd.DataFrame()
    out["t"] = pd.to_numeric(df[col_t], errors="coerce")

    if col_s is not None:
        s = pd.to_numeric(df[col_s], errors="coerce")
        s = s - s.iloc[0]                    # relativo a la primera lectura
        # auto-signo: que el asentamiento neto sea creciente (positivo)
        finitos = s.dropna()
        if len(finitos) and finitos.iloc[-1] < 0:
            s = -s
        out["s"] = s

    if col_u is not None:
        out["u"] = pd.to_numeric(df[col_u], errors="coerce")

    out = out.dropna(subset=["t"]).sort_values("t").reset_index(drop=True)
    return out


def desde_texto_pegado(texto: str) -> pd.DataFrame:
    """Lee una tabla pegada desde el portapapeles (tab o coma, con encabezado)."""
    texto = texto.strip()
    sep = "\t" if "\t" in texto else ","
    return pd.read_csv(io.StringIO(texto), sep=sep)


# --------------------------------------------------------------------------- #
# Formato nativo RS2 "History Query" (.txt por etapas).                        #
# --------------------------------------------------------------------------- #
_RE_CABECERA = re.compile(r"HQ\s+(\d+)\s+Stage\s+(\d+)", re.IGNORECASE)
_RE_NUM = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def parsear_history_query(texto: str) -> pd.DataFrame:
    """Parsea un .txt de History Query de RS2.

    Bloques ``HQ n Stage k`` con columnas X, Y, Stage Time, variable. El
    "Stage Time" es tiempo CONTINUO del modelo. Devuelve un DataFrame largo con
    columnas: ``hq``, ``stage``, ``x``, ``y``, ``stage_time``, ``valor``.
    """
    filas = []
    hq = stage = None
    for linea in texto.splitlines():
        m = _RE_CABECERA.search(linea)
        if m:
            hq, stage = int(m.group(1)), int(m.group(2))
            continue
        if hq is None:
            continue
        nums = _RE_NUM.findall(linea)
        if len(nums) >= 4:
            x, y, st, val = (float(nums[0]), float(nums[1]),
                             float(nums[2]), float(nums[3]))
            filas.append((hq, stage, x, y, st, val))
    return pd.DataFrame(filas,
                        columns=["hq", "stage", "x", "y", "stage_time", "valor"])


def listar_incrementos(df_u: pd.DataFrame) -> pd.DataFrame:
    """Marca cada stage como CARGA (pico de u positivo) o DESCARGA/REBOTE.

    ``df_u`` es la salida de :func:`parsear_history_query` para el punto de PWP.
    """
    reg = []
    for (hq, stage), g in df_u.groupby(["hq", "stage"]):
        pico = g["valor"].abs().max()
        signo = g.loc[g["valor"].abs().idxmax(), "valor"]
        reg.append((hq, stage, float(signo),
                    "CARGA" if signo > 0 else "DESCARGA/REBOTE"))
    return pd.DataFrame(reg, columns=["hq", "stage", "pico_u", "tipo"])


def extraer_stage(df_largo: pd.DataFrame, stage: int,
                  hq_s: Optional[int] = None,
                  hq_u: Optional[int] = None) -> pd.DataFrame:
    """Extrae un stage a un DataFrame limpio t, s, u con tiempo local en 0.

    ``hq_s`` y ``hq_u`` seleccionan los puntos de consulta (History Query) de
    asentamiento y presión de poro; si se omiten se toma el primer HQ disponible.
    El "Stage Time" continuo se reinicia a 0 al inicio del stage.
    """
    g = df_largo[df_largo["stage"] == stage]
    if g.empty:
        raise ValueError(f"No hay datos para el stage {stage}.")

    t0 = g["stage_time"].min()
    datos: Dict[str, pd.Series] = {}

    def _serie(hq):
        sub = g if hq is None else g[g["hq"] == hq]
        sub = sub.sort_values("stage_time")
        return sub["stage_time"].to_numpy() - t0, sub["valor"].to_numpy()

    hqs = sorted(g["hq"].unique())
    if hq_s is None and hqs:
        hq_s = hqs[0]
    if hq_u is None and len(hqs) > 1:
        hq_u = hqs[1]
    elif hq_u is None:
        hq_u = hqs[0] if hqs else None

    ts, vs = _serie(hq_s)
    salida = {"t": ts, "s": vs}
    if hq_u is not None and hq_u != hq_s:
        tu, vu = _serie(hq_u)
        # Alinear u a los tiempos de s por interpolación si difieren las mallas.
        if not np.array_equal(ts, tu):
            vu = np.interp(ts, tu, vu)
        salida["u"] = vu
    out = pd.DataFrame(salida)
    return out
