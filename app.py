import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import tempfile
from PIL import Image, ImageDraw
import math
import base64
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image as RLImage, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# Configuración de la página
st.set_page_config(page_title="Análisis Biomecánico", layout="wide")

# Título de la aplicación
st.title("Análisis Biomecánico")

# Inicializar el estado de la sesión si no existe
if 'frames' not in st.session_state:
    st.session_state.frames = []
if 'current_frame_idx' not in st.session_state:
    st.session_state.current_frame_idx = 0
if 'measurements' not in st.session_state:
    st.session_state.measurements = pd.DataFrame(columns=['Frame', 'Tipo', 'Valor', 'Descripción'])
if 'points' not in st.session_state:
    st.session_state.points = []
if 'video_info' not in st.session_state:
    st.session_state.video_info = {"nombre": "", "fps": 0, "total_frames": 0, "duracion": 0}
if 'factor_escala' not in st.session_state:
    st.session_state.factor_escala = 1.0  # 1 pixel = 1 unidad
if 'unidad_medida' not in st.session_state:
    st.session_state.unidad_medida = "cm"  # Unidad de medida predeterminada

# Función para calcular la distancia entre dos puntos
def calcular_distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Función para calcular el ángulo entre tres puntos
def calcular_angulo(p1, p2, p3):
    # p2 es el vértice
    vector1 = (p1[0] - p2[0], p1[1] - p2[1])
    vector2 = (p3[0] - p2[0], p3[1] - p2[1])
    
    # Producto punto
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    
    # Magnitudes de los vectores
    mag1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
    mag2 = math.sqrt(vector2[0]**2 + vector2[1]**2)
    
    # Evitar división por cero
    if mag1 * mag2 == 0:
        return 0
    
    # Calcular el coseno del ángulo
    cos_angle = dot_product / (mag1 * mag2)
    
    # Asegurar que el valor está en el rango válido de arcocoseno
    cos_angle = max(-1, min(1, cos_angle))
    
    # Convertir de radianes a grados
    angle = math.degrees(math.acos(cos_angle))
    return angle

