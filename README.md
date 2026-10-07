# Tiempos y grado de consolidación — RS2

Aplicativo en **Python + Streamlit** para calcular los tiempos característicos
**t50 / t70 / t90 / t100** y el **grado de consolidación U(t)** a partir de
curvas asentamiento–tiempo y de disipación de presión de poro exportadas de
**RS2 (Rocscience)**.

Todo se construye desde cero: **no se usa ningún archivo auxiliar, plantilla,
CSV de ejemplo ni dependencia externa de datos**. Los datos de ejemplo y los de
los tests los **genera el propio código** con las fórmulas de la teoría de
Terzaghi (`core/datos_sinteticos.py`).

## Arquitectura (lógica separada de la interfaz)

La numérica es un conjunto de **módulos puros** (solo numpy/scipy, sin
Streamlit), de modo que la interfaz puede reescribirse en JavaScript sin tocar
los cálculos.

```
core/metodos.py          — funciones puras: los 4 métodos + cv + factores Tv
core/datos_sinteticos.py — generador Terzaghi (ejemplo y tests)
core/io_datos.py         — lectura CSV/Excel, autodetección de columnas, RS2 .txt
app.py                   — interfaz Streamlit (solo presentación)
tests/test_metodos.py    — validación con el Terzaghi sintético interno
requirements.txt, README.md
```

## Instalación y ejecución

```bash
pip install -r requirements.txt
streamlit run app.py
```

En la barra lateral: elige el modo de entrada. Para probar sin datos propios,
pulsa **«Cargar ejemplo (sintético)»** → **«Generar datos de ejemplo»**.

## Entrada de datos

Una fila por paso de tiempo. Encabezados auto-detectados por nombre (con
sinónimos); unidades arbitrarias y **conservadas** (todos los tiempos salen en
la unidad del archivo):

| Clave | Variable            | Sinónimos reconocidos                                             |
|-------|---------------------|-------------------------------------------------------------------|
| `t`   | tiempo              | `t`, `tiempo`, `time`, `stage time`                               |
| `s`   | asentamiento        | `s`, `Sy`, `asentamiento`, `settlement`, `vertical displacement`  |
| `u`   | exceso de PWP       | `u`, `pwp`, `excess pore`, `excess pwp`, `exceso`, `poro`         |

Modos de entrada:

1. **Subir CSV/Excel** con selector de hoja y mapeo manual de columnas si falla
   la autodetección.
2. **Entrada manual** pegando una tabla (coma o tabulador) con encabezados.
3. **Cargar ejemplo**: llama al generador sintético interno.

El asentamiento se toma **relativo a la primera lectura** y se **auto-detecta el
signo** para que sea creciente. Para los cálculos con log/ln se filtra `t > 0`.

### Formato nativo RS2 «History Query» (.txt por etapas)

`core/io_datos.py` incluye un lector para los `.txt` de History Query (bloques
`HQ n Stage k`, columnas `X, Y, Stage Time, variable`). El *Stage Time* es
tiempo **continuo**; el lector reinicia el tiempo local a 0 por stage, marca los
incrementos de carga (pico de `u` positivo) y extrae un stage a un DataFrame
limpio `t, s, u` (permite elegir el HQ de asentamiento y el de presión).

## Métodos (teoría y constantes fijas)

`t70` se toma **siempre** en U = 70.15 % (0.7015). La interpolación de tiempos
es **siempre por primer cruce** del umbral, con interpolación lineal entre los
dos puntos que lo encierran.

1. **Casagrande (log t).** `s0` por parábola (t2 = 4·t1); `s100`/`t100` por
   intersección de la tangente de máxima pendiente (primaria) con la del tramo
   final (secundaria); anclaje `s_U = s0 + U·(s100 − s0)`. Ajustables: `t1`,
   ventana de la tangente secundaria.
2. **Taylor (√t).** `s0` por recta inicial (`n_init` puntos); `t90` por la recta
   a pendiente inicial/1.15; `s100 = s0 + (10/9)(s90 − s0)`,
   `s50 = s0 + (5/9)(s90 − s0)`, `s70 = s0 + 0.7015(s100 − s0)`. Ajustable:
   `n_init`.
3. **Punto de inflexión (Cour/Mesri).** `D_k = |Δs/Δln t|`; su máximo es
   `t_i = t70` (Tv = 0.405); `t50 = 0.486·t70`, `t90 = 2.094·t70`,
   `t100 = 4.398·t70`.
4. **Disipación de PWP.** `U(t) = 1 − u/u0` (u0 = pico del exceso); `t50`:
   u/u0 = 0.50; `t70`: 0.2985; `t90`: 0.10; `t100` (EOP): u/u0 ≤ 0.01.

Factores de tiempo: 50 %→0.197, 70.15 %→0.405, 90 %→0.848, 99 %→1.781; para
U > 60 %, `Tv = 1.781 − 0.933·log10(100 − U%)`. **No se modifican** 1.15, 10/9,
5/9, 0.7015 ni los Tv.

**cv (opcional).** Con la trayectoria de drenaje `H_dr` y la condición
(simple/doble), `cv = Tv·H_dr²/t` por método y tiempo.

## Salidas

- Tabla **t50/t70/t90/t100** por cada método aplicable (unidad del archivo),
  mostrando todos los métodos juntos (nunca un solo número sin exponer las
  diferencias).
- Gráficas de **verificación** de cada construcción (Casagrande s–log t con las
  dos tangentes; Taylor s–√t con las dos rectas; inflexión ds/d(ln t)–log t con
  el pico; PWP U(t)–log t con marcas).
- **Exportación** de resultados a CSV y Excel.

## Generador sintético (ejemplo y tests)

`core/datos_sinteticos.py` implementa Terzaghi:

- U(Tv): `Tv = (π/4)U²` (U ≤ 0.60) o `U = 1 − (8/π²)exp(−π²Tv/4)` (U > 0.60).
- u/u0 en el plano medio: `Σ (2/M)·sin(M·Z)·exp(−M²Tv)`, `M = (2m+1)π/2`, `Z = 1`.
- Rejilla de Tv log-espaciada de 0.002 a 1.8 (~40 puntos) + puntos tempranos;
  `t = 2000·Tv`; `s = U·10 mm`; `u = 100 kPa·(u/u0)`.

## Validación (tests)

```bash
pytest -q
```

Con el Terzaghi sintético:

- **Taylor** y **punto de inflexión** recuperan los factores dentro del 5 %
  (`t50/K ≈ 0.197`, `t70/K ≈ 0.405`, `t90/K ≈ 0.848`, con `K = 2000`).
- **Casagrande** se valida con tolerancia más amplia: el Terzaghi sintético es
  consolidación primaria pura (sin rama secundaria) y se trunca en U ≈ 99 %, por
  lo que `s100` queda subestimado y sus tiempos son menos precisos — es la
  limitación que la metodología documenta para Casagrande sin tramo secundario.
- **Disipación** en el plano medio da tiempos mayores (rezago del punto medio);
  el test comprueba que U(t) es monótona creciente y alcanza un grado muy alto.
