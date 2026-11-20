# ¿Cuánto te sale GTA VI hoy, en pesos?

Calculadora del precio de GTA VI en Argentina con el dólar en vivo. Muestra cuánto pagás según cómo cancelás el resumen de la tarjeta, y dónde queda Argentina en el ranking mundial de precios.

**Probala:** https://lucasselis.github.io/gta6-precio-argentina/

## Qué responde

- ¿Cuánto sale GTA VI (Estándar o Ultimate) en pesos, con la cotización de este momento?
- ¿Cuánto más pagás si dejás que la tarjeta lo pase a pesos, en vez de pagar el resumen en dólares?
- ¿Cuántos días de sueldo promedio costaba GTA V en 2013 y cuántos cuesta GTA VI hoy?
- ¿Por qué Argentina está entre los países donde el juego sale más caro, si el precio de lista es el mismo que en EE.UU.?

## Datos

| Dato | Fuente | Se actualiza |
|---|---|---|
| Cotizaciones oficial, MEP (`bolsa`) y tarjeta, precio de venta | [dolarapi.com](https://dolarapi.com) `/v1/dolares` | En vivo, cada vez que abrís la página |
| Precio de lista PS Store Argentina: US$79,99 / US$99,99 | PS Store, relevado por medios (nov-2026) | Fijo |
| RIPTE, salario promedio registrado (`158.1_REPTE_0_0_5`) | [datos.gob.ar](https://datos.gob.ar/) | Mensual, vía GitHub Actions |
| Dólar de referencia BCRA "A" 3500 (`175.1_DR_REFE500_0_0_25`), promedio mensual | [datos.gob.ar](https://datos.gob.ar/) | Mensual, vía GitHub Actions |
| Ranking de precios por país | GTA 6 Price Index de Leonida Lab, vía [LM Neuquén](https://www.lmneuquen.com/estilo-vida/gta-vi-el-precio-argentina-y-que-es-el-sexto-pais-donde-cuesta-mas-caro-todo-el-mundo-n1261618) (18/11/2026) | Fijo |

Si la API no responde, la página usa una copia de las cotizaciones del 19/11/2026 y lo avisa.

## Método

1. Precio final en USD = precio de lista × 1,21 (IVA por servicios digitales, que la PS Store suma al pagar).
2. Tres escenarios, cada uno con su cotización:
   - **Resumen en dólares, comprados al oficial:** dólar oficial.
   - **Resumen en dólares, comprados por MEP:** dólar MEP.
   - **Resumen en pesos:** dólar tarjeta (oficial + 30% de percepción a cuenta de Ganancias).
3. Ingresos Brutos es opcional (de 2% a 5,5% según la provincia) y se suma sobre el total en pesos.

**GTA V vs. GTA VI** (`analisis.py`, solo biblioteca estándar de Python):

1. Baja las dos series de datos.gob.ar con promedio mensual y se queda con los meses que tienen ambas.
2. **Control de calidad:** descarta los meses en que el RIPTE repite al centavo un valor anterior. No es un caso teórico: la fuente publicó para ago-2026 exactamente el valor de jun-2026.
3. Salario en dólares = RIPTE ÷ dólar. Días de sueldo = precio del juego en USD ÷ salario en USD × 30.
4. Escribe `data.csv`, que la página lee. Un workflow de GitHub Actions lo actualiza una vez por mes.

## Resultado (19/11/2026, edición estándar)

- Lo más barato: **$153.412**, pagando el resumen con dólares comprados al oficial.
- Lo más caro: **$199.436**, dejando que la tarjeta lo pase a pesos.
- Diferencia: **$46.024 (30%)** por la misma copia del juego.
- GTA V costaba **1,2 días** de sueldo promedio en sep-2013 (US$59,99 frente a un salario de US$1.471). GTA VI cuesta **2,2 días** (US$96,79 con IVA frente a US$1.308, con el RIPTE de jul-2026): **1,8 veces más**.

## Tests

- `test_analisis.py`: 11 tests con `unittest` sobre limpieza, el control de repetidos (con el caso real de ago-2026), salario en dólares y la comparación. Corren en GitHub Actions en cada push.
- `tests.html`: 10 tests de `calculo.js` en el navegador (IVA, conversión, Ingresos Brutos, cotizaciones faltantes o inválidas, orden de escenarios).

## Límites

- No es asesoramiento impositivo. El cargo exacto lo ves en el checkout y en tu resumen.
- La exención del 30% para plataformas de videojuegos rige desde abril de 2025 (ARCA) cuando el resumen se paga en dólares. Si cambia la normativa, cambia el cálculo.
- El ranking es una foto del 18/11/2026: los tipos de cambio de otros países no se actualizan.
- La comparación histórica usa el dólar mayorista como referencia y el precio sin impuestos para GTA V. En 2013 regía el cepo y con tarjeta se pagaba un recargo, así que GTA V salía más caro de lo que muestra el gráfico. El RIPTE cubre solo trabajadores registrados estables.

## Stack

Python (biblioteca estándar) para el pipeline de datos. HTML, CSS y JavaScript sin dependencias para la página, con gráficos en SVG dibujados a mano. GitHub Actions para tests y actualización mensual. Publicado en GitHub Pages.

---

Lucas Selis · Data Analyst & BI · [LinkedIn](https://www.linkedin.com/in/lucas-selis/)