# Función para dibujar puntos, líneas y ángulos en el frame
def dibujar_elementos(frame):
    img = frame.copy()
    
    # Dibujar puntos
    for i, point in enumerate(st.session_state.points):
        cv2.circle(img, point, 5, (255, 0, 0), -1)
        cv2.putText(img, f"{i+1}", (point[0]+10, point[1]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    return img

# Función para generar informe PDF
def generar_pdf(measurements, video_info):
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos para el documento
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Añadir título e información del video
    elements.append(Paragraph("Informe de Análisis Biomecánico", title_style))
    elements.append(Paragraph(f"Información del Video:", subtitle_style))
    elements.append(Paragraph(f"Nombre: {video_info['nombre']}", normal_style))
    elements.append(Paragraph(f"FPS: {video_info['fps']}", normal_style))
    elements.append(Paragraph(f"Total de frames: {video_info['total_frames']}", normal_style))
    elements.append(Paragraph(f"Duración: {video_info['duracion']:.2f} segundos", normal_style))
    
    # Añadir tabla de mediciones
    elements.append(Paragraph("Mediciones Realizadas:", subtitle_style))
    
    if not measurements.empty:
        # Preparar datos para la tabla
        data = [['Frame', 'Tipo', 'Valor', 'Descripción']]
        for _, row in measurements.iterrows():
            data.append([row['Frame'], row['Tipo'], f"{row['Valor']:.2f}", row['Descripción']])
        
        # Crear la tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No hay mediciones registradas.", normal_style))
    
    # Generar el PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Función para añadir medición
def añadir_medicion(tipo, valor, descripcion):
    nueva_medicion = pd.DataFrame({
        'Frame': [st.session_state.current_frame_idx + 1],
        'Tipo': [tipo],
        'Valor': [valor],
        'Descripción': [descripcion]
    })
    st.session_state.measurements = pd.concat([st.session_state.measurements, nueva_medicion], ignore_index=True)

# Función para definir escala
def definir_escala(longitud_real, unidad):
    if len(st.session_state.points) == 2:
        longitud_pixels = calcular_distancia(st.session_state.points[0], st.session_state.points[1])
        if longitud_pixels > 0:
            st.session_state.factor_escala = longitud_real / longitud_pixels
            st.session_state.unidad_medida = unidad
            st.success(f"Escala definida: {st.session_state.factor_escala:.4f} {unidad}/pixel")
        else:
            st.error("Error: Los puntos están superpuestos.")
    else:
        st.error("Es necesario marcar exactamente 2 puntos para definir la escala.")

# Sidebar para controles
with st.sidebar:
    st.header("Controles")
    
    # Sección de carga de video
    st.subheader("Cargar Video")
    uploaded_file = st.file_uploader("Seleccionar archivo de video", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file:
        # Guardar el archivo en un archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}")
        temp_file.write(uploaded_file.read())
        temp_file.close()
        
        # Abrir el video con OpenCV
        cap = cv2.VideoCapture(temp_file.name)
        
        # Verificar que el video se ha cargado correctamente
        if not cap.isOpened():
            st.error("Error al abrir el archivo de video.")
        else:
            # Leer los frames del video
            st.session_state.frames = []
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Crear una barra de progreso
            progress_bar = st.progress(0)
            
            # Leer todos los frames
            for i in range(total_frames):
                ret, frame = cap.read()
                if ret:
                    # Convertir BGR a RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.session_state.frames.append(frame_rgb)
                progress_bar.progress((i + 1) / total_frames)
            
            # Guardar información del video
            st.session_state.video_info = {
                "nombre": uploaded_file.name,
                "fps": fps,
                "total_frames": total_frames,
                "duracion": total_frames / fps if fps > 0 else 0
            }
            
            # Reiniciar índice de frame
            st.session_state.current_frame_idx = 0
            st.session_state.points = []
            
            # Mostrar información
            st.success(f"Video cargado: {uploaded_file.name}")
            st.info(f"Frames: {total_frames}, FPS: {fps:.2f}")
            
            # Limpiar archivo temporal
            os.unlink(temp_file.name)
        
        # Cerrar el video
        cap.release()
    
    # Sección de navegación (si hay frames cargados)
    if st.session_state.frames:
        st.subheader("Navegación")
        
        # Mostramos el número de frame actual y el total
        st.write(f"Frame: {st.session_state.current_frame_idx + 1}/{len(st.session_state.frames)}")
        
        # Slider para navegar entre frames
        frame_slider = st.slider("Seleccionar frame", 
                                min_value=1, 
                                max_value=len(st.session_state.frames), 
                                value=st.session_state.current_frame_idx + 1)
        st.session_state.current_frame_idx = frame_slider - 1
        
        # Botones para navegar entre frames
        cols = st.columns(4)
        if cols[0].button("⏪", help="Retroceder 10 frames"):
            st.session_state.current_frame_idx = max(0, st.session_state.current_frame_idx - 10)
        if cols[1].button("◀️", help="Frame anterior"):
            st.session_state.current_frame_idx = max(0, st.session_state.current_frame_idx - 1)
        if cols[2].button("▶️", help="Frame siguiente"):
            st.session_state.current_frame_idx = min(len(st.session_state.frames) - 1, st.session_state.current_frame_idx + 1)
        if cols[3].button("⏩", help="Avanzar 10 frames"):
            st.session_state.current_frame_idx = min(len(st.session_state.frames) - 1, st.session_state.current_frame_idx + 10)
        
        # Botón para limpiar los puntos
        if st.button("Limpiar puntos marcados", help="Eliminar todos los puntos del frame actual"):
            st.session_state.points = []
    
    # Sección de herramientas de medición (si hay frames cargados)
    if st.session_state.frames:
        st.subheader("Herramientas de Medición")
        
        # Calibración
        st.write("Calibración:")
        
        col1, col2 = st.columns(2)
        longitud_real = col1.number_input("Longitud real:", min_value=0.1, value=1.0, step=0.1)
        unidad = col2.selectbox("Unidad:", ["cm", "mm", "m", "pulgadas"])
        
        if st.button("Definir escala", help="Usar los 2 puntos marcados para definir la escala"):
            definir_escala(longitud_real, unidad)
        
        st.write(f"Escala actual: 1 pixel = {st.session_state.factor_escala:.4f} {st.session_state.unidad_medida}")
        
        # Herramientas
        st.write("Seleccione una herramienta:")
        herramienta = st.radio(
            "Herramienta:",
            ["Medir distancia", "Medir ángulo"]
        )
        
        descripcion = st.text_input("Descripción de la medición:")
        
        if herramienta == "Medir distancia" and st.button("Calcular distancia"):
            if len(st.session_state.points) >= 2:
                distancia_px = calcular_distancia(st.session_state.points[0], st.session_state.points[1])
                distancia_real = distancia_px * st.session_state.factor_escala
                st.write(f"Distancia: {distancia_real:.2f} {st.session_state.unidad_medida}")
                
                # Añadir a las mediciones
                añadir_medicion("Distancia", distancia_real, descripcion)
            else:
                st.error("Marque al menos 2 puntos para medir distancia")
        
        elif herramienta == "Medir ángulo" and st.button("Calcular ángulo"):
            if len(st.session_state.points) >= 3:
                angulo = calcular_angulo(st.session_state.points[0], st.session_state.points[1], st.session_state.points[2])
                st.write(f"Ángulo: {angulo:.2f}°")
                
                # Añadir a las mediciones
                añadir_medicion("Ángulo", angulo, descripcion)
            else:
                st.error("Marque 3 puntos para medir ángulo (el segundo punto es el vértice)")
        
        # Opción para generar gráficas
        if not st.session_state.measurements.empty and st.button("Generar gráfica de mediciones"):
            # Filtrar mediciones por tipo
            df_angulos = st.session_state.measurements[st.session_state.measurements['Tipo'] == 'Ángulo']
            df_distancias = st.session_state.measurements[st.session_state.measurements['Tipo'] == 'Distancia']
            
            if not df_angulos.empty:
                fig_angulos = px.line(df_angulos, x='Frame', y='Valor', title=f'Ángulos por Frame')
                st.plotly_chart(fig_angulos, use_container_width=True)
            
            if not df_distancias.empty:
                fig_distancias = px.line(df_distancias, x='Frame', y='Valor', title=f'Distancias por Frame ({st.session_state.unidad_medida})')
                st.plotly_chart(fig_distancias, use_container_width=True)
    
    # Sección de mediciones guardadas
    st.subheader("Mediciones Guardadas")
    if not st.session_state.measurements.empty:
        if st.button("Borrar todas las mediciones"):
            st.session_state.measurements = pd.DataFrame(columns=['Frame', 'Tipo', 'Valor', 'Descripción'])
            st.success("Mediciones eliminadas")
        
        # Mostrar las últimas 5 mediciones
        st.write("Últimas mediciones:")
        st.dataframe(st.session_state.measurements.tail(5))
        
        # Botón para descargar mediciones como CSV
        csv = st.session_state.measurements.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name="mediciones_biomecanicas.csv",
            mime="text/csv",
        )
        
        # Botón para generar informe PDF
        if st.button("Generar informe PDF"):
            pdf_buffer = generar_pdf(st.session_state.measurements, st.session_state.video_info)
            st.download_button(
                label="Descargar informe PDF",
                data=pdf_buffer,
                file_name="informe_biomecanico.pdf",
                mime="application/pdf"
            )
    else:
        st.info("No hay mediciones guardadas")

# Área principal para mostrar el frame actual
if st.session_state.frames and len(st.session_state.frames) > 0:
    st.header(f"Frame {st.session_state.current_frame_idx + 1} de {len(st.session_state.frames)}")
    
    # Preparar frame actual con anotaciones
    current_frame = st.session_state.frames[st.session_state.current_frame_idx]
    img_with_annotations = dibujar_elementos(current_frame)
    
    # Tamaño del canvas para dibujar
    frame_height, frame_width = img_with_annotations.shape[:2]
    
    # Crear dos columnas para el área principal
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Convertir la imagen OpenCV para el canvas
        canvas_img = Image.fromarray(img_with_annotations)
        
        # Crear el canvas donde se pueden dibujar
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=canvas_img,
            update_streamlit=True,
            height=frame_height,
            width=frame_width,
            drawing_mode="point",
            key=f"canvas_{st.session_state.current_frame_idx}",
        )
        
        # Procesar nuevos puntos marcados
        if canvas_result.json_data is not None and canvas_result.json_data["objects"]:
            points_data = canvas_result.json_data["objects"]
            new_points = []
            
            # Extraer coordenadas de los puntos
            for point in points_data:
                if point["type"] == "circle":
                    x = int(point["left"] + point["radius"])
                    y = int(point["top"] + point["radius"])
                    new_points.append((x, y))
            
            # Actualizar la lista de puntos
            if new_points:
                st.session_state.points = new_points
                st.experimental_rerun()
    
    with col2:
        # Mostrar las coordenadas de los puntos marcados
        st.subheader("Puntos Marcados")
        for i, point in enumerate(st.session_state.points):
            st.write(f"Punto {i+1}: ({point[0]}, {point[1]})")
        
        # Mostrar mediciones para el frame actual
        st.subheader("Mediciones en este Frame")
        frame_measurements = st.session_state.measurements[st.session_state.measurements['Frame'] == st.session_state.current_frame_idx + 1]
        
        if not frame_measurements.empty:
            for idx, row in frame_measurements.iterrows():
                st.write(f"{row['Tipo']}: {row['Valor']:.2f} {st.session_state.unidad_medida if row['Tipo'] == 'Distancia' else '°'}")
                if row['Descripción']:
                    st.write(f"Descripción: {row['Descripción']}")
                st.divider()
        else:
            st.info("No hay mediciones para este frame")

else:
    st.write("Cargue un video para comenzar el análisis biomecánico.")
    
    # Instrucciones de uso
    st.header("Instrucciones de Uso")
    st.markdown("""
    1. **Carga un video** usando el selector de archivos en la barra lateral.
    2. **Navega entre frames** usando los botones o el slider.
    3. **Marca puntos** haciendo clic directamente en el frame.
    4. **Define la escala** (opcional) marcando dos puntos de referencia y especificando su longitud real.
    5. **Realiza mediciones** de distancias o ángulos utilizando las herramientas de la barra lateral.
    6. **Añade descripciones** a tus mediciones para identificarlas mejor.
    7. **Guarda tus resultados** descargando las mediciones como CSV o generando un informe PDF.
    """)
    
    st.info("Esta aplicación está diseñada para análisis biomecánico básico sin necesidad de conocimientos de programación.")
