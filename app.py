import streamlit as st
import pandas as pd
import datetime
import json
import os

# ======================================
# 1. CONFIGURACIÓN DE LA PÁGINA (SIEMPRE ARRIBA)
# ======================================
st.set_page_config(
    page_title="Beniaján C.F. - Infantil A",
    page_icon="⚽",
    layout="wide"
)

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
# 3. ENCABEZADO SUPERIOR CON ESCUDO
# ======================================
col1, col2 = st.columns([1, 4])

with col1:
    st.image("escudo.png.png", width=100)

with col2:
    st.title("Beniaján C.F.")
    st.subheader("⚽ Infantil A · Temporada 2026/2027")

# ======================================
# 4. MENÚ LATERAL Y CONTRASEÑA
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
        <h1>⚽ BENIAJÁN C.F.</h1>
        <p>Aplicación oficial de nuestro equipo - Infantil A</p>
        <p>Temporada 2026/2027</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
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
# PLANTILLA
# ======================================
elif opcion == "Plantilla":
    st.title("👥 Plantilla de jugadores - Infantil A")

    archivo_plantilla = "plantilla.csv"
    if os.path.exists(archivo_plantilla):
        df_plantilla = pd.read_csv(archivo_plantilla)

        # Resumen rápido en 4 tarjetas métricas
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Total Jugadores", len(df_plantilla))
        col_m2.metric("Disponibles", len(df_plantilla[df_plantilla["Estado"] == "Disponible"]))
        col_m3.metric("Lesionados", len(df_plantilla[df_plantilla["Estado"] == "Lesionado"]))
        col_m4.metric("Sancionados / Baja", len(df_plantilla[df_plantilla["Estado"] == "Sancionado"]))

        st.divider()

        # Filtro por posición
        posiciones = ["Todas", "Portero", "Defensa", "Centrocampista", "Delantero"]
        filtro_pos = st.selectbox("Filtrar por demarcación:", posiciones)

        if filtro_pos != "Todas":
            df_vista = df_plantilla[df_plantilla["Posicion"] == filtro_pos]
        else:
            df_vista = df_plantilla

        # Modo edición si tienes la contraseña activada
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
                        options=["Portero", "Defensa", "Centrocampista", "Delantero"],
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
                    st.success("Plantilla actualizada correctamente.")
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
            # Vista visual por tarjetas agrupadas para familias y jugadores
            for _, jugador in df_vista.iterrows():
                icono_estado = "🟢" if jugador["Estado"] == "Disponible" else ("🔴" if jugador["Estado"] == "Lesionado" else "🟡")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 4, 2])
                    c1.markdown(f"### #{jugador['Dorsal']}")
                    c2.markdown(f"**{jugador['Nombre']}**\n\n*{jugador['Posicion']}*")
                    c3.markdown(f"{icono_estado} {jugador['Estado']}")
    else:
        st.warning("No se encontró el archivo plantilla.csv en el repositorio.")


