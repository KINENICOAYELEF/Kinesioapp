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
from reportlab.lib.pagesizes import letter
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
    
    .canvas-container {
        margin: 0 auto;
        max-width: 100%;
        overflow: hidden;
        background-color: rgba(255,255,255,0.8);
    }
    
    /* Ajustar color de trazos según tipo */
    .angle-stroke {
        stroke: #e74c3c !important;
    }
    
    .line-stroke {
        stroke: #2ecc71 !important;
    }
    
    .force-stroke {
        stroke: #9b59b6 !important;
    }
    
    /* Arreglar tamaño de canvas */
    .canvas-container {
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Instrucciones para dibujo */
    .drawing-instructions {
        background-color: #eaf7fb;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 3px solid #3498db;
    }
    
    .tool-selector {
        border-radius: 8px;
        padding: 10px;
        background-color: #f8f9fa;
        margin-bottom: 15px;
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
    st.session_state.stroke_color = "#00FF00"
if "calibration_factor" not in st.session_state:
    st.session_state.calibration_factor = 1.0  # Píxeles por cm
if "tool_type" not in st.session_state:
    st.session_state.tool_type = "angle"  # angle, line, force, moment
if "joint_type" not in st.session_state:
    st.session_state.joint_type = "Rodilla"
if "last_canvas_output" not in st.session_state:
    st.session_state.last_canvas_output = None
if "pivots" not in st.session_state:
    st.session_state.pivots = []
if "force_vectors" not in st.session_state:
    st.session_state.force_vectors = []
if "moment_arms" not in st.session_state:
    st.session_state.moment_arms = []

# Funciones para el análisis de video
def process_video(video_file):
    """Procesa un video y lo almacena temporalmente"""
    try:
        # Guardar el video temporalmente
        temp_file_path = os.path.join("temp", f"temp_video_{uuid.uuid4()}.mp4")
        with open(temp_file_path, "wb") as f:
            f.write(video_file.getbuffer())
        
        # Abrir el video con OpenCV
        cap = cv2.VideoCapture(temp_file_path)
        if not cap.isOpened():
            st.error("No se pudo abrir el video. Formato no compatible.")
            return False
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if total_frames <= 0:
            st.error("El video no tiene frames válidos.")
            return False
        
        # Actualizar el estado
        st.session_state.current_video_path = temp_file_path
        st.session_state.total_frames = total_frames
        st.session_state.frame_width = width
        st.session_state.frame_height = height
        
        # Obtener el primer frame
        get_frame(0)
        
        return True
    except Exception as e:
        st.error(f"Error al procesar el video: {str(e)}")
        return False

def get_frame(frame_index):
    """Obtiene un fotograma específico del video actual"""
    try:
        if st.session_state.current_video_path:
            cap = cv2.VideoCapture(st.session_state.current_video_path)
            if not cap.isOpened():
                st.error("No se pudo abrir el video guardado.")
                return False
                
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
                st.error(f"No se pudo leer el frame {frame_index} del video.")
                return False
        else:
            st.error("No hay un video cargado actualmente.")
            return False
    except Exception as e:
        st.error(f"Error al obtener el frame: {str(e)}")
        return False

def calculate_angle(p1, p2, p3):
    """Calcula el ángulo entre tres puntos (en grados)"""
    # Vectores
    a = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    b = np.array([p3[0] - p2[0], p3[1] - p2[1]])
    
    # Verificar vectores no nulos
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0
    
    # Calcular el ángulo
    cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_distance(p1, p2):
    """Calcula la distancia entre dos puntos"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def calculate_moment_arm(pivot_point, force_line_p1, force_line_p2):
    """
    Calcula el brazo de momento (distancia perpendicular desde el punto de pivote a la línea de fuerza)
    """
    # Vectorizar para facilitar cálculos
    pivot = np.array(pivot_point)
    p1 = np.array(force_line_p1)
    p2 = np.array(force_line_p2)
    
    # Vector de dirección de la línea de fuerza
    force_direction = p2 - p1
    force_direction_norm = np.linalg.norm(force_direction)
    
    # Evitar división por cero
    if force_direction_norm == 0:
        return 0
    
    # Normalizar vector de dirección
    force_direction = force_direction / force_direction_norm
    
    # Vector desde un punto de la línea al pivote
    pivot_to_line = pivot - p1
    
    # Proyección escalar del vector pivot_to_line sobre force_direction
    projection = np.dot(pivot_to_line, force_direction)
    
    # Punto más cercano en la línea de fuerza al pivote
    closest_point = p1 + projection * force_direction
    
    # Distancia perpendicular (brazo de momento)
    moment_arm = np.linalg.norm(pivot - closest_point)
    
    return moment_arm, tuple(map(int, closest_point))

def process_canvas_result(canvas_result, drawing_mode, joint="", description=""):
    """Procesa el resultado del canvas para extraer mediciones"""
    if not canvas_result or not canvas_result.json_data or "objects" not in canvas_result.json_data:
        return None
    
    objects = canvas_result.json_data["objects"]
    if not objects:
        return None
        
    if drawing_mode == "circle":
        # Para ángulos necesitamos 3 puntos (círculos)
        if len(objects) >= 3:
            angle_points = []
            for i in range(-3, 0):
                if i + len(objects) >= 0:  # Asegurarse de que el índice es válido
                    obj = objects[i + len(objects)]
                    if "left" in obj and "top" in obj and "radius" in obj:
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
    
    elif drawing_mode == "line":
        # Para líneas buscamos el último objeto tipo línea
        for obj in reversed(objects):
            if "x1" in obj and "x2" in obj:
                p1 = (int(obj["x1"]), int(obj["y1"]))
                p2 = (int(obj["x2"]), int(obj["y2"]))
                
                distance = calculate_distance(p1, p2)
                
                # Convertir a unidades reales si hay calibración
                if st.session_state.calibration_factor != 1.0:
                    real_distance = distance / st.session_state.calibration_factor
                    unit = "cm"
                else:
                    real_distance = distance
                    unit = "px"
                
                measurement = {
                    "id": str(uuid.uuid4()),
                    "type": "Línea",
                    "value": distance,
                    "real_value": real_distance,
                    "unit": unit,
                    "description": description or "Medición de distancia",
                    "joint": joint,
                    "points": [p1, p2],
                    "frame_index": st.session_state.frame_index,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return measurement
    
    elif drawing_mode == "arrow":
        # Para vectores de fuerza buscamos el último objeto tipo línea/flecha
        for obj in reversed(objects):
            if "x1" in obj and "x2" in obj:
                p1 = (int(obj["x1"]), int(obj["y1"]))
                p2 = (int(obj["x2"]), int(obj["y2"]))
                
                magnitude = calculate_distance(p1, p2)
                
                # Convertir a unidades reales si hay calibración
                if st.session_state.calibration_factor != 1.0:
                    real_magnitude = magnitude / st.session_state.calibration_factor
                    unit = "cm"
                else:
                    real_magnitude = magnitude
                    unit = "px"
                
                vector = {
                    "id": str(uuid.uuid4()),
                    "type": "Vector de Fuerza",
                    "points": [p1, p2],
                    "magnitude": magnitude,
                    "real_magnitude": real_magnitude,
                    "unit": unit,
                    "description": description or "Vector de fuerza",
                    "frame_index": st.session_state.frame_index,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return vector
                
    return None

def process_pivot_selection(canvas_result, description=""):
    """Procesa la selección de un punto de pivote (articulación)"""
    if not canvas_result or not canvas_result.json_data or "objects" not in canvas_result.json_data:
        return None
    
    objects = canvas_result.json_data["objects"]
    if not objects:
        return None
    
    # Buscamos el último círculo dibujado (punto de pivote)
    for obj in reversed(objects):
        if "type" in obj and obj["type"] == "circle":
            center_x = int(obj["left"] + obj["radius"])
            center_y = int(obj["top"] + obj["radius"])
            pivot_point = (center_x, center_y)
            
            pivot = {
                "id": str(uuid.uuid4()),
                "type": "Pivote",
                "point": pivot_point,
                "description": description or "Punto de pivote",
                "frame_index": st.session_state.frame_index,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return pivot
            
    return None

def process_moment_arm(pivot, force_vector, description=""):
    """Calcula el brazo de momento entre un pivote y un vector de fuerza"""
    if not pivot or not force_vector:
        return None
    
    p1, p2 = force_vector["points"]
    pivot_point = pivot["point"]
    
    # Calcular brazo de momento
    moment_value, perpendicular_point = calculate_moment_arm(pivot_point, p1, p2)
    
    # Convertir a unidades reales si hay calibración
    if st.session_state.calibration_factor != 1.0:
        real_value = moment_value / st.session_state.calibration_factor
        unit = "cm"
    else:
        real_value = moment_value
        unit = "px"
    
    moment_arm = {
        "id": str(uuid.uuid4()),
        "type": "Brazo de Momento",
        "value": moment_value,
        "real_value": real_value,
        "unit": unit,
        "pivot": pivot_point,
        "perpendicular_point": perpendicular_point,
        "force_vector_id": force_vector["id"],
        "description": description or "Brazo de momento",
        "frame_index": st.session_state.frame_index,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return moment_arm

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

def draw_line(frame, points, distance, color=(0, 255, 0), unit="px"):
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
    
    cv2.putText(frame, f"{distance:.1f} {unit}", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def draw_force_vector(frame, points, description="", color=(148, 0, 211)):
    """Dibuja un vector de fuerza con flecha en el frame"""
    # Dibujar flecha
    cv2.arrowedLine(frame, points[0], points[1], color, 2, tipLength=0.2)
    
    # Mostrar puntos
    cv2.circle(frame, points[0], 5, color, -1)
    cv2.circle(frame, points[1], 5, color, -1)
    
    # Mostrar la descripción
    text_pos = (points[1][0] + 10, points[1][1] + 10)
    cv2.putText(frame, description, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def draw_moment_arm(frame, pivot, perp_point, moment_value, color=(231, 76, 60), unit="px"):
    """Dibuja el brazo de momento (distancia perpendicular) en el frame"""
    # Dibujar línea del brazo de momento
    cv2.line(frame, pivot, perp_point, color, 2, cv2.LINE_AA)
    
    # Mostrar puntos
    cv2.circle(frame, pivot, 5, color, -1)
    cv2.circle(frame, perp_point, 5, color, -1)
    
    # Mostrar el valor
    mid_x = (pivot[0] + perp_point[0]) // 2
    mid_y = (pivot[1] + perp_point[1]) // 2
    text_pos = (mid_x + 5, mid_y - 5)
    
    cv2.putText(frame, f"BM: {moment_value:.1f} {unit}", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def draw_pivot(frame, point, color=(255, 255, 0)):
    """Dibuja un punto de pivote con un círculo destacado"""
    cv2.circle(frame, point, 8, color, -1)
    cv2.circle(frame, point, 12, color, 2)
    
    return frame

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
    
    # Datos del cliente
    client_title = Paragraph("Datos del Cliente", subtitle_style)
    elements.append(client_title)
    elements.append(Spacer(1, 6))
    
    client_info = [
        f"<b>Nombre:</b> {client['name']}",
        f"<b>Edad:</b> {client['age']} años",
        f"<b>Género:</b> {client['gender']}",
        f"<b>Altura:</b> {client['height']} cm",
        f"<b>Peso:</b> {client['weight']} kg",
        f"<b>Objetivo:</b> {client['goal']}"
    ]
    
    for info in client_info:
        elements.append(Paragraph(info, normal_style))
    
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
        data = [["Tipo", "Articulación/Descripción", "Valor", "Notas"]]
        for m in measurements:
            value_text = ""
            if m["type"] == "Ángulo":
                value_text = f"{m['value']:.1f}°"
            elif m["type"] == "Línea":
                if "real_value" in m and "unit" in m:
                    value_text = f"{m['real_value']:.1f} {m['unit']}"
                else:
                    value_text = f"{m['value']:.1f} px"
            elif m["type"] == "Vector de Fuerza":
                if "real_magnitude" in m and "unit" in m:
                    value_text = f"{m['real_magnitude']:.1f} {m['unit']}"
                else:
                    value_text = f"{m.get('magnitude', 0):.1f} px"
            elif m["type"] == "Brazo de Momento":
                if "real_value" in m and "unit" in m:
                    value_text = f"{m['real_value']:.1f} {m['unit']}"
                else:
                    value_text = f"{m['value']:.1f} px"
            
            data.append([
                m["type"],
                m.get("joint", ""),
                value_text,
                m.get("description", "")
            ])
        
        table = Table(data, colWidths=[100, 120, 80, 160])
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
                st.session_state.pivots = []
                st.session_state.force_vectors = []
                st.session_state.moment_arms = []
                
                # Procesar el video
                with st.spinner("Procesando video..."):
                    if process_video(uploaded_file):
                        st.success("Video cargado correctamente!")
                    else:
                        st.error("No se pudo procesar el video. Intenta con otro formato.")
            
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
                
                # Herramienta de calibración
                with st.expander("Calibración", expanded=False):
                    st.write("Para tener mediciones en centímetros, calibra usando un objeto de referencia conocido.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        ref_pixels = st.number_input("Longitud en píxeles:", min_value=1.0, max_value=1000.0, value=100.0, step=1.0)
                    with col2:
                        ref_cm = st.number_input("Longitud real (cm):", min_value=1.0, max_value=200.0, value=10.0, step=1.0)
                    
                    if st.button("Aplicar Calibración"):
                        if ref_pixels > 0 and ref_cm > 0:
                            st.session_state.calibration_factor = ref_pixels / ref_cm
                            st.success(f"Calibración aplicada: 1 cm = {st.session_state.calibration_factor:.2f} píxeles")
                        else:
                            st.error("Los valores deben ser mayores que cero.")
                    
                    current_calibration = st.session_state.calibration_factor
                    if current_calibration != 1.0:
                        st.info(f"Calibración actual: 1 cm = {current_calibration:.2f} píxeles")
                    else:
                        st.warning("No hay calibración aplicada. Las medidas se mostrarán en píxeles.")
                
                # Columnas para frame y herramientas
                col1, col2 = st.columns([3, 1])
                
                # Frame principal con mediciones
                with col1:
                    # Preparar frame para visualización con mediciones
                    display_frame = st.session_state.current_frame.copy()
                    
                    # Dibujar mediciones guardadas
                    # Dibujar ángulos
                    for m in st.session_state.measurements:
                        if m["frame_index"] == st.session_state.frame_index:
                            if m["type"] == "Ángulo" and "points" in m and len(m["points"]) == 3:
                                draw_angle(display_frame, m["points"], m["value"], color=(231, 76, 60))
                            elif m["type"] == "Línea" and "points" in m and len(m["points"]) == 2:
                                unit = m.get("unit", "px")
                                value = m.get("real_value", m["value"])
                                draw_line(display_frame, m["points"], value, color=(46, 204, 113), unit=unit)
                    
                    # Dibujar puntos de pivote
                    for p in st.session_state.pivots:
                        if p["frame_index"] == st.session_state.frame_index:
                            draw_pivot(display_frame, p["point"], color=(255, 215, 0))  # Gold
                    
                    # Dibujar vectores de fuerza
                    for v in st.session_state.force_vectors:
                        if v["frame_index"] == st.session_state.frame_index:
                            draw_force_vector(display_frame, v["points"], v.get("description", ""), color=(155, 89, 182))
                    
                    # Dibujar brazos de momento
                    for m in st.session_state.moment_arms:
                        if m["frame_index"] == st.session_state.frame_index and "pivot" in m and "perpendicular_point" in m:
                            unit = m.get("unit", "px")
                            value = m.get("real_value", m["value"])
                            draw_moment_arm(display_frame, m["pivot"], m["perpendicular_point"], value, color=(231, 76, 60), unit=unit)
                    
                    # Mostrar frame con mediciones
                    st.image(display_frame, channels="RGB", use_column_width=True)
                    
                    # Selección de herramienta de dibujo
                    st.markdown("<div class='tool-selector'>", unsafe_allow_html=True)
                    tool_type = st.radio(
                        "Selecciona la herramienta de análisis:",
                        ["angle", "line", "force", "moment"],
                        format_func=lambda x: {
                            "angle": "Ángulo Articular", 
                            "line": "Medir Distancia/Segmento", 
                            "force": "Vector de Fuerza",
                            "moment": "Brazo de Momento"
                        }[x],
                        horizontal=True,
                        key="tool_select"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Actualizar estado de herramienta
                    if tool_type != st.session_state.tool_type:
                        st.session_state.tool_type = tool_type
                        st.session_state.last_canvas_output = None
                    
                    # Panel de dibujo según herramienta seleccionada
                    if tool_type == "angle":
                        st.markdown("""
                        <div class="drawing-instructions">
                            <h4>Medir Ángulo Articular</h4>
                            <p>Dibuja 3 círculos para medir un ángulo. El punto central será el vértice (articulación).</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Opciones para ángulos
                        joint_options = ["Rodilla", "Cadera", "Hombro", "Codo", "Tobillo", "Columna", "Otro"]
                        joint = st.selectbox("Articulación:", joint_options, key="angle_joint")
                        angle_desc = st.text_input("Descripción del ángulo:", placeholder="Ej: Flexión de rodilla", key="angle_desc")
                        
                        # Canvas para dibujar ángulo
                        canvas_result = st_canvas(
                            fill_color="rgba(200, 0, 0, 0.3)",
                            stroke_width=3,
                            stroke_color="#E74C3C",  # Rojo
                            background_image=Image.fromarray(st.session_state.current_frame),
                            height=st.session_state.frame_height,
                            width=st.session_state.frame_width,
                            drawing_mode="circle",
                            key="canvas_angle",
                            update_streamlit=True
                        )
                        
                        st.session_state.last_canvas_output = canvas_result
                        
                        # Botón para guardar ángulo
                        if st.button("Guardar Ángulo"):
                            angle_measurement = process_canvas_result(
                                st.session_state.last_canvas_output, 
                                "circle", 
                                joint=joint, 
                                description=angle_desc
                            )
                            
                            if angle_measurement:
                                st.session_state.measurements.append(angle_measurement)
                                st.success(f"Ángulo de {angle_measurement['joint']} guardado: {angle_measurement['value']:.1f}°")
                                st.experimental_rerun()
                            else:
                                st.error("No se pudo calcular el ángulo. Asegúrate de dibujar 3 puntos.")
                    
                    elif tool_type == "line":
                        st.markdown("""
                        <div class="drawing-instructions">
                            <h4>Medir Distancia/Segmento</h4>
                            <p>Dibuja una línea para medir la distancia entre dos puntos.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Opciones para líneas
                        segment_options = ["Fémur", "Tibia", "Húmero", "Radio", "Tronco", "Otro"]
                        segment = st.selectbox("Segmento:", segment_options, key="line_segment")
                        line_desc = st.text_input("Descripción:", placeholder="Ej: Longitud del fémur", key="line_desc")
                        
                        # Canvas para dibujar línea
                        canvas_result = st_canvas(
                            stroke_width=3,
                            stroke_color="#2ECC71",  # Verde
                            background_image=Image.fromarray(st.session_state.current_frame),
                            height=st.session_state.frame_height,
                            width=st.session_state.frame_width,
                            drawing_mode="line",
                            key="canvas_line",
                            update_streamlit=True
                        )
                        
                        st.session_state.last_canvas_output = canvas_result
                        
                        # Botón para guardar línea
                        if st.button("Guardar Medición"):
                            line_measurement = process_canvas_result(
                                st.session_state.last_canvas_output, 
                                "line", 
                                joint=segment, 
                                description=line_desc
                            )
                            
                            if line_measurement:
                                st.session_state.measurements.append(line_measurement)
                                
                                # Mostrar en unidades correctas
                                if "real_value" in line_measurement and "unit" in line_measurement:
                                    st.success(f"Medición guardada: {line_measurement['real_value']:.1f} {line_measurement['unit']}")
                                else:
                                    st.success(f"Medición guardada: {line_measurement['value']:.1f} px")
                                
                                st.experimental_rerun()
                            else:
                                st.error("No se pudo calcular la distancia. Asegúrate de dibujar una línea.")
                    
                    elif tool_type == "force":
                        st.markdown("""
                        <div class="drawing-instructions">
                            <h4>Vector de Fuerza</h4>
                            <p>Dibuja una línea para representar un vector de fuerza. El inicio es el punto de aplicación y la dirección indica hacia dónde se dirige la fuerza.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Opciones para vectores de fuerza
                        force_desc = st.text_input("Descripción de la fuerza:", placeholder="Ej: Fuerza de gravedad", key="force_desc")
                        
                        # Canvas para dibujar vector
                        canvas_result = st_canvas(
                            stroke_width=3,
                            stroke_color="#9B59B6",  # Púrpura
                            background_image=Image.fromarray(st.session_state.current_frame),
                            height=st.session_state.frame_height,
                            width=st.session_state.frame_width,
                            drawing_mode="line",
                            key="canvas_force",
                            update_streamlit=True
                        )
                        
                        st.session_state.last_canvas_output = canvas_result
                        
                        # Botón para guardar vector de fuerza
                        if st.button("Guardar Vector de Fuerza"):
                            force_vector = process_canvas_result(
                                st.session_state.last_canvas_output, 
                                "arrow", 
                                description=force_desc
                            )
                            
                            if force_vector:
                                st.session_state.force_vectors.append(force_vector)
                                
                                # Mostrar en unidades correctas
                                if "real_magnitude" in force_vector and "unit" in force_vector:
                                    st.success(f"Vector de fuerza guardado: {force_vector['real_magnitude']:.1f} {force_vector['unit']}")
                                else:
                                    st.success(f"Vector de fuerza guardado: {force_vector['magnitude']:.1f} px")
                                
                                st.experimental_rerun()
                            else:
                                st.error("No se pudo definir el vector. Asegúrate de dibujar una línea.")
                    
                    elif tool_type == "moment":
                        st.markdown("""
                        <div class="drawing-instructions">
                            <h4>Análisis de Brazo de Momento</h4>
                            <p>Primero: Selecciona un punto de pivote (articulación). Segundo: Selecciona un vector de fuerza existente.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Mostrar vectores de fuerza disponibles
                        frame_vectors = [v for v in st.session_state.force_vectors if v["frame_index"] == st.session_state.frame_index]
                        
                        if not frame_vectors:
                            st.warning("Primero necesitas crear al menos un vector de fuerza en este frame.")
                        else:
                            # Opciones para pivote
                            pivot_desc = st.text_input("Descripción del punto de pivote:", placeholder="Ej: Centro de rotación de rodilla", key="pivot_desc")
                            
                            # Canvas para seleccionar punto de pivote
                            st.markdown("**Paso 1: Selecciona el punto de pivote (articulación)**")
                            canvas_result = st_canvas(
                                fill_color="rgba(255, 215, 0, 0.3)",
                                stroke_width=3,
                                stroke_color="#FFD700",  # Gold
                                background_image=Image.fromarray(st.session_state.current_frame),
                                height=st.session_state.frame_height,
                                width=st.session_state.frame_width,
                                drawing_mode="circle",
                                key="canvas_pivot",
                                update_streamlit=True
                            )
                            
                            st.session_state.last_canvas_output = canvas_result
                            
                            # Botón para guardar punto de pivote
                            if st.button("Guardar Punto de Pivote"):
                                pivot = process_pivot_selection(
                                    st.session_state.last_canvas_output,
                                    description=pivot_desc
                                )
                                
                                if pivot:
                                    st.session_state.pivots.append(pivot)
                                    st.success(f"Punto de pivote guardado.")
                                    st.experimental_rerun()
                                else:
                                    st.error("No se pudo seleccionar el pivote. Asegúrate de dibujar un punto.")
                            
                            # Paso 2: Seleccionar un vector de fuerza existente
                            st.markdown("**Paso 2: Selecciona un vector de fuerza existente**")
                            
                            # Mostrar vectores disponibles
                            vector_options = {v["id"]: f"{v.get('description', 'Vector')} ({v.get('magnitude', 0):.1f} px)" for v in frame_vectors}
                            selected_vector_id = st.selectbox("Vector de fuerza:", list(vector_options.keys()), format_func=lambda x: vector_options[x])
                            
                            # Mostrar puntos de pivote disponibles
                            frame_pivots = [p for p in st.session_state.pivots if p["frame_index"] == st.session_state.frame_index]
                            if frame_pivots:
                                pivot_options = {p["id"]: f"{p.get('description', 'Pivote')}" for p in frame_pivots}
                                selected_pivot_id = st.selectbox("Punto de pivote:", list(pivot_options.keys()), format_func=lambda x: pivot_options[x])
                                
                                # Botón para calcular brazo de momento
                                if st.button("Calcular Brazo de Momento"):
                                    # Obtener el vector y pivote seleccionados
                                    selected_vector = next((v for v in frame_vectors if v["id"] == selected_vector_id), None)
                                    selected_pivot = next((p for p in frame_pivots if p["id"] == selected_pivot_id), None)
                                    
                                    if selected_vector and selected_pivot:
                                        moment_arm = process_moment_arm(
                                            selected_pivot,
                                            selected_vector,
                                            description=f"Brazo de momento para {selected_vector.get('description', 'fuerza')}"
                                        )
                                        
                                        if moment_arm:
                                            st.session_state.moment_arms.append(moment_arm)
                                            
                                            # Mostrar en unidades correctas
                                            if "real_value" in moment_arm and "unit" in moment_arm:
                                                st.success(f"Brazo de momento calculado: {moment_arm['real_value']:.1f} {moment_arm['unit']}")
                                            else:
                                                st.success(f"Brazo de momento calculado: {moment_arm['value']:.1f} px")
                                            
                                            st.experimental_rerun()
                                        else:
                                            st.error("No se pudo calcular el brazo de momento.")
                                    else:
                                        st.error("No se encontró el vector o pivote seleccionado.")
                            else:
                                st.warning("Primero necesitas crear al menos un punto de pivote en este frame.")
                
                # Panel lateral con información
                with col2:
                    st.subheader("Información")
                    
                    # Mostrar información del frame
                    st.text(f"Frame {st.session_state.frame_index + 1} de {st.session_state.total_frames}")
                    st.text(f"Resolución: {st.session_state.frame_width}x{st.session_state.frame_height}")
                    
                    # Explicación de las herramientas
                    with st.expander("Guía de Herramientas", expanded=False):
                        st.markdown("""
                        **Herramientas de Análisis:**
                        
                        - **Ángulo Articular**: Mide ángulos entre segmentos corporales.
                        - **Medir Distancia**: Calcula longitudes de segmentos.
                        - **Vector de Fuerza**: Dibuja vectores para representar fuerzas.
                        - **Brazo de Momento**: Calcula el brazo de momento (distancia perpendicular entre un punto de pivote y la línea de acción de una fuerza).
                        
                        **Conceptos Biomecánicos:**
                        
                        - **Brazo de Palanca**: Distancia desde un eje de rotación al punto de aplicación de una fuerza.
                        - **Brazo de Momento**: Distancia perpendicular entre el eje de rotación y la línea de acción de una fuerza.
                        - **Torque**: Producto del brazo de momento y la magnitud de la fuerza.
                        """)
                    
                    # Resumen de mediciones en este frame
                    st.subheader("Mediciones en este Frame")
                    
                    # Combinar todas las mediciones para este frame
                    frame_measurements = [m for m in st.session_state.measurements if m["frame_index"] == st.session_state.frame_index]
                    frame_vectors = [v for v in st.session_state.force_vectors if v["frame_index"] == st.session_state.frame_index]
                    frame_pivots = [p for p in st.session_state.pivots if p["frame_index"] == st.session_state.frame_index]
                    frame_moments = [m for m in st.session_state.moment_arms if m["frame_index"] == st.session_state.frame_index]
                    
                    all_measurements = frame_measurements + frame_vectors + frame_moments
                    
                    if not all_measurements and not frame_pivots:
                        st.info("No hay mediciones en este frame. Utiliza las herramientas para añadir análisis.")
                    else:
                        # Mostrar ángulos
                        angles = [m for m in frame_measurements if m["type"] == "Ángulo"]
                        if angles:
                            st.write("**Ángulos:**")
                            for i, m in enumerate(angles):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.write(f"- {m['joint']}: {m['value']:.1f}° ({m.get('description', '')})")
                                with col2:
                                    if st.button("🗑️", key=f"del_angle_{i}"):
                                        st.session_state.measurements.remove(m)
                                        st.experimental_rerun()
                        
                        # Mostrar líneas
                        lines = [m for m in frame_measurements if m["type"] == "Línea"]
                        if lines:
                            st.write("**Distancias:**")
                            for i, m in enumerate(lines):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    if "real_value" in m and "unit" in m:
                                        st.write(f"- {m['joint']}: {m['real_value']:.1f} {m['unit']} ({m.get('description', '')})")
                                    else:
                                        st.write(f"- {m['joint']}: {m['value']:.1f} px ({m.get('description', '')})")
                                with col2:
                                    if st.button("🗑️", key=f"del_line_{i}"):
                                        st.session_state.measurements.remove(m)
                                        st.experimental_rerun()
                        
                        # Mostrar pivotes
                        if frame_pivots:
                            st.write("**Puntos de Pivote:**")
                            for i, p in enumerate(frame_pivots):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.write(f"- {p.get('description', 'Pivote')}")
                                with col2:
                                    if st.button("🗑️", key=f"del_pivot_{i}"):
                                        st.session_state.pivots.remove(p)
                                        st.experimental_rerun()
                        
                        # Mostrar vectores de fuerza
                        if frame_vectors:
                            st.write("**Vectores de Fuerza:**")
                            for i, v in enumerate(frame_vectors):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    if "real_magnitude" in v and "unit" in v:
                                        st.write(f"- {v.get('description', 'Vector')}: {v['real_magnitude']:.1f} {v['unit']}")
                                    else:
                                        st.write(f"- {v.get('description', 'Vector')}: {v['magnitude']:.1f} px")
                                with col2:
                                    if st.button("🗑️", key=f"del_vector_{i}"):
                                        # También eliminar brazos de momento asociados
                                        st.session_state.moment_arms = [m for m in st.session_state.moment_arms if m.get("force_vector_id") != v["id"]]
                                        st.session_state.force_vectors.remove(v)
                                        st.experimental_rerun()
                        
                        # Mostrar brazos de momento
                        if frame_moments:
                            st.write("**Brazos de Momento:**")
                            for i, m in enumerate(frame_moments):
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    if "real_value" in m and "unit" in m:
                                        st.write(f"- {m.get('description', 'Brazo de Momento')}: {m['real_value']:.1f} {m['unit']}")
                                    else:
                                        st.write(f"- {m.get('description', 'Brazo de Momento')}: {m['value']:.1f} px")
                                with col2:
                                    if st.button("🗑️", key=f"del_moment_{i}"):
                                        st.session_state.moment_arms.remove(m)
                                        st.experimental_rerun()
                    
                    # Exportar frame actual
                    if st.button("Exportar Frame con Análisis"):
                        if st.session_state.current_frame is not None:
                            # Preparar frame para exportación
                            export_frame = display_frame.copy()  # Ya tiene todas las mediciones dibujadas
                            
                            # Guardar imagen temporalmente
                            img_path = os.path.join("temp", f"frame_export_{uuid.uuid4()}.jpg")
                            cv2.imwrite(img_path, cv2.cvtColor(export_frame, cv2.COLOR_RGB2BGR))
                            
                            # Ofrecer para descargar
                            with open(img_path, "rb") as file:
                                btn = st.download_button(
                                    label="Descargar Imagen",
                                    data=file,
                                    file_name=f"analisis_frame_{st.session_state.frame_index}.jpg",
                                    mime="image/jpeg"
                                )
                            
                            # Limpiar archivo
                            if os.path.exists(img_path):
                                os.remove(img_path)
                    
                    # Borrar mediciones del frame
                    if st.button("Borrar Mediciones de este Frame", type="secondary"):
                        # Filtrar mediciones que no son del frame actual
                        st.session_state.measurements = [m for m in st.session_state.measurements if m["frame_index"] != st.session_state.frame_index]
                        st.session_state.pivots = [p for p in st.session_state.pivots if p["frame_index"] != st.session_state.frame_index]
                        st.session_state.force_vectors = [v for v in st.session_state.force_vectors if v["frame_index"] != st.session_state.frame_index]
                        st.session_state.moment_arms = [m for m in st.session_state.moment_arms if m["frame_index"] != st.session_state.frame_index]
                        st.success("Mediciones borradas correctamente!")
                        st.experimental_rerun()
                
                # Formulario para datos de la sesión
                st.subheader("Guardar Sesión")
                
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
                            # Recopilar todas las mediciones
                            all_session_measurements = []
                            all_session_measurements.extend(st.session_state.measurements)
                            all_session_measurements.extend(st.session_state.pivots)
                            all_session_measurements.extend(st.session_state.force_vectors)
                            all_session_measurements.extend(st.session_state.moment_arms)
                            
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
                                "measurements": all_session_measurements,
                                "video_name": st.session_state.current_video,
                                "calibration_factor": st.session_state.calibration_factor,
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
                            calibration = session.get("calibration_factor", 1.0)
                            
                            for m in session["measurements"]:
                                if m["type"] == "Ángulo":
                                    st.write(f"- {m.get('joint', 'Ángulo')}: {m['value']:.1f}° ({m.get('description', '')})")
                                elif m["type"] == "Línea":
                                    if calibration != 1.0 and "value" in m:
                                        real_distance = m.get("real_value", m["value"] / calibration)
                                        st.write(f"- {m.get('joint', 'Distancia')}: {real_distance:.1f} cm ({m.get('description', '')})")
                                    else:
                                        st.write(f"- {m.get('joint', 'Distancia')}: {m.get('value', 0):.1f} px ({m.get('description', '')})")
                                elif m["type"] == "Vector de Fuerza":
                                    if calibration != 1.0 and "magnitude" in m:
                                        real_magnitude = m.get("real_magnitude", m["magnitude"] / calibration)
                                        st.write(f"- Vector de Fuerza: {real_magnitude:.1f} cm ({m.get('description', '')})")
                                    elif "magnitude" in m:
                                        st.write(f"- Vector de Fuerza: {m['magnitude']:.1f} px ({m.get('description', '')})")
                                elif m["type"] == "Brazo de Momento" and "value" in m:
                                    if calibration != 1.0:
                                        real_value = m.get("real_value", m["value"] / calibration)
                                        st.write(f"- Brazo de Momento: {real_value:.1f} cm ({m.get('description', '')})")
                                    else:
                                        st.write(f"- Brazo de Momento: {m['value']:.1f} px ({m.get('description', '')})")
    
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
                        try:
                            # Recrear un frame con análisis
                            frame_with_analysis = None
                            
                            if st.session_state.current_video_path is not None and st.session_state.current_frame is not None:
                                # Encontrar el frame con más mediciones
                                frame_counts = {}
                                for m in selected_session.get("measurements", []):
                                    frame_idx = m.get("frame_index", 0)
                                    if frame_idx not in frame_counts:
                                        frame_counts[frame_idx] = 0
                                    frame_counts[frame_idx] += 1
                                
                                if frame_counts:
                                    best_frame = max(frame_counts.items(), key=lambda x: x[1])[0]
                                    # Cargar el frame
                                    get_frame(best_frame)
                                    frame_with_analysis = st.session_state.current_frame.copy()
                                    
                                    # Dibujar mediciones
                                    for m in selected_session.get("measurements", []):
                                        if m.get("frame_index") == best_frame:
                                            if m["type"] == "Ángulo" and "points" in m and len(m["points"]) == 3:
                                                draw_angle(frame_with_analysis, m["points"], m["value"], color=(231, 76, 60))
                                            elif m["type"] == "Línea" and "points" in m and len(m["points"]) == 2:
                                                unit = m.get("unit", "px")
                                                value = m.get("real_value", m["value"])
                                                draw_line(frame_with_analysis, m["points"], value, color=(46, 204, 113), unit=unit)
                                            elif m["type"] == "Pivote" and "point" in m:
                                                draw_pivot(frame_with_analysis, m["point"], color=(255, 215, 0))
                                            elif m["type"] == "Vector de Fuerza" and "points" in m:
                                                draw_force_vector(frame_with_analysis, m["points"], m.get("description", ""), color=(155, 89, 182))
                                            elif m["type"] == "Brazo de Momento" and "pivot" in m and "perpendicular_point" in m:
                                                unit = m.get("unit", "px")
                                                value = m.get("real_value", m["value"])
                                                draw_moment_arm(frame_with_analysis, m["pivot"], m["perpendicular_point"], value, color=(231, 76, 60), unit=unit)
                            
                            # Generar gráficos de progreso para el PDF
                            # Preparar datos para gráficos
                            client_exercise_sessions = [s for s in sessions if s["client_id"] == selected_client_id and s["exercise"] == selected_session["exercise"]]
                            
                            progress_charts = []
                            if len(client_exercise_sessions) > 1:
                                # Directorio temporal para gráficos
                                os.makedirs("temp", exist_ok=True)
                                
                                # Gráfico de volumen
                                dates = [s["date"] for s in client_exercise_sessions]
                                volumes = [s["sets"] * s["reps"] for s in client_exercise_sessions]
                                
                                df = pd.DataFrame({
                                    "Fecha": dates,
                                    "Volumen (Sets x Reps)": volumes
                                })
                                
                                fig_volume = px.line(
                                    df, 
                                    x="Fecha", 
                                    y="Volumen (Sets x Reps)",
                                    title="Progresión de Volumen",
                                    markers=True
                                )
                                
                                volume_chart_path = os.path.join("temp", f"volume_chart_{uuid.uuid4()}.png")
                                fig_volume.write_image(volume_chart_path, width=700, height=400)
                                progress_charts.append(volume_chart_path)
                                
                                # También podríamos añadir un gráfico de RIR
                                rirs = [s["rir"] for s in client_exercise_sessions]
                                
                                df_rir = pd.DataFrame({
                                    "Fecha": dates,
                                    "RIR": rirs
                                })
                                
                                fig_rir = px.line(
                                    df_rir, 
                                    x="Fecha", 
                                    y="RIR",
                                    title="Progresión de RIR",
                                    markers=True
                                )
                                fig_rir.update_layout(yaxis=dict(autorange="reversed"))
                                
                                rir_chart_path = os.path.join("temp", f"rir_chart_{uuid.uuid4()}.png")
                                fig_rir.write_image(rir_chart_path, width=700, height=400)
                                progress_charts.append(rir_chart_path)
                            
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
                            
                            # Limpiar archivos temporales
                            for chart_path in progress_charts:
                                if os.path.exists(chart_path):
                                    os.remove(chart_path)
                        
                        except Exception as e:
                            st.error(f"Error al generar el PDF: {str(e)}")

if __name__ == "__main__":
    main()
