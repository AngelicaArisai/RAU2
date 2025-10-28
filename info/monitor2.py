# -*- coding: utf-8 -*-
import psutil, time, socket, json, csv, os
from datetime import datetime, timezone
import pandas as pd
import streamlit as st

# ===============================
# PARTE 1: RECOLECCIÓN DE MÉTRICAS
# ===============================

# Archivo CSV donde guardaremos los datos
host_name = socket.gethostname()
csv_file = f"{host_name}.csv"
file_exists = os.path.isfile(csv_file)

# Función para obtener métricas
def get_metrics():
    data = {}
    data['timestamp'] = datetime.now(timezone.utc).isoformat()
    data['host'] = socket.gethostname()

    # CPU (rápido)
    data['cpu_percent'] = psutil.cpu_percent(interval=0)
    data['cpu_count'] = psutil.cpu_count(logical=True)

    # Memoria
    vm = psutil.virtual_memory()
    data['memory_total'] = vm.total
    data['memory_used'] = vm.used
    data['memory_available'] = vm.available
    data['memory_percent'] = vm.percent

    # Disco
    du = psutil.disk_usage('/')
    data['disk_total'] = du.total
    data['disk_used'] = du.used
    data['disk_free'] = du.free
    data['disk_percent'] = du.percent

    # Red
    net_io = psutil.net_io_counters()
    data['bytes_sent'] = net_io.bytes_sent
    data['bytes_recv'] = net_io.bytes_recv
    data['packets_sent'] = net_io.packets_sent
    data['packets_recv'] = net_io.packets_recv

    # Uptime
    boot = psutil.boot_time()
    data['uptime_seconds'] = int(time.time() - boot)

    # Top process por CPU (rápido)
    procs = []
    for p in psutil.process_iter(['name']):
        try:
            procs.append((p.pid, p.name(), p.cpu_percent(interval=None)))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    if procs:
        top = sorted(procs, key=lambda x: x[2], reverse=True)[0]
        data['top_process_pid'] = top[0]
        data['top_process_name'] = top[1]
        data['top_process_cpu_percent'] = top[2]
    else:
        data['top_process_pid'] = None
        data['top_process_name'] = None
        data['top_process_cpu_percent'] = None

    return data

# Obtener métricas y guardar en CSV
metrics = get_metrics()
print(json.dumps(metrics, indent=2))

fieldnames = [
    'timestamp','host',
    'cpu_percent','cpu_count',
    'memory_total','memory_used','memory_available','memory_percent',
    'disk_total','disk_used','disk_free','disk_percent',
    'bytes_sent','bytes_recv','packets_sent','packets_recv',
    'uptime_seconds',
    'top_process_pid','top_process_name','top_process_cpu_percent'
]

with open(csv_file, 'a', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    writer.writerow(metrics)

# ===============================
# PARTE 2: DASHBOARD STREAMLIT
# ===============================

st.title("Dashboard")

# Archivos CSV de los servidores
csv_files = ["s1.csv", "s2.csv"]  # agrega más si tienes
dfs = [pd.read_csv(f) for f in csv_files]
all_metrics = pd.concat(dfs, ignore_index=True)

# Selector de servidor
hosts = all_metrics['host'].unique()
selected_host = st.selectbox("Selecciona un servidor", hosts)

# Filtrar datos según el servidor seleccionado
filtered_metrics = all_metrics[all_metrics['host'] == selected_host]

st.subheader(f"Métricas de {selected_host}")
st.dataframe(filtered_metrics)

# Gráficos
st.subheader("CPU %")
st.line_chart(filtered_metrics['cpu_percent'])

st.subheader("Memoria %")
st.line_chart(filtered_metrics['memory_percent'])

st.subheader("Uso de disco %")
st.line_chart(filtered_metrics['disk_percent'])
