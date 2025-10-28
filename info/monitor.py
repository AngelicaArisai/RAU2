import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import os
import subprocess
import platform
import re  # <-- import necesario para regex

# CSV y hosts a monitorear
csv_file = "metrics_history.csv"
ping_host = "8.8.8.8"  # ejemplo de host para latencia

# Crear app Dash
app = dash.Dash(__name__)
app.title = "Mini LogicMonitor Casero"

# Función para medir latencia
def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        output = subprocess.check_output(
            ["ping", param, "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # Buscar 'time=' o 'tiempo=' seguido de números
        match = re.search(r'(?:time|tiempo)[=<]\s*(\d+(?:\.\d+)?)', output)
        if match:
            return float(match.group(1))
    except Exception:
        return None
    return None

# Layout de la app
app.layout = html.Div([
    html.H1("Mini LogicMonitor Casero", style={'textAlign': 'center'}),
    
    # Tarjetas métricas
    html.Div(id='cards', style={'display': 'flex', 'justify-content': 'space-around', 'marginBottom': '20px'}),
    
    # Gráficos
    html.Div([
        dcc.Graph(id='cpu-graph', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='memory-graph', style={'display': 'inline-block', 'width': '48%'}),
    ]),
    html.Div([
        dcc.Graph(id='disk-graph', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='network-graph', style={'display': 'inline-block', 'width': '48%'}),
    ]),
    
    # Top procesos
    html.H2("Top 5 procesos por CPU y Memoria", style={'textAlign': 'center'}),
    dcc.Graph(id='top-process-graph'),
    
    # Intervalo actualización
    dcc.Interval(
        id='interval-component',
        interval=5*1000,
        n_intervals=0
    )
])

# Callback para actualizar todo
@app.callback(
    Output('cards', 'children'),
    Output('cpu-graph', 'figure'),
    Output('memory-graph', 'figure'),
    Output('disk-graph', 'figure'),
    Output('network-graph', 'figure'),
    Output('top-process-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    # Leer CSV
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        return [html.Div()], go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    last_row = df.iloc[-1]

    # Medir latencia
    latency = ping(ping_host)

    # Colores según umbral
    def color_metric(value, thresholds=(50, 80)):
        if value < thresholds[0]:
            return 'green'
        elif value < thresholds[1]:
            return 'yellow'
        else:
            return 'red'
    
    # Tarjetas métricas
    cards = [
        html.Div([
            html.H3("CPU (%)"),
            html.H2(f"{last_row['cpu_percent']:.1f}", style={'color': color_metric(last_row['cpu_percent'])})
        ], style={'border':'1px solid black','padding':'10px','width':'20%','textAlign':'center'}),
        html.Div([
            html.H3("RAM (%)"),
            html.H2(f"{last_row['memory_percent']:.1f}", style={'color': color_metric(last_row['memory_percent'])})
        ], style={'border':'1px solid black','padding':'10px','width':'20%','textAlign':'center'}),
        html.Div([
            html.H3("Disco (%)"),
            html.H2(f"{last_row['disk_percent']:.1f}", style={'color': color_metric(last_row['disk_percent'])})
        ], style={'border':'1px solid black','padding':'10px','width':'20%','textAlign':'center'}),
        html.Div([
            html.H3(f"Latencia ({ping_host})"),
            html.H2(f"{latency if latency else 'N/A'} ms", style={'color': 'blue'})
        ], style={'border':'1px solid black','padding':'10px','width':'20%','textAlign':'center'})
    ]

    # Gráficos líneas
    fig_cpu = px.line(df, x='timestamp', y='cpu_percent', title='CPU (%)', markers=True)
    fig_cpu.update_layout(yaxis=dict(range=[0,100]))
    fig_mem = px.line(df, x='timestamp', y='memory_percent', title='Memoria (%)', markers=True)
    fig_mem.update_layout(yaxis=dict(range=[0,100]))
    fig_disk = px.line(df, x='timestamp', y='disk_percent', title='Disco (%)', markers=True)
    fig_disk.update_layout(yaxis=dict(range=[0,100]))
    fig_net = go.Figure()
    fig_net.add_trace(go.Scatter(x=df['timestamp'], y=df['bytes_sent'], mode='lines+markers', name='Bytes enviados'))
    fig_net.add_trace(go.Scatter(x=df['timestamp'], y=df['bytes_recv'], mode='lines+markers', name='Bytes recibidos'))
    fig_net.update_layout(title='Red', yaxis_title='Bytes')

    # Top 5 procesos por CPU y Memoria
    top_names = [last_row['top_process_name']] if pd.notna(last_row['top_process_name']) else []
    top_cpu = [last_row['top_process_cpu_percent']] if pd.notna(last_row['top_process_cpu_percent']) else []
    fig_top = px.bar(x=top_names, y=top_cpu, labels={'x':'Proceso','y':'CPU (%)'}, title='Top proceso por CPU')
    
    return cards, fig_cpu, fig_mem, fig_disk, fig_net, fig_top

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
