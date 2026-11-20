"""¿Cuánto salario cuesta un juego AAA? GTA V (2013) vs. GTA VI (2026).

Baja dos series de datos.gob.ar, las cruza por mes y escribe data.csv:
  - RIPTE: remuneración imponible promedio de los trabajadores estables (pesos).
  - Dólar de referencia BCRA, Comunicación "A" 3500 (mayorista), promedio mensual.

Salario en dólares = RIPTE / dólar. Peso del juego = precio en USD / salario en USD.
Solo biblioteca estándar: se corre con `python analisis.py`.
"""

import csv
import json
import sys
import urllib.request
from pathlib import Path

API = "https://apis.datos.gob.ar/series/api/series/"
RIPTE = "158.1_REPTE_0_0_5"
DOLAR = "175.1_DR_REFE500_0_0_25"
DESDE = "2012-01-01"

# Precio de lista en la PS Store, en USD.
GTA_V = {"fecha": "2013-09", "usd": 59.99}
GTA_VI = {"fecha": "2026-11", "usd": 79.99}
IVA_DIGITAL = 0.21

SALIDA = Path(__file__).with_name("data.csv")


def descargar():
    url = (
        f"{API}?ids={RIPTE},{DOLAR}&start_date={DESDE}"
        "&collapse=month&collapse_aggregation=avg&format=json&limit=1000"
    )
    # La API rechaza el User-Agent por defecto de urllib con un 403.
    req = urllib.request.Request(url, headers={"User-Agent": "gta6-precio-argentina/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def limpiar(filas):
    """Se queda con los meses que tienen las dos series y valores positivos."""
    out = []
    for fecha, ripte, dolar in filas:
        if ripte is None or dolar is None or ripte <= 0 or dolar <= 0:
            continue
        out.append({"mes": fecha[:7], "ripte": float(ripte), "dolar": float(dolar)})
    out.sort(key=lambda f: f["mes"])
    return out


def descartar_repetidos(filas, ventana=3):
    """Saca los meses cuyo RIPTE repite al centavo uno de los meses anteriores.

    Un promedio salarial no da exactamente igual dos veces: si pasa, es un error de
    carga en la fuente (en ago-2026 apareció el valor de jun-2026). Devuelve
    (filas_limpias, meses_descartados).
    """
    limpias, descartados = [], []
    for f in filas:
        previos = [p["ripte"] for p in limpias[-ventana:]]
        if f["ripte"] in previos:
            descartados.append(f["mes"])
        else:
            limpias.append(f)
    return limpias, descartados


def salario_en_dolares(filas):
    for f in filas:
        f["salario_usd"] = round(f["ripte"] / f["dolar"], 2)
    return filas


def peso_del_juego(usd, salario_usd):
    """Fracción del salario mensual que representa el juego (0,05 = 5%)."""
    if salario_usd <= 0:
        raise ValueError("salario en dólares debe ser positivo")
    return usd / salario_usd


def fila_del_mes(filas, mes):
    """La fila del mes pedido o, si todavía no se publicó, la última disponible."""
    previas = [f for f in filas if f["mes"] <= mes]
    if not previas:
        raise LookupError(f"no hay datos hasta {mes}")
    return previas[-1]


def resumen(filas):
    v = fila_del_mes(filas, GTA_V["fecha"])
    vi = fila_del_mes(filas, GTA_VI["fecha"])
    peso_v = peso_del_juego(GTA_V["usd"], v["salario_usd"])
    peso_vi = peso_del_juego(GTA_VI["usd"], vi["salario_usd"])
    peso_vi_iva = peso_del_juego(GTA_VI["usd"] * (1 + IVA_DIGITAL), vi["salario_usd"])
    return {
        "gta_v_mes": v["mes"],
        "gta_v_salario_usd": v["salario_usd"],
        "gta_v_peso": peso_v,
        "gta_vi_mes": vi["mes"],
        "gta_vi_salario_usd": vi["salario_usd"],
        "gta_vi_peso": peso_vi,
        "gta_vi_peso_con_iva": peso_vi_iva,
        "veces": peso_vi_iva / peso_v,
    }


def guardar(filas, ruta=SALIDA):
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["mes", "ripte", "dolar", "salario_usd"], lineterminator="\n")
        w.writeheader()
        for f in filas:
            w.writerow({"mes": f["mes"], "ripte": round(f["ripte"], 2), "dolar": round(f["dolar"], 4), "salario_usd": f["salario_usd"]})


def main():
    filas, descartados = descartar_repetidos(limpiar(descargar()))
    for mes in descartados:
        print(f"Aviso: RIPTE de {mes} repite un valor anterior al centavo; se descarta.")
    filas = salario_en_dolares(filas)
    if len(filas) < 100:
        sys.exit(f"Muy pocos meses con datos ({len(filas)}): no se pisa data.csv.")
    guardar(filas)
    r = resumen(filas)
    print(f"{len(filas)} meses, {filas[0]['mes']} a {filas[-1]['mes']}")
    print(f"GTA V  ({r['gta_v_mes']}): salario US${r['gta_v_salario_usd']:,.0f} -> juego = {r['gta_v_peso']:.1%}")
    print(f"GTA VI ({r['gta_vi_mes']}): salario US${r['gta_vi_salario_usd']:,.0f} -> juego = {r['gta_vi_peso']:.1%} "
          f"(con IVA {r['gta_vi_peso_con_iva']:.1%}, {r['veces']:.2f} veces GTA V)")


if __name__ == "__main__":
    main()
