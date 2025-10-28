import unittest
import pandas as pd
import os
from monitor import update_dashboard, csv_file

class TestSecurity(unittest.TestCase):

    def test_csv_corrupto(self):
        # Crear un CSV corrupto temporal
        corrupt_file = "temp_corrupt.csv"
        with open(corrupt_file, "w") as f:
            f.write("this,is,not,a,valid,csv\n123,abc,!,@,$")

        global csv_file
        original_csv = csv_file
        csv_file = corrupt_file  # apuntar a CSV corrupto

        try:
            # update_dashboard no debería lanzar excepción
            cards, fig_cpu, fig_mem, fig_disk, fig_net, fig_top = update_dashboard(0)
            # Verificar que se devuelven figuras y tarjetas aunque estén vacías
            self.assertIsInstance(cards, list)
            self.assertIsInstance(fig_cpu, pd.DataFrame.__bases__[0])  # Figuras de plotly son objetos
        finally:
            csv_file = original_csv  # restaurar CSV original
            os.remove(corrupt_file)
