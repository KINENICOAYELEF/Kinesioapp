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
import mediapipe as mp

# Configuración de la página
st.set_page_config(page_title="KinesioApp", page_icon="🏋️", layout="wide")

# Crear directorios necesarios si no existen
os.makedirs("temp", exist_ok=True)
os.makedirs("data", exist_ok=True)
    
# Archivo para almacenar datos de clientes
CLIENTS_FILE = "data/clients.json"
SESSIONS_FILE = "data/sessions.json"

# Inicializar modelos de MediaPipe para detección de pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

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
    
    /* Arreglo para que el canvas se muestre correctamente */
    [data-testid="stImage"] {
        display: block !important;
        max-width: 100% !important;
    }
    
    .canvas-container {
        margin: 0 auto;
        max-width: 100%;
        overflow: hidden;
    }
    
    .biomech-tool {
        background-color: #ecf0f1;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 3px solid #3498db;
    }
    
    .force-vector {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .leverage-arm {
        color: #9b59b6;
        font-weight: bold;
    }
    
    .moment-arm {
        color: #f39c12;
        font-weight: bold;
    }
    
    .detection-panel {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    
    .analysis-result {
        background-color: #e8f4fd;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2ecc71;
    }
    
    .result-value {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.1em;
    }
    
    .segment-name {
        color: #3498db;
        font-weight: 600;
    }
    
    .angle-name {
        color: #e74c3c;
        font-weight: 600;
    }
    
    .moment-name {
        color: #9b59b6;
        font-weight: 600;
    }
    
    .ai-button {
        background-color: #9b59b6 !important;
    }
    
    .ai-button:hover {
        background-color: #8e44ad !important;
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
if "pose_landmarks" not in st.session_state:
    st.session_state.pose_landmarks = None
if "calibration_factor" not in st.session_state:
    st.session_state.calibration_factor = 1.0  # Píxeles por cm
if "angle_measurements" not in st.session_state:
    st.session_state.angle_measurements = []
if "limb_measurements" not in st.session_state:
    st.session_state.limb_measurements = []
if "force_vectors" not in st.session_state:
    st.session_state.force_vectors = []
if "moment_arms" not in st.session_state:
    st.session_state.moment_arms = []
if "analyze_with_ai" not in st.session_state:
    st.session_state.analyze_with_ai = False

# Definición de puntos de referencia para ángulos comunes
LANDMARK_DICT = {
    "Tobillo Derecho": [mp_pose.PoseLandmark.RIGHT_ANKLE, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_HEEL],
    "Tobillo Izquierdo": [mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_HEEL],
    "Rodilla Derecha": [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE],
    "Rodilla Izquierda": [mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE],
    "Cadera Derecha": [mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE],
    "Cadera Izquierda": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE],
    "Codo Derecho": [mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],
    "Codo Izquierdo": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST],
    "Hombro Derecho": [mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP],
    "Hombro Izquierdo": [mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP],
    "Tronco": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE]
}

# Definición de segmentos corporales
SEGMENT_DICT = {
    "Antebrazo Derecho": [mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],
    "Antebrazo Izquierdo": [mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST],
    "Brazo Derecho": [mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW],
    "Brazo Izquierdo": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW],
    "Muslo Derecho": [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE],
    "Muslo Izquierdo": [mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE],
    "Pierna Derecha": [mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE],
    "Pierna Izquierda": [mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE],
    "Tronco": [mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP]
}

# Funciones para el análisis de video
def process_video(video_file):
    """Procesa un video y lo almacena temporalmente"""
    try:
        # Directorio temporal
        if not os.path.exists("temp"):
            os.makedirs("temp")
            
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
        
        # Obtener primer frame para verificar
        ret, frame = cap.read()
        if not ret:
            st.error("No se pudo leer el primer frame del video.")
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
                
                # Si la opción de análisis con IA está activada, detectar automáticamente
                if st.session_state.analyze_with_ai:
                    detect_pose(frame_rgb)
                else:
                    st.session_state.pose_landmarks = None
                    
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

