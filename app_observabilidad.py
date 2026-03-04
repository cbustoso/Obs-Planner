import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PESOS TÉCNICOS ---
PESOS_ACTIVOS = {
    "Datadog": {"host": 1.5, "net_device": 6.0, "apm_per_svc": 8.0, "rum_per_app": 10.0, "synthetic": 4.0},
    "Dynatrace": {"host": 0.5, "net_device": 4.0, "apm_per_svc": 3.0, "rum_per_app": 4.0, "synthetic": 3.0},
    "New Relic": {"host": 1.0, "net_device": 5.0, "apm_per_svc": 6.0, "rum_per_app": 7.0, "synthetic": 3.5},
    "SolarWinds": {"host": 2.5, "net_device": 3.0, "apm_per_svc": 12.0, "rum_per_app": 15.0, "synthetic": 5.0}
}

INTEGRACIONES = {
    "ServiceNow": 16, "Jira": 8, "PagerDuty": 6, "Teams/Slack": 4, "Alarms One": 8
}

st.set_page_config(page_title="Obs Planner Full Stack", layout="wide")

st.title("🚀 Planificador de Observabilidad: APM, RUM & Infra")

# --- SIDEBAR: ESCALA DEL PROYECTO ---
with st.sidebar:
    st.header("📊 Infraestructura y Red")
    n_hosts = st.number_input("Nº de Servidores (Agentes)", value=100)
    n_net_devices = st.number_input("Nº de Network Devices (SNMP)", value=20)
    
    st.divider()
    st.header("💻 Aplicaciones (APM & RUM)")
    n_apm_svcs = st.number_input("Nº de Microservicios (APM)", value=10, help="Esfuerzo de instrumentación de código/runtime")
    n_rum_apps = st.number_input("Nº de Aplicaciones Frontend (RUM)", value=2, help="Esfuerzo de inyección de scripts y trackeo de sesiones")
    
    st.divider()
    st.header("🧪 Validación y Contenido")
    n_synthetics = st.number_input("Nº de Tests Sintéticos", value=5)
    n_dashboards = st.number_input("Nº de Dashboards", value=5)
    
    st.divider()
    st.header("👥 Staffing")
    n_eng = st.slider("Ingenieros", 1, 10, 2)
    h_day = st.slider("Horas/Día", 1, 8, 6)

# --- NAVEGACIÓN ---
tab_resumen, tab_detalles = st.tabs(["📈 Reporte Consolidado", "⚙️ Desglose por Módulo"])

resultados = []

with tab_detalles:
    for tool in PESOS_ACTIVOS.keys():
        with st.expander(f"Configuración {tool}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔧 Servicios Proactivos**")
                h_setup = 8 if st.checkbox("Cuenta & RBAC", value=True, key=f"p_{tool}") else 0
                h_setup += 16 if st.checkbox("VPN/Network Tunneling", key=f"v_{tool}") else 0
                
                st.write("**🔗 Conectores**")
                h_ints = sum([hours for name, hours in INTEGRACIONES.items() if st.checkbox(name, key=f"i_{tool}_{name}")])
            
            with col2:
                st.write("**🛠️ Complejidad de Instrumentación**")
                opt_auto = st.checkbox("¿Usar Auto-instrumentación?", value=True, key=f"auto_{tool}")
                factor_instrumentacion = 0.6 if opt_auto else 1.0

            # --- CÁLCULO DE HORAS ---
            # Infraestructura
            h_infra = ((n_hosts/10) * PESOS_ACTIVOS[tool]["host"]) + ((n_net_devices/10) * PESOS_ACTIVOS[tool]["net_device"])
            
            # APM & RUM (El núcleo de esta actualización)
            h_apm = (n_apm_svcs * PESOS_ACTIVOS[tool]["apm_per_svc"]) * factor_instrumentacion
            h_rum = (n_rum_apps * PESOS_ACTIVOS[tool]["rum_per_app"])
            
            # Sintéticos y Contenido
            h_syn = n_synthetics * PESOS_ACTIVOS[tool]["synthetic"]
            h_content = (n_dashboards * 4)
            
            total_h = h_setup + h_infra + h_apm + h_rum + h_syn + h_content + h_ints
            dias = total_h / (n_eng * h_day)
            
            resultados.append({
                "Herramienta": tool,
                "Setup (h)": h_setup,
                "Infra (h)": round(h_infra, 1),
                "APM/RUM (h)": round(h_apm + h_rum, 1),
                "Sintéticos (h)": round(h_syn, 1),
                "Días Totales": round(dias, 1)
            })

with tab_resumen:
    df = pd.DataFrame(resultados)
    
    st.subheader("Estimación de Días por Herramienta")
    st.bar_chart(df.set_index("Herramienta")["Días Totales"])
    
    st.subheader("Matriz de Esfuerzo (Horas de Ingeniería)")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💡 Diferencias clave en APM/RUM")
    c_apm, c_rum = st.columns(2)
    
    with c_apm:
        st.write("**APM (Application Performance Monitoring)**")
        st.caption("Implica capturar trazas distribuidas, errores de código y métricas de JVM/CLR.")
        
        st.info("Dynatrace suele ser más rápido aquí gracias a su inyección automática en el proceso.")

    with c_rum:
        st.write("**RUM (Real User Monitoring)**")
        st.caption("Mide la experiencia real: Core Web Vitals, errores de JavaScript y tiempos de carga por región.")
        
        st.warning("SolarWinds requiere la configuración manual de un servidor intermedio para la recepción de trazas RUM.")

st.download_button("Exportar Plan de Trabajo", df.to_csv().encode('utf-8'), "plan_observabilidad.csv")