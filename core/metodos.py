"""Métodos numéricos para tiempos y grado de consolidación.

Módulo PURO: solo numpy (y, opcionalmente, scipy para utilidades). No importa
Streamlit ni toca la interfaz, de modo que puede probarse de forma aislada y la
UI puede reescribirse en otro lenguaje sin tocar la numérica.

Convenciones fijas (NO cambiar teoría ni constantes):
    * t70 se toma SIEMPRE en U = 70.15 % (0.7015) en todos los métodos.
    * La interpolación de tiempos es SIEMPRE por PRIMER cruce del umbral, con
      interpolación lineal entre los dos puntos consecutivos que lo encierran.
    * Factores 1.15, 10/9, 5/9, 0.7015 y los Tv de referencia no se modifican.

Cada método devuelve una tupla ``(tiempos, construccion)``:
    * ``tiempos``: dict con ``t50``, ``t70``, ``t90``, ``t100`` (NaN si no aplica),
      en la misma unidad de tiempo de la entrada.
    * ``construccion``: dict con los elementos geométricos para graficar la
      verificación del método.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

# --------------------------------------------------------------------------- #
# Factores de tiempo de referencia (Terzaghi).                                #
# --------------------------------------------------------------------------- #
TV_REF: Dict[float, float] = {50.0: 0.197, 70.15: 0.405, 90.0: 0.848, 99.0: 1.781}

# Tv asociado a cada etiqueta de tiempo (para retro-cálculo de cv).
TV_POR_ETIQUETA: Dict[str, float] = {
    "t50": 0.197,
    "t70": 0.405,
    "t90": 0.848,
    "t100": 1.781,  # fin de la primaria ~ 99 %
}

ETIQUETAS = ("t50", "t70", "t90", "t100")


def factor_tiempo(U_pct: float) -> float:
    """Factor de tiempo Tv para un grado de consolidación U (en %).

    Para U <= 60 %: Tv = (pi/4)*U^2. Para U > 60 %: Tv = 1.781 - 0.933*log10(100-U).
    """
    if U_pct <= 60.0:
        return (np.pi / 4.0) * (U_pct / 100.0) ** 2
    return 1.781 - 0.933 * np.log10(100.0 - U_pct)


# --------------------------------------------------------------------------- #
# Utilidades de interpolación.                                                 #
# --------------------------------------------------------------------------- #
def primer_cruce(x, y, objetivo: float) -> float:
    """Primer valor de ``x`` donde ``y`` cruza ``objetivo`` (interp. lineal).

    Recorre los puntos en orden y devuelve la interpolación lineal entre el par
    consecutivo que encierra el umbral. Funciona con ``y`` creciente o
    decreciente. Devuelve ``nan`` si no hay cruce.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    for i in range(len(x) - 1):
        y0, y1 = y[i], y[i + 1]
        if y0 == objetivo:
            return float(x[i])
        if (y0 - objetivo) * (y1 - objetivo) < 0.0:
            frac = (objetivo - y0) / (y1 - y0)
            return float(x[i] + frac * (x[i + 1] - x[i]))
    if len(y) and y[-1] == objetivo:
        return float(x[-1])
    return float("nan")


def _s_en_t(t, s, t_obj: float) -> float:
    """Asentamiento interpolado en un tiempo dado (interp. lineal)."""
    return float(np.interp(t_obj, t, s))


def _limpiar(t, s=None, u=None):
    """Ordena por t, elimina duplicados de t y descarta no-finitos."""
    t = np.asarray(t, dtype=float)
    orden = np.argsort(t)
    t = t[orden]
    salida = [t]
    for arr in (s, u):
        if arr is not None:
            salida.append(np.asarray(arr, dtype=float)[orden])
        else:
            salida.append(None)
    return tuple(salida)