def detect_pose(frame):
    """Detecta los puntos de referencia de la pose usando MediaPipe"""
    try:
        with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=False,
                min_detection_confidence=0.5) as pose:
            
            results = pose.process(frame)
            
            if results.pose_landmarks:
                st.session_state.pose_landmarks = results.pose_landmarks
                return True
            else:
                st.session_state.pose_landmarks = None
                return False
    except Exception as e:
        st.error(f"Error en la detección de pose: {str(e)}")
        st.session_state.pose_landmarks = None
        return False

def get_landmark_coordinates(landmark_index):
    """Obtiene las coordenadas normalizadas de un punto de referencia"""
    if st.session_state.pose_landmarks is None:
        return None
    
    landmark = st.session_state.pose_landmarks.landmark[landmark_index]
    
    # Convertir de coordenadas normalizadas a coordenadas de píxeles
    x = int(landmark.x * st.session_state.frame_width)
    y = int(landmark.y * st.session_state.frame_height)
    
    # Comprobar visibilidad
    if landmark.visibility < 0.5:  # Umbral de visibilidad
        return None
        
    return (x, y)

def calculate_angle(p1, p2, p3):
    """Calcula el ángulo entre tres puntos (en grados)"""
    if p1 is None or p2 is None or p3 is None:
        return None
        
    # Vectores
    a = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    b = np.array([p3[0] - p2[0], p3[1] - p2[1]])
    
    # Verificar vectores no nulos
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return None
    
    # Calcular el ángulo
    cos_angle = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_distance(p1, p2):
    """Calcula la distancia entre dos puntos"""
    if p1 is None or p2 is None:
        return None
        
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p2[1])**2)

def calculate_moment_arm(pivot_point, force_line_p1, force_line_p2):
    """
    Calcula el brazo de momento (distancia perpendicular desde el punto de pivote a la línea de fuerza)
    """
    if pivot_point is None or force_line_p1 is None or force_line_p2 is None:
        return None
        
    # Vectorizar para facilitar cálculos
    pivot = np.array(pivot_point)
    p1 = np.array(force_line_p1)
    p2 = np.array(force_line_p2)
    
    # Vector de dirección de la línea de fuerza
    force_direction = p2 - p1
    force_direction_norm = np.linalg.norm(force_direction)
    
    # Evitar división por cero
    if force_direction_norm == 0:
        return None
    
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
    
    return moment_arm

def get_key_body_landmarks():
    """Obtiene los puntos clave del cuerpo para análisis biomecánico"""
    if st.session_state.pose_landmarks is None:
        return None
    
    landmarks = {}
    
    # Articulaciones principales
    key_joints = {
        "Hombro Der": mp_pose.PoseLandmark.RIGHT_SHOULDER,
        "Hombro Izq": mp_pose.PoseLandmark.LEFT_SHOULDER,
        "Codo Der": mp_pose.PoseLandmark.RIGHT_ELBOW,
        "Codo Izq": mp_pose.PoseLandmark.LEFT_ELBOW,
        "Muñeca Der": mp_pose.PoseLandmark.RIGHT_WRIST,
        "Muñeca Izq": mp_pose.PoseLandmark.LEFT_WRIST,
        "Cadera Der": mp_pose.PoseLandmark.RIGHT_HIP,
        "Cadera Izq": mp_pose.PoseLandmark.LEFT_HIP,
        "Rodilla Der": mp_pose.PoseLandmark.RIGHT_KNEE,
        "Rodilla Izq": mp_pose.PoseLandmark.LEFT_KNEE,
        "Tobillo Der": mp_pose.PoseLandmark.RIGHT_ANKLE,
        "Tobillo Izq": mp_pose.PoseLandmark.LEFT_ANKLE
    }
    
    for name, landmark_id in key_joints.items():
        landmarks[name] = get_landmark_coordinates(landmark_id)
        
    return landmarks

def draw_landmark_connections(frame):
    """Dibuja las conexiones entre puntos de referencia en el frame"""
    if frame is None or st.session_state.pose_landmarks is None:
        return frame
    
    annotated_frame = frame.copy()
    
    # Dibujar puntos y conexiones
    mp_drawing.draw_landmarks(
        annotated_frame,
        st.session_state.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )
    
    return annotated_frame

