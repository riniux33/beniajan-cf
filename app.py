import streamlit as st
import pandas as pd
import datetime
import json
import os
import re
import base64
from io import BytesIO
from PIL import Image, ImageOps
from github import Github

# ======================================
# FUNCIONES DE SINCRONIZACIÓN CON GITHUB
# ======================================
def guardar_en_github(ruta_local, ruta_repo, mensaje_commit):
    try:
        if "github_token" in st.secrets:
            g = Github(st.secrets["github_token"])
            repo = g.get_repo("riniux33/beniajan-cf")
            with open(ruta_local, "rb") as f:
                contenido = f.read()
            try:
                archivo_existente = repo.get_contents(ruta_repo)
                repo.update_file(ruta_repo, mensaje_commit, contenido, archivo_existente.sha)
            except Exception:
                repo.create_file(ruta_repo, mensaje_commit, contenido)
    except Exception as e:
        st.error(f"Error al sincronizar con GitHub: {e}")

def borrar_en_github(ruta_repo, mensaje_commit):
    try:
        if "github_token" in st.secrets:
            g = Github(st.secrets["github_token"])
            repo = g.get_repo("riniux33/beniajan-cf")
            archivo_existente = repo.get_contents(ruta_repo)
            repo.delete_file(ruta_repo, mensaje_commit, archivo_existente.sha)
    except Exception:
        pass

