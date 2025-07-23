# app.py

import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc

import pandas as pd
from huggingface_hub import snapshot_download
from pathlib import Path
import plotly.express as px

# --- Descargar carpeta dashboard_data desde Hugging Face ---
HF_REPO = "jobejaranom/roof-dashboard-data"
LOCAL_DIR = Path("dashboard_data")

hf_dir = snapshot_download(
    repo_id=HF_REPO,
    allow_patterns="dashboard_data/*",
    local_dir=LOCAL_DIR,
    repo_type="model",
    local_dir_use_symlinks=False
)

CSV_PATH = Path(hf_dir) / "dashboard_data" / "df_metrics_clustered.csv"
assert CSV_PATH.exists(), f"❌ No se encontró {CSV_PATH}"

df_metrics = pd.read_csv(str(CSV_PATH))
print(f"✅ Datos cargados: {df_metrics.shape[0]} imágenes, {df_metrics.shape[1]} columnas.")

# --- Inicializar App ---
# Fuente moderna desde Google Fonts (Inter)
external_stylesheets = [
    dbc.themes.BOOTSTRAP,  # Base
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap"
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# Establecer la fuente global con un estilo personalizado
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dashboard de Daños en Techos</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f8f9fa;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- Layout Base con Tabs ---
app.layout = dbc.Container([
    html.H1("🏚️ Roof Damage Dashboard", className="text-center my-4"),

    dbc.Tabs([
        dbc.Tab(label="📊 Resumen General", tab_id="tab-general"),
        dbc.Tab(label="🖼️ Explorador Visual", tab_id="tab-visual"),
        dbc.Tab(label="📈 Distribuciones", tab_id="tab-dist"),
        dbc.Tab(label="🔍 Top Imágenes", tab_id="tab-top"),
    ], id="tabs", active_tab="tab-general"),

    html.Div(id="tab-content", className="mt-4")

], fluid=True, className="px-4 pt-2")

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "tab-general":
        n_img = df_metrics.shape[0]
        n_clusters = df_metrics["cluster"].nunique()
        metricas = ['damage_count', 'damage_density', 'mean_confidence', 'max_confidence']

        return dbc.Container([

            # --- TARJETAS RESUMEN ---

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("🖼️ Total Imágenes", className="card-title"),
                    html.H2(f"{n_img}", className="card-text")
                ])
            ], color="primary", inverse=True), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("🔢 Clusters Detectados", className="card-title"),
                    html.H2(f"{n_clusters}", className="card-text")
                ])
            ], color="info", inverse=True), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Prom. Densidad de Daño", className="card-title"),
                    html.H2(f"{df_metrics['damage_density'].mean():.2f}", className="card-text")
                ])
            ], color="danger", inverse=True), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("🎯 Prom. Confianza", className="card-title"),
                    html.H2(f"{df_metrics['mean_confidence'].mean():.2f}", className="card-text")
                ])
            ], color="success", inverse=True), width=3)
        ], className="mb-4"),


            html.Hr(),

            html.H4("📋 Tabla de Imágenes y Métricas"),
            dash_table.DataTable(
                id="tabla-metricas",
                columns=[{"name": col, "id": col} for col in df_metrics.columns],
                data=df_metrics.to_dict("records"),
                page_size=10,
                filter_action="native",
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center"},
                style_header={"backgroundColor": "#343a40", "color": "white", "fontWeight": "bold"}
            ),

            html.Div([
                html.Hr(),
                html.H4("⬇️ Descargar Tabla de Métricas como CSV"),
                html.Button("📥 Descargar CSV", id="download-button", n_clicks=0, className="btn btn-success"),
                dcc.Download(id="download-csv")
            ], className="my-4"),

            html.Hr(),

            html.H4("🧬 Visualización PCA por Cluster"),
            dcc.Graph(
                figure=px.scatter(
                    df_metrics,
                    x="PCA1",
                    y="PCA2",
                    color=df_metrics["cluster"].astype(str),
                    hover_name="image",
                    title="Espacio PCA de las Imágenes",
                    color_discrete_sequence=px.colors.qualitative.Set2
                ).update_traces(marker=dict(size=9, opacity=0.75))
            )
        ])

    # --- Tab Visual ---
    elif active_tab == "tab-visual":
        unique_clusters = sorted(df_metrics["cluster"].unique())

        return dbc.Container([
            html.H5("🎯 Selecciona un cluster para ver las imágenes:"),
            dcc.Dropdown(
                id="cluster-dropdown",
                options=[{"label": f"Cluster {c}", "value": c} for c in unique_clusters],
                value=unique_clusters[0],
                clearable=False,
                className="mb-3"
            ),
            dcc.Loading(
                id="loading-visual",
                type="default",
                children=html.Div(id="gallery-output")
            )
        ])

    # --- Tab Distribuciones ---
    elif active_tab == "tab-dist":
        metricas = ['damage_count', 'damage_density', 'mean_confidence', 'max_confidence']
        return dbc.Container([
            html.H5("📌 Selecciona una métrica para analizar:"),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[{"label": m.replace("_", " ").capitalize(), "value": m} for m in metricas],
                value=metricas[0],
                clearable=False,
                className="mb-4"
            ),
            dcc.Loading([
                dcc.Graph(id="histograma"),
                dcc.Graph(id="boxplot"),
                dcc.Graph(id="correlacion")
            ])
        ])

    # --- Tab Top ---
    elif active_tab == "tab-top":
        metricas = ['damage_count', 'damage_density', 'mean_confidence', 'max_confidence']
        return dbc.Container([
            html.H5("📌 Selecciona la métrica para ver las imágenes más extremas:"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="top-metric-dropdown",
                        options=[{"label": m.replace("_", " ").capitalize(), "value": m} for m in metricas],
                        value=metricas[0],
                        clearable=False
                    )
                ], width=6),

                dbc.Col([
                    dcc.Slider(
                        id="top-n-slider",
                        min=1,
                        max=10,
                        value=3,
                        marks={i: str(i) for i in range(1, 11)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=6)
            ], className="mb-4"),

            dcc.Loading(
                id="loading-top",
                type="circle",
                children=html.Div(id="top-images-output")
            )
        ])

    return html.Div("⚠️ Tab no reconocida.")

