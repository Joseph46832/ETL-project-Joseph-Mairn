import os
import pandas as pd
import yaml
import pycountry_convert as pc

# ==========================================
# 1. FUNCIÓN PARA LEER EL CONFIG.YAML
# ==========================================
def load_config(config_path="../../config/config.yaml"):
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el config.yaml en: {config_path}")
        return None

# ==========================================
# 2. FUNCIÓN DE LECTURA (SILVER A MEMORIA)
# ==========================================
def cargar_datos_limpios(config):
    print("--- INICIANDO EXTRACCIÓN DESDE CAPA SILVER ---")
    if not config:
        raise ValueError("Error: Configuración vacía.")
        
    carpeta_origen = config["path"]["silver_dir"]
    if not os.path.exists(carpeta_origen) and os.path.exists("../../" + carpeta_origen):
        carpeta_origen = "../../" + carpeta_origen
        
    ruta_silver = os.path.join(carpeta_origen, "calidad_aire_limpio.csv")
    
    if not os.path.exists(ruta_silver):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_silver}")
        
    df_limpio = pd.read_csv(ruta_silver)
    print(f"Datos limpios cargados: {df_limpio.shape[0]} registros listos para agregación.")
    return df_limpio

# ==========================================
# 3. FUNCIÓN AUXILIAR PARA MAPEO DE CONTINENTES
# ==========================================
def pais_a_continente(pais):
    try:
        if pais in ["United States of America", "USA"]: return "América del Norte"
        if pais in ["United Kingdom", "England", "Scotland", "Wales"]: return "Europa"
        if pais == "Russia": return "Europa"
        if pais == "Republic of China (Taiwan)": return "Asia"
        if "Congo" in pais: return "África"
        
        codigo_pais = pc.country_name_to_country_alpha2(pais, cn_name_format="default")
        codigo_continente = pc.country_alpha2_to_continent_code(codigo_pais)
        
        diccionario = {
            'NA': 'América del Norte', 'SA': 'América del Sur', 'AS': 'Asia',
            'OC': 'Oceanía', 'EU': 'Europa', 'AF': 'África'
        }
        return diccionario.get(codigo_continente, "Otro")
    except:
        return "Otro"

# ==========================================
# 4. FUNCIÓN DE CONSTRUCCIÓN DE DATA MARTS
# ==========================================
def construir_data_marts(df, config):
    print("\n--- CONSTRUYENDO DATA MARTS (MÉTRICAS DE NEGOCIO) ---")
    
    # 1. Resumen Ejecutivo por País
    df_metricas_pais = df.groupby('country').agg(
        total_ciudades=('city', 'count'),
        aqi_promedio=('aqi_value', 'mean'),
        aqi_maximo=('aqi_value', 'max')
    ).round(2).reset_index()
    df_metricas_pais = df_metricas_pais.sort_values(by='aqi_promedio', ascending=False)
    print("1. Creada vista de métricas agregadas por país.")
    
    # 2. Matriz de Peligrosidad Categórica (Tabla Pivote)
    df_matriz_peligro = pd.crosstab(df['country'], df['aqi_category']).reset_index()
    print("2. Creada matriz de recuento por categoría de peligrosidad.")
    
    # 3. Perspectiva Macro-Continental
    df_temp = df.copy()
    df_temp['continente'] = df_temp['country'].apply(pais_a_continente)
    df_temp = df_temp[df_temp['continente'] != 'Otro']
    
    df_metricas_continente = df_temp.groupby('continente').agg(
        aqi_general_promedio=('aqi_value', 'mean'),
        pm25_promedio=('pm2.5_aqi_value', 'mean'),
        co_promedio=('co_aqi_value', 'mean'),
        ozono_promedio=('ozone_aqi_value', 'mean'),
        no2_promedio=('no2_aqi_value', 'mean')
    ).round(2).reset_index().sort_values(by='aqi_general_promedio', ascending=False)
    print("3. Creada vista macro de métricas por continente.")

    # Guardar los tres Data Marts
    carpeta_destino = config["path"]["gold_dir"]
    if not os.path.exists(carpeta_destino) and os.path.exists("../../" + carpeta_destino):
        carpeta_destino = "../../" + carpeta_destino
        
    os.makedirs(carpeta_destino, exist_ok=True)
    
    ruta_pais = os.path.join(carpeta_destino, "gold_resumen_pais.csv")
    ruta_categorias = os.path.join(carpeta_destino, "gold_matriz_peligro.csv")
    ruta_continente = os.path.join(carpeta_destino, "gold_resumen_continente.csv")
    
    df_metricas_pais.to_csv(ruta_pais, index=False)
    df_matriz_peligro.to_csv(ruta_categorias, index=False)
    df_metricas_continente.to_csv(ruta_continente, index=False)
    
    print(f"\n¡Carga exitosa! Archivos analíticos guardados en: {carpeta_destino}")
    return ruta_pais, ruta_categorias, ruta_continente

# ==========================================
# BLOQUE DE PRUEBA LOCAL
# ==========================================
if __name__ == "__main__":
    ruta_config = "../../config/config.yaml" if os.path.exists("../../config/config.yaml") else "config/config.yaml"
    
    config_dict = load_config(config_path=ruta_config) 
    
    if config_dict:
        df_silver = cargar_datos_limpios(config_dict)
        construir_data_marts(df_silver, config_dict)