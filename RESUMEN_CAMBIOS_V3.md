# PPT25092026_v3.pptx — Rediseño al estilo de referencia + enriquecimiento de datos

**Base:** copia de la V2, reconstruida por completo en el **estilo teal-dorado** de la presentación de referencia (`Copia_de_Presustentación_IImateo.pdf`), conservando el pie **"TRABAJO DE GRADO II"**. 29 láminas. Validado (XSD/relaciones/charts OK) y revisado lámina por lámina.

Ningún número inventado: todo proviene del manuscrito v17, del análisis `Analisis_Discusion_Conclusiones_Bimsoil.docx` y de la base `comparacion_TODOS_VBP_Director_vs_SkillModelo.csv` (126 registros), que **recalculé y verifiqué** (MAPE, sesgo, reducciones V1/V2). Método emparejado respetado: t70 = inflexión · t90 = Taylor · t100 = Casagrande.

---

## 1. Sistema de diseño adoptado (de la referencia)
- **Fondo crema** `#F2F1EC`; **teal oscuro** `#365B6D`; **dorado** `#FACB47`; teal brillante, azul y tintes (azul/rosa/verde/amarillo) para filas y tarjetas.
- **Banner-píldora teal con borde dorado** como título de cada sección.
- **Chevrons angulares** en esquina superior-derecha e inferior-izquierda; motivo **"o o o o"**.
- **Portada:** panel teal + logo (con fondo claro para contraste) + caja dorada de autores.
- **Cierre:** "Gracias por su atención / ¿Preguntas o comentarios?".
- Tipografía sans-serif (Calibri), títulos blancos en banner, cuerpo con palabras clave en negrita teal.
- Pie conservado: **"TRABAJO DE GRADO II"** (abajo-der) + "Pontificia Universidad Javeriana" (arriba-izq) + número de página (centro).

## 2. Revisión de los nuevos resultados (verificada contra el CSV)
| | t70 | t90 | t100 |
|---|---|---|---|
| MAPE Explícito | 52.5 % | **18.2 %** | **17.3 %** |
| Sesgo Explícito | −52.5 % | **+2.1 %** | **−1.9 %** |
| MAPE Equivalente | 41.1 % | 23.0 % | 26.0 % |
| Sesgo Equivalente | −40.9 % | **+22.7 %** | **+20.4 %** |

Hallazgos nuevos incorporados a la narrativa:
1. **Sesgo direccional:** explícito casi insesgado en t90/t100; equivalente sobreestima sistemáticamente (+20 a +23 %).
2. **Test de magnitud:** explícito captura ~40 % de la magnitud en VBP0→30 pero la reproduce bien en VBP10→30 (−12.5 % vs −10.5 %); la brecha está en el salto VBP0→10.
3. **Mecanismo central:** rigidez (Cc baja 0.051→0.022) es de 1er orden pero **no basta** → componente geométrica/hidráulica (tortuosidad, caminos de flujo por bloques casi impermeables).
4. **Fragilidad de t70** (3 evidencias) → degradado a anexo.
5. **Convención V2** declarada; etapa 20.47 kPa (primer escalón, INVIAS) → MAPE t90 11.4 %/13.7 % al excluirla.

## 3. Decisiones aplicadas (acordadas contigo)
- **Profundidad completa:** 3 láminas de datos nuevas → Compresibilidad e–log σ′ (+Cc), Desempeño (MAPE+sesgo), Test de magnitud.
- **t70 degradado a anexo** (con aviso de fiabilidad); el cuerpo se apoya en **t90 y t100**.
- **Gráficas priorizadas por ti** promovidas al cuerpo: **e–log σ′** (lám. 12) y **sensibilidad de λ=0.0245** (lám. 17).

## 4. Estructura (29 láminas)
1. Portada · 2. Contenido · 3. Introducción · 4. Antecedentes y planteamiento · 5. Pregunta e hipótesis · 6. Objetivos
7. Metodología · 8. Obj 1 — Formulación Cv,BIM · 9. Obj 2 — Validación del Cv (16.1 %) · 10. Obj 3 — Del ensayo al modelo (FEM) · 11. Configuración RS2 (λ*=0.0245, κ*=0.0099)
12. **Compresibilidad e–log σ′ + Cc** · 13. **t90 (Taylor)** · 14. **t100 (Casagrande)** · 15. **Desempeño: MAPE + sesgo** · 16. **Test de magnitud** · 17. **Sensibilidad de λ*** · 18. Síntesis de resultados
19. Mecanismo (rigidez + geométrico/hidráulico) · 20. Conclusiones · 21. Estado de avance · 22. Trabajos futuros · 23. Gracias
**Anexos:** 24. Divisor · 25. t70 (indicativo, con aviso) · 26. e–log σ′ ciclos VBP0/10 · 27. e–log σ′ ciclos VBP20/30 · 28. Construcciones gráficas (Taylor/inflexión/Casagrande) · 29. Tendencias con la VBP

## 5. Notas
- **κ\*** en la lámina de configuración ahora usa el valor exacto del manuscrito (Tabla 2): **0.0099** (la V2 mostraba 0.00987).
- Las figuras de barras y FEM siguen en **inglés** (son las del artículo a 500 dpi), como en la V2.
- La V2 (`PPT25092026_v2.pptx`, estilo Javeriana azul) se conserva intacta por si quieres volver a ella.
