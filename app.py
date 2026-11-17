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

def formatear_jugador(fila):
    dorsal = fila.get("Dorsal", "")
    nombre = str(fila.get("Nombre", "")).strip()
    posicion = str(fila.get("Posicion", "")).strip()
    if pd.notna(dorsal) and str(dorsal).strip() != "":
        try:
            dorsal_texto = f"Dorsal {int(float(dorsal))}"
        except Exception:
            dorsal_texto = f"Dorsal {str(dorsal).strip()}"
    else:
        dorsal_texto = "Sin dorsal"
    return f"{dorsal_texto} - {nombre} ({posicion})"

def limpiar_pin(valor):
    if pd.isna(valor):
        return ""
    s = str(valor).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

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
.main-title {
    background-color: #172033;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
}
.main-title h1 {
    color: #ffcc00;
    margin-bottom: 5px;
}
.main-title p {
    color: white;
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
.aviso-banner {
    background-color: #fff8dc;
    border-left: 6px solid #ffcc00;
    border-top: 1px solid #f0e1a0;
    border-right: 1px solid #f0e1a0;
    border-bottom: 1px solid #f0e1a0;
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #172033;
}
.aviso-banner h4 {
    margin: 0 0 6px 0;
    color: #172033;
}
.aviso-banner p {
    margin: 0;
    font-size: 15px;
}
div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: white;
    border: 1px solid #d6d9e0;
    border-radius: 12px;
    padding: 20px 14px;
    min-height: 112px;
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

    import base64
    ruta_foto_portada = "equipo_portada.jpg"

    if es_admin:
        with st.expander("🖼️ Cambiar foto de fondo del cartel principal"):
            with st.form("form_foto_portada", clear_on_submit=True):
                foto_equipo = st.file_uploader("Selecciona una foto horizontal del equipo:")
                if st.form_submit_button("💾 Guardar foto de portada", type="primary"):
                    if foto_equipo is not None:
                        ext = os.path.splitext(foto_equipo.name)[1].lower()
                        if ext in [".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"]:
                            with open(ruta_foto_portada, "wb") as f:
                                f.write(foto_equipo.getbuffer())
                            guardar_en_github(ruta_foto_portada, ruta_foto_portada, "Actualiza foto de portada del equipo")
                            st.success("¡Foto de portada actualizada!")
                            st.rerun()
                        else:
                            st.warning("Formato no compatible. Sube una imagen JPG o PNG.")
                    else:
                        st.warning("Selecciona primero una imagen.")

    if os.path.exists(ruta_foto_portada):
        with open(ruta_foto_portada, "rb") as img_f:
            img_b64 = base64.b64encode(img_f.read()).decode()
        st.markdown(f"""
        <div style="
            background-image: linear-gradient(to top, rgba(23, 32, 51, 0.92) 0%, rgba(23, 32, 51, 0.25) 45%, rgba(23, 32, 51, 0.0) 100%), url('data:image/jpeg;base64,{img_b64}');
            background-size: cover;
            background-position: center 20%;
            min-height: 290px;
            padding: 18px 20px;
            border-radius: 15px;
            text-align: center;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
        ">
            <h1 style="color: #ffcc00; font-size: clamp(1.35rem, 4.5vw, 2.2rem); margin: 0 0 2px 0; text-shadow: 2px 2px 6px rgba(0,0,0,0.95); letter-spacing: 1px;">BENIAJÁN C.F.</h1>
            <p style="color: white; font-size: clamp(0.85rem, 2.8vw, 1.05rem); margin: 0; font-weight: 600; text-shadow: 1px 1px 4px rgba(0,0,0,0.95);">Infantil A · Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-title">
            <h1 style="font-size: clamp(1.4rem, 4.5vw, 2.2rem); margin-bottom: 4px;">BENIAJÁN C.F.</h1>
            <p style="margin: 0;">Aplicación oficial de nuestro equipo - Infantil A · Temporada 2026/2027</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    if os.path.exists("comunicados.csv"):
        df_avisos = pd.read_csv("comunicados.csv")
        if not df_avisos.empty:
            df_entrenador = df_avisos[df_avisos["Rol"] == "Entrenador"]
            ultimo = df_entrenador.iloc[0] if not df_entrenador.empty else df_avisos.iloc[0]
            st.markdown(f"""
            <div class="aviso-banner">
                <h4>🔔 ÚLTIMO AVISO ({ultimo['Autor']} · {ultimo['Fecha']})</h4>
                <p>{ultimo['Mensaje']}</p>
            </div>
            """, unsafe_allow_html=True)

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
            aviso_pend = f" · {pendientes_conv} pend." if pendientes_conv > 0 else ""
            texto_conv = f"📋 **Convocatorias ({num_convocados}) 🔔**\n\nActiva{aviso_pend} · Confirma asistencia"
        else:
            texto_conv = "📋 **Convocatorias**\n\nConsulta las convocatorias"
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

        if "PIN" not in df_plantilla.columns:
            df_plantilla["PIN"] = ""
        df_plantilla["PIN"] = df_plantilla["PIN"].apply(limpiar_pin)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Jugadores", len(df_plantilla))
        col_m2.metric("Disponibles", len(df_plantilla[df_plantilla["Estado"] == "Disponible"]))
        col_m3.metric("Lesionados", len(df_plantilla[df_plantilla["Estado"] == "Lesionado"]))
        col_m4.metric("Sancionados / Baja", len(df_plantilla[df_plantilla["Estado"] == "Sancionado"]))

        st.divider()

        posiciones_tacticas = [
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
        filtro_pos = st.selectbox("Filtrar por demarcación:", ["Todas"] + posiciones_tacticas)

        if filtro_pos != "Todas":
            df_vista = df_plantilla[df_plantilla["Posicion"] == filtro_pos]
        else:
            df_vista = df_plantilla

        if es_admin:
            st.info("✏️ **Modo Entrenador:** Haz doble clic para cambiar nombres, dorsales, demarcación, estado o asignar el **PIN de 4 dígitos** de cada jugador.")

            if st.button("🎲 Generar PIN aleatorio de 4 dígitos a los que no tengan"):
                usados = set(df_plantilla["PIN"].tolist())
                nuevos_pines = []
                for p in df_plantilla["PIN"]:
                    if p == "":
                        nuevo = f"{random.randint(1000, 9999)}"
                        while nuevo in usados:
                            nuevo = f"{random.randint(1000, 9999)}"
                        usados.add(nuevo)
                        nuevos_pines.append(nuevo)
                    else:
                        nuevos_pines.append(p)
                df_plantilla["PIN"] = nuevos_pines
                df_plantilla.to_csv(archivo_plantilla, index=False)
                guardar_en_github(archivo_plantilla, archivo_plantilla, "Genera PINes automáticos en plantilla")
                st.success("¡PINes generados y guardados en GitHub! Ya puedes verlos en la tabla y pasárselos a cada familia.")
                st.rerun()

            df_plantilla_editada = st.data_editor(
                df_plantilla,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Dorsal": st.column_config.NumberColumn("Dorsal", min_value=1, max_value=99, step=1),
                    "Posicion": st.column_config.SelectboxColumn(
                        "Demarcación",
                        options=posiciones_tacticas,
                        required=True
                    ),
                    "Estado": st.column_config.SelectboxColumn(
                        "Estado",
                        options=["Disponible", "Lesionado", "Sancionado"],
                        required=True
                    ),
                    "PIN": st.column_config.TextColumn(
                        "PIN (4 dígitos)",
                        help="Código personal de 4 cifras para confirmar asistencia (ej. 4821)",
                        max_chars=4
                    )
                }
            )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if st.button("💾 Guardar cambios de plantilla", type="primary"):
                    df_plantilla_editada["PIN"] = df_plantilla_editada["PIN"].apply(limpiar_pin)
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
                dorsal_val = int(float(jugador["Dorsal"])) if pd.notna(jugador["Dorsal"]) and str(jugador["Dorsal"]).strip() != "" else "-"
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 4, 2])
                    c1.markdown(f"### Dorsal {dorsal_val}")
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

    tipos_actividad = [
        "Descanso",
        "Entrenamiento",
        "Partido amistoso",
        "Partido competición"
    ]

    if os.path.exists("calendario.csv"):
        df = pd.read_csv("calendario.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date

        for col_texto in ["Tipo", "Evento", "Hora", "Lugar"]:
            if col_texto in df.columns:
                df[col_texto] = df[col_texto].fillna("").astype(str)

        if es_admin:
            with st.expander("🗓️ Planificador rápido (Generar hasta 3 meses de sesiones)", expanded=False):
                with st.form("form_planificador_3_meses"):
                    col_pl1, col_pl2 = st.columns(2)
                    with col_pl1:
                        fecha_inicio_plan = st.date_input("Fecha de inicio:", value=datetime.date.today())
                        dias_semana = st.multiselect(
                            "Días de la semana:",
                            options=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                            default=["Martes", "Jueves"]
                        )
                        tipo_plan = st.selectbox("Tipo de actividad:", options=tipos_actividad, index=1)
                    with col_pl2:
                        meses_plan = st.selectbox("Duración a planificar:", options=[1, 2, 3], index=2, format_func=lambda m: f"{m} {'mes' if m == 1 else 'meses'} ({m * 30} días)")
                        hora_plan = st.text_input("Hora (ej. 18:30):", value="18:30")
                        lugar_plan = st.text_input("Lugar / Campo:", value="Campo Municipal de Beniaján")
                        evento_plan = st.text_input("Descripción / Rival (opcional):", value="Sesión de entrenamiento")

                    if st.form_submit_button("📅 Generar y guardar planificación en GitHub", type="primary"):
                        if not dias_semana:
                            st.warning("Selecciona al menos un día de la semana.")
                        else:
                            mapa_dias = {
                                "Lunes": 0, "Martes": 1, "Miércoles": 2,
                                "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6
                            }
                            dias_num = [mapa_dias[d] for d in dias_semana]
                            fecha_fin_plan = fecha_inicio_plan + datetime.timedelta(days=meses_plan * 30)

                            nuevas_filas = []
                            dia_actual = fecha_inicio_plan
                            while dia_actual <= fecha_fin_plan:
                                if dia_actual.weekday() in dias_num:
                                    fila_nueva = {}
                                    for col in df.columns:
                                        if col == "Fecha":
                                            fila_nueva[col] = dia_actual
                                        elif col == "Tipo":
                                            fila_nueva[col] = tipo_plan
                                        elif col == "Hora":
                                            fila_nueva[col] = hora_plan
                                        elif col == "Lugar":
                                            fila_nueva[col] = lugar_plan
                                        elif col in ["Evento", "Actividad", "Descripcion"]:
                                            fila_nueva[col] = evento_plan
                                        else:
                                            fila_nueva[col] = ""
                                    nuevas_filas.append(fila_nueva)
                                dia_actual += datetime.timedelta(days=1)

                            if nuevas_filas:
                                df_nuevas = pd.DataFrame(nuevas_filas)
                                df_combinado = pd.concat([df, df_nuevas], ignore_index=True)
                                df_combinado["Fecha"] = pd.to_datetime(df_combinado["Fecha"]).dt.date
                                df_combinado = df_combinado.sort_values(by="Fecha").reset_index(drop=True)
                                df_combinado.to_csv("calendario.csv", index=False)
                                guardar_en_github("calendario.csv", "calendario.csv", f"Planifica {meses_plan} meses en calendario")
                                st.success(f"¡Se han planificado y guardado {len(nuevas_filas)} sesiones para los próximos {meses_plan} meses!")
                                st.rerun()

        opciones_filtro = list(dict.fromkeys(tipos_actividad + [t for t in df["Tipo"].dropna().unique().tolist() if t != ""]))

        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            tipo_seleccionado = st.multiselect(
                "Filtrar por actividad:",
                options=opciones_filtro,
                default=opciones_filtro
            )

        hoy = datetime.date.today()
        tres_meses = hoy + datetime.timedelta(days=90)
        fecha_min_csv = min(df["Fecha"].min(), hoy)
        fecha_max_csv = max(df["Fecha"].max(), datetime.date(2027, 8, 31))

        with col_filtro2:
            rango_fechas = st.date_input(
                "Selecciona rango de fechas (por defecto 3 meses):",
                value=(hoy, min(tres_meses, fecha_max_csv)),
                min_value=fecha_min_csv,
                max_value=fecha_max_csv
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
                st.info("✏️ **Modo Entrenador:** Haz doble clic en cualquier celda para editar eventos, horas o lugares.")
                config_cols = {
                    "Fecha": st.column_config.DateColumn("Fecha", required=True),
                    "Tipo": st.column_config.SelectboxColumn(
                        "Tipo",
                        options=opciones_filtro,
                        required=True
                    )
                }
                if "Evento" in df.columns:
                    config_cols["Evento"] = st.column_config.TextColumn("Evento")
                if "Hora" in df.columns:
                    config_cols["Hora"] = st.column_config.TextColumn(
                        "Hora",
                        help="Formato HH:MM (ej. 19:30)"
                    )
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
                        for col_texto in ["Tipo", "Evento", "Hora", "Lugar"]:
                            if col_texto in df_editado.columns:
                                df_editado[col_texto] = df_editado[col_texto].fillna("").astype(str)
                        df_editado = df_editado.sort_values(by="Fecha").reset_index(drop=True)
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

    mapa_pines = {}
    if os.path.exists(archivo_plantilla):
        df_pl_pines = pd.read_csv(archivo_plantilla)
        if "PIN" in df_pl_pines.columns:
            for _, r in df_pl_pines.iterrows():
                etiqueta_r = formatear_jugador(r)
                mapa_pines[etiqueta_r] = limpiar_pin(r["PIN"])

    if es_admin:
        with st.expander("✏️ Configurar nueva convocatoria (Solo Entrenador)", expanded=True):
            if os.path.exists(archivo_plantilla):
                df_pl = pd.read_csv(archivo_plantilla)
                df_disp = df_pl[df_pl["Estado"] == "Disponible"]
                opciones_jugadores = [
                    formatear_jugador(fila)
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
                st.caption("🔓 Modo Entrenador activo: puedes modificar cualquier jugador sin introducir su PIN.")
                col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])
                with col_sel1:
                    jugador_elegido = st.selectbox("Selecciona el jugador:", options=lista_nombres)
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
                        guardar_en_github(archivo_conv, archivo_conv, f"Asistencia: {jugador_elegido}")
                        st.success(f"Estado actualizado para {jugador_elegido}")
                        st.rerun()
            else:
                col_sel1, col_sel2, col_sel3, col_sel4 = st.columns([2.2, 1.8, 1.2, 1.2])
                with col_sel1:
                    jugador_elegido = st.selectbox("Selecciona el jugador:", options=lista_nombres)
                with col_sel2:
                    nuevo_estado = st.selectbox(
                        "Respuesta:",
                        options=["✅ Confirmado", "❌ No puede asistir", "⏳ Pendiente"]
                    )
                with col_sel3:
                    pin_introducido = st.text_input("PIN (4 cifras):", type="password", max_chars=4)
                with col_sel4:
                    st.write("")
                    st.write("")
                    if st.button("Guardar", type="primary", use_container_width=True):
                        pin_correcto = mapa_pines.get(jugador_elegido, "")
                        if pin_correcto == "":
                            st.error("Este jugador aún no tiene PIN asignado. Pídeselo al entrenador.")
                        elif pin_introducido.strip() != pin_correcto:
                            st.error("❌ PIN incorrecto. No se ha guardado el cambio.")
                        else:
                            for item in datos_conv["convocados"]:
                                if item["jugador"] == jugador_elegido:
                                    item["estado"] = nuevo_estado
                            with open(archivo_conv, "w", encoding="utf-8") as f:
                                json.dump(datos_conv, f, ensure_ascii=False, indent=4)
                            guardar_en_github(archivo_conv, archivo_conv, f"Asistencia: {jugador_elegido}")
                            st.success(f"✅ Asistencia guardada para {jugador_elegido}")
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
                        st.error("El archivo seleccionado no es una imagen válida (JPG, PNG, WEBP o HEIC).")
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
