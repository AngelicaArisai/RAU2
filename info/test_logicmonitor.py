import unittest
import os
import pandas as pd
from monitor import ping, csv_file  

class TestLogicMonitor(unittest.TestCase):

    def test_ping_google(self):
        """Verifica que la función ping funcione correctamente con un host válido"""
        result = ping("8.8.8.8")
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_ping_invalido(self):
        """Verifica que devuelva None al fallar"""
        result = ping("no_existe_host")
        self.assertIsNone(result)

    def test_csv_existe(self):
        """Verifica que el CSV de métricas exista"""
        self.assertTrue(os.path.exists(csv_file), "El archivo de métricas no existe")

    def test_csv_columnas(self):
        """Valida que el CSV contenga las columnas principales"""
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            columnas = ['timestamp', 'cpu_percent', 'memory_percent', 'disk_percent']
            for col in columnas:
                self.assertIn(col, df.columns, f"Falta la columna {col}")

if __name__ == '__main__':
    unittest.main()
