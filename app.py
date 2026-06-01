import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Analizador Inmobiliario", layout="wide")

st.title("📊 Simulador Inmobiliario + Inteligencia Demográfica (INE)")
st.write("Introduce los datos del inmueble para evaluar su viabilidad financiera y el riesgo de la zona.")

@st.cache_data
def cargar_datos_ine():
    # Lee el CSV que has subido a tu propio repositorio
    return pd.read_csv("datos_ine.csv")

df_ine = cargar_datos_ine()

col_inputs, col_resultados = st.columns([1, 2])

with col_inputs:
    st.header("🏠 Datos del Inmueble")
    direccion = st.text_input("Municipio a analizar (Ej: Igualada o Abrera):", value="Igualada")
    precio_compra = st.number_input("Precio de compra (€):", min_value=0, value=150000, step=5000)
    gastos_reforma = st.number_input("Gastos de reforma/notaría (€):", min_value=0, value=20000, step=1000)
    alquiler_mensual = st.number_input("Alquiler mensual estimado (€):", min_value=0, value=750, step=50)
    
    st.markdown("---")
    st.header("⚙️ Gastos Operativos Anuales")
    ibi_comunidad = st.number_input("IBI + Comunidad anual (€):", min_value=0, value=1200)
    seguros_otros = st.number_input("Seguros y mantenimiento anual (€):", min_value=0, value=600)

with col_resultados:
    st.header("📈 Análisis de Rentabilidad y Entorno")
    
    inversion_total = precio_compra + gastos_reforma
    ingresos_anuales = alquiler_mensual * 12
    gastos_anuales = ibi_comunidad + seguros_otros
    flujo_caja_neto_anual = ingresos_anuales - gastos_anuales
    
    rentabilidad_bruta = (ingresos_anuales / precio_compra) * 100 if precio_compra > 0 else 0
    rentabilidad_neta = (flujo_caja_neto_anual / inversion_total) * 100 if inversion_total > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Inversión Total", f"{inversion_total:,} €")
    kpi2.metric("Rentabilidad Bruta", f"{rentabilidad_bruta:.2f} %")
    kpi3.metric("Rentabilidad Neta", f"{rentabilidad_neta:.2f} %")
    
    geolocator = Nominatim(user_agent="proptech_analyzer_app_carlos")
    
    try:
        # Buscamos la localidad en el mapa
        location = geolocator.geocode(direccion + ", Barcelona, Spain", timeout=10)
        if location:
            st.subheader("📍 Ubicación y Análisis Socioeconómico")
            
            # Buscamos el municipio en tu CSV mapeado
            info_zona = df_ine[df_ine['municipio'].str.contains(direccion.strip(), case=False, na=False)]
            
            if not info_zona.empty:
                # Sacamos las medias del municipio basándonos en tus datos limpios
                renta_media = info_zona['renta_hogar'].mean()
                vuln_media = info_zona['pct_vulnerabilidad_extranjera'].mean()
                
                if vuln_media > 15:
                    riesgo_status = "🔴 ALTO (Revisar histórico de impagos en la zona)"
                elif vuln_media > 8:
                    riesgo_status = "🟡 MEDIO"
                else:
                    riesgo_status = "🟢 BAJO (Zona socioeconómicamente muy estable)"
                
                res1, res2 = st.columns(2)
                res1.markdown(f"**Renta Media Hogar en municipio:** {renta_media:,.0f} €")
                res2.markdown(f"**Score de Riesgo de Impago:** {riesgo_status}")
                res1.markdown(f"**Tasa de Vulnerabilidad Económica:** {vuln_media:.2f}%")
            else:
                st.info("Municipio localizado en el mapa, pero no coincide con la base de datos local de Barcelona.")
            
            m = folium.Map(location=[location.latitude, location.longitude], zoom_start=14)
            folium.Marker([location.latitude, location.longitude], popup=direccion).add_to(m)
            st_folium(m, width=700, height=300, key="mapa_mvp")
        else:
            st.warning("Introduce un municipio válido de la provincia de Barcelona.")
    except Exception as e:
        st.error(f"Error en la consulta de datos: {e}")
