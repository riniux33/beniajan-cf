
import streamlit as st

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