# --- Callbacks restantes (no se modifican) ---
import logging

# --- Configuración de logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- Callback 1: Galería por cluster ---
@app.callback(
    Output("gallery-output", "children"),
    Input("cluster-dropdown", "value")
)
def update_gallery(selected_cluster):
    logging.info(f"🖼️ Galería: cluster seleccionado = {selected_cluster}")
    subset = df_metrics[df_metrics["cluster"] == selected_cluster].head(12)
    cards = []

    for _, row in subset.iterrows():
        image_name = row["image"]
        img_url = f"https://huggingface.co/jobejaranom/yolo-roof-damage/resolve/main/train_inference/{image_name}"
        card = dbc.Col(dbc.Card([
            html.Img(src=img_url, style={"width": "100%", "borderRadius": "5px"}),
            dbc.CardBody([
                html.H6(image_name, className="card-title", style={"fontSize": "12px"}),
                html.P(f"Confianza: {row['mean_confidence']:.2f}", style={"fontSize": "12px"}),
                html.P(f"Densidad: {row['damage_density']:.2f}", style={"fontSize": "12px"}),
            ])
        ]), width=3, className="mb-4")
        cards.append(card)

    return dbc.Row(cards)

# --- Callback 2: Histograma de métrica ---
@app.callback(Output("histograma", "figure"), Input("metric-dropdown", "value"))
def update_histograma(col):
    logging.info(f"📊 Histograma: métrica seleccionada = {col}")
    fig = px.histogram(
        df_metrics,
        x=col,
        nbins=30,
        marginal="box",
        title=f"📈 Distribución de {col.replace('_', ' ').capitalize()}",
        color_discrete_sequence=["cornflowerblue"]
    )
    fig.update_traces(
        hovertemplate=f"{col.replace('_', ' ').capitalize()}: %{{x}}<br>Frecuencia: %{{y}}<extra></extra>"
    )
    fig.update_layout(
        height=350,
        template="plotly_white",
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig


# --- Callback 3: Boxplot por cluster ---
@app.callback(Output("boxplot", "figure"), Input("metric-dropdown", "value"))
def update_boxplot(col):
    logging.info(f"📦 Boxplot: métrica seleccionada = {col}")
    fig = px.box(
        df_metrics,
        x="cluster",
        y=col,
        points="all",
        color="cluster",
        title=f"📦 {col.replace('_', ' ').capitalize()} por Cluster",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(
        hovertemplate=f"Cluster: %{{x}}<br>{col.replace('_', ' ').capitalize()}: %{{y:.2f}}<extra></extra>"
    )
    fig.update_layout(
        height=350,
        template="plotly_white",
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig

# --- Callback 4: Matriz de correlación ---
@app.callback(Output("correlacion", "figure"), Input("metric-dropdown", "value"))
def update_corr(_):
    logging.info("🔗 Matriz de correlación actualizada")
    metricas = ['damage_count', 'damage_density', 'mean_confidence', 'max_confidence']
    corr = df_metrics[metricas].corr()
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        title="🔗 Matriz de Correlación entre Métricas"
    )
    fig.update_layout(
        height=400,
        template="plotly_white",
        margin=dict(l=30, r=30, t=50, b=30),
        coloraxis_colorbar=dict(title="Correlación", ticksuffix=""),
    )
    return fig


# --- Callback 5: Imágenes top por métrica ---
@app.callback(
    Output("top-images-output", "children"),
    Input("top-metric-dropdown", "value"),
    Input("top-n-slider", "value")
)
def update_top_images(metric, top_n):
    try:
        if not metric or metric not in df_metrics.columns:
            logging.warning(f"❌ Métrica inválida: {metric}")
            return html.Div(f"❌ Métrica inválida: {metric}")

        top_n = int(top_n)
        subset = df_metrics.dropna(subset=[metric])
        if subset.empty:
            logging.warning("⚠️ No hay datos válidos para esta métrica.")
            return html.Div("⚠️ No hay datos válidos para esta métrica.")

        subset = subset.sort_values(by=metric, ascending=False).head(top_n)
        cards = []

        for _, row in subset.iterrows():
            image_name = str(row.get("image", "")).strip()
            if not image_name or not image_name.endswith(".jpg"):
                continue

            img_url = f"https://huggingface.co/jobejaranom/yolo-roof-damage/resolve/main/train_inference/{image_name}"
            value = row.get(metric)
            cluster = row.get("cluster", "N/A")

            card = dbc.Col(
                dbc.Card([
                    html.Img(src=img_url, style={"width": "100%", "borderRadius": "5px"}),
                    dbc.CardBody([
                        html.H6(image_name, style={"fontSize": "12px", "overflowWrap": "break-word"}),
                        html.P(f"{metric}: {value:.3f}" if isinstance(value, (int, float)) else f"{metric}: N/A", style={"fontSize": "13px"}),
                        html.P(f"Cluster: {cluster}", style={"fontSize": "12px"})
                    ])
                ]),
                width=3, className="mb-4"
            )
            cards.append(card)

        if not cards:
            logging.warning("⚠️ No se encontraron imágenes válidas para mostrar.")
            return html.Div("⚠️ No se encontraron imágenes válidas para mostrar.")

        logging.info(f"🎯 Top imágenes por {metric} generado (top {top_n})")
        return dbc.Row(cards)

    except Exception as e:
        logging.error(f"❌ Error en el callback de top imágenes: {e}")
        return html.Div([
            html.H5("❌ Error en el callback"),
            html.Pre(str(e))
        ])

# --- Callback 6: Descargar CSV ---
@app.callback(
    Output("download-csv", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def download_table(n_clicks):
    if df_metrics.empty:
        logging.warning("⚠️ Intento de descarga con DataFrame vacío.")
        raise ValueError("❌ El DataFrame está vacío, no hay datos para exportar.")

    logging.info(f"📥 CSV descargado exitosamente ({len(df_metrics)} filas).")
    return dcc.send_data_frame(df_metrics.to_csv, filename="roof_metrics.csv", index=False)

server = app.server

# --- Ejecutar servidor ---
if __name__ == "__main__":
    app.run(debug=True)