def analyze_all_angles():
    """Analiza todos los ángulos articulares predefinidos"""
    if st.session_state.pose_landmarks is None:
        return []
    
    angle_results = []
    
    for angle_name, landmarks in LANDMARK_DICT.items():
        p1 = get_landmark_coordinates(landmarks[0])
        p2 = get_landmark_coordinates(landmarks[1])
        p3 = get_landmark_coordinates(landmarks[2])
        
        if p1 and p2 and p3:
            angle = calculate_angle(p1, p2, p3)
            if angle is not None:
                # Guardar medición
                measurement = {
                    "id": str(uuid.uuid4()),
                    "type": "Ángulo",
                    "joint": angle_name,
                    "value": angle,
                    "points": [p1, p2, p3],
                    "frame_index": st.session_state.frame_index,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": f"Ángulo de {angle_name}"
                }
                angle_results.append(measurement)
    
    return angle_results

def analyze_all_segments():
    """Analiza todos los segmentos corporales predefinidos"""
    if st.session_state.pose_landmarks is None:
        return []
    
    segment_results = []
    
    for segment_name, landmarks in SEGMENT_DICT.items():
        p1 = get_landmark_coordinates(landmarks[0])
        p2 = get_landmark_coordinates(landmarks[1])
        
        if p1 and p2:
            distance = calculate_distance(p1, p2)
            if distance is not None:
                # Convertir a cm si hay calibración
                if st.session_state.calibration_factor != 1.0:
                    real_distance = distance / st.session_state.calibration_factor
                    unit = "cm"
                else:
                    real_distance = distance
                    unit = "px"
                
                # Guardar medición
                measurement = {
                    "id": str(uuid.uuid4()),
                    "type": "Línea",
                    "joint": segment_name,
                    "value": distance,
                    "real_value": real_distance,
                    "unit": unit,
                    "points": [p1, p2],
                    "frame_index": st.session_state.frame_index,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": f"Longitud de {segment_name}"
                }
                segment_results.append(measurement)
    
    return segment_results

