import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect("metrics.db")
cursor = conn.cursor()

# Datos de prueba
timestamp = datetime.utcnow().isoformat()
host = "TEST_HOST"
cpu_percent = 12.5
memory_percent = 45.3
disk_percent = 70.1
bytes_sent = 123456
bytes_recv = 654321
top_process_name = "python.exe"
top_process_cpu_percent = 5.7

# Insertar fila de prueba
cursor.execute("""
INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (timestamp, host, cpu_percent, memory_percent, disk_percent,
      bytes_sent, bytes_recv, top_process_name, top_process_cpu_percent))

conn.commit()

# Leer los primeros registros para verificar
cursor.execute("SELECT * FROM metrics LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
