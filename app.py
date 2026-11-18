import streamlit as st
import pandas as pd
import datetime
import json
import os
import re
import random
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

def formatear_dorsal(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Sin dorsal"
    try:
        return f"Dorsal {int(float(val))}"
    except Exception:
        return f"Dorsal {str(val).strip()}"

def valor_dorsal_orden(val):
    try:
        if pd.isna(val) or str(val).strip() == "":
            return 999
        return int(float(val))
    except Exception:
        return 999

def limpiar_pin(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def normalizar_plantilla(df):
    df = df.copy()
    for col in ["Dorsal", "Nombre", "Posicion", "Estado", "PIN"]:
        if col not in df.columns:
            df[col] = ""
    df["Nombre"] = df["Nombre"].fillna("").astype(str).str.strip()
    df["Posicion"] = df["Posicion"].fillna("Ninguna").astype(str).str.strip()
    df.loc[df["Posicion"] == "", "Posicion"] = "Ninguna"
    df["Estado"] = df["Estado"].fillna("Disponible").astype(str).str.strip()
    df.loc[df["Estado"] == "", "Estado"] = "Disponible"
    df["PIN"] = df["PIN"].apply(limpiar_pin)
    # Eliminar filas totalmente vacías (sin nombre ni dorsal)
    df = df[~((df["Nombre"] == "") & (df["Dorsal"].isna() | (df["Dorsal"].astype(str).str.strip() == "")))].reset_index(drop=True)
    return df

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
st.markdown("""
<style>
.stApp {
    background-color: #f4f5f7;
}
.match {
    background-color: #172033;
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
}
.match h3 {
    color: #ffcc00;
}
.aviso-portada {
    background-color: #fff8db;
    border-left: 6px solid #ffcc00;
    padding: 15px 18px;
    border-radius: 10px;
    margin-bottom: 18px;
    color: #172033;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: white;
    border: 1px solid #d6d9e0;
    border-radius: 12px;
    padding: 20px 14px;
    min-height: 105px;
    color: #172033;
    font-size: 16px;
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

    foto_portada = "equipo_portada.jpg"
    if es_admin:
        with st.expander("🖼️ Cambiar foto de fondo del cartel principal"):
            nueva_portada = st.file_uploader("Sube una foto horizontal del equipo:")
            if st.button("💾 Guardar foto de portada", type="primary"):
                if nueva_portada is not None:
                    with open(foto_portada, "wb") as f:
                        f.write(nueva_portada.getbuffer())
                    guardar_en_github(foto_portada, foto_portada, "Actualiza foto de portada del equipo")
                    st.success("¡Foto de portada actualizada!")
                    st.rerun()
                else:
                    st.warning("Selecciona primero una imagen.")

    if os.path.exists(foto_portada):
        import base64
        with open(foto_portada, "rb") as img_f:
            b64_img = base64.b64encode(img_f.read()).decode()
        st.markdown(f"""
        <div style="
            background-image: linear-gradient(to top, rgba(23,32,51,0.92) 0%, rgba(23,32,51,0.25) 45%, rgba(23,32,51,0.05) 100%), url('data:image/jpeg;base64,{b64_img}');
            background-size: cover;
            background-position: center 25%;
            min-height: 290px;
            padding: 20px;
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            text-align: center;
            color: white;
        ">
            <h1 style="color: #ffcc00; font-size: clamp(1.4rem, 4.5vw, 2.3rem); margin: 0 0 4px 0; text-shadow: 1px 1px 4px rgba(0,0,0,0.8);">BENIAJÁN C.F.</h1>
            <p style="margin: 0; font-size: clamp(0.85rem, 2.8vw, 1.05rem); text-shadow: 1px 1px 3px rgba(0,0,0,0.8);">Aplicación oficial de nuestro equipo - Infantil A · Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background-color: #172033;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            color: white;
        ">
            <h1 style="color: #ffcc00; font-size: clamp(1.5rem, 5vw, 2.4rem); margin-bottom: 5px;">BENIAJÁN C.F.</h1>
            <p style="margin: 0;">Aplicación oficial de nuestro equipo - Infantil A</p>
            <p style="margin: 0;">Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Banner destacado con el último comunicado del entrenador
    if os.path.exists("comunicados.csv"):
        df_com_inicio = pd.read_csv("comunicados.csv")
        if not df_com_inicio.empty:
            oficiales = df_com_inicio[df_com_inicio["Rol"] == "Entrenador"]
            ultimo = oficiales.iloc[0] if not oficiales.empty else df_com_inicio.iloc[0]
            st.markdown(f"""
            <div class="aviso-portada">
                <strong>📢 ÚLTIMO AVISO ({ultimo['Autor']} · {ultimo['Fecha']}):</strong><br>
                {ultimo['Mensaje']}
            </div>
            """, unsafe_allow_html=True)

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

    # Contadores para los accesos rápidos
    num_jugadores = 0
    if os.path.exists("plantilla.csv"):
        df_tmp_pl = normalizar_plantilla(pd.read_csv("plantilla.csv"))
        num_jugadores = len(df_tmp_pl)

    num_convocados = 0
    num_pendientes = 0
    if os.path.exists("convocatoria_actual.json"):
        with open("convocatoria_actual.json", "r", encoding="utf-8") as f:
            d_conv_tmp = json.load(f)
            num_convocados = len(d_conv_tmp.get("convocados", []))
            num_pendientes = sum(1 for c in d_conv_tmp.get("convocados", []) if c.get("estado") == "⏳ Pendiente")

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
        texto_plantilla = f"👥 **Plantilla ({num_jugadores})**\n\nConsulta los jugadores del equipo"
        st.button(texto_plantilla, use_container_width=True, on_click=ir_a, args=("Plantilla",))

    with col2:
        texto_calendario = "📅 **Calendario**\n\nPartidos y entrenamientos"
        st.button(texto_calendario, use_container_width=True, on_click=ir_a, args=("Calendario",))

    with col3:
        aviso_pend = f" · {num_pendientes} pend. 🔔" if num_pendientes > 0 else ""
        texto_conv = f"📋 **Convocatorias ({num_convocados}{aviso_pend})**\n\nConsulta y confirma asistencia"
        st.button(texto_conv, use_container_width=True, on_click=ir_a, args=("Convocatorias",))

    col4, col5, col6 = st.columns(3)

    with col4:
        texto_com = f"📢 **Comunicados ({num_mensajes})**\n\nNoticias y avisos del entrenador"
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
    opciones_demarcacion = [
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

    if os.path.exists(archivo_plantilla):
        df_plantilla = normalizar_plantilla(pd.read_csv(archivo_plantilla))
    else:
        df_plantilla = pd.DataFrame(columns=["Dorsal", "Nombre", "Posicion", "Estado", "PIN"])

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Jugadores", len(df_plantilla))
    col_m2.metric("Disponibles", len(df_plantilla[df_plantilla["Estado"] == "Disponible"]))
    col_m3.metric("Lesionados", len(df_plantilla[df_plantilla["Estado"] == "Lesionado"]))
    col_m4.metric("Sancionados / Baja", len(df_plantilla[df_plantilla["Estado"] == "Sancionado"]))

    st.divider()

    posiciones_filtro = ["Todas"] + opciones_demarcacion
    filtro_pos = st.selectbox("Filtrar por demarcación:", posiciones_filtro)

    if filtro_pos != "Todas":
        df_vista = df_plantilla[df_plantilla["Posicion"] == filtro_pos]
    else:
        df_vista = df_plantilla

    if es_admin:
        st.info("✏️ **Modo Entrenador:** Añade jugadores al final de la tabla o haz doble clic para editar. **Recuerda pulsar '💾 Guardar cambios de plantilla' antes de salir de esta pantalla.**")

        if st.button("🎲 Generar PIN aleatorio de 4 dígitos a los que no tengan"):
            pines_usados = set(df_plantilla["PIN"].tolist())
            nuevos_pines = []
            for p_actual in df_plantilla["PIN"]:
                if len(p_actual) == 4 and p_actual.isdigit():
                    nuevos_pines.append(p_actual)
                else:
                    nuevo_p = f"{random.randint(1000, 9999)}"
                    while nuevo_p in pines_usados:
                        nuevo_p = f"{random.randint(1000, 9999)}"
                    pines_usados.add(nuevo_p)
                    nuevos_pines.append(nuevo_p)
            df_plantilla["PIN"] = nuevos_pines
            df_plantilla.to_csv(archivo_plantilla, index=False)
            guardar_en_github(archivo_plantilla, archivo_plantilla, "Genera PINes de asistencia en plantilla")
            st.success("¡PINes generados y guardados en GitHub! Ya puedes repartir cada código a su familia.")
            st.rerun()

        df_plantilla_editada = st.data_editor(
            df_plantilla,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Dorsal": st.column_config.NumberColumn("Dorsal", min_value=1, max_value=99, step=1),
                "Nombre": st.column_config.TextColumn("Nombre"),
                "Posicion": st.column_config.SelectboxColumn(
                    "Demarcación",
                    options=opciones_demarcacion,
                    default="Ninguna",
                    required=True
                ),
                "Estado": st.column_config.SelectboxColumn(
                    "Estado",
                    options=["Disponible", "Lesionado", "Sancionado"],
                    default="Disponible",
                    required=True
                ),
                "PIN": st.column_config.TextColumn(
                    "PIN (4 dígitos)",
                    help="Código privado de 4 cifras para confirmar asistencia",
                    max_chars=4
                )
            }
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("💾 Guardar cambios de plantilla", type="primary"):
                df_guardar = normalizar_plantilla(df_plantilla_editada)
                df_guardar.to_csv(archivo_plantilla, index=False)
                guardar_en_github(archivo_plantilla, archivo_plantilla, "Actualiza plantilla")
                st.success(f"Plantilla guardada permanentemente ({len(df_guardar)} jugadores).")
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
        if df_vista.empty:
            st.info("No hay jugadores registrados en esta demarcación.")
        else:
            for _, jugador in df_vista.iterrows():
                icono_estado = "🟢" if jugador["Estado"] == "Disponible" else ("🔴" if jugador["Estado"] == "Lesionado" else "🟡")
                dorsal_txt = formatear_dorsal(jugador["Dorsal"])
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1.3, 4, 2])
                    c1.markdown(f"### {dorsal_txt}")
                    c2.markdown(f"**{jugador['Nombre']}**\n\n*{jugador['Posicion']}*")
                    c3.markdown(f"{icono_estado} {jugador['Estado']}")

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
    else:
        df = pd.DataFrame(columns=["Fecha", "Hora", "Tipo", "Evento", "Lugar"])

    if not df.empty:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.date
        df = df.dropna(subset=["Fecha"]).reset_index(drop=True)

    for col_txt in ["Hora", "Tipo", "Evento", "Lugar"]:
        if col_txt in df.columns:
            df[col_txt] = df[col_txt].fillna("").astype(str)

    tipos_presentes = [t for t in df["Tipo"].dropna().unique().tolist() if t != "" and t not in opciones_tipo_cal]
    todas_opciones_tipo = opciones_tipo_cal + tipos_presentes

    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        tipo_seleccionado = st.multiselect(
            "Filtrar por actividad:",
            options=todas_opciones_tipo,
            default=todas_opciones_tipo
        )

    hoy = datetime.date.today()
    dentro_3_meses = hoy + datetime.timedelta(days=90)

    with col_filtro2:
        rango_fechas = st.date_input(
            "Selecciona rango de fechas:",
            value=(hoy, dentro_3_meses),
            min_value=datetime.date(2026, 1, 1),
            max_value=datetime.date(2027, 12, 31)
        )

    if es_admin:
        with st.expander("🗓️ Planificador rápido (Generar hasta 3 meses de sesiones)", expanded=False):
            with st.form("form_planificador_3_meses"):
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    fecha_inicio_plan = st.date_input("Fecha de inicio:", value=hoy)
                    dias_semana = st.multiselect(
                        "Días de la semana:",
                        options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                        default=["Martes", "Jueves"]
                    )
                    tipo_plan = st.selectbox("Tipo de actividad:", options=opciones_tipo_cal, index=1)
                with c_p2:
                    meses_plan = st.selectbox("Duración a planificar:", options=[1, 2, 3], index=2, format_func=lambda m: f"{m} {'mes' if m == 1 else 'meses'} ({m*30} días)")
                    hora_plan = st.text_input("Hora (HH:MM):", value="18:30")
                    lugar_plan = st.text_input("Campo / Lugar:", value="Campo Municipal de Beniaján")
                evento_plan = st.text_input("Descripción del evento:", value="Sesión de entrenamiento Infantil A")

                if st.form_submit_button("📅 Generar y guardar planificación en GitHub", type="primary"):
                    mapa_dias = {
                        "Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3,
                        "Viernes": 4, "Sábado": 5, "Domingo": 6
                    }
                    dias_num = [mapa_dias[d] for d in dias_semana]
                    nuevas_filas = []
                    total_dias = meses_plan * 30
                    for i in range(total_dias + 1):
                        dia_iter = fecha_inicio_plan + datetime.timedelta(days=i)
                        if dia_iter.weekday() in dias_num:
                            fila_nueva = {
                                "Fecha": dia_iter,
                                "Hora": hora_plan.strip(),
                                "Tipo": tipo_plan,
                                "Evento": evento_plan.strip(),
                                "Lugar": lugar_plan.strip()
                            }
                            for col_ex in df.columns:
                                if col_ex not in fila_nueva:
                                    fila_nueva[col_ex] = ""
                            nuevas_filas.append(fila_nueva)

                    if nuevas_filas:
                        df_nuevas = pd.DataFrame(nuevas_filas)
                        df_combinado = pd.concat([df, df_nuevas], ignore_index=True)
                        df_combinado["Fecha"] = pd.to_datetime(df_combinado["Fecha"]).dt.date
                        df_combinado = df_combinado.sort_values(by=["Fecha", "Hora"]).reset_index(drop=True)
                        df_combinado.to_csv("calendario.csv", index=False)
                        guardar_en_github("calendario.csv", "calendario.csv", f"Planifica {meses_plan} meses en calendario")
                        st.success(f"¡Se han planificado y guardado {len(nuevas_filas)} sesiones para los próximos {meses_plan} meses!")
                        st.rerun()
                    else:
                        st.warning("Selecciona al menos un día de la semana.")

    if len(rango_fechas) == 2:
        inicio, fin = rango_fechas
        if not df.empty:
            mascara = (
                (df["Tipo"].isin(tipo_seleccionado))
                & (df["Fecha"] >= inicio)
                & (df["Fecha"] <= fin)
            )
            df_filtrado = df[mascara]
        else:
            df_filtrado = df

        if es_admin:
            st.info("✏️ **Modo Entrenador:** Haz doble clic en cualquier celda (incluida la columna Evento) para escribir o editar.")
            col_cfg = {
                "Fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD", required=True),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=todas_opciones_tipo,
                    required=True
                ),
                "Hora": st.column_config.TextColumn(
                    "Hora",
                    help="Formato HH:MM (ej. 19:30)"
                )
            }
            if "Evento" in df.columns:
                col_cfg["Evento"] = st.column_config.TextColumn("Evento")
            if "Lugar" in df.columns:
                col_cfg["Lugar"] = st.column_config.TextColumn("Lugar")

            df_editado = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config=col_cfg
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
            if df_filtrado.empty:
                st.info("No hay actividades programadas en el rango de fechas seleccionado.")
            else:
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("Selecciona una fecha de inicio y otra de fin.")

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

    # Cargar mapa de PINes y lista de jugadores desde plantilla.csv
    mapa_pines = {}
    df_pl = pd.DataFrame()
    if os.path.exists(archivo_plantilla):
        df_pl = normalizar_plantilla(pd.read_csv(archivo_plantilla))
        for _, fila in df_pl.iterrows():
            nombre_etiqueta = f"{formatear_dorsal(fila['Dorsal'])} - {fila['Nombre']} ({fila['Posicion']})"
            mapa_pines[nombre_etiqueta] = fila["PIN"]

    if es_admin:
        with st.expander("✏️ Configurar nueva convocatoria (Solo Entrenador)", expanded=True):
            if not df_pl.empty:
                # Excluir únicamente a lesionados o sancionados explícitos
                estados_baja = ["lesionado", "sancionado"]
                df_disp = df_pl[~df_pl["Estado"].str.lower().isin(estados_baja)].copy()
                df_disp["_orden_dorsal"] = df_disp["Dorsal"].apply(valor_dorsal_orden)
                df_disp = df_disp.sort_values(by=["_orden_dorsal", "Nombre"])

                opciones_jugadores = [
                    f"{formatear_dorsal(fila['Dorsal'])} - {fila['Nombre']} ({fila['Posicion']})"
                    for _, fila in df_disp.iterrows()
                ]

                st.caption(f"Jugadores cargados desde plantilla: {len(df_pl)} totales · {len(opciones_jugadores)} disponibles para convocar.")

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
                st.warning("Primero debes añadir jugadores en la sección Plantilla y pulsar 'Guardar cambios de plantilla'.")

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
                        guardar_en_github(archivo_conv, archivo_conv, f"Asistencia (Entrenador): {jugador_elegido}")
                        st.success(f"Estado actualizado para {jugador_elegido}")
                        st.rerun()
            else:
                col_sel1, col_sel2, col_sel3, col_sel4 = st.columns([2.2, 1.8, 1.2, 1.2])
                with col_sel1:
                    jugador_elegido = st.selectbox("1. Selecciona tu dorsal y nombre:", options=lista_nombres)
                with col_sel2:
                    nuevo_estado = st.selectbox("2. ¿Asistes al partido?", options=["✅ Confirmado", "❌ No puede asistir", "⏳ Pendiente"])
                with col_sel3:
                    pin_introducido = st.text_input("3. Tu PIN (4 cifras):", type="password", max_chars=4)
                with col_sel4:
                    st.write("")
                    st.write("")
                    if st.button("Confirmar", type="primary"):
                        pin_correcto = mapa_pines.get(jugador_elegido, "")
                        if not pin_correcto:
                            st.error("Este jugador aún no tiene PIN asignado. Pídeselo al entrenador.")
                        elif pin_introducido.strip() != pin_correcto:
                            st.error("❌ PIN incorrecto. Revisa tu código de 4 cifras.")
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
                "Selecciona una fotografía de tu galería:"
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
                        nombre_limpio = re.sub(r"[^a-zA-Z0-9._-]", "_", archivo_subido.name)
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
                        ext_img = os.path.splitext(foto["archivo"])[1].lower()
                        mime_img = "image/png" if ext_img == ".png" else ("image/webp" if ext_img == ".webp" else "image/jpeg")

                        st.download_button(
                            label="📥 Descargar foto",
                            data=bytes_img,
                            file_name=foto["archivo"],
                            mime=mime_img,
                            key=f"dl_foto_{indice}",
                            use_container_width=True
                        )

                        if es_admin:
                            if st.button("🗑️ Eliminar", key=f"del_foto_{indice}", use_container_width=True):
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
