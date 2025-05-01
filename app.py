import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import tempfile
import os
import datetime
from PIL import Image
import io
from matplotlib.patches import Rectangle
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, Table, TableStyle
import base64
import plotly.express as px
import plotly.graph_objects as go
import json
import math
import uuid
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(page_title="KinesioApp", page_icon="🏋️", layout="wide")

# Crear directorios necesarios si no existen
os.makedirs("temp", exist_ok=True)
os.makedirs("data", exist_ok=True)
    
# Archivo para almacenar datos de clientes
CLIENTS_FILE = "data/clients.json"
SESSIONS_FILE = "data/sessions.json"

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Título principal */
    .title {
        text-align: center;
        color: #2c3e50;
        padding-bottom: 1.5rem;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
        font-weight: 700;
        font-size: 2.5rem;
    }
    
    /* Botones */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Botón de informe */
    .report-btn {
        background-color: #2ecc71 !important;
    }
    
    .report-btn:hover {
        background-color: #27ae60 !important;
    }
    
    /* Botón de eliminación */
    .delete-btn {
        background-color: #e74c3c !important;
    }
    
    .delete-btn:hover {
        background-color: #c0392b !important;
    }
    
    /* Tarjetas de cliente */
    .client-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 4px solid #3498db;
    }
    
    .client-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .client-card h3 {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 1.3rem;
    }
    
    .client-card p {
        color: #34495e;
        margin-bottom: 5px;
        font-size: 0.95rem;
    }
    
    /* Tarjetas de medición */
    .measurement-card {
        background-color: rgba(240, 249, 255, 0.8);
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border-left: 3px solid #3498db;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Encabezados de sección */
    h2, h3, .stSubheader {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Personalización de widgets */
    .stSlider {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .stSlider > div {
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* Barra de navegación por pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px 5px 0 0;
        border: none;
        font-weight: 500;
        color: #7f8c8d;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important;
        color: white !important;
    }
    
    /* Contenedor de video */
    .stImage {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #2c3e50;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .streamlit-expanderContent {
        border-left: 2px solid #3498db;
        padding-left: 1rem;
    }
    
    /* Text inputs */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox, .stDateInput input {
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }
    
    /* Formularios */
    [data-testid="stForm"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Controles de video */
    .video-controls {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    
    /* Botones de control de frame */
    .frame-button {
        background-color: #7f8c8d !important;
        color: white !important;
        width: 60px !important;
        text-align: center !important;
    }
    
    .frame-button:hover {
        background-color: #95a5a6 !important;
    }
    
    /* Mostrar tiempo de video de manera más visible */
    .video-time {
        background-color: rgba(52, 152, 219, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    
    /* Textos informativos */
    .info-text {
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 3px solid #2ecc71;
        padding: 0.8rem;
        border-radius: 0 5px 5px 0;
        color: #2c3e50;
    }
    
    /* Textos de advertencia */
    .warning-text {
        background-color: rgba(241, 196, 15, 0.1);
        border-left: 3px solid #f1c40f;
        padding: 0.8rem;
        border-radius: 0 5px 5px 0;
        color: #2c3e50;
    }
    
    /* Custom file uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 1rem;
        background-color: rgba(52, 152, 219, 0.05);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #2980b9;
        background-color: rgba(52, 152, 219, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Funciones de utilidad para la gestión de datos
def load_clients():
    if os.path.exists(CLIENTS_FILE):
        with open(CLIENTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}
        
def save_clients(clients):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f)

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    else:
        return []
        
def save_sessions(sessions):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

# Estado de la aplicación
if "current_client" not in st.session_state:
    st.session_state.current_client = None
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "current_frame" not in st.session_state:
    st.session_state.current_frame = None
if "frame_index" not in st.session_state:
    st.session_state.frame_index = 0
if "current_video_path" not in st.session_state:
    st.session_state.current_video_path = None
if "angle_points" not in st.session_state:
    st.session_state.angle_points = []
if "line_points" not in st.session_state:
    st.session_state.line_points = []
if "frame_width" not in st.session_state:
    st.session_state.frame_width = 0
if "frame_height" not in st.session_state:
    st.session_state.frame_height = 0
if "total_frames" not in st.session_state:
    st.session_state.total_frames = 0
if "measurements" not in st.session_state:
    st.session_state.measurements = []
if "drawing_mode" not in st.session_state:
    st.session_state.drawing_mode = "line"
if "stroke_width" not in st.session_state:
    st.session_state.stroke_width = 3
if "stroke_color" not in st.session_state:
    st.session_state.stroke_color = "#FF0000"
if "canvas_result" not in st.session_state:
    st.session_state.canvas_result = None

# Funciones para el análisis de video
def process_video(video_file):
    """Procesa un video y lo almacena temporalmente"""
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    vf_path = tfile.name
    
    # Abrir el video con OpenCV
    cap = cv2.VideoCapture(vf_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Actualizar el estado
    st.session_state.current_video_path = vf_path
    st.session_state.total_frames = total_frames
    st.session_state.frame_width = width
    st.session_state.frame_height = height
    
    # Obtener el primer frame
    get_frame(0)
    
    return True

def get_frame(frame_index):
    """Obtiene un fotograma específico del video actual"""
    if st.session_state.current_video_path:
        cap = cv2.VideoCapture(st.session_state.current_video_path)
        
        # Verificar si el índice de frame es válido
        if frame_index < 0:
            frame_index = 0
        if frame_index >= st.session_state.total_frames:
            frame_index = st.session_state.total_frames - 1
        
        # Actualizar el índice de frame en el estado
        st.session_state.frame_index = frame_index
        
        # Establecer la posición del video
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # Leer el frame
        ret, frame = cap.read()
        if ret:
            # Convertir de BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.session_state.current_frame = frame_rgb
            return True
        else:
            st.error("No se pudo leer el frame del video.")
            return False
    else:
        st.error("No hay un video cargado actualmente.")
        return False

def calculate_angle(p1, p2, p3):
    """Calcula el ángulo entre tres puntos (en grados)"""
    # Vectores
    a = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    b = np.array([p3[0] - p2[0], p3[1] - p2[1]])
    
    # Calcular el ángulo
    cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_distance(p1, p2):
    """Calcula la distancia entre dos puntos"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def process_canvas_result(canvas_result, drawing_mode, joint="", description=""):
    """Procesa el resultado del canvas para extraer mediciones"""
    if not canvas_result or not canvas_result.json_data or "objects" not in canvas_result.json_data:
        return None
    
    objects = canvas_result.json_data["objects"]
    if not objects:
        return None
    
    # Obtener el último objeto dibujado
    last_object = objects[-1]
    
    if drawing_mode == "line" and "x1" in last_object and "x2" in last_object:
        # Es una línea
        p1 = (int(last_object["x1"]), int(last_object["y1"]))
        p2 = (int(last_object["x2"]), int(last_object["y2"]))
        
        distance = calculate_distance(p1, p2)
        
        measurement = {
            "id": str(uuid.uuid4()),
            "type": "Línea",
            "value": distance,
            "description": description or "Medición de distancia",
            "joint": "N/A",
            "points": [p1, p2],
            "frame_index": st.session_state.frame_index,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return measurement
    
    elif drawing_mode == "circle" and len(objects) >= 3:
        # Para un ángulo necesitamos 3 puntos (círculos)
        # Tomamos los últimos 3 objetos dibujados
        if len(objects) >= 3:
            angle_points = []
            for i in range(-3, 0):
                obj = objects[i]
                if "left" in obj and "top" in obj:
                    # Calcular el centro del círculo
                    center_x = int(obj["left"] + obj["radius"])
                    center_y = int(obj["top"] + obj["radius"])
                    angle_points.append((center_x, center_y))
            
            if len(angle_points) == 3:
                angle = calculate_angle(angle_points[0], angle_points[1], angle_points[2])
                
                measurement = {
                    "id": str(uuid.uuid4()),
                    "type": "Ángulo",
                    "value": angle,
                    "description": description or f"Ángulo en {joint}",
                    "joint": joint,
                    "points": angle_points,
                    "frame_index": st.session_state.frame_index,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return measurement
    
    return None

def draw_angle(frame, points, angle, color=(255, 0, 0)):
    """Dibuja un ángulo en el frame"""
    # Dibujar líneas
    cv2.line(frame, (points[0][0], points[0][1]), (points[1][0], points[1][1]), color, 2)
    cv2.line(frame, (points[1][0], points[1][1]), (points[2][0], points[2][1]), color, 2)
    
    # Mostrar puntos
    for p in points:
        cv2.circle(frame, (p[0], p[1]), 5, color, -1)
    
    # Mostrar el ángulo
    text_pos = (points[1][0] + 10, points[1][1] + 10)
    cv2.putText(frame, f"{angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def draw_line(frame, points, distance, color=(0, 255, 0)):
    """Dibuja una línea con su longitud en el frame"""
    # Dibujar línea
    cv2.line(frame, (points[0][0], points[0][1]), (points[1][0], points[1][1]), color, 2)
    
    # Mostrar puntos
    for p in points:
        cv2.circle(frame, (p[0], p[1]), 5, color, -1)
    
    # Mostrar la distancia
    mid_x = (points[0][0] + points[1][0]) // 2
    mid_y = (points[0][1] + points[1][1]) // 2
    text_pos = (mid_x + 10, mid_y + 10)
    cv2.putText(frame, f"{distance:.1f} px", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def save_measurement(measurement):
    """Guarda una medición en el estado de la sesión"""
    st.session_state.measurements.append(measurement)
    return measurement

def get_time_from_frame(frame_index, fps=30):
    """Convierte un índice de frame a tiempo (minutos:segundos)"""
    total_seconds = frame_index / fps
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# Funciones para generar PDF
def generate_pdf(client, session_data, measurements, frame_with_analysis, progress_charts):
    """Genera un informe PDF profesional"""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Definir estilos
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Centrado
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Crear una lista de elementos para el PDF
    elements = []
    
    # Título del informe
    title = Paragraph(f"Informe Biomecánico: {client['name']}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Información del cliente y sesión
    date_text = Paragraph(f"<b>Fecha:</b> {session_data['date']}", normal_style)
    exercise_text = Paragraph(f"<b>Ejercicio:</b> {session_data['exercise']}", normal_style)
    sets_reps_text = Paragraph(f"<b>Series/Repeticiones:</b> {session_data['sets']} x {session_data['reps']}", normal_style)
    rir_text = Paragraph(f"<b>RIR:</b> {session_data['rir']}", normal_style)
    
    elements.append(date_text)
    elements.append(exercise_text)
    elements.append(sets_reps_text)
    elements.append(rir_text)
    elements.append(Spacer(1, 12))
    
    # Análisis de movimiento
    movement_title = Paragraph("Análisis de Movimiento", subtitle_style)
    elements.append(movement_title)
    elements.append(Spacer(1, 6))
    
    # Convertir el frame numpy a imagen para el PDF
    if frame_with_analysis is not None:
        # Guardar la imagen temporalmente
        img_path = "temp/analysis_frame.jpg"
        cv2.imwrite(img_path, cv2.cvtColor(frame_with_analysis, cv2.COLOR_RGB2BGR))
        
        # Añadir la imagen al PDF
        img = ReportLabImage(img_path, width=400, height=300)
        elements.append(img)
        elements.append(Spacer(1, 12))
    
    # Tabla de mediciones
    if measurements:
        measurements_title = Paragraph("Mediciones Biomecánicas", subtitle_style)
        elements.append(measurements_title)
        elements.append(Spacer(1, 6))
        
        # Crear tabla
        data = [["Tipo", "Articulación", "Valor", "Descripción"]]
        for m in measurements:
            data.append([
                m["type"],
                m["joint"],
                f"{m['value']:.1f}°" if m["type"] == "Ángulo" else f"{m['value']:.1f} px",
                m["description"]
            ])
        
        table = Table(data, colWidths=[80, 100, 80, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
    
    # Gráficos de progreso
    if progress_charts:
        progress_title = Paragraph("Progreso del Cliente", subtitle_style)
        elements.append(progress_title)
        elements.append(Spacer(1, 6))
        
        # Añadir imágenes de gráficos
        for chart_path in progress_charts:
            chart_img = ReportLabImage(chart_path, width=450, height=250)
            elements.append(chart_img)
            elements.append(Spacer(1, 10))
    
    # Comentarios y feedback
    if session_data.get("comments"):
        feedback_title = Paragraph("Feedback y Recomendaciones", subtitle_style)
        elements.append(feedback_title)
        elements.append(Spacer(1, 6))
        
        feedback_text = Paragraph(session_data["comments"], normal_style)
        elements.append(feedback_text)
    
    # Generar el PDF
    doc.build(elements)
    
    # Limpiar archivos temporales
    if os.path.exists("temp/analysis_frame.jpg"):
        os.remove("temp/analysis_frame.jpg")
    
    # Devolver el PDF
    pdf_buffer.seek(0)
    return pdf_buffer

# Interfaz de usuario con Streamlit
def main():
    # Aplicamos título con mejor formato
    st.markdown("<h1 class='title'>🏋️ KinesioApp - Análisis Biomecánico</h1>", unsafe_allow_html=True)
    
    # Pestañas de navegación
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Clientes", "📹 Análisis de Video", "📊 Visualización de Datos", "📑 Informes"])
    
    # Cargar datos
    clients = load_clients()
    sessions = load_sessions()
    
    # Pestaña 1: Gestión de Clientes
    with tab1:
        st.subheader("Gestión de Clientes")
        
        # Formulario para agregar cliente
        with st.expander("Agregar Nuevo Cliente", expanded=len(clients) == 0):
            with st.form("new_client_form"):
                name = st.text_input("Nombre completo")
                age = st.number_input("Edad", min_value=1, max_value=120, value=30)
                gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
                height = st.number_input("Altura (cm)", min_value=50, max_value=250, value=170)
                weight = st.number_input("Peso (kg)", min_value=10, max_value=300, value=70)
                goal = st.text_area("Objetivo", placeholder="Ej: Rehabilitación, Hipertrofia, Fuerza, etc.")
                notes = st.text_area("Notas adicionales", placeholder="Historial médico, lesiones previas, etc.")
                
                submit_client = st.form_submit_button("Guardar Cliente")
                
                if submit_client and name:
                    # Generar ID único
                    client_id = str(uuid.uuid4())
                    
                    # Crear nuevo cliente
                    clients[client_id] = {
                        "id": client_id,
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "height": height,
                        "weight": weight,
                        "goal": goal,
                        "notes": notes,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Guardar en archivo
                    save_clients(clients)
                    st.success(f"Cliente {name} agregado correctamente!")
                    st.experimental_rerun()
        
        # Lista de clientes
        st.subheader("Mis Clientes")
        
        if not clients:
            st.info("No hay clientes registrados. Agrega uno nuevo para comenzar.")
        else:
            # Buscador de clientes
            search = st.text_input("🔍 Buscar cliente", placeholder="Nombre del cliente...")
            
            filtered_clients = {k: v for k, v in clients.items() if search.lower() in v["name"].lower()} if search else clients
            
            if not filtered_clients:
                st.info(f"No se encontraron clientes con '{search}'")
            
            # Mostrar clientes filtrados
            cols = st.columns(3)
            i = 0
            
            for client_id, client in filtered_clients.items():
                col = cols[i % 3]
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div class='client-card'>
                            <h3>{client['name']}</h3>
                            <p><strong>Edad:</strong> {client['age']} años</p>
                            <p><strong>Objetivo:</strong> {client['goal']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botones de acción
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✏️ Editar", key=f"edit_{client_id}"):
                                st.session_state.current_client = client
                                st.experimental_rerun()
                        with col2:
                            if st.button(f"📊 Analizar", key=f"analyze_{client_id}"):
                                st.session_state.current_client = client
                                st.experimental_rerun()
                
                i += 1
                
            # Editar cliente seleccionado
            if st.session_state.current_client:
                client = st.session_state.current_client
                
                st.subheader(f"Editar: {client['name']}")
                
                with st.form("edit_client_form"):
                    name = st.text_input("Nombre completo", value=client["name"])
                    age = st.number_input("Edad", min_value=1, max_value=120, value=client["age"])
                    gender = st.selectbox("Género", ["Masculino", "Femenino", "Otro"], index=["Masculino", "Femenino", "Otro"].index(client["gender"]))
                    height = st.number_input("Altura (cm)", min_value=50, max_value=250, value=client["height"])
                    weight = st.number_input("Peso (kg)", min_value=10, max_value=300, value=client["weight"])
                    goal = st.text_area("Objetivo", value=client["goal"])
                    notes = st.text_area("Notas adicionales", value=client.get("notes", ""))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submit_edit = st.form_submit_button("Actualizar Cliente")
                    with col2:
                        cancel_edit = st.form_submit_button("Cancelar")
                    
                    if submit_edit and name:
                        # Actualizar cliente
                        client_id = client["id"]
                        clients[client_id] = {
                            "id": client_id,
                            "name": name,
                            "age": age,
                            "gender": gender,
                            "height": height,
                            "weight": weight,
                            "goal": goal,
                            "notes": notes,
                            "created_at": client.get("created_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                        
                        # Guardar en archivo
                        save_clients(clients)
                        st.success(f"Cliente {name} actualizado correctamente!")
                        st.session_state.current_client = None
                        st.experimental_rerun()
                    
                    if cancel_edit:
                        st.session_state.current_client = None
                        st.experimental_rerun()
    
    # Pestaña 2: Análisis de Video
    with tab2:
        if not st.session_state.current_client:
            st.warning("Por favor, selecciona un cliente en la pestaña 'Clientes'")
        else:
            client = st.session_state.current_client
            st.subheader(f"Análisis de Video para: {client['name']}")
            
            # Cargar video
            uploaded_file = st.file_uploader("Cargar video para análisis", type=["mp4", "mov", "avi"])
            
            if uploaded_file is not None and st.session_state.current_video != uploaded_file.name:
                st.session_state.current_video = uploaded_file.name
                st.session_state.measurements = []
                
                # Procesar el video
                with st.spinner("Procesando video..."):
                    if process_video(uploaded_file):
                        st.success("Video cargado correctamente!")
            
            # Mostrar controles de video si hay un video cargado
            if st.session_state.current_video_path and st.session_state.current_frame is not None:
                # Control de frames
                st.subheader("Control de Video")
                
                col1, col2, col3 = st.columns([1, 8, 1])
                with col1:
                    if st.button("⏪ -10"):
                        get_frame(st.session_state.frame_index - 10)
                with col2:
                    selected_frame = st.slider("Frame", 0, max(0, st.session_state.total_frames - 1), st.session_state.frame_index)
                    if selected_frame != st.session_state.frame_index:
                        get_frame(selected_frame)
                with col3:
                    if st.button("⏩ +10"):
                        get_frame(st.session_state.frame_index + 10)
                
                # Tiempo del video
                st.markdown(f"<div class='video-time'>Tiempo: {get_time_from_frame(st.session_state.frame_index)}</div>", unsafe_allow_html=True)
                
                # Columnas para frame y herramientas
                col1, col2 = st.columns([3, 1])
                
                # Frame principal con mediciones
                with col1:
                    # Mostrar frame con mediciones aplicadas
                    frame_display = st.session_state.current_frame.copy()
                    
                    # Dibujar ángulos y líneas almacenados en measurements
                    for m in st.session_state.measurements:
                        if m["frame_index"] == st.session_state.frame_index:
                            if m["type"] == "Ángulo":
                                # Recuperar los puntos del ángulo
                                points = m.get("points", [])
                                if len(points) == 3:
                                    draw_angle(frame_display, points, m["value"], color=(255, 0, 0))
                            elif m["type"] == "Línea":
                                points = m.get("points", [])
                                if len(points) == 2:
                                    draw_line(frame_display, points, m["value"], color=(0, 255, 0))
                    
                    # Configuración del canvas para dibujar mediciones
                    st.subheader("Dibuja en el frame")
                    
                    drawing_mode = st.radio(
                        "Herramienta de dibujo:",
                        ("line", "circle"),
                        format_func=lambda x: "Línea" if x == "line" else "Punto (para ángulos)",
                        horizontal=True
                    )
                    
                    # Configuración personalizada según el modo de dibujo
                    if drawing_mode == "line":
                        stroke_color = st.color_picker("Color de línea:", "#00FF00")
                        stroke_width = st.slider("Grosor de línea:", 1, 5, 3)
                        st.markdown("**Instrucciones:** Dibuja una línea arrastrando de un punto a otro.")
                        
                        # Descripciones para líneas
                        line_desc = st.text_input("Descripción de la línea:", placeholder="Ej: Longitud del fémur")
                    else:  # circle para ángulos
                        stroke_color = st.color_picker("Color de punto:", "#FF0000")
                        stroke_width = st.slider("Tamaño de punto:", 5, 15, 10)
                        st.markdown("**Instrucciones:** Dibuja 3 puntos para medir un ángulo. El punto central será el vértice.")
                        
                        # Opciones para ángulos
                        joint_options = ["Rodilla", "Cadera", "Hombro", "Codo", "Tobillo", "Columna", "Otro"]
                        joint = st.selectbox("Articulación:", joint_options)
                        angle_desc = st.text_input("Descripción del ángulo:", placeholder="Ej: Flexión de rodilla")
                    
                    # Canvas interactivo
                    canvas_result = st_canvas(
                        fill_color="rgba(255, 165, 0, 0.3)",
                        stroke_width=stroke_width,
                        stroke_color=stroke_color,
                        background_image=Image.fromarray(frame_display),
                        height=st.session_state.frame_height,
                        width=st.session_state.frame_width,
                        drawing_mode=drawing_mode,
                        key="canvas",
                    )
                    
                    # Botón para guardar la medición
                    if st.button("Guardar Medición"):
                        if drawing_mode == "line":
                            measurement = process_canvas_result(canvas_result, drawing_mode, description=line_desc)
                        else:  # circle para ángulos
                            measurement = process_canvas_result(canvas_result, drawing_mode, joint=joint, description=angle_desc)
                        
                        if measurement:
                            save_measurement(measurement)
                            st.success(f"{measurement['type']} guardado correctamente!")
                            st.experimental_rerun()
                        else:
                            st.error("No se pudo procesar la medición. Asegúrate de dibujar correctamente.")
                
                # Herramientas de análisis
                with col2:
                    st.subheader("Herramientas")
                    
                    # Información del frame
                    st.text(f"Frame {st.session_state.frame_index + 1} de {st.session_state.total_frames}")
                    st.text(f"Resolución: {st.session_state.frame_width}x{st.session_state.frame_height}")
                    
                    # Calibración (función más avanzada, simplificada para esta versión)
                    with st.expander("Calibración", expanded=False):
                        st.write("Para una calibración básica, puedes usar un objeto de referencia de tamaño conocido.")
                        ref_size = st.number_input("Tamaño de referencia (cm)", min_value=1, max_value=200, value=100)
                        st.info("Dibuja una línea sobre un objeto de referencia conocido y utiliza esta medida para calibrar.")
                    
                    # Exportar frame actual
                    if st.button("Exportar Frame Actual"):
                        # Guardar el frame actual con las mediciones
                        frame_with_measurements = st.session_state.current_frame.copy()
                        
                        # Aplicar mediciones
                        for m in st.session_state.measurements:
                            if m["frame_index"] == st.session_state.frame_index:
                                if m["type"] == "Ángulo" and "points" in m and len(m["points"]) == 3:
                                    draw_angle(frame_with_measurements, m["points"], m["value"], color=(255, 0, 0))
                                elif m["type"] == "Línea" and "points" in m and len(m["points"]) == 2:
                                    draw_line(frame_with_measurements, m["points"], m["value"], color=(0, 255, 0))
                        
                        # Guardar imagen temporalmente
                        img_path = "temp/frame_export.jpg"
                        cv2.imwrite(img_path, cv2.cvtColor(frame_with_measurements, cv2.COLOR_RGB2BGR))
                        
                        # Ofrecer para descargar
                        with open(img_path, "rb") as file:
                            btn = st.download_button(
                                label="Descargar Imagen",
                                data=file,
                                file_name=f"frame_{st.session_state.frame_index}.jpg",
                                mime="image/jpeg"
                            )
                
                # Mostrar mediciones del frame actual
                st.subheader("Mediciones en este Frame")
                
                frame_measurements = [m for m in st.session_state.measurements if m["frame_index"] == st.session_state.frame_index]
                
                if not frame_measurements:
                    st.info("No hay mediciones en este frame. Utiliza las herramientas para añadir mediciones.")
                else:
                    for i, m in enumerate(frame_measurements):
                        col1, col2, col3, col4 = st.columns([2, 3, 3, 1])
                        with col1:
                            st.markdown(f"<b>{m['type']}</b>", unsafe_allow_html=True)
                        with col2:
                            if m['type'] == "Ángulo":
                                st.markdown(f"<b>Valor:</b> {m['value']:.1f}°", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<b>Valor:</b> {m['value']:.1f} px", unsafe_allow_html=True)
                        with col3:
                            st.markdown(f"<b>Descripción:</b> {m['description']}", unsafe_allow_html=True)
                        with col4:
                            if st.button("🗑️", key=f"delete_measure_{i}"):
                                st.session_state.measurements.remove(m)
                                st.experimental_rerun()
                
                # Formulario para datos de la sesión
                st.subheader("Datos de la Sesión")
                
                with st.form("session_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        session_date = st.date_input("Fecha", value=datetime.date.today())
                        exercise = st.text_input("Ejercicio", placeholder="Ej: Sentadilla, Press de banca...")
                    
                    with col2:
                        sets = st.number_input("Series", min_value=1, max_value=20, value=3)
                        reps = st.number_input("Repeticiones", min_value=1, max_value=100, value=10)
                        rir = st.slider("RIR (Repeticiones en Reserva)", 0, 10, 2)
                    
                    comments = st.text_area("Comentarios y Feedback", placeholder="Observaciones, correcciones, indicaciones...")
                    
                    submitted = st.form_submit_button("Guardar Sesión")
                    
                    if submitted:
                        if not exercise:
                            st.error("Por favor, ingresa el nombre del ejercicio.")
                        else:
                            # Crear datos de la sesión
                            session_data = {
                                "id": str(uuid.uuid4()),
                                "client_id": client["id"],
                                "date": session_date.strftime("%Y-%m-%d"),
                                "exercise": exercise,
                                "sets": sets,
                                "reps": reps,
                                "rir": rir,
                                "comments": comments,
                                "measurements": st.session_state.measurements,
                                "video_name": st.session_state.current_video,
                                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Añadir a las sesiones
                            sessions.append(session_data)
                            save_sessions(sessions)
                            
                            st.success("Sesión guardada correctamente! Puedes generar el informe en la pestaña 'Informes'.")
    
    # Pestaña 3: Visualización de Datos
    with tab3:
        if not clients:
            st.warning("No hay clientes registrados. Agrega uno nuevo en la pestaña 'Clientes'.")
        else:
            st.subheader("Visualización de Datos y Progreso")
            
            # Seleccionar cliente
            client_names = {client_id: client["name"] for client_id, client in clients.items()}
            selected_client_id = st.selectbox("Seleccionar Cliente", list(client_names.keys()), format_func=lambda x: client_names[x])
            
            # Filtrar sesiones del cliente seleccionado
            client_sessions = [s for s in sessions if s["client_id"] == selected_client_id]
            
            if not client_sessions:
                st.info("No hay sesiones registradas para este cliente.")
            else:
                # Agrupar sesiones por ejercicio
                exercises = set([s["exercise"] for s in client_sessions])
                selected_exercise = st.selectbox("Seleccionar Ejercicio", list(exercises))
                
                # Filtrar sesiones por ejercicio seleccionado
                exercise_sessions = [s for s in client_sessions if s["exercise"] == selected_exercise]
                
                # Visualizar progreso
                st.subheader(f"Progreso: {selected_exercise}")
                
                # Preparar datos para gráficos
                dates = [s["date"] for s in exercise_sessions]
                volumes = [s["sets"] * s["reps"] for s in exercise_sessions]
                rirs = [s["rir"] for s in exercise_sessions]
                
                # Crear DataFrame para Plotly
                df = pd.DataFrame({
                    "Fecha": dates,
                    "Volumen (Sets x Reps)": volumes,
                    "RIR": rirs
                })
                
                # Gráfico de volumen
                fig_volume = px.line(
                    df, 
                    x="Fecha", 
                    y="Volumen (Sets x Reps)",
                    title="Progresión de Volumen",
                    markers=True
                )
                st.plotly_chart(fig_volume, use_container_width=True)
                
                # Gráfico de RIR
                fig_rir = px.line(
                    df, 
                    x="Fecha", 
                    y="RIR",
                    title="Progresión de RIR (Repeticiones en Reserva)",
                    markers=True
                )
                fig_rir.update_layout(yaxis=dict(autorange="reversed"))  # Invertir eje Y para RIR
                st.plotly_chart(fig_rir, use_container_width=True)
                
                # Análisis de microciclos
                st.subheader("Análisis de Microciclo")
                microcycle_size = st.slider("Tamaño del Microciclo (semanas)", 1, 6, 2)
                
                # Convertir fechas a datetime para procesamiento
                df["Fecha"] = pd.to_datetime(df["Fecha"])
                
                # Agregar columna de microciclo basada en fechas
                df = df.sort_values("Fecha")
                df["Semana"] = df["Fecha"].dt.isocalendar().week
                df["Año"] = df["Fecha"].dt.isocalendar().year
                df["Microciclo"] = ((df["Semana"] - df["Semana"].min()) // microcycle_size) + 1
                
                # Agrupar por microciclo
                microcycle_data = df.groupby("Microciclo").agg({
                    "Volumen (Sets x Reps)": "mean",
                    "RIR": "mean"
                }).reset_index()
                
                # Gráfico de microciclo
                fig_micro = px.bar(
                    microcycle_data,
                    x="Microciclo",
                    y="Volumen (Sets x Reps)",
                    title=f"Volumen Promedio por Microciclo ({microcycle_size} semanas)",
                    color="Volumen (Sets x Reps)"
                )
                st.plotly_chart(fig_micro, use_container_width=True)
                
                # Tabla detallada de sesiones
                st.subheader("Historial de Sesiones")
                
                for session in sorted(exercise_sessions, key=lambda x: x["date"], reverse=True):
                    with st.expander(f"{session['date']} - {session['exercise']} ({session['sets']}x{session['reps']})"):
                        st.write(f"**RIR:** {session['rir']}")
                        st.write(f"**Volumen Total:** {session['sets'] * session['reps']} repeticiones")
                        
                        if session.get("comments"):
                            st.write(f"**Comentarios:** {session['comments']}")
                        
                        if session.get("measurements"):
                            st.write("**Mediciones:**")
                            for m in session["measurements"]:
                                if m["type"] == "Ángulo":
                                    st.write(f"- {m['joint']}: {m['value']:.1f}° ({m['description']})")
                                else:
                                    st.write(f"- Distancia: {m['value']:.1f} px ({m['description']})")
    
    # Pestaña 4: Generación de Informes
    with tab4:
        st.subheader("Generación de Informes PDF")
        
        if not sessions:
            st.warning("No hay sesiones registradas. Analiza un video en la pestaña 'Análisis de Video'.")
        else:
            # Filtrar por cliente
            client_names = {client_id: client["name"] for client_id, client in clients.items()}
            selected_client_id = st.selectbox("Cliente", list(client_names.keys()), format_func=lambda x: client_names[x], key="pdf_client")
            
            # Filtrar sesiones del cliente seleccionado
            client_sessions = [s for s in sessions if s["client_id"] == selected_client_id]
            
            if not client_sessions:
                st.info("No hay sesiones registradas para este cliente.")
            else:
                # Seleccionar sesión
                session_options = [f"{s['date']} - {s['exercise']} ({s['sets']}x{s['reps']})" for s in client_sessions]
                selected_session_idx = st.selectbox("Sesión", range(len(session_options)), format_func=lambda i: session_options[i])
                
                selected_session = client_sessions[selected_session_idx]
                
                # Mostrar vista previa de la sesión
                st.subheader("Vista Previa del Informe")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Fecha:** {selected_session['date']}")
                    st.write(f"**Ejercicio:** {selected_session['exercise']}")
                
                with col2:
                    st.write(f"**Series x Repeticiones:** {selected_session['sets']} x {selected_session['reps']}")
                    st.write(f"**RIR:** {selected_session['rir']}")
                
                if selected_session.get("comments"):
                    st.write(f"**Comentarios:** {selected_session['comments']}")
                
                # Generar informe PDF
                if st.button("Generar Informe PDF", type="primary"):
                    with st.spinner("Generando informe..."):
                        # Crear frame con análisis para el PDF
                        frame_with_analysis = None
                        if st.session_state.current_frame is not None:
                            frame_with_analysis = st.session_state.current_frame.copy()
                            
                            # Dibujar mediciones en el frame
                            for m in selected_session.get("measurements", []):
                                if m["type"] == "Ángulo":
                                    points = m.get("points", [])
                                    if len(points) == 3:
                                        draw_angle(frame_with_analysis, points, m["value"], color=(255, 0, 0))
                                elif m["type"] == "Línea":
                                    points = m.get("points", [])
                                    if len(points) == 2:
                                        draw_line(frame_with_analysis, points, m["value"], color=(0, 255, 0))
                        
                        # Generar gráficos de progreso para el PDF
                        progress_charts = []
                        
                        # Guardar PDF
                        pdf_buffer = generate_pdf(
                            clients[selected_client_id],
                            selected_session,
                            selected_session.get("measurements", []),
                            frame_with_analysis,
                            progress_charts
                        )
                        
                        # Ofrecer descarga
                        st.success("Informe generado correctamente!")
                        
                        # Convertir a base64 para descarga
                        b64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                        pdf_display = f'<a href="data:application/pdf;base64,{b64_pdf}" download="informe_{selected_session["date"]}_{selected_session["exercise"]}.pdf">📥 Descargar Informe PDF</a>'
                        st.markdown(pdf_display, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
