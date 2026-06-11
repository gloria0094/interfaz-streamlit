import streamlit as st
import plotly.graph_objects as go
import requests

# CONFIGURACIÓN INICIAL DE LA INTERFAZ
st.set_page_config(page_title="Clasificador de Exoplanetas", layout="wide")

# Inicializar variables en el estado de la sesión si no existen
if 'probabilidad_exoplaneta' not in st.session_state:
    st.session_state.probabilidad_exoplaneta = 0.0
if 'veredicto_ia' not in st.session_state:
    st.session_state.veredicto_ia = "PENDIENTE DE ANÁLISIS"

#Limpiar interfaz
def limpiar_interfaz():
    st.session_state.probabilidad_exoplaneta = 0.0
    st.session_state.veredicto_ia = "PENDIENTE DE ANÁLISIS"
    # Esto le dice a Streamlit que borre los datos guardados en el formulario de abajo
    if "entity_inputs" in st.session_state:
        st.session_state.entity_inputs = {}

# Estilo para mantener la estética de tu diseño oscuro original
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, span, label, p { color: white !important; }
    .stButton>button {
        background-color: #00acee;
        color: white;
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #0084b4;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🪐 Clasificador de Exoplanetas Kepler")

# Separación en dos grandes columnas
col1, col2 = st.columns([1, 1.4], gap="large")

# COLUMNA 1: EL MEDIDOR (GAUGE)
with col1:
    st.subheader("Resultado de Clasificación")

    prob_porcentaje = st.session_state.probabilidad_exoplaneta
    veredicto = st.session_state.veredicto_ia

    if veredicto == "CONFIRMADO":
        color_estado = "#22c55e"
    elif veredicto == "CANDIDATO":
        color_estado = "#00acee"
    elif veredicto == "FALSO POSITIVO":
        color_estado = "#ef4444"
    else:
        color_estado = "#94a3b8"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob_porcentaje,
        number = {'suffix': "%", 'font': {'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#B19CD9"},
            'bgcolor': "#1e293b",
            'steps': [
                {'range': [0, 50], 'color': "#f08282"},
                {'range': [50, 75], 'color': "#59bde5"},
                {'range': [75, 100], 'color': "#8ad4a5"}
            ]
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=320
    )

    # Se eliminó el parámetro obsoleto 'use_container_width' que te llenaba la consola de advertencias
    st.plotly_chart(fig, width="stretch")
    st.markdown(f"<center><h3>Estado: <span style='color:{color_estado};'>{veredicto}</span></h3></center>", unsafe_allow_html=True)
    st.info("Nota: Este valor representa la probabilidad de que el objeto sea un Exoplaneta.")
    # Botón para limpiar pantalla
    st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco
    if st.button("🧹 Limpiar Campos y Volver a Clasificar", use_container_width=True):
        limpiar_interfaz()
        st.rerun()

# Lista para guardar los nombres de los campos que queden vacíos
campos_vacios = []

# COLUMNA 2: FORMULARIO ADAPTADO Al ENTITY DE JAVA
with col2:
    st.subheader("Datos Técnicos")
    st.write("Completa los parámetros requeridos para la clasificación")

    with st.form("entity_inputs"):

        # Organizamos los campos en Pestañas (Tabs) para que se vea ordenado y quepan las 32 variables
        tab1, tab2, tab3, tab4 = st.tabs(["Banderas (Flags)", "Datos de Tránsito", "Datos Estelares", "Coordenadas"])

        with tab1:
            st.caption("Falsos Positivos Potenciales")
            c1, c2 = st.columns(2)
            koi_fpflag_nt = c1.toggle("Flag No Transit-Like (nt)", value=0)
            koi_fpflag_ss = c2.toggle("Flag Stellar Co-Passenger (ss)", value=0)

            c3, c4 = st.columns(2)
            koi_fpflag_co = c3.toggle("Flag Centroid Offset (co)", value=0)
            koi_fpflag_ec = c4.toggle("Flag Ephemeris Match (ec)", value=0)

        with tab2:
            st.caption("Parámetros de la curva de luz y tránsitos")
            t_c1, t_c2 = st.columns(2)
            if st.session_state.get("input_period") is None and "input_period" in st.session_state:
                label_period = "Período Orbital (koi_period) :red[*]"
                campos_vacios.append("Período Orbital (koi_period)")
            else:
                label_period = "Período Orbital (koi_period)"
            koi_period = t_c1.number_input(label_period, value=None, format="%.6f",placeholder="Ej: 51.07926", key="input_period")

            if st.session_state.get("input_ruido") is None and "input_ruido" in st.session_state:
                label_ruido = "Relación Señal/Ruido (koi_model_snr) :red[*]"
                campos_vacios.append("Relación Señal/Ruido (koi_model_snr)")
            else:
                label_ruido = "Relación Señal/Ruido (koi_model_snr)"
            koi_model_snr = t_c2.number_input(label_ruido, value=None, format="%.2f", placeholder="Ej: 126.8", key="input_ruido")

            t_c3, t_c4 = st.columns(2)
            if st.session_state.get("input_0bk") is None and "input_0bk" in st.session_state:
                label_time = "Época de Tránsito (koi_time0bk) :red[*]"
                campos_vacios.append("Época de Tránsito (koi_time0bk)")
            else:
                label_time = "Época de Tránsito (koi_time0bk)"
            koi_time0bk = t_c3.number_input(label_time, value=None, format="%.6f", placeholder="Ej: 185.18087", key="input_time0bk")

            if st.session_state.get("input_duration") is None and "input_duration" in st.session_state:
                label_duration = "Duración Tránsito (koi_duration) :red[*]"
                campos_vacios.append("Duración Tránsito (koi_duration)")
            else:
                label_duration = "Duración Tránsito (koi_duration)"
            koi_duration = t_c4.number_input(label_duration, value=None,format="%.5f", placeholder="Ej: 6.3729", key="input_duration")

            # Errores asociados
            with st.expander("Ver Errores de Medición de Tránsito"):
                e1, e2 = st.columns(2)
                if st.session_state.get("input_time01") is None and "input_time01" in st.session_state:
                    label_time01 = "koi_time0bk_err1 :red[*]"
                    campos_vacios.append("koi_time0bk_err1")
                else:
                    label_time01 = "koi_time0bk_err1"
                koi_time0bk_err1 = e1.number_input(label_time01,value=None, format="%.7f", placeholder="Ej: 0.000981", key="input_time01")

                if st.session_state.get("input_time02") is None and "input_time02" in st.session_state:
                    label_time02= "koi_time0bk_err2 :red[*]"
                    campos_vacios.append("koi_time0bk_err2")
                else:
                    label_time02 = "koi_time0bk_err2"
                koi_time0bk_err2 = e2.number_input(label_time02, value=None, format="%.3f", placeholder="0.0", key="input_time02")

                e3, e4 = st.columns(2)
                if st.session_state.get("input_duration01") is None and "input_duration01" in st.session_state:
                    label_duration01 = "koi_duration_err1 :red[*]"
                    campos_vacios.append("koi_duration_err1")
                else:
                    label_duration01 = "koi_duration_err1"
                koi_duration_err1 = e3.number_input(label_duration01, value=None,format="%.5f", placeholder="Ej:0.0312", key="input_duration01")

                if st.session_state.get("input_duration02") is None and "input_duration02" in st.session_state:
                    label_duration02 = "koi_duration_err2 :red[*]"
                    campos_vacios.append("koi_duration_err2")
                else:
                    label_duration02 = "koi_duration_err2"
                koi_duration_err2 = e4.number_input(label_duration02, value=None,format="%.5f", placeholder="Ej:-0.0312", key="input_duration02")

        with tab3:
            st.caption("Física del Planeta Candidato y su Estrella")
            p_c1, p_c2 = st.columns(2)
            if st.session_state.get("input_prad") is None and "input_prad" in st.session_state:
                label_prad ="Radio Planetario (koi_prad)"
                campos_vacios.append("Radio Planetario (koi_prad)")
            else:
                label_prad = "Radio Planetario (koi_prad)"
            koi_prad = p_c1.number_input(label_prad, value=None,format="%.2f", placeholder="Ej:2.75", key="input_prad")

            if st.session_state.get("input_teq") is None and "input_teq" in st.session_state:
                label_teq ="Temp. Equilibrio (koi_teq)"
                campos_vacios.append("Temp. Equilibrio (koi_teq)")
            else:
                label_teq = "Temp. Equilibrio (koi_teq)"
            koi_teq = p_c2.number_input(label_teq, value=None, step=1, placeholder="Ej:503", key="input_teq")

            p_c3, p_c4 = st.columns(2)
            if st.session_state.get("input_depth") and "input_depth" in st.session_state:
                label_depth = "Profundidad de Tránsito (koi_depth)"
                campos_vacios.append("Profundidad de Tránsito (koi_depth)")
            else:
                label_depth = "Profundidad de Tránsito (koi_depth)"
            koi_depth = p_c3.number_input(label_depth, value=None,format="%.1f", placeholder="Ej:736.8", key="input_depth")

            if st.session_state.get("input_insol") and "input_insol" in st.session_state:
                label_insol= "Insolación (koi_insol)"
                campos_vacios.append("Insolación (koi_insol)")
            else:
                label_insol = "Insolación (koi_insol)"
            koi_insol = p_c4.number_input(label_insol, value=None,format="%.2f",placeholder="Ej:15.17", key="input_insol")

            p_c5, p_c6 = st.columns(2)#--------------------------------------------------------------
            if st.session_state.get("input_impact") and "input_impact" in st.session_state:
                label_impact= "Parámetro de Impacto (koi_impact)"
                campos_vacios.append("Parámetro de Impacto (koi_impact)")
            else:
                label_impact = "Parámetro de Impacto (koi_impact)"
            koi_impact = p_c5.number_input(label_impact, value=None,format="%.3f", placeholder="Ej:0.017", key="input_impact")

            if st.session_state.get("input_plnt_num") and "input_plnt_num" in st.session_state:
                label_plnt_num= "Número TCE Planet (koi_tce_plnt_num)"
                campos_vacios.append("Número TCE Planet (koi_tce_plnt_num)")
            else:
                label_plnt_num = "Número TCE Planet (koi_tce_plnt_num)"
            koi_tce_plnt_num = p_c6.number_input(label_plnt_num, value=None, step=1, placeholder="Ej: 1", key="input_plnt_num")

            p_c7, p_c8 = st.columns(2)
            if st.session_state.get("input_steff") and "input_steff" in st.session_state:
                label_steff= "Temp. Efectiva Estelar (koi_steff)"
                campos_vacios.append("Temp. Efectiva Estelar (koi_steff)")
            else:
                label_steff ="Temp. Efectiva Estelar (koi_steff)"
            koi_steff = p_c7.number_input(label_steff, value=None, step=1, placeholder="Ej:5833", key="input_steff")#-----------

            if st.session_state.get("input_slogg") and "input_slogg" in st.session_state:
                label_slogg= "Gravedad Estelar (koi_slogg)"
                campos_vacios.append("Gravedad Estelar (koi_slogg)")
            else:
                label_slogg = "Gravedad Estelar (koi_slogg)"
            koi_slogg = p_c8.number_input(label_slogg, value=None, format="%.3f", placeholder="Ej: 4.407", key="input_slogg")

            with st.expander("Ver Errores de Medición Física"):
                ex1, ex2 = st.columns(2)
                if st.session_state.get("input_impact01") and "input_impact01" in st.session_state:
                    label_impact01= "koi_impact_err1"
                    campos_vacios.append("koi_impact_err1")
                else:
                    label_impact01 = "koi_impact_err1"
                koi_impact_err1 = ex1.number_input(label_impact01, value=None, format="%.3f", placeholder="Ej:0.267", key="input_impact01")

                if st.session_state.get("input_impact02") and "input_impact02" in st.session_state:
                    label_impact02= "koi_impact_err2"
                    campos_vacios.append("koi_impact_err2")
                else:
                    label_impact02 = "koi_impact_err2"
                koi_impact_err2 = ex2.number_input(label_impact02, value=None, format="%.3f", placeholder="Ej. -0.017", key="input_impact02")

                ex3, ex4 = st.columns(2)
                if st.session_state.get("input_depth01") and "input_depth01" in st.session_state:
                    label_depth01= "koi_depth_err1"
                    campos_vacios.append("koi_depth_err1")
                else:
                    label_depth01 = "koi_depth_err1"
                koi_depth_err1 = ex3.number_input(label_depth01, value=None,format="%.1f", placeholder="Ej:6", key="input_depth01")

                if st.session_state.get("input_depth02") and "input_depth02" in st.session_state:
                    label_depth02= "koi_depth_err2"
                    campos_vacios.append("koi_depth_err2")
                else:
                    label_depth02 = "koi_depth_err2"
                koi_depth_err2 = ex4.number_input(label_depth02, value=None,format="%.1f", placeholder="Ej: -6", key="input_depth02")

                ex5, ex6 = st.columns(2)
                if st.session_state.get("input_prad02") and "input_prad02" in st.session_state:
                    label_prad02= "koi_prad_err2"
                    campos_vacios.append("koi_prad_err2")
                else:
                    label_prad02 = "koi_prad_err2"
                koi_prad_err2 = ex5.number_input(label_prad02, value=None,format="%.2f", placeholder="Ej:-0.28", key="input_prad02")

                if st.session_state.get("input_insol02") and "input_insol02" in st.session_state:
                    label_insol02= "koi_insol_err2"
                    campos_vacios.append("koi_insol_err2")
                else:
                    label_insol02 = "koi_insol_err2"
                koi_insol_err2 = ex6.number_input("koi_insol_err2", value=None,format="%.2f", placeholder="Ej:-3.96", key="input_insol02")

                ex7, ex8 = st.columns(2)
                if st.session_state.get("input_steff01") and "input_steff01" in st.session_state:
                    label_steff01= "koi_steff_err1"
                    campos_vacios.append("koi_steff_err1")
                else:
                    label_steff01 = "koi_steff_err1"
                koi_steff_err1 = ex7.number_input(label_steff01, value=None, step=1, placeholder="Ej: 105", key="input_steff01")

                if st.session_state.get("input_slogg02") and "input_slogg02" in st.session_state:
                    label_slogg02= "koi_slogg_err2"
                    campos_vacios.append("koi_slogg_err2")
                else:
                    label_slogg02 = "koi_slogg_err2"
                koi_slogg_err2 = ex8.number_input(label_slogg02, value=None, format="%.3f", placeholder="Ej:-0.114", key="input_slogg02")

                ex9 = st.columns(1)[0]
                if st.session_state.get("input_srad01") and "input_srad01" in st.session_state:
                    label_srad01= "koi_srad_err1"
                    campos_vacios.append("koi_srad_err1")
                else:
                    label_srad01 = "koi_srad_err1"
                koi_srad_err1 = ex9.number_input(label_srad01, value=None, format="%.3f", placeholder="Ej: 0.143", key="input_srad01")

        with tab4:
            st.caption("Identificación de Localización Estelar")
            g_c1, g_c2 = st.columns(2)
            if st.session_state.get("input_ra") and "input_ra" in st.session_state:
                label_ra= "Ascensión Recta (ra)"
                campos_vacios.append("Ascensión Recta (ra)")
            else:
                label_ra = "Ascensión Recta (ra)"
            ra = g_c1.number_input(label_ra, value=None, format="%.5f", placeholder="Ej: 295.64871", key="input_ra")

            if st.session_state.get("input_dec") and "input_dec" in st.session_state:
                label_dec= "Declinación (dec)"
                campos_vacios.append("Declinación (dec)")
            else:
                label_dec = "Declinación (dec)"
            dec_val = g_c2.number_input(label_dec, value=None, format="%.6f", placeholder="Ej: 48.49556", key="input_dec")

            g_c3 = st.columns(1)[0]
            if st.session_state.get("input_kepmag") and "input_kepmag" in st.session_state:
                label_kepmag= "Magnitud Kepler (koi_kepmag)"
                campos_vacios.append("Magnitud Kepler (koi_kepmag)")
            else:
                label_kepmag = "Magnitud Kepler (koi_kepmag)"
            koi_kepmag = g_c3.number_input(label_kepmag, value=None, format="%.4f", placeholder="Ej:12.772", key="input_kepmag")

        # Si la lista contiene elementos, significa que hay campos vacíos
        if campos_vacios:
            st.warning(f"⚠️ Nota: Los campos con :red[*] están vacíos. Se procesarán como 0.0 para no interrumpir la clasificación.")
        # Botón de ejecución
        submit_btn = st.form_submit_button("Ejecutar Clasificación")

    # para evitar que Streamlit limpie el session_state al recargar la página.
    if submit_btn:
        payload = {
            "koi_fpflag_nt": int(koi_fpflag_nt),
            "koi_fpflag_ss": int(koi_fpflag_ss),
            "koi_fpflag_co": int(koi_fpflag_co),
            "koi_fpflag_ec": int(koi_fpflag_ec),
            "koi_period": float(koi_period) if koi_period is not None else 0.0,
            "koi_time0bk": float(koi_time0bk) if koi_time0bk is not None else 0.0,
            "koi_time0bk_err1": float(koi_time0bk_err1) if koi_time0bk_err1 is not None else 0.0,
            "koi_time0bk_err2": float(koi_time0bk_err2) if koi_time0bk_err2 is not None else 0.0,
            "koi_impact": float(koi_impact) if koi_impact is not None else 0.0,
            "koi_impact_err1": float(koi_impact_err1) if koi_impact_err1 is not None else 0.0,
            "koi_impact_err2": float(koi_impact_err2) if koi_impact_err2 is not None else 0.0,
            "koi_duration": float(koi_duration) if koi_duration is not None else 0.0,
            "koi_duration_err1": float(koi_duration_err1) if koi_duration_err1 is not None else 0.0,
            "koi_duration_err2": float(koi_duration_err2) if koi_duration_err2 is not None else 0.0,
            "koi_depth": float(koi_depth) if koi_depth is not None else 0.0,
            "koi_depth_err1": float(koi_depth_err1) if koi_depth_err1 is not None else 0.0,
            "koi_depth_err2": float(koi_depth_err2) if koi_depth_err2 is not None else 0.0,
            "koi_prad": float(koi_prad) if koi_prad is not None else 0.0,
            "koi_prad_err2": float(koi_prad_err2) if koi_prad_err2 is not None else 0.0,
            "koi_teq": float(koi_teq) if koi_teq is not None else 0.0,
            "koi_insol": float(koi_insol) if koi_insol is not None else 0.0,
            "koi_insol_err2": float(koi_insol_err2) if koi_insol_err2 is not None else 0.0,
            "koi_model_snr": float(koi_model_snr) if koi_model_snr is not None else 0.0,
            "koi_tce_plnt_num": int(koi_tce_plnt_num) if koi_tce_plnt_num is not None else 0.0,
            "koi_steff": float(koi_steff) if koi_steff is not None else 0.0,
            "koi_steff_err1": float(koi_steff_err1) if koi_steff_err1 is not None else 0.0,
            "koi_slogg": float(koi_slogg) if koi_slogg is not None else 0.0,
            "koi_slogg_err2": float(koi_slogg_err2) if koi_slogg_err2 is not None else 0.0,
            "koi_srad_err1": float(koi_srad_err1) if koi_srad_err1 is not None else 0.0,
            "ra": float(ra) if ra is not None else 0.0,
            "dec": float(dec_val) if dec_val is not None else 0.0,
            "koi_kepmag": float(koi_kepmag) if koi_kepmag is not None else 0.0,
        }

        url_spring = "http://esoplanet01-production.up.railway.app/api/v1/exoplanets/classify"
        
        with st.spinner("Enviando datos..."):
            try:
                response = requests.post(url_spring, json=payload)

                if response.status_code == 200:
                    resultado = response.json()

                    # Guardamos los resultados de forma persistente
                    st.session_state.probabilidad_exoplaneta = float(resultado.get("probability", 0.0))

                    clase = resultado.get("prediction")
                    # Sincronizado: 0 es Candidato/Rechazado y 1 es Confirmado en tu IA Binaria
                    etiquetas = {0: "CANDIDATO", 1: "CONFIRMADO", 2: "FALSO POSITIVO"}
                    st.session_state.veredicto_ia = etiquetas.get(int(clase), "DESCONOCIDO")

                    st.toast("¡Predicción procesada con éxito!", icon="🚀")
                    st.rerun()
                else:
                    st.error(f"Error en el mapeo de Spring Boot ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"No se pudo establecer contacto con la API en Java: {e}")
