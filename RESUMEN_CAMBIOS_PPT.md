# Resumen de cambios — PPT25092026_v2.pptx

**Autor:** Omar E. Maestre Martínez · **Director:** Alfonso M. Ramos-Cañón · **Codirector:** Andrés H. Clavijo Rincón
**Trabajo:** Influencia de la VBP en los tiempos del final de la consolidación primaria de un Bimsoil.

Se trabajó sobre una **copia** (`PPT25092026_v2.pptx`); el original `PPT25092026.pptx` no se modificó.
Se respetaron la plantilla, los colores, el pie de página («TRABAJO DE GRADO II») y **todas las citas/fuentes** existentes (Clavijo R. 2022, Duan et al. 2020, capturas RS2, etc.). No se inventó ni alteró ninguna cifra: todas provienen del manuscrito `Manuscrito_Bimsoil_SoilsRocks_v17` (Abstract, Resultados y Tabla 2), corroboradas con `BASE_MAESTRA_BIMSOIL_CONSOLIDADA.xlsx`.

Método emparejado respetado en todo momento: **t70 = punto de inflexión · t90 = Taylor · t100 = Casagrande** (no se mezclaron métodos).

La presentación pasó de **21 a 27 slides**.

---

## Cambios realizados (según lo solicitado)

1. **Slide de Agenda/Contenido** (nuevo, slide 2, tras el título): los tres objetivos específicos como hilo conductor (formulación analítica → validación → modelación numérica).

2. **Láminas de tiempos consolidadas.** Quedó **una lámina principal por tiempo** con la gráfica de **barras** por VBP (familias Experimental / Explícito / Equivalente), usando las figuras entregadas:
   - Slide 12 — **t70** (`Figura_barras_t70_metodos`, punto de inflexión)
   - Slide 13 — **t90** (`Figura_barras_t90_metodos`, Taylor)
   - Slide 14 — **t100** (`Figura_barras_t100_metodos`, Casagrande)
   Las láminas de **TENDENCIA** (antiguas 17, 19, 21) se movieron a la sección de **Anexos/Respaldo** al final (slides 25, 26, 27).

3. **Figura FEM reemplazada** por la composición limpia `Figura_FEM_modelo` (explícito vs. equivalente). Para que encajara sin distorsión en la maqueta existente, se dividió en sus dos paneles autoexplicativos —(a) explícito con bloques y (b) dominio equivalente homogéneo— y se colocaron en los huecos de modelo de:
   - Slide 10 (Objetivo 3 — representación numérica): se reemplazó la captura del modelo explícito y se actualizó el rótulo inferior a «Modelo equivalente (homogéneo)».
   - Slide 11 (Configuración RS2): se reemplazaron las dos mallas del panel derecho por los paneles limpios.
   Se eliminaron las capturas RS2 antiguas, ahora redundantes.

4. **Slides huérfanas 13 y 15** (ahora 22 y 24): **no eran duplicados** (una es inflexión-t70 y la otra Casagrande-t100). Son imágenes de página completa que **ya traen título, procedimiento y fuente incrustados** (companion de la de Taylor). Se reubicaron en la sección de Anexos, agrupadas con la lámina del método de Taylor (slide 23), con contexto dado por el separador «Anexos · Respaldo». **Ver advertencia (A) abajo.**

5. **Slide de Resultados-síntesis** (nuevo, slide 15) con las cifras clave tomadas del .docx:
   - Reducción experimental a VBP30 vs. VBP0 (promedio de 6 esfuerzos): **t70 −28.4 %, t90 −26.9 %, t100 −30.2 %**.
   - MAPE de t90 (Taylor): **Explícito 18.2 %, Equivalente 23.0 %** (**11.4 %** y **13.7 %** excluyendo la etapa de 20.47 kPa).
   - MAPE de la formulación analítica Cv,BIM vs. experimental: **16.1 %**.

6. **Slide de Conclusiones** (nuevo, slide 16) respondiendo la hipótesis: la evidencia experimental confirma la **dirección** (mayor VBP → menor tiempo); el modelo **explícito** reproduce la dirección pero **subestima la magnitud** (−11.9 % vs. −26.9 % en t90 a VBP30) y no la reproduce en VBP10; el **equivalente no preserva la dirección** → la menor deformabilidad por sí sola no explica toda la respuesta temporal.

