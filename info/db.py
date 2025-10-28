import sqlite3

# Conectar y crear tabla si no existe
conn = sqlite3.connect("metrics.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS metrics (
    timestamp TEXT,
    host TEXT,
    cpu_percent REAL,
    memory_percent REAL,
    disk_percent REAL,
    bytes_sent INTEGER,
    bytes_recv INTEGER,
    top_process_name TEXT,
    top_process_cpu_percent REAL
)
""")
conn.commit()
conn.close()

# ---- Aquí continúa tu código de monitor ----
# import psutil, datetime, socket, etc.
# recolectas métricas y las insertas en la base de datos