# --------------------------------------------------------------------------- #
# 1) Casagrande (log t).                                                       #
# --------------------------------------------------------------------------- #
def casagrande(t, s, t1: float | None = None,
               ventana_sec: int | None = None) -> Tuple[Dict, Dict]:
    """Método de Casagrande (s vs log t).

    - ``s0`` por parábola: t1 temprano, t2 = 4*t1; s0 = s1 - (s2 - s1).
    - ``s100``/``t100`` por intersección de la tangente de máxima pendiente
      (primaria) con la tangente del tramo final (secundaria).
    - Anclaje: s_U = s0 + U*(s100 - s0) con U = 0.50, 0.7015, 0.90 e
      interpolación de t50, t70, t90 en la curva s-t.

    Parámetros ajustables: ``t1`` y ``ventana_sec`` (nº de puntos finales para
    la tangente secundaria).
    """
    t, s, _ = _limpiar(t, s)
    mask = t > 0
    t, s = t[mask], s[mask]
    if len(t) < 5:
        raise ValueError("Casagrande necesita al menos 5 puntos con t > 0.")

    L = np.log10(t)

    # --- s0 por parábola ---------------------------------------------------- #
    if t1 is None:
        t1 = float(t[1])
    t2 = 4.0 * t1
    s1 = _s_en_t(t, s, t1)
    s2 = _s_en_t(t, s, t2)
    s0 = s1 - (s2 - s1)

    # --- tangente primaria: punto de máxima pendiente en (log10 t, s) ------- #
    dsdL = np.gradient(s, L)
    k = int(np.argmax(dsdL))
    m_prim = float(dsdL[k])
    Lk, sk = float(L[k]), float(s[k])

    # --- tangente secundaria: recta a los últimos n puntos ------------------ #
    if ventana_sec is None:
        ventana_sec = max(3, len(t) // 10)
    ventana_sec = int(min(ventana_sec, len(t) - 1))
    L_sec, s_sec = L[-ventana_sec:], s[-ventana_sec:]
    b_sec, a_sec = np.polyfit(L_sec, s_sec, 1)  # s = b_sec*L + a_sec

    # --- intersección de tangentes -> t100, s100 ---------------------------- #
    if abs(m_prim - b_sec) < 1e-12:
        L100 = L[-1]
    else:
        L100 = (a_sec - sk + m_prim * Lk) / (m_prim - b_sec)
    t100 = float(10.0 ** L100)
    s100 = float(b_sec * L100 + a_sec)

    # --- anclaje de U y lectura de tiempos ---------------------------------- #
    tiempos = {}
    for U, etiqueta in ((0.50, "t50"), (0.7015, "t70"), (0.90, "t90")):
        sU = s0 + U * (s100 - s0)
        tiempos[etiqueta] = primer_cruce(t, s, sU)
    tiempos["t100"] = t100

    construccion = {
        "t": t, "s": s, "logt": L,
        "s0": s0, "s100": s100, "t100": t100,
        "tangente_primaria": {"m": m_prim, "L0": Lk, "s0": sk},
        "tangente_secundaria": {"b": float(b_sec), "a": float(a_sec)},
        "t1": t1, "t2": t2, "s1": s1, "s2": s2,
    }
    return tiempos, construccion


# --------------------------------------------------------------------------- #
# 2) Taylor (raiz de t).                                                       #
# --------------------------------------------------------------------------- #
def taylor(t, s, n_init: int = 4) -> Tuple[Dict, Dict]:
    """Método de Taylor (s vs sqrt(t)).

    - ``s0``: recta a los primeros ``n_init`` puntos en (sqrt t, s), extrapolada
      a sqrt t = 0.
    - ``t90``: recta de Taylor desde s0 con pendiente = inicial/1.15; su corte
      con la curva experimental da sqrt(t90).
    - s100 = s0 + (10/9)(s90 - s0); s50 = s0 + (5/9)(s90 - s0);
      s70 = s0 + 0.7015*(s100 - s0).

    Parámetro ajustable: ``n_init``.
    """
    t, s, _ = _limpiar(t, s)
    mask = t > 0
    t, s = t[mask], s[mask]
    if len(t) < n_init + 1:
        raise ValueError("Taylor necesita mas puntos que n_init.")

    sq = np.sqrt(t)

    # --- recta inicial y s0 ------------------------------------------------- #
    b_init, s0 = np.polyfit(sq[:n_init], s[:n_init], 1)  # s = b_init*sq + s0
    m_taylor = b_init / 1.15

    # --- corte de la recta 1.15 con la curva experimental ------------------- #
    linea = s0 + m_taylor * sq
    resid = s - linea  # positivo al inicio, cruza a cero en sqrt(t90)
    kmax = int(np.argmax(resid))
    sq90 = primer_cruce(sq[kmax:], resid[kmax:], 0.0)
    t90 = float(sq90 ** 2) if np.isfinite(sq90) else float("nan")
    s90 = float(s0 + m_taylor * sq90) if np.isfinite(sq90) else float("nan")

    # --- escalas de U ------------------------------------------------------- #
    s100 = s0 + (10.0 / 9.0) * (s90 - s0)
    s50 = s0 + (5.0 / 9.0) * (s90 - s0)
    s70 = s0 + 0.7015 * (s100 - s0)

    tiempos = {
        "t50": primer_cruce(t, s, s50),
        "t70": primer_cruce(t, s, s70),
        "t90": t90,
        "t100": primer_cruce(t, s, s100),
    }
    construccion = {
        "t": t, "s": s, "sqt": sq,
        "s0": float(s0), "b_init": float(b_init), "m_taylor": float(m_taylor),
        "sq90": sq90, "t90": t90, "s90": s90,
        "s50": float(s50), "s90_calc": float(s90), "s100": float(s100),
        "n_init": n_init,
    }
    return tiempos, construccion


# --------------------------------------------------------------------------- #
# 3) Punto de inflexión (Cour / Mesri).                                        #
# --------------------------------------------------------------------------- #
def inflexion(t, s) -> Tuple[Dict, Dict]:
    """Método del punto de inflexión.

    D_k = |(s_{k+1}-s_k)/(ln t_{k+1}-ln t_k)|; el máximo define t_i = t70
    (Tv = 0.405). El resto por cocientes de factores de tiempo:
        t50 = 0.486*t70;  t90 = 2.094*t70;  t100 = 4.398*t70.
    """
    t, s, _ = _limpiar(t, s)
    mask = t > 0
    t, s = t[mask], s[mask]
    if len(t) < 4:
        raise ValueError("Inflexion necesita al menos 4 puntos con t > 0.")

    lnt = np.log(t)
    D = np.abs(np.diff(s) / np.diff(lnt))
    k = int(np.argmax(D))
    t70 = float(np.sqrt(t[k] * t[k + 1]))  # media geométrica del intervalo pico

    tiempos = {
        "t50": 0.486 * t70,
        "t70": t70,
        "t90": 2.094 * t70,
        "t100": 4.398 * t70,
    }
    t_mid = np.sqrt(t[:-1] * t[1:])
    construccion = {"t": t, "s": s, "t_mid": t_mid, "D": D, "t70": t70, "k": k}
    return tiempos, construccion


# --------------------------------------------------------------------------- #
# 4) Módulo PWP (disipación u/u0).                                             #
# --------------------------------------------------------------------------- #
def pwp(t, u) -> Tuple[Dict, Dict]:
    """Método de disipación de presión de poro.

    u0 = u(t=0+) o el máximo del exceso; U(t) = 1 - u/u0. La disipación arranca
    en el pico de u. Umbrales:
        t50: u/u0 = 0.50;  t70: u/u0 = 0.2985;  t90: u/u0 = 0.10;
        t100 (EOP): u/u0 <= 0.01 (U >= 0.99).
    """
    t, _, u = _limpiar(t, None, u)
    if len(t) < 3:
        raise ValueError("PWP necesita al menos 3 puntos.")

    k_pico = int(np.argmax(u))
    u0 = float(u[k_pico])
    if u0 <= 0:
        raise ValueError("u0 (exceso de PWP) debe ser positivo.")

    tp = t[k_pico:]
    up = u[k_pico:]
    razon = up / u0
    U = 1.0 - razon

    tiempos = {
        "t50": primer_cruce(tp, razon, 0.50),
        "t70": primer_cruce(tp, razon, 0.2985),
        "t90": primer_cruce(tp, razon, 0.10),
        "t100": primer_cruce(tp, razon, 0.01),
    }
    construccion = {
        "t": tp, "razon": razon, "U": U, "u0": u0, "t_pico": float(t[k_pico]),
    }
    return tiempos, construccion


# --------------------------------------------------------------------------- #
# Orquestación y cv.                                                           #
# --------------------------------------------------------------------------- #
def aplicar_todos(t=None, s=None, u=None, *, t1=None, ventana_sec=None,
                  n_init: int = 4) -> Dict[str, Dict]:
    """Aplica todos los métodos aplicables según las columnas disponibles.

    Devuelve ``{nombre_metodo: {"tiempos": {...}, "construccion": {...}}}``.
    Los métodos de asentamiento requieren ``s``; el de disipación requiere ``u``.
    """
    resultados: Dict[str, Dict] = {}
    if s is not None:
        for nombre, fn, kwargs in (
            ("Casagrande", casagrande, {"t1": t1, "ventana_sec": ventana_sec}),
            ("Taylor", taylor, {"n_init": n_init}),
            ("Inflexion", inflexion, {}),
        ):
            try:
                tiempos, construccion = fn(t, s, **kwargs)
                resultados[nombre] = {"tiempos": tiempos, "construccion": construccion}
            except Exception as exc:  # pragma: no cover - robustez de UI
                resultados[nombre] = {"error": str(exc)}
    if u is not None:
        try:
            tiempos, construccion = pwp(t, u)
            resultados["PWP"] = {"tiempos": tiempos, "construccion": construccion}
        except Exception as exc:  # pragma: no cover
            resultados["PWP"] = {"error": str(exc)}
    return resultados


def calcular_cv(tiempos: Dict[str, float], H_dr: float) -> Dict[str, float]:
    """Coeficiente de consolidación cv = Tv*H_dr^2/t para cada tiempo.

    ``H_dr`` es la trayectoria de drenaje (longitud); la condición
    simple/doble drenaje se usa aguas arriba para obtener H_dr a partir del
    espesor del estrato.
    """
    cv = {}
    for etiqueta, t_val in tiempos.items():
        Tv = TV_POR_ETIQUETA.get(etiqueta)
        if Tv is None or t_val is None or not np.isfinite(t_val) or t_val <= 0:
            cv[etiqueta] = float("nan")
        else:
            cv[etiqueta] = Tv * H_dr ** 2 / t_val
    return cv


def tabla_resultados(resultados: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
    """Reduce la salida de ``aplicar_todos`` a ``{metodo: {t50,...,t100}}``."""
    tabla = {}
    for metodo, data in resultados.items():
        if "tiempos" in data:
            tabla[metodo] = {e: data["tiempos"].get(e, float("nan")) for e in ETIQUETAS}
    return tabla