7. **Slide de Estado de avance** (nuevo, slide 17): columna «Terminado» (formulación Cv,BIM implementada y evaluada; modelos RS2 explícito y equivalente para VBP 0/10/20/30 y 6 esfuerzos; base de datos consolidada; artículo redactado para *Soils and Rocks* con figuras a 500 dpi) y «En curso / pendiente» (revisión de directores; recorte al límite de palabras; ajustes finales de figuras).

8. **Consistencia de λ\* y κ\* en la slide de Configuración RS2** (ahora slide 11) frente a la Tabla 2 del .docx — **ver advertencia (B) abajo.** No se cambió ningún número.

9. Este resumen + la lista de anexos (abajo).

**Extra (corrección de plantilla, sin tocar contenido):** el cuadro del **número de página** era demasiado angosto y partía los números de dos cifras en dos líneas (p. ej. «1/5» en vez de «15») en todas las láminas. Se ensanchó el cuadro en todas las diapositivas/diseños; ahora los números se ven en una sola línea.

---

## Advertencias que requieren tu decisión (no cambié nada)

**(A) Rótulos «ANEXO» incrustados en imágenes (slides 22 y 24).**
Las láminas de método de inflexión (slide 22) y Casagrande (slide 24) son **mapas de bits planos**: su título, procedimiento, fuente y el rótulo «ANEXO» están quemados en la imagen y **no son editables**. La de inflexión trae «ANEXO A4», que **coincide** con el «ANEXO A4» de la lámina e–log σ′ (slide 20); la de Casagrande trae «ANEXO A2» y la de Taylor «ANEXO A1». Si quieres unificar la numeración de anexos, habría que **regenerar esas dos láminas como diapositivas nativas** (como la de Taylor). Avísame y las reconstruyo.

**(B) κ\* en la slide de Configuración RS2.**
La lámina muestra **λ\* = 0.0245** (coincide exacto con la Tabla 2, fila VBP0) y **κ\* = 0.00987**. El manuscrito (Tabla 2 y §4.1) y la base de datos reportan **κ\* = 0.0099** para VBP0. Es solo una diferencia de redondeo (0.00987 ≈ 0.0099), pero si quieres que la lámina diga exactamente **0.0099**, confírmame y lo ajusto. La lámina muestra solo el caso base congelado (VBP0), que es lo correcto para esa diapositiva; el juego completo λ\*/κ\* por VBP está en la Tabla 2 del artículo.

**(C) Idioma de las figuras de barras y FEM.**
Las figuras entregadas (`Figura_barras_*` y `Figura_FEM_modelo`) están rotuladas en **inglés** («Experimental / Explicit block / Analytical equivalent», «(a) Explicit-block mesostructure», etc.) porque son las del artículo a 500 dpi. Se usaron tal cual, como pediste. Si prefieres versiones en español para la sustentación, puedo señalarte qué re-exportar.

---

## Orden final de las 27 diapositivas

**Cuerpo principal**
1. Portada
2. Contenido (Agenda) — *nuevo*
3. Introducción
4. Antecedentes / Planteamiento del problema
5. Pregunta + Hipótesis
6. Objetivos
7. Metodología (separador)
8. Objetivo 1 — Cv,BIM (Terzaghi → Bimsoil)
9. Objetivo 2 — Validación del Cv equivalente analítico
10. Objetivo 3 — Del ensayo edométrico al modelo numérico *(figura FEM limpia)*
11. Configuración del modelo numérico en RS2 *(figura FEM limpia)*
12. **t70 — barras (punto de inflexión)**
13. **t90 — barras (Taylor)**
14. **t100 — barras (Casagrande)**
15. Resultados — síntesis — *nuevo*
16. Conclusiones — *nuevo*
17. Estado de avance — *nuevo*

**Anexos / Respaldo**
18. Separador «Anexos · Respaldo» — *nuevo*
19. Respaldo — sensibilidad de λ\* (VBP 0 %) — *nuevo* (`Figura_sensibilidad_lambda_VBP0`)
20. Trayectorias e–log σ′ — VBP 0 % / 10 % (Anexo)
21. Trayectorias e–log σ′ — VBP 20 % / 30 % (Anexo)
22. Método del punto de inflexión — t70 (Anexo, imagen) — *reubicada (antigua huérfana 13)*
23. Método de Taylor — t90 (Anexo)
24. Método de Casagrande — t100 (Anexo, imagen) — *reubicada (antigua huérfana 15)*
25. t70 — Tendencia con VBP (Anexo) — *movida desde el cuerpo*
26. t90 — Tendencia con VBP (Anexo) — *movida desde el cuerpo*
27. t100 — Tendencia con VBP (Anexo) — *movida desde el cuerpo*
