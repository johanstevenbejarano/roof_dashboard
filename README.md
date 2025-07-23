# 🏠 Roof Damage Detection Dashboard

Este repositorio contiene un sistema completo de visualización y análisis interactivo para daños en techos a partir de imágenes aéreas, integrando modelos de **detección (YOLOv8)** y **segmentación (SegFormer)**. El sistema está desplegado como una aplicación web en la nube mediante **Render**, con backend en Flask y frontend en Dash.

## 🔗 Demo en vivo

Accede al dashboard en línea:  
👉 [https://roof-dashboard.onrender.com](https://roof-dashboard.onrender.com)

> ⚠️ Nota: En modo gratuito, puede entrar en reposo por inactividad. El reinicio puede tardar unos segundos.

---

## 🎯 Objetivo del Proyecto

El propósito de este proyecto es brindar una herramienta interactiva para:

- Explorar métricas generadas por modelos de visión por computadora aplicados a techos.
- Visualizar resultados por clusters usando análisis no supervisado (KMeans).
- Identificar las imágenes más relevantes con base en confianza, densidad de daño, etc.
- Permitir la descarga directa de los datos analizados en CSV.

---

## 📁 Estructura del Repositorio

```
roof_dashboard/
├── app.py                  # App principal de Dash/Flask
├── requirements.txt        # Dependencias del entorno
├── Procfile                # Para despliegue en Render
├── runtime.txt             # Versión de Python para Render
├── assets/
│   └── styles.css          # Estilos personalizados
```

---

## 🧠 Modelos utilizados

Los modelos fueron entrenados y exportados previamente, y sus resultados se usaron como entrada al dashboard:

- 🔎 **YOLOv8** para detección de defectos (bounding boxes)
- 🟩 **SegFormer** para segmentación semántica de techos

Los resultados están disponibles públicamente en Hugging Face:
- 🔗 [HuggingFace Repo - jobejaranom/yolo-roof-damage](https://huggingface.co/jobejaranom/yolo-roof-damage)
- 🔗 [HuggingFace Repo - jobejaranom/segformer-roofdefects](https://huggingface.co/jobejaranom/segformer-roofdefects)

---

## 📊 Funcionalidades del Dashboard

### 1. 🧾 Resumen
- Tarjetas con KPIs: total imágenes, clusters, promedios de métricas.
- Descarga CSV completa.

### 2. 🔍 Exploración
- Galería por cluster con thumbnails.
- Dropdown dinámico para cambiar de cluster.

### 3. 📈 Análisis Estadístico
- Histograma interactivo + Boxplot por cluster.
- Matriz de correlación de métricas.

### 4. 🏆 Top imágenes
- Visualización de imágenes top según cualquier métrica seleccionada.
- Slider para ajustar cuántas mostrar.

---

## ⚙️ Tecnologías usadas

- **Python 3.10**
- **Plotly Dash**
- **Dash Bootstrap Components**
- **Flask + Gunicorn**
- **Render.com** para despliegue
- **GitHub** como control de versiones
- **Hugging Face** para almacenar inferencias

---

## 🚀 Cómo desplegar (local)

```bash
# Clonar repositorio
git clone https://github.com/tu_usuario/roof_dashboard.git
cd roof_dashboard

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar localmente
python app.py
```

---

## ☁️ Despliegue en Render

Este proyecto fue desplegado con éxito en Render siguiendo estos pasos:

1. Agregar `Procfile`, `runtime.txt`, `requirements.txt`
2. Agregar `server = app.server` en `app.py`
3. Subir repositorio a GitHub
4. Crear Web Service en Render conectado al repo
5. Usar comandos:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:server`

---


---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y adaptarlo libremente citando la fuente.