def analyze_gravity_moments():
    """Analiza los momentos de fuerza producidos por la gravedad"""
    if st.session_state.pose_landmarks is None:
        return []
    
    moment_results = []
    
    # Definir articulaciones de pivote y segmentos para análisis de momento
    moment_analyses = [
        {
            "name": "Momento Flexión Codo Der",
            "pivot": mp_pose.PoseLandmark.RIGHT_ELBOW,
            "com": [mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST],  # Centro de masa aproximado
            "force_dir": [0, 1]  # Dirección hacia abajo (gravedad)
        },
        {
            "name": "Momento Flexión Codo Izq",
            "pivot": mp_pose.PoseLandmark.LEFT_ELBOW,
            "com": [mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST],
            "force_dir": [0, 1]
        },
        {
            "name": "Momento Flexión Rodilla Der",
            "pivot": mp_pose.PoseLandmark.RIGHT_KNEE,
            "com": [mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE],
            "force_dir": [0, 1]
        },
        {
            "name": "Momento Flexión Rodilla Izq",
            "pivot": mp_pose.PoseLandmark.LEFT_KNEE,
            "com": [mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE],
            "force_dir": [0, 1]
        },
        {
            "name": "Momento Flexión Cadera Der",
            "pivot": mp_pose.PoseLandmark.RIGHT_HIP,
            "com": [mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE],
            "force_dir": [0, 1]
        },
        {
            "name": "Momento Flexión Cadera Izq",
            "pivot": mp_pose.PoseLandmark.LEFT_HIP,
            "com": [mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE],
            "force_dir": [0, 1]
        }
    ]
    
    for analysis in moment_analyses:
        # Obtener punto de pivote
        pivot = get_landmark_coordinates(analysis["pivot"])
        
        if pivot:
            # Obtener punto aproximado del centro de masa (punto medio del segmento como aproximación)
            p1 = get_landmark_coordinates(analysis["com"][0])
            p2 = get_landmark_coordinates(analysis["com"][1])
            
            if p1 and p2:
                com_x = (p1[0] + p2[0]) // 2
                com_y = (p1[1] + p2[1]) // 2
                com = (com_x, com_y)
                
                # Crear un segundo punto para la línea de fuerza (siguiendo la dirección de la gravedad)
                force_x = com[0] + analysis["force_dir"][0] * 100  # Extender 100px
                force_y = com[1] + analysis["force_dir"][1] * 100
                force_end = (force_x, force_y)
                
                # Calcular el brazo de momento
                moment_arm_value = calculate_moment_arm(pivot, com, force_end)
                
                if moment_arm_value is not None:
                    # Convertir a cm si hay calibración
                    if st.session_state.calibration_factor != 1.0:
                        real_value = moment_arm_value / st.session_state.calibration_factor
                        unit = "cm"
                    else:
                        real_value = moment_arm_value
                        unit = "px"
                    
                    # Crear vector de fuerza
                    force_vector = {
                        "id": str(uuid.uuid4()),
                        "type": "Vector de Fuerza",
                        "points": [com, force_end],
                        "description": f"Gravedad en {analysis['name']}",
                        "frame_index": st.session_state.frame_index,
                        "magnitude": calculate_distance(com, force_end),
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Crear medición de brazo de momento
                    moment = {
                        "id": str(uuid.uuid4()),
                        "type": "Brazo de Momento",
                        "joint": analysis["name"],
                        "value": moment_arm_value,
                        "real_value": real_value,
                        "unit": unit,
                        "pivot": pivot,
                        "force_vector_id": force_vector["id"],
                        "force_vector": force_vector,  # Incluir el vector para facilitar el dibujo
                        "frame_index": st.session_state.frame_index,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "description": analysis["name"]
                    }
                    
                    moment_results.append(moment)
    
    return moment_results

def draw_angle(frame, points, angle, color=(255, 0, 0)):
    """Dibuja un ángulo en el frame"""
    if frame is None or not all(p is not None for p in points):
        return frame
        
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
    if frame is None or not all(p is not None for p in points):
        return frame
        
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

def draw_force_vector(frame, points, description="", color=(255, 0, 0)):
    """Dibuja un vector de fuerza con flecha en el frame"""
    if frame is None or not all(p is not None for p in points):
        return frame
        
    # Dibujar flecha
    cv2.arrowedLine(frame, points[0], points[1], color, 2, tipLength=0.2)
    
    # Mostrar la descripción
    text_pos = (points[1][0] + 10, points[1][1] + 10)
    cv2.putText(frame, description, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def draw_moment_arm(frame, pivot, force_vector, moment_value, color=(148, 0, 211), unit="px"):
    """Dibuja el brazo de momento (distancia perpendicular) en el frame"""
    if frame is None or pivot is None or force_vector is None:
        return frame
    
    # Extraer puntos
    if isinstance(force_vector, dict) and "points" in force_vector:
        force_p1, force_p2 = force_vector["points"]
    else:
        return frame
    
    # Vectorizar para facilitar cálculos
    pivot_np = np.array(pivot)
    p1 = np.array(force_p1)
    p2 = np.array(force_p2)
    
    # Vector de dirección de la línea de fuerza
    force_direction = p2 - p1
    force_direction_norm = np.linalg.norm(force_direction)
    
    # Evitar división por cero
    if force_direction_norm == 0:
        return frame
    
    # Normalizar vector de dirección
    force_direction = force_direction / force_direction_norm
    
    # Vector desde un punto de la línea al pivote
    pivot_to_line = pivot_np - p1
    
    # Proyección escalar del vector pivot_to_line sobre force_direction
    projection = np.dot(pivot_to_line, force_direction)
    
    # Punto más cercano en la línea de fuerza al pivote
    closest_point = p1 + projection * force_direction
    closest_point_tuple = (int(closest_point[0]), int(closest_point[1]))
    
    # Dibujar línea del brazo de momento
    cv2.line(frame, pivot, closest_point_tuple, color, 2, cv2.LINE_AA)
    
    # Mostrar puntos
    cv2.circle(frame, pivot, 5, color, -1)
    cv2.circle(frame, closest_point_tuple, 5, color, -1)
    
    # Mostrar el valor
    mid_x = (pivot[0] + closest_point_tuple[0]) // 2
    mid_y = (pivot[1] + closest_point_tuple[1]) // 2
    text_pos = (mid_x + 5, mid_y - 5)
    
    cv2.putText(frame, f"BM: {moment_value:.1f} {unit}", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return frame

def save_measurements(measurements):
    """Guarda las mediciones en el estado de la sesión"""
    for m in measurements:
        if m["type"] == "Ángulo":
            st.session_state.angle_measurements.append(m)
        elif m["type"] == "Línea":
            st.session_state.limb_measurements.append(m)
        elif m["type"] == "Brazo de Momento":
            # Guardar el vector de fuerza asociado
            if "force_vector" in m:
                st.session_state.force_vectors.append(m["force_vector"])
            st.session_state.moment_arms.append(m)

def save_session_data(client, form_data):
    """Guarda los datos de la sesión"""
    # Recopilar todas las mediciones
    all_measurements = []
    all_measurements.extend(st.session_state.angle_measurements)
    all_measurements.extend(st.session_state.limb_measurements)
    all_measurements.extend(st.session_state.force_vectors)
    all_measurements.extend(st.session_state.moment_arms)
    
    # Crear datos de la sesión
    session_data = {
        "id": str(uuid.uuid4()),
        "client_id": client["id"],
        "date": form_data.get("date", datetime.date.today().strftime("%Y-%m-%d")),
        "exercise": form_data.get("exercise", ""),
        "sets": form_data.get("sets", 0),
        "reps": form_data.get("reps", 0),
        "rir": form_data.get("rir", 0),
        "comments": form_data.get("comments", ""),
        "measurements": all_measurements,
        "video_name": st.session_state.current_video,
        "calibration_factor": st.session_state.calibration_factor,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Cargar sesiones existentes
    sessions = load_sessions()
    
    # Añadir la nueva sesión
    sessions.append(session_data)
    
    # Guardar en archivo
    save_sessions(sessions)
    
    return True

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
        data = [["Tipo", "Articulación/Descripción", "Valor", "Notas"]]
        for m in measurements:
            value_text = ""
            if m["type"] == "Ángulo":
                value_text = f"{m['value']:.1f}°"
            elif m["type"] == "Línea":
                unit = m.get("unit", "px")
                if "real_value" in m:
                    value_text = f"{m['real_value']:.1f} {unit}"
                else:
                    value_text = f"{m['value']:.1f} {unit}"
            elif m["type"] == "Vector de Fuerza":
                if "magnitude" in m:
                    value_text = f"{m['magnitude']:.1f} px"
            elif m["type"] == "Brazo de Momento":
                unit = m.get("unit", "px")
                if "real_value" in m:
                    value_text = f"{m['real_value']:.1f} {unit}"
                else:
                    value_text = f"{m['value']:.1f} {unit}"
            
            data.append([
                m["type"],
                m.get("joint", m.get("description", "")),
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
    st.markdown("<h1 class='title'>🏋️ KinesioApp - Análisis Biomecánico Automático</h1>", unsafe_allow_html=True)
    
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
                st.session_state.angle_measurements = []
                st.session_state.limb_measurements = []
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
                    # Activar/desactivar detección automática
                    ai_analyze = st.checkbox("Activar análisis automático con IA", value=st.session_state.analyze_with_ai)
                    
                    if ai_analyze != st.session_state.analyze_with_ai:
                        st.session_state.analyze_with_ai = ai_analyze
                        # Si se activa, detectar pose inmediatamente
                        if ai_analyze and st.session_state.current_frame is not None:
                            detect_pose(st.session_state.current_frame)
                    
                    # Preparar frame para visualización
                    if st.session_state.current_frame is not None:
                        display_frame = st.session_state.current_frame.copy()
                        
                        # Si la detección automática está activada, dibujar el esqueleto
                        if st.session_state.analyze_with_ai and st.session_state.pose_landmarks is not None:
                            display_frame = draw_landmark_connections(display_frame)
                            
                            # Dibujar mediciones de ángulos
                            for m in st.session_state.angle_measurements:
                                if m["frame_index"] == st.session_state.frame_index and "points" in m and len(m["points"]) == 3:
                                    draw_angle(display_frame, m["points"], m["value"], color=(255, 0, 0))
                            
                            # Dibujar mediciones de segmentos
                            for m in st.session_state.limb_measurements:
                                if m["frame_index"] == st.session_state.frame_index and "points" in m and len(m["points"]) == 2:
                                    unit = m.get("unit", "px")
                                    value = m.get("real_value", m["value"])
                                    draw_line(display_frame, m["points"], value, color=(0, 255, 0), unit=unit)
                            
                            # Dibujar vectores de fuerza
                            for v in st.session_state.force_vectors:
                                if v["frame_index"] == st.session_state.frame_index and "points" in v:
                                    draw_force_vector(display_frame, v["points"], v.get("description", ""), color=(231, 76, 60))
                            
                            # Dibujar brazos de momento
                            for m in st.session_state.moment_arms:
                                if m["frame_index"] == st.session_state.frame_index and "pivot" in m:
                                    # Encontrar el vector asociado
                                    if "force_vector" in m:
                                        unit = m.get("unit", "px")
                                        value = m.get("real_value", m["value"])
                                        draw_moment_arm(display_frame, m["pivot"], m["force_vector"], value, color=(148, 0, 211), unit=unit)
                        
                        # Mostrar el frame
                        st.image(display_frame, channels="RGB", use_column_width=True)
                    else:
                        st.warning("No se pudo cargar el frame del video.")
                    
                    # Panel de análisis automático
                    if st.session_state.analyze_with_ai and st.session_state.pose_landmarks is not None:
                        st.markdown("""
                        <div class='detection-panel'>
                            <h3>Análisis Biomecánico Automático</h3>
                            <p>La IA ha detectado al sujeto en el frame. Selecciona qué análisis quieres realizar.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Calcular Ángulos Articulares", key="calc_angles", type="primary", use_container_width=True):
                                with st.spinner("Calculando ángulos articulares..."):
                                    angle_results = analyze_all_angles()
                                    if angle_results:
                                        save_measurements(angle_results)
                                        st.success(f"Se calcularon {len(angle_results)} ángulos articulares!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("No se pudieron detectar ángulos articulares. Intenta con otro frame.")
                        
                        with col2:
                            if st.button("Medir Segmentos Corporales", key="calc_segments", type="primary", use_container_width=True):
                                with st.spinner("Midiendo segmentos corporales..."):
                                    segment_results = analyze_all_segments()
                                    if segment_results:
                                        save_measurements(segment_results)
                                        st.success(f"Se midieron {len(segment_results)} segmentos corporales!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("No se pudieron detectar segmentos corporales. Intenta con otro frame.")
                        
                        with col3:
                            if st.button("Analizar Brazos de Momento", key="calc_moments", type="primary", use_container_width=True):
                                with st.spinner("Analizando brazos de momento..."):
                                    moment_results = analyze_gravity_moments()
                                    if moment_results:
                                        save_measurements(moment_results)
                                        st.success(f"Se calcularon {len(moment_results)} brazos de momento!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("No se pudieron calcular brazos de momento. Intenta con otro frame.")
                    
                    # Mostrar detección fallida
                    elif st.session_state.analyze_with_ai and st.session_state.pose_landmarks is None:
                        st.error("No se detectó ninguna persona en este frame. Intenta con otro frame o ajusta la posición.")
                
                # Panel lateral con información y ajustes
                with col2:
                    st.subheader("Información")
                    
                    # Información del frame
                    st.text(f"Frame {st.session_state.frame_index + 1} de {st.session_state.total_frames}")
                    st.text(f"Resolución: {st.session_state.frame_width}x{st.session_state.frame_height}")
                    
                    # Explicación de herramientas
                    st.markdown("""
                    <div class="info-text">
                        <strong>Instrucciones:</strong>
                        <ol>
                            <li>Pausa el video en el frame deseado</li>
                            <li>Activa el análisis con IA</li>
                            <li>Usa los botones para calcular automáticamente:</li>
                            <ul>
                                <li>Ángulos articulares</li>
                                <li>Longitudes de segmentos</li>
                                <li>Brazos de momento</li>
                            </ul>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Exportar frame actual
                    if st.button("Exportar Frame con Análisis"):
                        if st.session_state.current_frame is not None:
                            # Preparar frame para exportación
                            export_frame = st.session_state.current_frame.copy()
                            
                            # Añadir todas las mediciones
                            if st.session_state.pose_landmarks is not None:
                                export_frame = draw_landmark_connections(export_frame)
                                
                                # Dibujar mediciones de ángulos
                                for m in st.session_state.angle_measurements:
                                    if m["frame_index"] == st.session_state.frame_index and "points" in m:
                                        draw_angle(export_frame, m["points"], m["value"], color=(255, 0, 0))
                                
                                # Dibujar mediciones de segmentos
                                for m in st.session_state.limb_measurements:
                                    if m["frame_index"] == st.session_state.frame_index and "points" in m:
                                        unit = m.get("unit", "px")
                                        value = m.get("real_value", m["value"])
                                        draw_line(export_frame, m["points"], value, color=(0, 255, 0), unit=unit)
                                
                                # Dibujar vectores de fuerza
                                for v in st.session_state.force_vectors:
                                    if v["frame_index"] == st.session_state.frame_index and "points" in v:
                                        draw_force_vector(export_frame, v["points"], v.get("description", ""), color=(231, 76, 60))
                                
                                # Dibujar brazos de momento
                                for m in st.session_state.moment_arms:
                                    if m["frame_index"] == st.session_state.frame_index and "pivot" in m and "force_vector" in m:
                                        unit = m.get("unit", "px")
                                        value = m.get("real_value", m["value"])
                                        draw_moment_arm(export_frame, m["pivot"], m["force_vector"], value, color=(148, 0, 211), unit=unit)
                            
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
                
                # Mostrar resultados del análisis
                if st.session_state.analyze_with_ai and st.session_state.pose_landmarks is not None:
                    st.subheader("Resultados del Análisis")
                    
                    # Filtrar mediciones del frame actual
                    frame_angles = [m for m in st.session_state.angle_measurements if m["frame_index"] == st.session_state.frame_index]
                    frame_segments = [m for m in st.session_state.limb_measurements if m["frame_index"] == st.session_state.frame_index]
                    frame_moments = [m for m in st.session_state.moment_arms if m["frame_index"] == st.session_state.frame_index]
                    
                    tab1, tab2, tab3 = st.tabs(["Ángulos", "Segmentos", "Brazos de Momento"])
                    
                    with tab1:
                        if not frame_angles:
                            st.info("No hay mediciones de ángulos para este frame. Usa el botón 'Calcular Ángulos Articulares'.")
                        else:
                            for i, m in enumerate(frame_angles):
                                st.markdown(f"""
                                <div class="analysis-result">
                                    <span class="angle-name">{m["joint"]}</span>: <span class="result-value">{m["value"]:.1f}°</span>
                                    <p>{m.get("description", "")}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button("Eliminar", key=f"del_angle_{i}"):
                                    st.session_state.angle_measurements.remove(m)
                                    st.experimental_rerun()
                    
                    with tab2:
                        if not frame_segments:
                            st.info("No hay mediciones de segmentos para este frame. Usa el botón 'Medir Segmentos Corporales'.")
                        else:
                            for i, m in enumerate(frame_segments):
                                unit = m.get("unit", "px")
                                value = m.get("real_value", m["value"])
                                
                                st.markdown(f"""
                                <div class="analysis-result">
                                    <span class="segment-name">{m["joint"]}</span>: <span class="result-value">{value:.1f} {unit}</span>
                                    <p>{m.get("description", "")}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button("Eliminar", key=f"del_segment_{i}"):
                                    st.session_state.limb_measurements.remove(m)
                                    st.experimental_rerun()
                    
                    with tab3:
                        if not frame_moments:
                            st.info("No hay análisis de brazos de momento para este frame. Usa el botón 'Analizar Brazos de Momento'.")
                        else:
                            for i, m in enumerate(frame_moments):
                                unit = m.get("unit", "px")
                                value = m.get("real_value", m["value"])
                                
                                st.markdown(f"""
                                <div class="analysis-result">
                                    <span class="moment-name">{m["joint"]}</span>: <span class="result-value">{value:.1f} {unit}</span>
                                    <p>{m.get("description", "")}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if st.button("Eliminar", key=f"del_moment_{i}"):
                                    # Encontrar y eliminar el vector de fuerza asociado
                                    if "force_vector_id" in m:
                                        vector = next((v for v in st.session_state.force_vectors if v["id"] == m["force_vector_id"]), None)
                                        if vector:
                                            st.session_state.force_vectors.remove(vector)
                                    
                                    st.session_state.moment_arms.remove(m)
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
                            # Crear datos para enviar
                            form_data = {
                                "date": session_date.strftime("%Y-%m-%d"),
                                "exercise": exercise,
                                "sets": sets,
                                "reps": reps,
                                "rir": rir,
                                "comments": comments
                            }
                            
                            # Guardar sesión
                            if save_session_data(client, form_data):
                                st.success("Sesión guardada correctamente! Puedes generar el informe en la pestaña 'Informes'.")
                            else:
                                st.error("Error al guardar la sesión. Inténtalo de nuevo.")
    
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
                                    st.write(f"- {m.get('joint', '')}: {m['value']:.1f}° ({m.get('description', '')})")
                                elif m["type"] == "Línea":
                                    if calibration != 1.0 and "value" in m:
                                        real_distance = m['value'] / calibration
                                        st.write(f"- {m.get('joint', 'Distancia')}: {real_distance:.1f} cm ({m.get('description', '')})")
                                    else:
                                        st.write(f"- {m.get('joint', 'Distancia')}: {m.get('value', 0):.1f} px ({m.get('description', '')})")
                                elif m["type"] == "Vector de Fuerza" and "magnitude" in m:
                                    if calibration != 1.0:
                                        real_magnitude = m['magnitude'] / calibration
                                        st.write(f"- Vector de Fuerza: {real_magnitude:.1f} cm ({m.get('description', '')})")
                                    else:
                                        st.write(f"- Vector de Fuerza: {m['magnitude']:.1f} px ({m.get('description', '')})")
                                elif m["type"] == "Brazo de Momento" and "value" in m:
                                    if calibration != 1.0:
                                        real_value = m['value'] / calibration
                                        st.write(f"- {m.get('joint', 'Brazo de Momento')}: {real_value:.1f} cm ({m.get('description', '')})")
                                    else:
                                        st.write(f"- {m.get('joint', 'Brazo de Momento')}: {m['value']:.1f} px ({m.get('description', '')})")
    
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
                            # Cargar un frame para el informe
                            if st.session_state.current_video_path is not None and st.session_state.current_frame is not None:
                                frame_with_analysis = st.session_state.current_frame.copy()
                                
                                # Aplicar las mediciones al frame
                                if "measurements" in selected_session:
                                    # Encontrar el frame con más mediciones
                                    frame_counts = {}
                                    for m in selected_session["measurements"]:
                                        frame_idx = m.get("frame_index", 0)
                                        if frame_idx not in frame_counts:
                                            frame_counts[frame_idx] = 0
                                        frame_counts[frame_idx] += 1
                                    
                                    if frame_counts:
                                        best_frame = max(frame_counts.items(), key=lambda x: x[1])[0]
                                        get_frame(best_frame)
                                        frame_with_analysis = st.session_state.current_frame.copy()
                                        
                                        # Detectar pose para el frame
                                        detect_pose(frame_with_analysis)
                                        
                                        # Dibujar esqueleto si hay landmarks
                                        if st.session_state.pose_landmarks is not None:
                                            frame_with_analysis = draw_landmark_connections(frame_with_analysis)
                                        
                                        # Dibujar mediciones en este frame
                                        for m in selected_session["measurements"]:
                                            if m.get("frame_index") == best_frame:
                                                if m["type"] == "Ángulo" and "points" in m and len(m["points"]) == 3:
                                                    draw_angle(frame_with_analysis, m["points"], m["value"], color=(255, 0, 0))
                                                elif m["type"] == "Línea" and "points" in m and len(m["points"]) == 2:
                                                    calibration = selected_session.get("calibration_factor", 1.0)
                                                    if calibration != 1.0 and "value" in m:
                                                        real_value = m["value"] / calibration
                                                        draw_line(frame_with_analysis, m["points"], real_value, color=(0, 255, 0), unit="cm")
                                                    else:
                                                        draw_line(frame_with_analysis, m["points"], m["value"], color=(0, 255, 0))
                            else:
                                frame_with_analysis = None
                            
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
