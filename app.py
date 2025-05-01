import streamlit as st
import cv2
import numpy as np
import os
import tempfile
from PIL import Image
import datetime

# Configuración básica de la página
st.set_page_config(page_title="KinesioApp Simple", page_icon="🏋️", layout="wide")

# Crear directorio temporal si no existe
os.makedirs("temp", exist_ok=True)

# Estado de la aplicación
if "frame_index" not in st.session_state:
    st.session_state.frame_index = 0
if "total_frames" not in st.session_state:
    st.session_state.total_frames = 0
if "current_video_path" not in st.session_state:
    st.session_state.current_video_path = None
if "measures" not in st.session_state:
    st.session_state.measures = []

# Funciones básicas
def process_video(video_file):
    """Procesa un video y devuelve la ruta temporal"""
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(video_file.read())
    video_path = tfile.name
    
    # Verificar si se puede abrir el video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("No se pudo abrir el video")
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    st.session_state.total_frames = total_frames
    st.session_state.current_video_path = video_path
    
    return video_path

def get_frame(video_path, frame_idx):
    """Obtiene un frame específico del video"""
    if not os.path.exists(video_path):
        return None
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    
    # Asegurarse de que el índice es válido
    if frame_idx < 0:
        frame_idx = 0
    if frame_idx >= st.session_state.total_frames:
        frame_idx = st.session_state.total_frames - 1
    
    st.session_state.frame_index = frame_idx
    
    # Leer el frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    
    if ret:
        # Convertir de BGR a RGB
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return None

def add_measure(frame_idx, name, value, notes=""):
    """Añade una medida manual"""
    measure = {
        "frame": frame_idx,
        "name": name,
        "value": value,
        "notes": notes,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.measures.append(measure)

# Título principal
st.title("🏋️ KinesioApp - Visualizador de Video")

# Subir video
uploaded_file = st.file_uploader("Cargar video para análisis", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Procesar el video
    video_path = process_video(uploaded_file)
    
    if video_path and st.session_state.total_frames > 0:
        # Controles de frame
        st.subheader("Control de Video")
        
        col1, col2, col3 = st.columns([1, 8, 1])
        with col1:
            if st.button("⏪ -10"):
                st.session_state.frame_index = max(0, st.session_state.frame_index - 10)
        
        with col2:
            selected_frame = st.slider("Frame", 0, st.session_state.total_frames-1, st.session_state.frame_index)
            if selected_frame != st.session_state.frame_index:
                st.session_state.frame_index = selected_frame
        
        with col3:
            if st.button("⏩ +10"):
                st.session_state.frame_index = min(st.session_state.total_frames-1, st.session_state.frame_index + 10)
        
        # Mostrar frame actual
        frame = get_frame(video_path, st.session_state.frame_index)
        if frame is not None:
            st.image(frame, use_column_width=True)
            
            # Información del frame
            st.text(f"Frame: {st.session_state.frame_index + 1}/{st.session_state.total_frames}")
        
        # Formulario para mediciones manuales
        st.subheader("Registro Manual de Mediciones")
        
        col1, col2 = st.columns(2)
        with col1:
            measure_name = st.text_input("Nombre de la medición", placeholder="Ej: Ángulo de rodilla")
            measure_value = st.text_input("Valor", placeholder="Ej: 120 grados")
        
        with col2:
            measure_notes = st.text_area("Observaciones", placeholder="Notas adicionales", height=95)
        
        if st.button("Guardar Medición"):
            if measure_name and measure_value:
                add_measure(st.session_state.frame_index, measure_name, measure_value, measure_notes)
                st.success(f"Medición '{measure_name}' guardada correctamente!")
            else:
                st.error("Debe ingresar nombre y valor de la medición")
        
        # Mostrar mediciones existentes
        if st.session_state.measures:
            st.subheader("Mediciones Guardadas")
            
            # Filtrar mediciones para el frame actual
            frame_measures = [m for m in st.session_state.measures if m["frame"] == st.session_state.frame_index]
            
            if frame_measures:
                for i, m in enumerate(frame_measures):
                    st.write(f"**{m['name']}**: {m['value']}")
                    if m['notes']:
                        st.write(f"*{m['notes']}*")
                    st.write("---")
            else:
                st.info("No hay mediciones guardadas para este frame")
else:
    st.info("Sube un video para comenzar el análisis")
