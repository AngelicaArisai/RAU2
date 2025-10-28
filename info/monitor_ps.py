import psutil, time, socket, json, csv, os
from datetime import datetime, timezone

# Archivo CSV donde guardaremos los datos
csv_file = "metrics_history.csv"
file_exists = os.path.isfile(csv_file)

# Función para obtener métricas
def get_metrics():
    data = {}
    data['timestamp'] = datetime.now(timezone.utc).isoformat()
    data['host'] = socket.gethostname()

    # CPU
    data['cpu_percent'] = psutil.cpu_percent(interval=1)
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

    # Top process por CPU
    procs = []
    for p in psutil.process_iter(['name']):
        try:
            procs.append((p.pid, p.name(), p.cpu_percent(interval=0.1)))
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

# Obtener métricas
metrics = get_metrics()

# Imprimir JSON en pantalla
print(json.dumps(metrics, indent=2))

# Guardar en CSV
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
        writer.writeheader()  # Escribir cabecera solo si el archivo no existe
    writer.writerow(metrics)
