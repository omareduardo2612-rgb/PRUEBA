"""Validación de los métodos con el Terzaghi sintético interno.

Todos los datos los genera el código (``core.datos_sinteticos``): no se usa
ningún archivo, plantilla ni CSV de ejemplo externo.

Con t = K*Tv (K = 2000) los métodos de ASENTAMIENTO deben recuperar los
factores de tiempo, es decir t50/K ~= 0.197, t70/K ~= 0.405, t90/K ~= 0.848
(tolerancia 3-5 %).

El método de DISIPACIÓN en el plano medio da tiempos mayores (rezago del punto
medio): es esperado, no un error. El test solo comprueba que U(t) es monótona
creciente y que alcanza un grado de consolidación muy alto.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import metodos  # noqa: E402
from core.datos_sinteticos import K, generar_ejemplo  # noqa: E402

TV_OBJ = {"t50": 0.197, "t70": 0.405, "t90": 0.848}
TOL = 0.05  # 5 %

# Casagrande depende de un tramo de consolidación SECUNDARIA para fijar s100.
# El Terzaghi sintético es consolidación primaria pura (sin rama secundaria) y
# se trunca en U~=99 % (Tv=1.8), por lo que su s100 queda subestimado y los
# tiempos anclados se recuperan con menor precisión. Es la limitación que la
# propia skill documenta ("t100 de Casagrande sin tramo secundario claro...
# poco fiable"); por eso Casagrande se valida con una tolerancia más amplia.
TOL_CASAGRANDE = 0.25


@pytest.fixture(scope="module")
def ejemplo():
    return generar_ejemplo()


@pytest.mark.parametrize("metodo_fn", [metodos.taylor, metodos.inflexion])
def test_asentamiento_recupera_factores(ejemplo, metodo_fn):
    """Taylor y Punto de inflexión recuperan los factores dentro del 5 %."""
    tiempos, _ = metodo_fn(ejemplo["t"].to_numpy(), ejemplo["s"].to_numpy())
    for etiqueta, tv_obj in TV_OBJ.items():
        tv_calc = tiempos[etiqueta] / K
        assert np.isfinite(tv_calc), f"{metodo_fn.__name__}: {etiqueta} es NaN"
        err = abs(tv_calc - tv_obj) / tv_obj
        assert err <= TOL, (
            f"{metodo_fn.__name__} {etiqueta}: Tv={tv_calc:.4f} "
            f"vs {tv_obj:.4f} (err={err:.1%})"
        )


def test_casagrande_en_rango(ejemplo):
    """Casagrande: tiempos ordenados y en el rango (ver nota sobre secundaria)."""
    tiempos, _ = metodos.casagrande(ejemplo["t"].to_numpy(),
                                    ejemplo["s"].to_numpy())
    assert tiempos["t50"] < tiempos["t70"] < tiempos["t90"] < tiempos["t100"]
    for etiqueta, tv_obj in TV_OBJ.items():
        tv_calc = tiempos[etiqueta] / K
        assert np.isfinite(tv_calc)
        assert abs(tv_calc - tv_obj) / tv_obj <= TOL_CASAGRANDE


def test_inflexion_t70_en_tv_0405(ejemplo):
    tiempos, _ = metodos.inflexion(ejemplo["t"].to_numpy(), ejemplo["s"].to_numpy())
    assert abs(tiempos["t70"] / K - 0.405) / 0.405 <= TOL


def test_casagrande_s0_cercano_a_cero(ejemplo):
    _, c = metodos.casagrande(ejemplo["t"].to_numpy(), ejemplo["s"].to_numpy())
    # En el tramo parabólico U<=0.6, s0 teórico es 0.
    assert abs(c["s0"]) < 0.05  # mm


def test_pwp_monotona_y_alta(ejemplo):
    tiempos, c = metodos.pwp(ejemplo["t"].to_numpy(), ejemplo["u"].to_numpy())
    U = c["U"]
    # Monótona creciente (tolerando ruido numérico mínimo).
    assert np.all(np.diff(U) >= -1e-9), "U(t) de disipación no es monótona"
    # El plano medio va rezagado: a Tv=1.8 alcanza ~0.985 (por eso >= 0.98).
    assert U[-1] >= 0.98
    # Los tiempos de disipación son mayores que los de asentamiento (rezago).
    t_asent, _ = metodos.inflexion(ejemplo["t"].to_numpy(), ejemplo["s"].to_numpy())
    assert tiempos["t50"] > t_asent["t50"]


def test_pwp_umbrales_coherentes(ejemplo):
    tiempos, _ = metodos.pwp(ejemplo["t"].to_numpy(), ejemplo["u"].to_numpy())
    # Orden temporal esperado.
    assert tiempos["t50"] < tiempos["t70"] < tiempos["t90"]


def test_factor_tiempo_tabla():
    assert abs(metodos.factor_tiempo(50) - 0.197) < 0.01
    assert abs(metodos.factor_tiempo(90) - 0.848) < 0.01
    assert abs(metodos.factor_tiempo(99) - 1.781) < 0.01


def test_primer_cruce_interpola_lineal():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([0.0, 10.0, 20.0, 30.0])
    assert abs(metodos.primer_cruce(x, y, 15.0) - 1.5) < 1e-9


def test_cv_basico():
    tiempos = {"t50": 394.0, "t70": 810.0, "t90": 1696.0, "t100": 3562.0}
    cv = metodos.calcular_cv(tiempos, H_dr=5.0)
    # cv = Tv*H^2/t -> con t50=394, Tv=0.197, H=5 -> 0.197*25/394
    assert abs(cv["t50"] - 0.197 * 25.0 / 394.0) < 1e-9
