import os
import pandas as pd
import yaml
ruta_bronze = "data/bronze/calidad_aire_raw.csv"
# ==========================================
# 1. FUNCION PARA LEER EL CONFIG.YAML
# ==========================================
def load_config(config_path="../../config/config.yaml"):
    """Lee el archivo YAML de configuracion."""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: No se encontro el config.yaml en la ruta: {config_path}")
        return None

# ==========================================
# 2. FUNCION DE CARGA (BRONZE A MEMORIA)
# ==========================================
def cargar_datos_csv(config):

    print("Iniciando la carga de datos crudos (capa bronze)")
    if not config:
        raise ValueError("Error: Configuracion vacia.")
        
    ruta_bronze = config["sources"]["raw_airquality_data"]["path"]
    
    if not os.path.exists(ruta_bronze):
        raise FileNotFoundError(f"No se encontro el archivo Bronze: {ruta_bronze}")
        
    df = pd.read_csv(ruta_bronze)
    print(f"¡Carga exitosa! {len(df)} registros leidos.")
    return df


# ==========================================
# BLOQUE DE PRUEBA LOCAL
# ==========================================
if __name__ == "__main__":
    # Ajusta la ruta para pruebas locales
    config_dict = load_config(config_path="config/config.yaml") 
    
    if config_dict:
        # 1. Cargamos los datos crudos a una variable local
        df_raw = cargar_datos_csv(config_dict)

