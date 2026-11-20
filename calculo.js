// Lógica pura del cálculo: sin DOM ni red, para poder testearla aparte (tests.html).

const IVA = 0.21;

const EDICIONES = {
  estandar: { nombre: "Estándar", usd: 79.99 },
  ultimate: { nombre: "Ultimate", usd: 99.99 },
};

// Cada escenario dice qué cotización de dolarapi.com usa y por qué.
const ESCENARIOS = [
  {
    id: "oficial",
    nombre: "Resumen en dólares, comprados al oficial",
    detalle: "Comprás los dólares en tu home banking y pagás el resumen en dólares. Sin percepción del 30%.",
    casa: "oficial",
  },
  {
    id: "mep",
    nombre: "Resumen en dólares, comprados por MEP",
    detalle: "Comprás dólares MEP en tu broker y pagás el resumen en dólares. Sin percepción del 30%.",
    casa: "bolsa",
  },
  {
    id: "tarjeta",
    nombre: "Resumen en pesos",
    detalle: "Dejás que la tarjeta lo convierta a pesos. Se cobra la percepción del 30% a cuenta de Ganancias (dólar tarjeta).",
    casa: "tarjeta",
  },
];

// Precio final en USD: la PS Store muestra el precio sin IVA y lo suma al pagar.
function precioConIva(usd) {
  return redondear(usd * (1 + IVA), 2);
}

// Pesos = USD con IVA × cotización × (1 + Ingresos Brutos de la provincia, si aplica).
function costoEnPesos(usd, cotizacion, iibb = 0) {
  if (!(usd > 0) || !(cotizacion > 0)) return NaN;
  if (iibb < 0 || iibb > 0.2) throw new RangeError("Ingresos Brutos fuera de rango: " + iibb);
  return Math.round(precioConIva(usd) * cotizacion * (1 + iibb));
}

// dolares: respuesta de /v1/dolares → { casa: venta }
function cotizacionesPorCasa(dolares) {
  const out = {};
  for (const d of dolares) {
    if (d && d.casa && d.venta > 0) out[d.casa] = d.venta;
  }
  return out;
}

// Devuelve los escenarios con su costo, ordenados del más barato al más caro.
function calcularEscenarios(usd, cotizaciones, iibb = 0) {
  return ESCENARIOS
    .filter((e) => cotizaciones[e.casa] > 0)
    .map((e) => ({ ...e, cotizacion: cotizaciones[e.casa], pesos: costoEnPesos(usd, cotizaciones[e.casa], iibb) }))
    .sort((a, b) => a.pesos - b.pesos);
}

// Cuánto más caro sale el peor escenario frente al mejor (0,30 = 30%).
function brecha(escenarios) {
  if (escenarios.length < 2) return 0;
  const min = escenarios[0].pesos;
  const max = escenarios[escenarios.length - 1].pesos;
  return max / min - 1;
}

function redondear(x, dec) {
  const f = 10 ** dec;
  return Math.round(x * f) / f;
}

if (typeof module !== "undefined") {
  module.exports = { IVA, EDICIONES, ESCENARIOS, precioConIva, costoEnPesos, cotizacionesPorCasa, calcularEscenarios, brecha };
}
