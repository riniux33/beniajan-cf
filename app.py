import streamlit as st

col1, col2 = st.columns([1, 4])

with col1:
    st.image("escudo.png.png", width=100)

with col2:
    st.title("Beniaján C.F.")

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

    # Próximo partido: datos de demostración
    st.markdown("""
    <div class="match">
        <h3>🏆 PRÓXIMO PARTIDO</h3>
        <h2>BENIAJÁN C.F. - EQUIPO RIVAL</h2>
        <p>📅 Sábado | 10:00 horas</p>
        <p>📍 Campo de fútbol</p>
        <p>⏰ Hora de citación: 09:15 horas</p>
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
