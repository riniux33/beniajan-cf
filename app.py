import streamlit as st

col1, col2 = st.columns([1, 4])

with col1:
    st.image("escudo.png.png", width=100)

with col2:
    st.title("Beniaján C.F.")
    st.subheader("⚽ Infantil A · Temporada 2026/2027")
# ======================================
# BENIAJÁN C.F. - APLICACIÓN OFICIAL
# Primera versión visual
# ======================================

# Configuración de la página
st.set_page_config(
    page_title="Beniaján C.F.",
    page_icon="⚽",
    layout="wide"
)

# Diseño visual y colores
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

.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    min-height: 130px;
    margin-bottom: 12px;
}

.card h3 {
    color: #172033;
}

.card p {
    color: #555555;
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

</style>
""", unsafe_allow_html=True)


# ======================================
# MENÚ LATERAL
# ======================================

st.sidebar.title("⚽ BENIAJÁN C.F.")

st.sidebar.markdown("### Menú principal")

opcion = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Inicio",
        "Plantilla",
        "Calendario",
        "Convocatorias",
        "Comunicados",
        "Galería"
    ]
)

st.sidebar.divider()

st.sidebar.caption("Temporada 2026/2027")
st.sidebar.caption("Aplicación del equipo")


# ======================================
# PANTALLA DE INICIO
# ======================================

if opcion == "Inicio":

    st.markdown("""
    <div class="main-title">
        <h1>⚽ BENIAJÁN C.F.</h1>
        <p>Aplicación oficial de nuestro equipo</p>
        <p>Temporada 2026/2027</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.subheader("Bienvenido a tu equipo")

    st.write(
        "Aquí encontrarás toda la información "
        "deportiva y las comunicaciones del equipo."
    )

    import json
    import os

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

    # Formulario oculto que solo ves tú al meter la contraseña
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
                    st.success("¡Cartel actualizado!")
                    st.rerun()

    # Tu tarjeta original conectada a los datos editables
    st.markdown(f"""
    <div class="match">
        <h3>🏆 PRÓXIMO PARTIDO</h3>
        <h2>{datos_partido['encuentro']}</h2>
        <p>📅 {datos_partido['fecha_hora']}</p>
        <p>📍 {datos_partido['campo']}</p>
        <p>⏰ Hora de citación: {datos_partido['citacion']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Accesos principales
    st.subheader("Accesos rápidos")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h3>👥 Plantilla</h3>
            <p>Consulta los jugadores del equipo.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3>📅 Calendario</h3>
            <p>Partidos y entrenamientos.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>📋 Convocatorias</h3>
            <p>Consulta las convocatorias.</p>
        </div>
        """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="card">
            <h3>📢 Comunicados</h3>
            <p>Noticias y avisos del entrenador.</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="card">
            <h3>📸 Galería</h3>
            <p>Fotos y vídeos del equipo.</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="card">
            <h3>⚙️ Administración</h3>
            <p>Gestión del equipo.</p>
        </div>
        """, unsafe_allow_html=True)


# ======================================
# RESTO DE SECCIONES
# ======================================

elif opcion == "Plantilla":
    st.title("👥 Plantilla de jugadores")
    st.info("Aquí incorporaremos las fichas de los jugadores.")

elif opcion == "Calendario":
    st.title("📅 Calendario deportivo")
    st.info("Aquí incorporaremos los partidos y entrenamientos.")

elif opcion == "Convocatorias":
    st.title("📋 Convocatorias")
    st.info("Aquí crearemos el sistema de confirmación de asistencia.")

elif opcion == "Comunicados":
    st.title("📢 Comunicados")
    st.info("Aquí publicaremos los avisos para las familias.")

elif opcion == "Galería":
    st.title("📸 Galería de fotografías")
    st.info("Aquí crearemos los álbumes privados del equipo.")


# ======================================
# PIE DE PÁGINA
# ======================================

st.divider()

st.caption(
    "BENIAJÁN C.F. | Aplicación de gestión y comunicación "
    "| Versión inicial de prueba"
)
# ======================================
# CALENDARIO
# ======================================
import pandas as pd
import datetime

st.divider()
st.header("📅 Calendario y Entrenamientos (2026 - 2027)")

# Control de acceso en la barra lateral
st.sidebar.divider()
st.sidebar.subheader("🔒 Acceso Cuerpo Técnico")
clave_introducida = st.sidebar.text_input("Contraseña de edición:", type="password")

# Comprobar si la contraseña coincide con la guardada en Secrets
es_admin = False
if clave_introducida:
    if clave_introducida == st.secrets["password_entrenador"]:
        es_admin = True
        st.sidebar.success("Modo edición activado")
    else:
        st.sidebar.error("Contraseña incorrecta")

# Cargar los datos del archivo CSV
df = pd.read_csv("calendario.csv")
df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date

# Filtros interactivos
col_filtro1, col_filtro2 = st.columns(2)

with col_filtro1:
    tipo_seleccionado = st.multiselect(
        "Filtrar por actividad:",
        options=["Entrenamiento", "Partido"],
        default=["Entrenamiento", "Partido"]
    )

with col_filtro2:
    rango_fechas = st.date_input(
        "Selecciona rango de fechas:",
        value=(datetime.date(2026, 8, 1), datetime.date(2027, 8, 31)),
        min_value=datetime.date(2026, 8, 1),
        max_value=datetime.date(2027, 8, 31)
    )

if len(rango_fechas) == 2:
    inicio, fin = rango_fechas
    mascara = (
        (df["Tipo"].isin(tipo_seleccionado)) &
        (df["Fecha"] >= inicio) &
        (df["Fecha"] <= fin)
    )
    df_filtrado = df[mascara]

    # Mostrar tabla editable SOLO si tienes la contraseña
    if es_admin:
        st.info("✏️ **Modo Entrenador:** Haz doble clic en cualquier celda para editar horas o añadir eventos.")
        
        df_editado = st.data_editor(
            df_filtrado,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["Entrenamiento", "Partido"],
                    required=True
                ),
                "Hora": st.column_config.TextColumn(
                    "Hora",
                    help="Formato HH:MM (ej. 19:30)"
                )
            }
        )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("💾 Guardar cambios en la sesión", type="primary"):
                df_editado.to_csv("calendario.csv", index=False)
                st.success("Horarios actualizados.")

        with col_btn2:
            csv_descarga = df_editado.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar CSV actualizado",
                data=csv_descarga,
                file_name="calendario.csv",
                mime="text/csv"
            )
    else:
        # Vista de solo lectura para jugadores y familias
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
else:
    st.info("Selecciona una fecha de inicio y otra de fin.")


# =============================================================
# COMUNICADOS
# =============================================================

import os

st.divider()
st.header("📢 Tablón de Comunicados (Padres y Entrenador)")

# Cargar los mensajes existentes
archivo_comunicados = "comunicados.csv"
if os.path.exists(archivo_comunicados):
    df_mensajes = pd.read_csv(archivo_comunicados)
else:
    df_mensajes = pd.DataFrame(columns=["Fecha", "Autor", "Rol", "Mensaje"])

# Formulario para escribir un nuevo mensaje
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
            st.success("¡Mensaje publicado!")
            st.rerun()

# Mostrar el historial de mensajes (los más recientes arriba)
st.subheader("Últimos mensajes")

if df_mensajes.empty:
    st.info("Aún no hay comunicados publicados.")
else:
    for indice, fila in df_mensajes.iterrows():
        # Estilo destacado si lo escribe el entrenador
        if fila["Rol"] == "Entrenador":
            with st.container(border=True):
                st.markdown(f"⚽ **{fila['Autor']} (Oficial)** · *{fila['Fecha']}*")
                st.info(fila["Mensaje"])
        else:
            with st.container(border=True):
                st.markdown(f"👤 **{fila['Autor']}** · *{fila['Fecha']}*")
                st.write(fila["Mensaje"])

# Herramientas de moderación solo para el entrenador
if es_admin and not df_mensajes.empty:
    with st.expander("🛠️ Opciones de Entrenador (Borrar o descargar mensajes)"):
        opcion_borrar = st.selectbox(
            "Selecciona un mensaje para eliminar:",
            options=df_mensajes.index,
            format_func=lambda x: f"{df_mensajes.loc[x, 'Fecha']} - {df_mensajes.loc[x, 'Autor']}: {df_mensajes.loc[x, 'Mensaje'][:40]}..."
        )
        if st.button("🗑️ Eliminar mensaje seleccionado"):
            df_mensajes = df_mensajes.drop(opcion_borrar).reset_index(drop=True)
            df_mensajes.to_csv(archivo_comunicados, index=False)
            st.success("Mensaje eliminado.")
            st.rerun()
            
        csv_chat = df_mensajes.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar copia de seguridad del tablón",
            data=csv_chat,
            file_name="comunicados.csv",
            mime="text/csv"
        )
