"""Generador de datos sintéticos de consolidación (teoría de Terzaghi).

Todo se calcula en código con las fórmulas de la teoría unidimensional de
consolidación. No se lee ningún archivo externo: este módulo es la única
fuente de los datos de "ejemplo" de la interfaz y de los datos de los tests.

Fórmulas (NO modificar constantes ni teoría):

Grado de consolidación PROMEDIO de Terzaghi U(Tv):
    - si U <= 0.60  ->  Tv = (pi/4)*U^2        <=>  U = 2*sqrt(Tv/pi)
    - si U  > 0.60  ->  U = 1 - (8/pi^2)*exp(-pi^2*Tv/4)

Exceso de presión de poro adimensional en el plano medio (doble drenaje, Z=1):
    u/u0 = sum_{m=0}^{N} (2/M)*sin(M*Z)*exp(-M^2*Tv),
    con  M = (2m+1)*pi/2,  Z = 1,  N ~ 100.
    (en el plano medio sin(M*1) = (-1)^m).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Constantes del ejemplo (ver especificación).
S_ULT = 10.0      # asentamiento último, mm
U0 = 100.0        # exceso de presión de poro inicial, kPa
K = 2000.0        # escala temporal t = K*Tv (unidades "min")
N_SERIE = 100     # número de términos de la serie de Fourier
Z_PLANO_MEDIO = 1.0

# Frontera U = 0.60 expresada en Tv.
_TV_60 = (np.pi / 4.0) * 0.60 ** 2


def grado_consolidacion_terzaghi(Tv):
    """Grado de consolidación PROMEDIO U(Tv) de Terzaghi.

    Devuelve un escalar o un ``numpy.ndarray`` según la entrada.
    """
    Tv = np.asarray(Tv, dtype=float)
    U_bajo = 2.0 * np.sqrt(Tv / np.pi)
    U_alto = 1.0 - (8.0 / np.pi ** 2) * np.exp(-np.pi ** 2 * Tv / 4.0)
    U = np.where(Tv <= _TV_60, U_bajo, U_alto)
    return U if U.shape else float(U)


def pwp_adimensional_plano_medio(Tv, N: int = N_SERIE, Z: float = Z_PLANO_MEDIO):
    """Exceso de PWP adimensional u/u0 en el plano medio (serie de Terzaghi)."""
    Tv = np.atleast_1d(np.asarray(Tv, dtype=float))
    m = np.arange(0, N + 1)
    M = (2 * m + 1) * np.pi / 2.0            # (N+1,)
    terminos = (2.0 / M)[None, :] * np.sin(M[None, :] * Z) \
        * np.exp(-(M[None, :] ** 2) * Tv[:, None])
    uu0 = terminos.sum(axis=1)
    return uu0


def malla_tv(n_grid: int = 40) -> np.ndarray:
    """Rejilla de Tv log-espaciada de 0.002 a 1.8 más algunos puntos tempranos."""
    grid = np.logspace(np.log10(0.002), np.log10(1.8), n_grid)
    tempranos = np.array([0.0005, 0.001, 0.0015])
    Tv = np.unique(np.concatenate([tempranos, grid]))
    return Tv


def generar_ejemplo(s_ult: float = S_ULT, u0: float = U0, K_: float = K,
                    N: int = N_SERIE, n_grid: int = 40) -> pd.DataFrame:
    """Construye el DataFrame de ejemplo con columnas ``t``, ``s`` y ``u``.

    - ``t = K*Tv`` (con K=2000 -> t50~=394, t90~=1696, t100~=3562, unidades "min").
    - ``s = U(Tv)*s_ult``  con s_ult = 10 mm (U promedio de Terzaghi).
    - ``u = u0*(u/u0)``    con u0 = 100 kPa (disipación en el plano medio).
    """
    Tv = malla_tv(n_grid)
    t = K_ * Tv
    U = grado_consolidacion_terzaghi(Tv)
    s = U * s_ult
    uu0 = pwp_adimensional_plano_medio(Tv, N=N)
    u = u0 * uu0
    return pd.DataFrame({"t": t, "s": s, "u": u})


if __name__ == "__main__":  # pragma: no cover - utilidad de inspección
    df = generar_ejemplo()
    print(df.to_string(index=False))
    print(f"\nU_max (asentamiento) = {df['s'].iloc[-1] / S_ULT:.4f}")
    print(f"U_max (disipacion)   = {1 - df['u'].iloc[-1] / df['u'].max():.4f}")
