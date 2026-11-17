import streamlit as st
import pandas as pd
import datetime
import json
import os
import re
import base64
from github import Github

# Función para guardar archivos de forma permanente en GitHub
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

def obtener_base64_imagen(ruta_img):
    with open(ruta_img, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ======================================
# 1. CONFIGURACIÓN DE LA PÁGINA (SIEMPRE ARRIBA)
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
ruta_portada = "equipo_portada.jpg"
if os.path.exists(ruta_portada):
    img_b64 = obtener_base64_imagen(ruta_portada)
    fondo_titulo_css = f"""
    background-image: linear-gradient(to top, rgba(23, 32, 51, 0.90) 0%, rgba(23, 32, 51, 0.25) 45%, rgba(23, 32, 51, 0.05) 100%), url("data:image/jpeg;base64,{img_b64}");
    background-size: cover;
    background-position: center 20%;
    min-height: 290px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 16px 20px;
    """
else:
    fondo_titulo_css = """
    background-color: #172033;
    padding: 25px;
    """

st.markdown(f"""
<style>
.stApp {{
    background-color: #f4f5f7;
}}
.main-title {{
    {fondo_titulo_css}
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}
.main-title h1 {{
    color: #ffcc00;
    font-size: clamp(1.35rem, 4.5vw, 2.2rem);
    margin: 0 0 2px 0;
    line-height: 1.15;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.9);
}}
.main-title p {{
    color: white;
    font-size: clamp(0.82rem, 2.8vw, 1.05rem);
    margin: 0;
    line-height: 1.3;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
}}
.aviso-banner {{
    background-color: #fff8db;
    border-left: 6px solid #ffcc00;
    border-top: 1px solid #f0e1a1;
    border-right: 1px solid #f0e1a1;
    border-bottom: 1px solid #f0e1a1;
    padding: 15px 18px;
    border-radius: 10px;
    margin-bottom: 18px;
    color: #172033;
}}
.aviso-banner-titulo {{
    font-weight: bold;
    font-size: 15px;
    color: #9a6700;
    margin-bottom: 4px;
}}
.aviso-banner-texto {{
    font-size: 16px;
    margin-bottom: 4px;
}}
.aviso-banner-meta {{
    font-size: 12px;
    color: #666666;
}}
.match {{
    background-color: #172033;
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
}}
.match h3 {{
    color: #ffcc00;
}}
div[data-testid="stButton"] > button[kind="secondary"] {{
    background-color: white;
    border: 1px solid #d6d9e0;
    border-radius: 12px;
    padding: 22px 16px;
    min-height: 110px;
    color: #172033;
    font-size: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}}
div[data-testid="stButton"] > button[kind="secondary"]:hover {{
    border-color: #172033;
    background-color: #eef1f6;
    transform: translateY(-2px);
}}
</style>
""", unsafe_allow_html=True)

# ======================================
# 3. ENCABEZADO SUPERIOR CON ESCUDO
# ======================================
col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists("escudo.png.png"):
        st.image("escudo.png.png", width=100)
    elif os.path.exists("escudo.png"):
        st.image("escudo.png", width=100)
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
st.sidebar.caption("Aplicación del equipo")

# ======================================
# PANTALLA DE INICIO
# ======================================
if opcion == "Inicio":

    st.markdown("""
    <div class="main-title">
        <h1>BENIAJÁN C.F.</h1>
        <p>Aplicación oficial de nuestro equipo - Infantil A</p>
        <p>Temporada 2026/2027</p>
    </div>
    """, unsafe_allow_html=True)

    if es_admin:
        with st.expander("🖼️ Cambiar foto de fondo del cartel principal"):
            foto_portada_subida = st.file_uploader(
                "Selecciona una foto horizontal del equipo:",
                key="uploader_portada"
            )
            if st.button("💾 Guardar foto en portada", type="primary"):
                if foto_portada_subida is not None:
                    ext = os.path.splitext(foto_portada_subida.name)[1].lower()
                    if ext in [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]:
                        with open(ruta_portada, "wb") as f:
                            f.write(foto_portada_subida.getbuffer())
                        guardar_en_github(ruta_portada, ruta_portada, "Actualiza foto de portada del equipo")
                        st.success("¡Foto de portada actualizada!")
                        st.rerun()
                    else:
                        st.error("Selecciona un archivo de imagen válido.")
                else:
                    st.warning("Selecciona primero una imagen.")

    st.write("")

    if os.path.exists("comunicados.csv"):
        try:
            df_com_inicio = pd.read_csv("comunicados.csv")
            if not df_com_inicio.empty:
                df_entrenador = df_com_inicio[df_com_inicio["Rol"] == "Entrenador"]
                ultimo_aviso = df_entrenador.iloc[0] if not df_entrenador.empty else df_com_inicio.iloc[0]
                st.markdown(f"""
                <div class="aviso-banner">
                    <div class="aviso-banner-titulo">🔔 ÚLTIMO AVISO DEL EQUIPO</div>
                    <div class="aviso-banner-texto">{ultimo_aviso['Mensaje']}</div>
                    <div class="aviso-banner-meta">Publicado por {ultimo_aviso['Autor']} · {ultimo_aviso['Fecha']}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass

    st.subheader("Bienvenido a tu equipo")
    st.write(
        "Aquí encontrarás toda la información "
        "deportiva y las comunicaciones del equipo."
    )

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

    num_jugadores = len(pd.read_csv("plantilla.csv")) if os.path.exists("plantilla.csv") else 0
    num_mensajes = len(pd.read_csv("comunicados.csv")) if os.path.exists("comunicados.csv") else 0
    num_fotos = 0
    if os.path.exists("galeria_datos.json"):
        with open("galeria_datos.json", "r", encoding="utf-8") as f:
            num_fotos = len(json.load(f))

    num_convocados = 0
    pendientes_conv = 0
    if os.path.exists("convocatoria_actual.json"):
        with open("convocatoria_actual.json", "r", encoding="utf-8") as f:
            c_data = json.load(f)
            num_convocados = len(c_data.get("convocados", []))
            pendientes_conv = sum(1 for c in c_data.get("convocados", []) if c.get("estado") == "⏳ Pendiente")

    st.subheader("Accesos rápidos")

    col1, col2, col3 = st.columns(3)

    with col1:
        texto_plantilla = f"👥 **Plantilla ({num_jugadores})**\n\nConsulta los jugadores del equipo" if num_jugadores > 0 else "👥 **Plantilla**\n\nConsulta los jugadores del equipo"
        st.button(
            texto_plantilla,
            use_container_width=True,
            on_click=ir_a,
            args=("Plantilla",)
        )

    with col2:
        st.button(
            "📅 **Calendario**\n\nPartidos y entrenamientos",
            use_container_width=True,
            on_click=ir_a,
            args=("Calendario",)
        )

    with col3:
        if num_convocados > 0:
            detalle_conv = f"{num_convocados} convocados ({pendientes_conv} pendientes)" if pendientes_conv > 0 else f"{num_convocados} convocados"
            texto_conv = f"📋 **Convocatorias 🔔**\n\n{detalle_conv}"
        else:
            texto_conv = "📋 **Convocatorias**\n\nConsulta y confirma asistencia"
        st.button(
            texto_conv,
            use_container_width=True,
            on_click=ir_a,
            args=("Convocatorias",)
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        texto_com = f"📢 **Comunicados ({num_mensajes})**\n\nNoticias y avisos del entrenador" if num_mensajes > 0 else "📢 **Comunicados**\n\nNoticias y avisos del entrenador"
        st.button(
            texto_com,
            use_container_width=True,
            on_click=ir_a,
            args=("Comunicados",)
        )

    with col5:
        texto_gal = f"📸 **Galería ({num_fotos})**\n\nFotos y recuerdos del equipo" if num_fotos > 0 else "📸 **Galería**\n\nFotos y recuerdos del equipo"
        st.button(
            texto_gal,
            use_container_width=True,
            on_click=ir_a,
            args=("Galería",)
        )

    with col6:
        if st.button(
            "🔒 **Cuerpo Técnico**\n\nAcceso edición en menú lateral",
            use_container_width=True
        ):
            st.info("Pulsa la flecha **`>`** arriba a la izquierda para abrir el menú lateral e introducir la contraseña de entrenador.")

# ======================================
# PLANTILLA
# ======================================
elif opcion == "Plantilla":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("👥 Plantilla de jugadores - Infantil A")

    archivo_plantilla = "plantilla.csv"
    if os.path.exists(archivo_plantilla):
        df_plantilla = pd.read_csv(archivo_plantilla)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Jugadores", len(df_plantilla))
        col_m2.metric("Disponibles", len(df_plantilla[df_plantilla["Estado"] == "Disponible"]))
        col_m3.metric("Lesionados", len(df_plantilla[df_plantilla["Estado"] == "Lesionado"]))
        col_m4.metric("Sancionados / Baja", len(df_plantilla[df_plantilla["Estado"] == "Sancionado"]))

        st.divider()

        lista_posiciones = [
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

        posiciones_filtro = ["Todas"] + lista_posiciones
        filtro_pos = st.selectbox("Filtrar por demarcación:", posiciones_filtro)

        if filtro_pos != "Todas":
            df_vista = df_plantilla[df_plantilla["Posicion"] == filtro_pos]
        else:
            df_vista = df_plantilla

        if es_admin:
            st.info("✏️ **Modo Entrenador:** Haz doble clic para cambiar nombres, dorsales, demarcación o estado.")

            df_plantilla_editada = st.data_editor(
                df_plantilla,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Dorsal": st.column_config.NumberColumn("Dorsal", min_value=1, max_value=99, step=1),
                    "Posicion": st.column_config.SelectboxColumn(
                        "Demarcación",
                        options=lista_posiciones,
                        required=True
                    ),
                    "Estado": st.column_config.SelectboxColumn(
                        "Estado",
                        options=["Disponible", "Lesionado", "Sancionado"],
                        required=True
                    )
                }
            )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("💾 Guardar cambios de plantilla", type="primary"):
                    df_plantilla_editada.to_csv(archivo_plantilla, index=False)
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
        else:
            for _, jugador in df_vista.iterrows():
                icono_estado = "🟢" if jugador["Estado"] == "Disponible" else ("🔴" if jugador["Estado"] == "Lesionado" else "🟡")
                dorsal_txt = int(jugador["Dorsal"]) if pd.notna(jugador["Dorsal"]) else "-"
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 4, 2])
                    c1.markdown(f"### #{dorsal_txt}")
                    c2.markdown(f"**{jugador['Nombre']}**\n\n*{jugador['Posicion']}*")
                    c3.markdown(f"{icono_estado} {jugador['Estado']}")
    else:
        st.warning("No se encontró el archivo plantilla.csv en el repositorio.")

# ======================================
# SECCIÓN: CALENDARIO
# ======================================
elif opcion == "Calendario":
    st.button("⬅️ Volver a Inicio", on_click=ir_a, args=("Inicio",))
    st.title("📅 Calendario deportivo (2026 - 2027)")

    opciones_tipo_cal = [
        "Descanso",
        "Entrenamiento",
        "Partido amistoso",
        "Partido competición"
    ]

    if os.path.exists("calendario.csv"):
        df = pd.read_csv("calendario.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date

        # Convertir columnas de texto a string limpio para evitar bloqueo "None" en st.data_editor
        for col_texto in ["Evento", "Hora", "Lugar"]:
            if col_texto in df.columns:
                df[col_texto] = df[col_texto].fillna("").astype(str).replace({"None": "", "nan": "", "NaN": ""})

        tipos_presentes = [t for t in df["Tipo"].dropna().unique() if t not in opciones_tipo_cal]
        opciones_filtro_cal = opciones_tipo_cal + tipos_presentes

        hoy = datetime.date.today()
        dentro_3_meses = hoy + datetime.timedelta(days=90)
        fecha_min = min(datetime.date(2026, 8, 1), hoy)
        fecha_max = max(datetime.date(2027, 8, 31), dentro_3_meses)

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            tipo_seleccionado = st.multiselect(
                "Filtrar por actividad:",
                options=opciones_filtro_cal,
                default=opciones_filtro_cal
            )

        with col_filtro2:
            rango_fechas = st.date_input(
                "Selecciona rango de fechas (por defecto 3 meses):",
                value=(hoy, dentro_3_meses),
                min_value=fecha_min,
                max_value=fecha_max
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
                with st.expander("🗓️ Planificador rápido (Generar hasta 3 meses de sesiones)", expanded=False):
                    with st.form("form_planificador_3_meses"):
                        col_pl1, col_pl2 = st.columns(2)
                        with col_pl1:
                            fecha_inicio_plan = st.date_input(
                                "Fecha de inicio:",
                                value=hoy,
                                min_value=fecha_min,
                                max_value=fecha_max
                            )
                            tipo_plan = st.selectbox(
                                "Tipo de actividad:",
                                options=opciones_tipo_cal,
                                index=1
                            )
                            hora_plan = st.text_input("Hora (ej. 18:30):", value="18:30")
                        with col_pl2:
                            dias_semana_map = {
                                "Lunes": 0,
                                "Martes": 1,
                                "Miércoles": 2,
                                "Jueves": 3,
                                "Viernes": 4,
                                "Sábado": 5,
                                "Domingo": 6
                            }
                            dias_elegidos = st.multiselect(
                                "Días de la semana:",
                                options=list(dias_semana_map.keys()),
                                default=["Martes", "Jueves"]
                            )
                            meses_plan = st.slider("Duración a planificar (meses):", min_value=1, max_value=3, value=3)
                            lugar_plan = st.text_input("Lugar / Campo:", value="Campo Municipal de Beniaján")
                        evento_plan = st.text_input("Descripción o rival (opcional):", value="")

                        if st.form_submit_button("📆 Generar y guardar planificación", type="primary"):
                            if not dias_elegidos:
                                st.warning("Selecciona al menos un día de la semana.")
                            else:
                                indices_dias = [dias_semana_map[d] for d in dias_elegidos]
                                fecha_limite = fecha_inicio_plan + datetime.timedelta(days=30 * meses_plan)
                                nuevas_filas = []
                                dia_cursor = fecha_inicio_plan
                                while dia_cursor <= fecha_limite:
                                    if dia_cursor.weekday() in indices_dias:
                                        fila_nueva = {col: "" for col in df.columns}
                                        fila_nueva["Fecha"] = dia_cursor
                                        fila_nueva["Tipo"] = tipo_plan
                                        if "Hora" in fila_nueva:
                                            fila_nueva["Hora"] = hora_plan
                                        if "Lugar" in fila_nueva:
                                            fila_nueva["Lugar"] = lugar_plan
                                        if "Evento" in fila_nueva:
                                            fila_nueva["Evento"] = evento_plan
                                        elif "Actividad" in fila_nueva:
                                            fila_nueva["Actividad"] = evento_plan
                                        nuevas_filas.append(fila_nueva)
                                    dia_cursor += datetime.timedelta(days=1)

                                if nuevas_filas:
                                    df_nuevas = pd.DataFrame(nuevas_filas)
                                    df_combinado = pd.concat([df, df_nuevas], ignore_index=True)
                                    df_combinado = df_combinado.sort_values(by="Fecha").reset_index(drop=True)
                                    df_combinado.to_csv("calendario.csv", index=False)
                                    guardar_en_github("calendario.csv", "calendario.csv", f"Planifica {meses_plan} meses en calendario")
                                    st.success(f"¡Se han planificado y guardado {len(nuevas_filas)} sesiones para los próximos {meses_plan} meses!")
                                    st.rerun()

                st.info("✏️ **Modo Entrenador:** Haz doble clic en cualquier celda (incluido **Evento**) para escribir y pulsa **Guardar cambios de calendario**.")

                config_columnas = {
                    "Fecha": st.column_config.DateColumn("Fecha", required=True),
                    "Tipo": st.column_config.SelectboxColumn(
                        "Tipo",
                        options=opciones_tipo_cal,
                        required=True
                    ),
                    "Hora": st.column_config.TextColumn(
                        "Hora",
                        help="Formato HH:MM (ej. 19:30)"
                    )
                }
                if "Evento" in df.columns:
                    config_columnas["Evento"] = st.column_config.TextColumn("Evento")
                if "Lugar" in df.columns:
                    config_columnas["Lugar"] = st.column_config.TextColumn("Lugar")

                df_editado = st.data_editor(
                    df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config=config_columnas
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar cambios de calendario", type="primary"):
                        for col_texto in ["Evento", "Hora", "Lugar"]:
                            if col_texto in df_editado.columns:
                                df_editado[col_texto] = df_editado[col_texto].fillna("").astype(str).replace({"None": "", "nan": ""})
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

    datos_conv = {
        "partido": "Próximo Partido Oficial",
        "notas": "Traer primera equipación (verde) y botella de agua.",
        "convocados": []
    }

    if os.path.exists(archivo_conv):
        with open(archivo_conv, "r", encoding="utf-8") as f:
            datos_conv = json.load(f)

    if es_admin:
        with st.expander("✏️ Configurar nueva convocatoria (Solo Entrenador)", expanded=True):
            if os.path.exists(archivo_plantilla):
                df_pl = pd.read_csv(archivo_plantilla)
                df_disp = df_pl[df_pl["Estado"] == "Disponible"]
                opciones_jugadores = []
                for _, fila in df_disp.iterrows():
                    dorsal_limpio = f"Dorsal {int(fila['Dorsal'])}" if pd.notna(fila["Dorsal"]) else "Sin dorsal"
                    opciones_jugadores.append(f"{dorsal_limpio} - {fila['Nombre']} ({fila['Posicion']})")

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
            col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])

            with col_sel1:
                jugador_elegido = st.selectbox(
                    "Selecciona el jugador:",
                    options=lista_nombres
                )

            with col_sel2:
                nuevo_estado = st.selectbox(
                    "Respuesta:",
                    options=["✅ Confirmado", "❌ No puede asistir", "⏳ Pendiente"]
                )

            with col_sel3:
                st.write("")
                st.write("")
                if st.button("Guardar respuesta", type="primary"):
                    for item in datos_conv["convocados"]:
                        if item["jugador"] == jugador_elegido:
                            item["estado"] = nuevo_estado

                    with open(archivo_conv, "w", encoding="utf-8") as f:
                        json.dump(datos_conv, f, ensure_ascii=False, indent=4)

                    guardar_en_github(
                        archivo_conv,
                        archivo_conv,
                        f"Asistencia: {jugador_elegido}"
                    )
                    st.success(f"Estado actualizado para {jugador_elegido}")
                    st.rerun()

        st.subheader("Lista oficial de convocados")
        for item in datos_conv["convocados"]:
            with st.container(border=True):
                col_j1, col_j2 = st.columns([3, 1])
                col_j1.markdown(f"**{item['jugador']}**")
                col_j2.markdown(f"{item['estado']}")

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
                    extension = os.path.splitext(archivo_subido.name)[1].lower()
                    extensiones_validas = [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]
                    if extension not in extensiones_validas:
                        st.error("Formato no compatible. Por favor, selecciona una imagen (JPG, PNG, WEBP o HEIC).")
                    else:
                        marca_tiempo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre_base, _ = os.path.splitext(archivo_subido.name)
                        nombre_limpio = re.sub(r'[^a-zA-Z0-9_-]', '_', nombre_base)
                        nombre_archivo = f"{marca_tiempo}_{nombre_limpio}{extension}"
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
