import unittest

import analisis


class TestLimpieza(unittest.TestCase):
    def test_descarta_meses_con_una_serie_vacia(self):
        filas = [["2013-09-01", 8440.0, 5.8], ["2013-10-01", None, 5.9], ["2013-11-01", 8700.0, None]]
        self.assertEqual([f["mes"] for f in analisis.limpiar(filas)], ["2013-09"])

    def test_descarta_valores_no_positivos(self):
        self.assertEqual(analisis.limpiar([["2013-09-01", 0, 5.8], ["2013-10-01", 8500.0, -1]]), [])

    def test_ordena_por_mes(self):
        filas = [["2014-01-01", 2.0, 1.0], ["2013-12-01", 1.0, 1.0]]
        self.assertEqual([f["mes"] for f in analisis.limpiar(filas)], ["2013-12", "2014-01"])


class TestRepetidos(unittest.TestCase):
    def test_descarta_valor_copiado_de_dos_meses_antes(self):
        # Caso real: el RIPTE de ago-2026 vino igual al de jun-2026.
        filas = [
            {"mes": "2026-06", "ripte": 1915878.76},
            {"mes": "2026-07", "ripte": 1946028.12},
            {"mes": "2026-08", "ripte": 1915878.76},
        ]
        limpias, descartados = analisis.descartar_repetidos(filas)
        self.assertEqual([f["mes"] for f in limpias], ["2026-06", "2026-07"])
        self.assertEqual(descartados, ["2026-08"])

    def test_no_descarta_valores_distintos(self):
        filas = [{"mes": f"2026-0{i}", "ripte": 100.0 + i} for i in range(1, 6)]
        self.assertEqual(analisis.descartar_repetidos(filas)[1], [])


class TestCalculo(unittest.TestCase):
    def test_salario_en_dolares(self):
        filas = analisis.salario_en_dolares([{"mes": "2013-09", "ripte": 8440.0, "dolar": 5.8}])
        self.assertAlmostEqual(filas[0]["salario_usd"], 1455.17, places=2)

    def test_peso_del_juego(self):
        self.assertAlmostEqual(analisis.peso_del_juego(60, 1200), 0.05)

    def test_salario_cero_no_divide(self):
        with self.assertRaises(ValueError):
            analisis.peso_del_juego(60, 0)

    def test_mes_sin_publicar_usa_el_ultimo_disponible(self):
        filas = [{"mes": "2026-06"}, {"mes": "2026-07"}]
        self.assertEqual(analisis.fila_del_mes(filas, "2026-11")["mes"], "2026-07")

    def test_mes_anterior_a_los_datos_falla(self):
        with self.assertRaises(LookupError):
            analisis.fila_del_mes([{"mes": "2026-07"}], "2013-09")

    def test_resumen_compara_con_iva(self):
        filas = [
            {"mes": "2013-09", "salario_usd": 1200.0},
            {"mes": "2026-07", "salario_usd": 1200.0},
        ]
        r = analisis.resumen(filas)
        self.assertAlmostEqual(r["gta_v_peso"], 59.99 / 1200)
        self.assertAlmostEqual(r["gta_vi_peso_con_iva"], 79.99 * 1.21 / 1200)
        self.assertAlmostEqual(r["veces"], 79.99 * 1.21 / 59.99)


if __name__ == "__main__":
    unittest.main()