def imagen_a_base64(ruta_img):
    if os.path.exists(ruta_img):
        with open(ruta_img, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

def limpiar_nombre_archivo(nombre):
    base, ext = os.path.splitext(nombre)
    base_limpia = re.sub(r'[^a-zA-Z0-9_-]', '_', base)
    return f"{base_limpia}{ext.lower()}"

# ======================================
# GESTIÓN DE FOTOS DE JUGADORES
# ======================================
CARPETA_FOTOS_JUGADORES = "fotos_jugadores"
ARCHIVO_FOTOS_JUGADORES = "jugadores_fotos.json"

def cargar_mapa_fotos_jugadores():
    if os.path.exists(ARCHIVO_FOTOS_JUGADORES):
        try:
            with open(ARCHIVO_FOTOS_JUGADORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_mapa_fotos_jugadores(mapa):
    with open(ARCHIVO_FOTOS_JUGADORES, "w", encoding="utf-8") as f:
        json.dump(mapa, f, ensure_ascii=False, indent=4)
    guardar_en_github(ARCHIVO_FOTOS_JUGADORES, ARCHIVO_FOTOS_JUGADORES, "Actualiza registro fotos jugadores")

def procesar_y_guardar_foto_jugador(archivo_subido, clave_jugador):
    if not os.path.exists(CARPETA_FOTOS_JUGADORES):
        os.makedirs(CARPETA_FOTOS_JUGADORES)
    img = Image.open(archivo_subido)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img_cuadrada = ImageOps.fit(img, (240, 240), method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    
    clave_limpia = re.sub(r'[^a-zA-Z0-9_-]', '_', str(clave_jugador))
    nombre_archivo = f"jugador_{clave_limpia}.jpg"
    ruta_local = os.path.join(CARPETA_FOTOS_JUGADORES, nombre_archivo)
    
    img_cuadrada.save(ruta_local, format="JPEG", quality=88)
    guardar_en_github(ruta_local, f"{CARPETA_FOTOS_JUGADORES}/{nombre_archivo}", f"Foto jugador: {clave_jugador}")
    return nombre_archivo

def generar_avatar_html(nombre, dorsal, mapa_fotos, tamano=64):
    clave = f"{dorsal}_{nombre}".strip()
    nombre_foto = mapa_fotos.get(clave) or mapa_fotos.get(str(nombre).strip())
    
    if nombre_foto:
        ruta_foto = os.path.join(CARPETA_FOTOS_JUGADORES, nombre_foto)
        b64 = imagen_a_base64(ruta_foto)
        if b64:
            return f"""
            <div style="width:{tamano}px; height:{tamano}px; border-radius:50%; overflow:hidden; border:3px solid #ffcc00; box-shadow:0 3px 8px rgba(0,0,0,0.18); flex-shrink:0; background:#172033;">
                <img src="data:image/jpeg;base64,{b64}" style="width:100%; height:100%; object-fit:cover; display:block;" />
            </div>
            """
    
    texto_dorsal = f"#{dorsal}" if str(dorsal).isdigit() and int(dorsal) > 0 else "⚽"
    font_size = int(tamano * 0.34)
    return f"""
    <div style="width:{tamano}px; height:{tamano}px; border-radius:50%; border:3px solid #ffcc00; background:linear-gradient(135deg, #172033 0%, #263554 100%); color:#ffcc00; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:{font_size}px; box-shadow:0 3px 8px rgba(0,0,0,0.15); flex-shrink:0;">
        {texto_dorsal}
    </div>
    """

# ======================================
# NORMALIZACIÓN DE PLANTILLA
# ======================================
POSICIONES_OFICIALES = [
    "Ninguna",
    "Portero",
    "Defensa LD / LI",
    "Defensa C.",
    "MO / Pivote",
    "MC / I",
    "MP / C.O",
    "Extremo I-D / IO",
    "DC / Ariete"
]

def normalizar_plantilla(df):
    df = df.copy()
    for col in ["Dorsal", "Nombre", "Posicion", "Estado", "PIN"]:
        if col not in df.columns:
            if col == "Posicion":
                df[col] = "Ninguna"
            elif col == "Estado":
                df[col] = "Disponible"
            else:
                df[col] = ""
    
    df["Nombre"] = df["Nombre"].fillna("").astype(str).str.strip()
    df = df[df["Nombre"] != ""].copy()
    
    def limpiar_dorsal(val):
        try:
            num = int(float(val))
            return num if num > 0 else 0
        except Exception:
            return 0
            
    df["Dorsal"] = df["Dorsal"].apply(limpiar_dorsal)
    
    def limpiar_pos(val):
        s = str(val).strip() if pd.notna(val) else "Ninguna"
        return s if s in POSICIONES_OFICIALES else "Ninguna"
        
    df["Posicion"] = df["Posicion"].apply(limpiar_pos)
    
    def limpiar_estado(val):
        s = str(val).strip() if pd.notna(val) else ""
        if s in ["Lesionado", "Sancionado"]:
            return s
        return "Disponible"
        
    df["Estado"] = df["Estado"].apply(limpiar_estado)
    
    def limpiar_pin(val):
        if pd.isna(val):
            return ""
        s = str(val).strip()
        if s.endswith(".0"):
            s = s[:-2]
        return s if s.isdigit() else ""
        
    df["PIN"] = df["PIN"].apply(limpiar_pin)
    df = df.sort_values(by=["Dorsal", "Nombre"], ascending=[True, True]).reset_index(drop=True)
    return df[["Dorsal", "Nombre", "Posicion", "Estado", "PIN"]]

# ======================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ======================================
icono_app = "escudo.png.png" if os.path.exists("escudo.png.png") else ("escudo.png" if os.path.exists("escudo.png") else "⚽")

st.set_page_config(
    page_title="Beniaján C.F. - Infantil A",
    page_icon=icono_app,
    layout="wide"
)

if "seccion_actual" not in st.session_state:
    st.session_state.seccion_actual = "Inicio"

def ir_a(seccion):
    st.session_state.seccion_actual = seccion

# ======================================
# 2. DISEÑO VISUAL Y COLORES
# ======================================
st.markdown("""
<style>
.stApp {
    background-color: #f4f5f7;
}
.main-title-default {
    background: linear-gradient(135deg, #172033 0%, #243352 100%);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.main-title-default h1 {
    color: #ffcc00;
    margin-bottom: 5px;
    font-size: clamp(22px, 5vw, 36px);
}
.main-title-default p {
    color: white;
    margin: 2px 0;
}
.match {
    background-color: #172033;
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}
.match h3 {
    color: #ffcc00;
    margin-top: 0;
}
.aviso-portada {
    background-color: #fff8db;
    border-left: 6px solid #ffcc00;
    border-top: 1px solid #f0e0a0;
    border-right: 1px solid #f0e0a0;
    border-bottom: 1px solid #f0e0a0;
    padding: 15px 18px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #172033;
}
.ficha-jugador {
    background-color: white;
    border: 1px solid #e2e6ee;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    box-shadow: 0 2px 6px rgba(23,32,51,0.04);
}
.ficha-izq {
    display: flex;
    align-items: center;
    gap: 14px;
}
.ficha-info {
    display: flex;
    flex-direction: column;
}
.ficha-nombre {
    font-size: 16px;
    font-weight: 700;
    color: #172033;
    line-height: 1.25;
}
.ficha-sub {
    font-size: 13px;
    color: #5c667a;
    margin-top: 3px;
}
.badge-dorsal {
    background-color: #172033;
    color: #ffcc00;
    font-weight: 700;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 6px;
    margin-right: 6px;
    display: inline-block;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: white;
    border: 1px solid #d6d9e0;
    border-radius: 12px;
    padding: 20px 14px;
    min-height: 105px;
    color: #172033;
    font-size: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: #172033;
    background-color: #eef1f6;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

# ======================================
# 3. ENCABEZADO SUPERIOR CON ESCUDO
# ======================================
col1, col2 = st.columns([1, 5])

with col1:
    if os.path.exists("escudo.png.png"):
        st.image("escudo.png.png", width=95)
    elif os.path.exists("escudo.png"):
        st.image("escudo.png", width=95)
    else:
        st.markdown("# ⚽")

with col2:
    st.title("Beniaján C.F.")
    st.subheader("Infantil A · Temporada 2026/2027")

# ======================================
# 4. MENÚ LATERAL Y CONTRASEÑA
# ======================================
st.sidebar.title("⚽ BENIAJÁN C.F.")
st.sidebar.markdown("### Menú principal")

secciones = [
    "Inicio",
    "Plantilla",
    "Calendario",
    "Convocatorias",
    "Comunicados",
    "Galería"
]

opcion = st.sidebar.radio(
    "Selecciona una sección:",
    secciones,
    key="seccion_actual"
)

st.sidebar.divider()
st.sidebar.subheader("🔒 Acceso Cuerpo Técnico")
clave_introducida = st.sidebar.text_input("Contraseña de edición:", type="password")

es_admin = False
if clave_introducida:
    if "password_entrenador" in st.secrets and clave_introducida == st.secrets["password_entrenador"]:
        es_admin = True
        st.sidebar.success("Modo edición activado")
    else:
        st.sidebar.error("Contraseña incorrecta")

st.sidebar.divider()
st.sidebar.caption("Temporada 2026/2027")
st.sidebar.caption("Aplicación oficial del equipo")

# ======================================
# PANTALLA DE INICIO
# ======================================
if opcion == "Inicio":

    archivo_foto_equipo = "equipo_portada.jpg"

    if es_admin:
        with st.expander("🖼️ Cambiar foto de fondo del cartel principal"):
            foto_eq_subida = st.file_uploader("Selecciona una foto horizontal del equipo:", key="up_portada")
            if st.button("💾 Guardar foto en portada", type="primary"):
                if foto_eq_subida is not None:
                    img_eq = Image.open(foto_eq_subida)
                    img_eq = ImageOps.exif_transpose(img_eq).convert("RGB")
                    img_eq.save(archivo_foto_equipo, format="JPEG", quality=88)
                    guardar_en_github(archivo_foto_equipo, archivo_foto_equipo, "Actualiza foto de portada")
                    st.success("¡Foto de portada guardada!")
                    st.rerun()
                else:
                    st.warning("Selecciona primero una imagen.")

    b64_equipo = imagen_a_base64(archivo_foto_equipo)
    if b64_equipo:
        st.markdown(f"""
        <div style="
            background-image: linear-gradient(to top, rgba(23,32,51,0.92) 0%, rgba(23,32,51,0.35) 45%, rgba(23,32,51,0.05) 100%), url('data:image/jpeg;base64,{b64_equipo}');
            background-size: cover;
            background-position: center top;
            min-height: 290px;
            border-radius: 15px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <h1 style="color:#ffcc00; margin:0 0 4px 0; font-size:clamp(20px, 4.5vw, 32px); text-shadow: 1px 1px 4px rgba(0,0,0,0.8);">BENIAJÁN C.F.</h1>
            <p style="color:white; margin:0; font-size:clamp(13px, 3vw, 16px); text-shadow: 1px 1px 3px rgba(0,0,0,0.8);">Aplicación oficial de nuestro equipo · Infantil A · Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-title-default">
            <h1>BENIAJÁN C.F.</h1>
            <p>Aplicación oficial de nuestro equipo - Infantil A</p>
            <p>Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Último comunicado destacado en portada
    if os.path.exists("comunicados.csv"):
        df_com_inicio = pd.read_csv("comunicados.csv")
        if not df_com_inicio.empty:
            df_oficial = df_com_inicio[df_com_inicio["Rol"] == "Entrenador"]
            ultimo = df_oficial.iloc[0] if not df_oficial.empty else df_com_inicio.iloc[0]
            st.markdown(f"""
            <div class="aviso-portada">
                <strong>📢 ÚLTIMO AVISO ({ultimo['Autor']} · {ultimo['Fecha']}):</strong><br>
                {ultimo['Mensaje']}
            </div>
            """, unsafe_allow_html=True)

    # Cartel próximo partido
    archivo_partido = "proximo_partido.json"
    datos_partido = {
        "encuentro": "BENIAJÁN C.F. - EQUIPO RIVAL",
        "fecha_hora": "Sábado | 10:00 horas",
        "campo": "Campo de fútbol",
        "citacion": "09:15 horas"
    }

    if os.path.exists(archivo_partido):
        with open(archivo_partido, "r", encoding="utf-8") as f:
            datos_partido = json.load(f)

    if es_admin:
        with st.expander("✏️ Editar cartel de Próximo Partido"):
            with st.form("form_proximo_partido"):
                nuevo_encuentro = st.text_input("Partido (Local - Visitante):", value=datos_partido["encuentro"])
                nueva_fecha = st.text_input("Día y hora:", value=datos_partido["fecha_hora"])
                nuevo_campo = st.text_input("Campo:", value=datos_partido["campo"])
                nueva_citacion = st.text_input("Hora de citación:", value=datos_partido["citacion"])

                if st.form_submit_button("💾 Actualizar cartel", type="primary"):
                    datos_partido = {
                        "encuentro": nuevo_encuentro,
                        "fecha_hora": nueva_fecha,
                        "campo": nuevo_campo,
                        "citacion": nueva_citacion
                    }
                    with open(archivo_partido, "w", encoding="utf-8") as f:
                        json.dump(datos_partido, f, ensure_ascii=False, indent=4)
                    guardar_en_github(archivo_partido, archivo_partido, "Actualiza próximo partido")
                    st.success("¡Cartel actualizado y guardado!")
                    st.rerun()

    st.markdown(f"""
    <div class="match">
        <h3>🏆 PRÓXIMO PARTIDO</h3>
        <h2>{datos_partido['encuentro']}</h2>
        <p>📅 {datos_partido['fecha_hora']}</p>
        <p>📍 {datos_partido['campo']}</p>
        <p>⏰ Hora de citación: {datos_partido['citacion']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Contadores para botones
    num_jugadores = 0
    if os.path.exists("plantilla.csv"):
        num_jugadores = len(normalizar_plantilla(pd.read_csv("plantilla.csv")))

    num_conv = 0
    pendientes_conv = 0
    if os.path.exists("convocatoria_actual.json"):
        with open("convocatoria_actual.json", "r", encoding="utf-8") as f:
            c_data = json.load(f)
            num_conv = len(c_data.get("convocados", []))
            pendientes_conv = sum(1 for c in c_data.get("convocados", []) if c.get("estado") == "⏳ Pendiente")

    num_mensajes = 0
    if os.path.exists("comunicados.csv"):
        num_mensajes = len(pd.read_csv("comunicados.csv"))

    num_fotos = 0
    if os.path.exists("galeria_datos.json"):
        with open("galeria_datos.json", "r", encoding="utf-8") as f:
            num_fotos = len(json.load(f))

    st.subheader("Accesos rápidos")

    col1, col2, col3 = st.columns(3)

    with col1:
        texto_plantilla = f"👥 **Plantilla ({num_jugadores})**\n\nFichas y fotos de jugadores"
        st.button(texto_plantilla, use_container_width=True, on_click=ir_a, args=("Plantilla",))

    with col2:
        texto_calendario = "📅 **Calendario**\n\nPartidos y entrenamientos"
        st.button(texto_calendario, use_container_width=True, on_click=ir_a, args=("Calendario",))

    with col3:
        aviso_conv = f" 🔔 ({pendientes_conv} pend.)" if pendientes_conv > 0 else ""
        texto_conv = f"📋 **Convocatorias ({num_conv}){aviso_conv}**\n\nConsulta y confirma asistencia"
        st.button(texto_conv, use_container_width=True, on_click=ir_a, args=("Convocatorias",))

    col4, col5, col6 = st.columns(3)

    with col4:
        texto_com = f"📢 **Comunicados ({num_mensajes})**\n\nNoticias y avisos del equipo"
        st.button(texto_com, use_container_width=True, on_click=ir_a, args=("Comunicados",))

    with col5:
        texto_gal = f"📸 **Galería ({num_fotos})**\n\nFotos y recuerdos del equipo"
        st.button(texto_gal, use_container_width=True, on_click=ir_a, args=("Galería",))

    with col6:
        if st.button("🔒 **Cuerpo Técnico**\n\nAcceso edición en menú lateral", use_container_width=True):
            st.info("Pulsa la flecha **`>`** arriba a la izquierda para abrir el menú lateral e introducir la contraseña de entrenador.")

# ======================================
# PLANTILLA
# ======================================
elif opcion == "Plantilla":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("👥 Plantilla de jugadores - Infantil A")

    archivo_plantilla = "plantilla.csv"
    mapa_fotos = cargar_mapa_fotos_jugadores()

    if os.path.exists(archivo_plantilla):
        df_plantilla = normalizar_plantilla(pd.read_csv(archivo_plantilla))

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Jugadores", len(df_plantilla))
        col_m2.metric("Disponibles", len(df_plantilla[df_plantilla["Estado"] == "Disponible"]))
        col_m3.metric("Lesionados", len(df_plantilla[df_plantilla["Estado"] == "Lesionado"]))
        col_m4.metric("Sancionados / Baja", len(df_plantilla[df_plantilla["Estado"] == "Sancionado"]))

        st.divider()

        if es_admin:
            # Gestor de fotos de jugadores
            with st.expander("📸 Gestionar fotos de jugadores (Subir o cambiar retrato)", expanded=False):
                opciones_foto_jug = [
                    f"Dorsal {row['Dorsal']} - {row['Nombre']}" if row["Dorsal"] > 0 else f"Sin dorsal - {row['Nombre']}"
                    for _, row in df_plantilla.iterrows()
                ]
                mapa_opciones_row = {
                    (f"Dorsal {row['Dorsal']} - {row['Nombre']}" if row["Dorsal"] > 0 else f"Sin dorsal - {row['Nombre']}"): row
                    for _, row in df_plantilla.iterrows()
                }
                
                if opciones_foto_jug:
                    jug_foto_sel = st.selectbox("Selecciona el jugador o portero:", options=opciones_foto_jug, key="sel_foto_jug")
                    row_sel = mapa_opciones_row[jug_foto_sel]
                    clave_jug = f"{row_sel['Dorsal']}_{row_sel['Nombre']}".strip()
                    
                    col_f1, col_f2 = st.columns([1, 3])
                    with col_f1:
                        st.markdown(generar_avatar_html(row_sel["Nombre"], row_sel["Dorsal"], mapa_fotos, tamano=84), unsafe_allow_html=True)
                    with col_f2:
                        archivo_foto_j = st.file_uploader("Sube la fotografía del jugador (se recortará automáticamente en círculo):", key="up_foto_jug")
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            if st.button("💾 Guardar foto del jugador", type="primary"):
                                if archivo_foto_j is not None:
                                    nombre_guardado = procesar_y_guardar_foto_jugador(archivo_foto_j, clave_jug)
                                    mapa_fotos[clave_jug] = nombre_guardado
                                    guardar_mapa_fotos_jugadores(mapa_fotos)
                                    st.success(f"¡Foto guardada para {row_sel['Nombre']}!")
                                    st.rerun()
                                else:
                                    st.warning("Selecciona primero una imagen.")
                        with b_col2:
                            if clave_jug in mapa_fotos:
                                if st.button("🗑️ Quitar foto actual"):
                                    archivo_ant = mapa_fotos.pop(clave_jug)
                                    ruta_ant = os.path.join(CARPETA_FOTOS_JUGADORES, archivo_ant)
                                    if os.path.exists(ruta_ant):
                                        os.remove(ruta_ant)
                                    borrar_en_github(f"{CARPETA_FOTOS_JUGADORES}/{archivo_ant}", f"Elimina foto de {row_sel['Nombre']}")
                                    guardar_mapa_fotos_jugadores(mapa_fotos)
                                    st.success("Foto eliminada.")
                                    st.rerun()

            st.info("✏️ **Modo Entrenador:** Edita dorsales, nombres, demarcaciones, estados o asigna el **PIN de 4 dígitos** a cada jugador.")

            if st.button("🎲 Generar PIN aleatorio de 4 dígitos a los que no tengan"):
                import random
                pines_usados = set(df_plantilla["PIN"].tolist())
                for idx, row in df_plantilla.iterrows():
                    if not str(row["PIN"]).strip():
                        nuevo_pin = str(random.randint(1000, 9999))
                        while nuevo_pin in pines_usados:
                            nuevo_pin = str(random.randint(1000, 9999))
                        df_plantilla.at[idx, "PIN"] = nuevo_pin
                        pines_usados.add(nuevo_pin)
                df_plantilla.to_csv(archivo_plantilla, index=False)
                guardar_en_github(archivo_plantilla, archivo_plantilla, "Genera PINes de asistencia")
                st.success("¡PINes generados y guardados!")
                st.rerun()

            df_plantilla_editada = st.data_editor(
                df_plantilla,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Dorsal": st.column_config.NumberColumn("Dorsal", min_value=0, max_value=99, step=1),
                    "Posicion": st.column_config.SelectboxColumn(
                        "Demarcación",
                        options=POSICIONES_OFICIALES,
                        required=True
                    ),
                    "Estado": st.column_config.SelectboxColumn(
                        "Estado",
                        options=["Disponible", "Lesionado", "Sancionado"],
                        required=True
                    ),
                    "PIN": st.column_config.TextColumn(
                        "PIN (4 dígitos)",
                        help="Código secreto de 4 números para confirmar asistencia"
                    )
                }
            )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("💾 Guardar cambios de plantilla", type="primary"):
                    df_limpia = normalizar_plantilla(df_plantilla_editada)
                    df_limpia.to_csv(archivo_plantilla, index=False)
                    guardar_en_github(archivo_plantilla, archivo_plantilla, "Actualiza plantilla")
                    st.success("Plantilla guardada permanentemente.")
                    st.rerun()
            with col_p2:
                csv_plantilla = df_plantilla_editada.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Descargar plantilla.csv",
                    data=csv_plantilla,
                    file_name="plantilla.csv",
                    mime="text/csv"
                )
            st.divider()

        # Vista pública profesional con fichas y fotos
        filtro_pos = st.selectbox("Filtrar por demarcación:", ["Todas"] + POSICIONES_OFICIALES)

        if filtro_pos != "Todas":
            df_vista = df_plantilla[df_plantilla["Posicion"] == filtro_pos]
        else:
            df_vista = df_plantilla

        for _, jugador in df_vista.iterrows():
            icono_estado = "🟢" if jugador["Estado"] == "Disponible" else ("🔴" if jugador["Estado"] == "Lesionado" else "🟡")
            avatar_html = generar_avatar_html(jugador["Nombre"], jugador["Dorsal"], mapa_fotos, tamano=64)
            badge_dorsal = f"<span class='badge-dorsal'>Dorsal {jugador['Dorsal']}</span>" if jugador["Dorsal"] > 0 else "<span class='badge-dorsal'>Sin dorsal</span>"
            
            st.markdown(f"""
            <div class="ficha-jugador">
                <div class="ficha-izq">
                    {avatar_html}
                    <div class="ficha-info">
                        <div class="ficha-nombre">{badge_dorsal} {jugador['Nombre']}</div>
                        <div class="ficha-sub">⚽ {jugador['Posicion']}</div>
                    </div>
                </div>
                <div style="font-weight:600; font-size:14px; color:#172033; white-space:nowrap;">
                    {icono_estado} {jugador['Estado']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No se encontró el archivo plantilla.csv en el repositorio.")

# ======================================
# SECCIÓN: CALENDARIO
# ======================================
elif opcion == "Calendario":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("📅 Calendario deportivo (2026 - 2027)")

    tipos_calendario = ["Descanso", "Entrenamiento", "Partido amistoso", "Partido competición"]

    if os.path.exists("calendario.csv"):
        df = pd.read_csv("calendario.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date
        for col_txt in ["Tipo", "Hora", "Evento", "Lugar"]:
            if col_txt in df.columns:
                df[col_txt] = df[col_txt].fillna("").astype(str)

        if es_admin:
            with st.expander("🗓️ Planificador rápido (Generar hasta 3 meses de sesiones)", expanded=False):
                with st.form("form_planificador_3m"):
                    p_col1, p_col2 = st.columns(2)
                    with p_col1:
                        fecha_inicio_plan = st.date_input("Fecha de inicio:", value=datetime.date.today())
                        dias_semana = st.multiselect(
                            "Días de la semana:",
                            options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                            default=["Martes", "Jueves"]
                        )
                        tipo_plan = st.selectbox("Tipo de actividad:", options=tipos_calendario, index=1)
                    with p_col2:
                        hora_plan = st.text_input("Hora (ej. 18:30):", value="18:30")
                        evento_plan = st.text_input("Descripción / Evento:", value="Entrenamiento Infantil A")
                        lugar_plan = st.text_input("Campo / Lugar:", value="Campo Municipal de Beniaján")

                    if st.form_submit_button("⚡ Generar y guardar planificación de 3 meses", type="primary"):
                        mapa_dias = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}
                        numeros_dias = [mapa_dias[d] for d in dias_semana]
                        nuevas_filas = []
                        for i in range(90):
                            dia_actual = fecha_inicio_plan + datetime.timedelta(days=i)
                            if dia_actual.weekday() in numeros_dias:
                                fila_nueva = {col: "" for col in df.columns}
                                fila_nueva["Fecha"] = dia_actual
                                if "Hora" in df.columns: fila_nueva["Hora"] = hora_plan
                                if "Tipo" in df.columns: fila_nueva["Tipo"] = tipo_plan
                                if "Evento" in df.columns: fila_nueva["Evento"] = evento_plan
                                if "Lugar" in df.columns: fila_nueva["Lugar"] = lugar_plan
                                nuevas_filas.append(fila_nueva)
                        if nuevas_filas:
                            df_nuevas = pd.DataFrame(nuevas_filas)
                            df = pd.concat([df, df_nuevas], ignore_index=True)
                            df = df.sort_values(by="Fecha").reset_index(drop=True)
                            df.to_csv("calendario.csv", index=False)
                            guardar_en_github("calendario.csv", "calendario.csv", "Planificación 3 meses calendario")
                            st.success(f"¡Se han añadido y guardado {len(nuevas_filas)} sesiones para los próximos 3 meses!")
                            st.rerun()
                        else:
                            st.warning("Selecciona al menos un día de la semana.")

        opciones_existentes = list(dict.fromkeys(tipos_calendario + [t for t in df["Tipo"].unique() if t]))

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            tipo_seleccionado = st.multiselect(
                "Filtrar por actividad:",
                options=opciones_existentes,
                default=opciones_existentes
            )

        hoy = datetime.date.today()
        fecha_def_ini = max(datetime.date(2026, 8, 1), hoy)
        fecha_def_fin = min(datetime.date(2027, 8, 31), hoy + datetime.timedelta(days=90))
        if fecha_def_ini > fecha_def_fin:
            fecha_def_ini = datetime.date(2026, 8, 1)
            fecha_def_fin = datetime.date(2027, 8, 31)

        with col_filtro2:
            rango_fechas = st.date_input(
                "Selecciona rango de fechas:",
                value=(fecha_def_ini, fecha_def_fin),
                min_value=datetime.date(2026, 8, 1),
                max_value=datetime.date(2027, 8, 31)
            )

        if len(rango_fechas) == 2:
            inicio, fin = rango_fechas
            mascara = (
                (df["Tipo"].isin(tipo_seleccionado))
                & (df["Fecha"] >= inicio)
                & (df["Fecha"] <= fin)
            )
            df_filtrado = df[mascara]

            if es_admin:
                st.info("✏️ **Modo Entrenador:** Haz doble clic en cualquier celda para editar o añadir eventos.")
                config_cols = {
                    "Tipo": st.column_config.SelectboxColumn(
                        "Tipo",
                        options=opciones_existentes,
                        required=True
                    ),
                    "Hora": st.column_config.TextColumn(
                        "Hora",
                        help="Formato HH:MM (ej. 19:30)"
                    )
                }
                if "Evento" in df.columns:
                    config_cols["Evento"] = st.column_config.TextColumn("Evento")
                if "Lugar" in df.columns:
                    config_cols["Lugar"] = st.column_config.TextColumn("Lugar")

                df_editado = st.data_editor(
                    df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config=config_cols
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar cambios de calendario", type="primary"):
                        df_editado.to_csv("calendario.csv", index=False)
                        guardar_en_github("calendario.csv", "calendario.csv", "Actualiza calendario")
                        st.success("Horarios guardados permanentemente.")
                        st.rerun()

                with col_btn2:
                    csv_descarga = df_editado.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Descargar CSV actualizado",
                        data=csv_descarga,
                        file_name="calendario.csv",
                        mime="text/csv"
                    )
            else:
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.info("Selecciona una fecha de inicio y otra de fin.")
    else:
        st.warning("No se encontró el archivo calendario.csv.")

# ======================================
# SECCIÓN: CONVOCATORIAS
# ======================================
elif opcion == "Convocatorias":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("📋 Convocatorias y Asistencia")

    archivo_conv = "convocatoria_actual.json"
    archivo_plantilla = "plantilla.csv"
    mapa_fotos = cargar_mapa_fotos_jugadores()

    datos_conv = {
        "partido": "Próximo Partido Oficial",
        "notas": "Traer primera equipación (verde) y botella de agua.",
        "convocados": []
    }

    if os.path.exists(archivo_conv):
        with open(archivo_conv, "r", encoding="utf-8") as f:
            datos_conv = json.load(f)

    df_pl = pd.DataFrame()
    if os.path.exists(archivo_plantilla):
        df_pl = normalizar_plantilla(pd.read_csv(archivo_plantilla))

    if es_admin:
        with st.expander("✏️ Configurar nueva convocatoria (Solo Entrenador)", expanded=True):
            if not df_pl.empty:
                df_disp = df_pl[~df_pl["Estado"].isin(["Lesionado", "Sancionado"])]
                st.caption(f"Jugadores cargados desde plantilla: {len(df_pl)} totales · {len(df_disp)} disponibles")
                
                opciones_jugadores = [
                    (f"Dorsal {fila['Dorsal']} - {fila['Nombre']} ({fila['Posicion']})" if fila["Dorsal"] > 0 else f"Sin dorsal - {fila['Nombre']} ({fila['Posicion']})")
                    for _, fila in df_disp.iterrows()
                ]

                nombres_previos = [
                    c["jugador"]
                    for c in datos_conv["convocados"]
                    if c["jugador"] in opciones_jugadores
                ]

                with st.form("form_convocatoria"):
                    titulo_partido = st.text_input(
                        "Título del partido / Jornada:",
                        value=datos_conv["partido"]
                    )
                    notas_partido = st.text_area(
                        "Indicaciones (equipación, punto de encuentro...):",
                        value=datos_conv["notas"]
                    )
                    seleccionados = st.multiselect(
                        f"Selecciona los jugadores convocados ({len(opciones_jugadores)} disponibles):",
                        options=opciones_jugadores,
                        default=nombres_previos
                    )

                    if st.form_submit_button("📢 Publicar Convocatoria Oficial", type="primary"):
                        estados_previos = {
                            c["jugador"]: c["estado"]
                            for c in datos_conv["convocados"]
                        }
                        nueva_lista = []
                        for jug in seleccionados:
                            nueva_lista.append({
                                "jugador": jug,
                                "estado": estados_previos.get(jug, "⏳ Pendiente")
                            })

                        datos_conv = {
                            "partido": titulo_partido,
                            "notas": notas_partido,
                            "convocados": nueva_lista
                        }

                        with open(archivo_conv, "w", encoding="utf-8") as f:
                            json.dump(datos_conv, f, ensure_ascii=False, indent=4)

                        guardar_en_github(
                            archivo_conv,
                            archivo_conv,
                            "Publica convocatoria oficial"
                        )
                        st.success("¡Convocatoria publicada y guardada!")
                        st.rerun()
            else:
                st.warning("Primero debes crear el archivo plantilla.csv para elegir jugadores.")

    if not datos_conv["convocados"]:
        st.info("Todavía no se ha publicado la convocatoria para el próximo partido.")
    else:
        st.subheader(f"🏆 {datos_conv['partido']}")
        st.info(f"📌 Notas del cuerpo técnico: {datos_conv['notas']}")

        total_conv = len(datos_conv["convocados"])
        confirmados = sum(
            1 for c in datos_conv["convocados"]
            if c["estado"] == "✅ Confirmado"
        )
        pendientes = sum(
            1 for c in datos_conv["convocados"]
            if c["estado"] == "⏳ Pendiente"
        )
        bajas = sum(
            1 for c in datos_conv["convocados"]
            if c["estado"] == "❌ No puede asistir"
        )

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Convocados", total_conv)
        c_m2.metric("Confirmados", confirmados)
        c_m3.metric("Pendientes", pendientes)
        c_m4.metric("Bajas avisadas", bajas)

        st.divider()

        with st.container(border=True):
            st.markdown("### 🙋‍♂️ Confirmar asistencia del jugador")
            lista_nombres = [c["jugador"] for c in datos_conv["convocados"]]
            
            if es_admin:
                col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])
                with col_sel1:
                    jugador_elegido = st.selectbox("Selecciona el jugador:", options=lista_nombres)
                with col_sel2:
                    nuevo_estado = st.selectbox("Respuesta:", options=["✅ Confirmado", "❌ No puede asistir", "⏳ Pendiente"])
                with col_sel3:
                    st.write("")
                    st.write("")
                    if st.button("Guardar respuesta", type="primary"):
                        for item in datos_conv["convocados"]:
                            if item["jugador"] == jugador_elegido:
                                item["estado"] = nuevo_estado
                        with open(archivo_conv, "w", encoding="utf-8") as f:
                            json.dump(datos_conv, f, ensure_ascii=False, indent=4)
                        guardar_en_github(archivo_conv, archivo_conv, f"Asistencia: {jugador_elegido}")
                        st.success(f"Estado actualizado para {jugador_elegido}")
                        st.rerun()
            else:
                col_sel1, col_sel2, col_pin, col_sel3 = st.columns([2, 1.5, 1.2, 1.3])
                with col_sel1:
                    jugador_elegido = st.selectbox("Selecciona tu nombre:", options=lista_nombres)
                with col_sel2:
                    nuevo_estado = st.selectbox("Respuesta:", options=["✅ Confirmado", "❌ No puede asistir", "⏳ Pendiente"])
                with col_pin:
                    pin_introducido = st.text_input("PIN (4 cifras):", type="password", max_chars=4)
                with col_sel3:
                    st.write("")
                    st.write("")
                    if st.button("Confirmar", type="primary"):
                        pin_correcto = ""
                        if not df_pl.empty:
                            for _, r in df_pl.iterrows():
                                etiqueta_r = f"Dorsal {r['Dorsal']} - {r['Nombre']} ({r['Posicion']})" if r["Dorsal"] > 0 else f"Sin dorsal - {r['Nombre']} ({r['Posicion']})"
                                if etiqueta_r == jugador_elegido or str(r["Nombre"]) in jugador_elegido:
                                    pin_correcto = str(r["PIN"]).strip()
                                    break
                        
                        if pin_correcto and pin_introducido.strip() != pin_correcto:
                            st.error("❌ PIN incorrecto. Revisa el código de 4 dígitos de tu jugador.")
                        elif not pin_correcto and pin_introducido.strip() == "":
                            st.warning("Introduce el PIN de 4 dígitos asignado por el entrenador.")
                        else:
                            for item in datos_conv["convocados"]:
                                if item["jugador"] == jugador_elegido:
                                    item["estado"] = nuevo_estado
                            with open(archivo_conv, "w", encoding="utf-8") as f:
                                json.dump(datos_conv, f, ensure_ascii=False, indent=4)
                            guardar_en_github(archivo_conv, archivo_conv, f"Asistencia: {jugador_elegido}")
                            st.success(f"¡Asistencia guardada para {jugador_elegido}!")
                            st.rerun()

        st.subheader("Lista oficial de convocados")
        for item in datos_conv["convocados"]:
            texto_jug = item["jugador"]
            dorsal_encontrado = 0
            nombre_encontrado = texto_jug
            
            m_dorsal = re.search(r"Dorsal\s+(\d+)\s*-\s*([^(]+)", texto_jug)
            if m_dorsal:
                dorsal_encontrado = int(m_dorsal.group(1))
                nombre_encontrado = m_dorsal.group(2).strip()
            else:
                m_sin = re.search(r"Sin dorsal\s*-\s*([^(]+)", texto_jug)
                if m_sin:
                    nombre_encontrado = m_sin.group(1).strip()

            avatar_conv = generar_avatar_html(nombre_encontrado, dorsal_encontrado, mapa_fotos, tamano=54)
            
            st.markdown(f"""
            <div class="ficha-jugador">
                <div class="ficha-izq">
                    {avatar_conv}
                    <div class="ficha-info">
                        <div class="ficha-nombre">{texto_jug}</div>
                    </div>
                </div>
                <div style="font-weight:700; font-size:14px; color:#172033; white-space:nowrap;">
                    {item['estado']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ======================================
# SECCIÓN: COMUNICADOS
# ======================================
elif opcion == "Comunicados":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("📢 Tablón de Comunicados (Padres y Entrenador)")

    archivo_comunicados = "comunicados.csv"
    if os.path.exists(archivo_comunicados):
        df_mensajes = pd.read_csv(archivo_comunicados)
    else:
        df_mensajes = pd.DataFrame(columns=["Fecha", "Autor", "Rol", "Mensaje"])

    with st.form("nuevo_comunicado", clear_on_submit=True):
        col_nombre, col_texto = st.columns([1, 3])
        with col_nombre:
            if es_admin:
                autor = st.text_input("Tu nombre:", value="Entrenador", disabled=True)
                rol = "Entrenador"
            else:
                autor = st.text_input("Tu nombre (ej. Madre de Hugo):")
                rol = "Familia"

        with col_texto:
            mensaje = st.text_area("Escribe tu comunicado o consulta:", height=68)

        enviado = st.form_submit_button("📨 Publicar mensaje", type="primary")
        if enviado:
            if autor.strip() == "" or mensaje.strip() == "":
                st.warning("Por favor, escribe tu nombre y el mensaje antes de publicar.")
            else:
                ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                nueva_fila = pd.DataFrame([{
                    "Fecha": ahora,
                    "Autor": autor.strip(),
                    "Rol": rol,
                    "Mensaje": mensaje.strip()
                }])

                df_mensajes = pd.concat([nueva_fila, df_mensajes], ignore_index=True)
                df_mensajes.to_csv(archivo_comunicados, index=False)
                guardar_en_github(
                    archivo_comunicados,
                    archivo_comunicados,
                    f"Nuevo comunicado de {autor.strip()}"
                )
                st.success("¡Mensaje publicado y guardado!")
                st.rerun()

    st.subheader("Últimos mensajes")
    if df_mensajes.empty:
        st.info("Aún no hay comunicados publicados.")
    else:
        for indice, fila in df_mensajes.iterrows():
            if fila["Rol"] == "Entrenador":
                with st.container(border=True):
                    st.markdown(f"⚽ **{fila['Autor']} (Oficial)** · *{fila['Fecha']}*")
                    st.info(fila["Mensaje"])
            else:
                with st.container(border=True):
                    st.markdown(f"👤 **{fila['Autor']}** · *{fila['Fecha']}*")
                    st.write(fila["Mensaje"])

    if es_admin and not df_mensajes.empty:
        with st.expander("🛠️ Opciones de Entrenador (Borrar o descargar mensajes)"):
            opcion_borrar = st.selectbox(
                "Selecciona un mensaje para eliminar:",
                options=df_mensajes.index,
                format_func=lambda x: (
                    f"{df_mensajes.loc[x, 'Fecha']} - "
                    f"{df_mensajes.loc[x, 'Autor']}: "
                    f"{str(df_mensajes.loc[x, 'Mensaje'])[:40]}..."
                )
            )

            if st.button("🗑️ Eliminar mensaje seleccionado"):
                df_mensajes = df_mensajes.drop(opcion_borrar).reset_index(drop=True)
                df_mensajes.to_csv(archivo_comunicados, index=False)
                guardar_en_github(
                    archivo_comunicados,
                    archivo_comunicados,
                    "Elimina mensaje en tablón"
                )
                st.success("Mensaje eliminado.")
                st.rerun()

            csv_chat = df_mensajes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar copia de seguridad del tablón",
                data=csv_chat,
                file_name="comunicados.csv",
                mime="text/csv"
            )

# ======================================
# SECCIÓN: GALERÍA DE FOTOGRAFÍAS
# ======================================
elif opcion == "Galería":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("📸 Galería de fotografías - Infantil A")

    carpeta_fotos = "galeria_fotos"
    archivo_registro = "galeria_datos.json"

    if not os.path.exists(carpeta_fotos):
        os.makedirs(carpeta_fotos)

    lista_fotos = []
    if os.path.exists(archivo_registro):
        with open(archivo_registro, "r", encoding="utf-8") as f:
            lista_fotos = json.load(f)

    with st.expander("📤 Subir una nueva foto del equipo", expanded=False):
        with st.form("form_subir_foto", clear_on_submit=True):
            archivo_subido = st.file_uploader(
                "Selecciona una imagen desde tu galería o cámara:"
            )
            titulo_foto = st.text_input(
                "Título o jornada (ej. Victoria vs Murcia C.F. - Jornada 3):"
            )
            autor_foto = st.text_input(
                "Subida por:",
                value="Entrenador" if es_admin else ""
            )

            if st.form_submit_button("🖼️ Publicar en la galería", type="primary"):
                if archivo_subido is None:
                    st.warning("Por favor, selecciona primero una fotografía.")
                elif titulo_foto.strip() == "":
                    st.warning("Escribe un breve título para identificar la foto.")
                else:
                    ext = os.path.splitext(archivo_subido.name)[1].lower()
                    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]:
                        st.error("Formato no compatible. Por favor, sube una imagen (JPG, PNG, WEBP o HEIC).")
                    else:
                        marca_tiempo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre_limpio = limpiar_nombre_archivo(archivo_subido.name)
                        nombre_archivo = f"{marca_tiempo}_{nombre_limpio}"
                        ruta_guardado = os.path.join(carpeta_fotos, nombre_archivo)

                        with open(ruta_guardado, "wb") as f:
                            f.write(archivo_subido.getbuffer())

                        nueva_foto = {
                            "archivo": nombre_archivo,
                            "titulo": titulo_foto.strip(),
                            "autor": autor_foto.strip() if autor_foto.strip() else "Familia Beniaján",
                            "fecha": datetime.datetime.now().strftime("%d/%m/%Y")
                        }
                        lista_fotos.insert(0, nueva_foto)

                        with open(archivo_registro, "w", encoding="utf-8") as f:
                            json.dump(lista_fotos, f, ensure_ascii=False, indent=4)

                        guardar_en_github(
                            ruta_guardado,
                            f"galeria_fotos/{nombre_archivo}",
                            f"Nueva foto: {titulo_foto.strip()}"
                        )
                        guardar_en_github(
                            archivo_registro,
                            archivo_registro,
                            "Actualiza índice de galería"
                        )
                        st.success("¡Fotografía subida y guardada permanentemente!")
                        st.rerun()

    st.divider()

    if not lista_fotos:
        st.info("Aún no hay fotografías en el álbum. ¡Sé el primero en subir una desde el botón de arriba!")
    else:
        columnas = st.columns(3)
        for indice, foto in enumerate(lista_fotos):
            ruta_img = os.path.join(carpeta_fotos, foto["archivo"])
            if os.path.exists(ruta_img):
                with columnas[indice % 3]:
                    with st.container(border=True):
                        st.image(ruta_img)
                        st.markdown(f"**{foto['titulo']}**")
                        st.caption(f"📷 {foto['autor']} · 📅 {foto['fecha']}")

                        with open(ruta_img, "rb") as file_dl:
                            bytes_img = file_dl.read()
                        st.download_button(
                            label="📥 Descargar foto",
                            data=bytes_img,
                            file_name=foto["archivo"],
                            key=f"dl_foto_{indice}"
                        )

                        if es_admin:
                            if st.button("🗑️ Eliminar", key=f"del_foto_{indice}"):
                                if os.path.exists(ruta_img):
                                    os.remove(ruta_img)

                                borrar_en_github(
                                    f"galeria_fotos/{foto['archivo']}",
                                    f"Elimina foto: {foto['titulo']}"
                                )
                                lista_fotos.pop(indice)

                                with open(archivo_registro, "w", encoding="utf-8") as f:
                                    json.dump(lista_fotos, f, ensure_ascii=False, indent=4)

                                guardar_en_github(
                                    archivo_registro,
                                    archivo_registro,
                                    "Actualiza índice tras borrar foto"
                                )
                                st.success("Foto eliminada.")
                                st.rerun()

# ======================================
# PIE DE PÁGINA
# ======================================
st.divider()
st.caption(
    "BENIAJÁN C.F. - Infantil A | Aplicación de gestión y comunicación "
    "| Temporada 2026/2027"
)