# ======================================
# SECCIÓN: CALENDARIO
# ======================================
elif opcion == "Calendario":
    st.title("📅 Calendario deportivo (2026 - 2027)")

    if os.path.exists("calendario.csv"):
        df = pd.read_csv("calendario.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date

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
                st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        else:
            st.info("Selecciona una fecha de inicio y otra de fin.")
    else:
        st.warning("No se encontró el archivo calendario.csv.")

# ======================================
# SECCIÓN: CONVOCATORIAS
# ======================================
elif opcion == "Convocatorias":
    st.title("📋 Convocatorias y Asistencia")

    archivo_conv = "convocatoria_actual.json"
    archivo_plantilla = "plantilla.csv"

    # Cargar datos de convocatoria si ya existe
    datos_conv = {
        "partido": "Próximo Partido Oficial",
        "notas": "Traer primera equipación (verde) y botella de agua.",
        "convocados": []
    }
    if os.path.exists(archivo_conv):
        with open(archivo_conv, "r", encoding="utf-8") as f:
            datos_conv = json.load(f)

    # ==========================================
    # PANEL DEL ENTRENADOR (SELECCIÓN DE LISTA)
    # ==========================================
    if es_admin:
        with st.expander("✏️ Configurar nueva convocatoria (Solo Entrenador)", expanded=True):
            if os.path.exists(archivo_plantilla):
                df_pl = pd.read_csv(archivo_plantilla)
                # Filtrar solo los jugadores disponibles
                df_disp = df_pl[df_pl["Estado"] == "Disponible"]
                opciones_jugadores = [
                    f"#{fila['Dorsal']} - {fila['Nombre']} ({fila['Posicion']})"
                    for _, fila in df_disp.iterrows()
                ]

                # Recuperar los ya marcados previamente si siguen disponibles
                nombres_previos = [c["jugador"] for c in datos_conv["convocados"] if c["jugador"] in opciones_jugadores]

                with st.form("form_convocatoria"):
                    titulo_partido = st.text_input("Título del partido / Jornada:", value=datos_conv["partido"])
                    notas_partido = st.text_area("Indicaciones (equipación, punto de encuentro...):", value=datos_conv["notas"])
                    seleccionados = st.multiselect(
                        f"Selecciona los jugadores convocados ({len(opciones_jugadores)} disponibles):",
                        options=opciones_jugadores,
                        default=nombres_previos
                    )

                    if st.form_submit_button("📢 Publicar Convocatoria Oficial", type="primary"):
                        # Conservar el estado de confirmación si el jugador ya estaba en la lista
                        estados_previos = {c["jugador"]: c["estado"] for c in datos_conv["convocados"]}
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
                        st.success("¡Convocatoria publicada correctamente!")
                        st.rerun()
            else:
                st.warning("Primero debes crear el archivo plantilla.csv para elegir jugadores.")

    # ==========================================
    # VISTA PÚBLICA Y CONFIRMACIÓN DE FAMILIAS
    # ==========================================
    if not datos_conv["convocados"]:
        st.info("Todavía no se ha publicado la convocatoria para el próximo partido.")
    else:
        st.subheader(f"🏆 {datos_conv['partido']}")
        st.info(f"📌 **Notas del cuerpo técnico:** {datos_conv['notas']}")

        # Contadores de asistencia
        total_conv = len(datos_conv["convocados"])
        confirmados = sum(1 for c in datos_conv["convocados"] if c["estado"] == "✅ Confirmado")
        pendientes = sum(1 for c in datos_conv["convocados"] if c["estado"] == "⏳ Pendiente")
        bajas = sum(1 for c in datos_conv["convocados"] if c["estado"] == "❌ No puede asistir")

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Convocados", total_conv)
        c_m2.metric("Confirmados", confirmados)
        c_m3.metric("Pendientes", pendientes)
        c_m4.metric("Bajas avisadas", bajas)

        st.divider()

        # Formulario rápido para que padres/jugadores confirmen
        with st.container(border=True):
            st.markdown("### 🙋‍♂️ Confirmar asistencia del jugador")
            lista_nombres = [c["jugador"] for c in datos_conv["convocados"]]
            
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
                    st.success(f"Estado actualizado para {jugador_elegido}")
                    st.rerun()

        # Listado visual de todos los convocados y su estado
        st.subheader("Lista oficial de convocados")
        for item in datos_conv["convocados"]:
            with st.container(border=True):
                col_j1, col_j2 = st.columns([3, 1])
                col_j1.markdown(f"**{item['jugador']}**")
                col_j2.markdown(f"**{item['estado']}**")

# ======================================
# SECCIÓN: COMUNICADOS
# ======================================

elif opcion == "Comunicados":
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
                st.success("¡Mensaje publicado!")
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
elif opcion == "Galería":
    st.title("📸 Galería de fotografías - Infantil A")

    carpeta_fotos = "galeria_fotos"
    archivo_registro = "galeria_datos.json"

    # Crear carpeta para guardar las imágenes si no existe
    if not os.path.exists(carpeta_fotos):
        os.makedirs(carpeta_fotos)

    # Cargar registro de títulos y autores de las fotos
    lista_fotos = []
    if os.path.exists(archivo_registro):
        with open(archivo_registro, "r", encoding="utf-8") as f:
            lista_fotos = json.load(f)

    # ==========================================
    # SUBIDA DE NUEVAS FOTOS (PADRES Y ENTRENADOR)
    # ==========================================
    with st.expander("📤 Subir una nueva foto del equipo", expanded=False):
        with st.form("form_subir_foto", clear_on_submit=True):
            archivo_subido = st.file_uploader("Selecciona una imagen (JPG o PNG):", type=["jpg", "jpeg", "png"])
            titulo_foto = st.text_input("Título o jornada (ej. Victoria vs Murcia C.F. - Jornada 3):")
            autor_foto = st.text_input("Subida por:", value="Entrenador" if es_admin else "")

            if st.form_submit_button("🖼️ Publicar en la galería", type="primary"):
                if archivo_subido is None:
                    st.warning("Por favor, selecciona primero una fotografía.")
                elif titulo_foto.strip() == "":
                    st.warning("Escribe un breve título para identificar la foto.")
                else:
                    # Generar nombre único con fecha y hora para no sobrescribir
                    marca_tiempo = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"{marca_tiempo}_{archivo_subido.name}"
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

                    st.success("¡Fotografía subida correctamente!")
                    st.rerun()

    st.divider()

    # ==========================================
    # MURO DE FOTOGRAFÍAS EN CUADRÍCULA
    # ==========================================
    if not lista_fotos:
        st.info("Aún no hay fotografías en el álbum. ¡Sé el primero en subir una desde el botón de arriba!")
    else:
        # Mostrar en filas de 3 columnas
        columnas = st.columns(3)
        for indice, foto in enumerate(lista_fotos):
            ruta_img = os.path.join(carpeta_fotos, foto["archivo"])
            if os.path.exists(ruta_img):
                with columnas[indice % 3]:
                    with st.container(border=True):
                        st.image(ruta_img, use_container_width=True)
                        st.markdown(f"**{foto['titulo']}**")
                        st.caption(f"📷 {foto['autor']} · 📅 {foto['fecha']}")

                        # Botón de borrado solo visible para el entrenador
                        if es_admin:
                            if st.button("🗑️ Eliminar", key=f"del_foto_{indice}"):
                                if os.path.exists(ruta_img):
                                    os.remove(ruta_img)
                                lista_fotos.pop(indice)
                                with open(archivo_registro, "w", encoding="utf-8") as f:
                                    json.dump(lista_fotos, f, ensure_ascii=False, indent=4)
                                st.success("Foto eliminada.")
                                st.rerun()

