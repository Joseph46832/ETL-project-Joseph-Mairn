import os
import pandas as pd
import yaml

# ==========================================
# 1. FUNCION PARA LEER EL CONFIG.YAML
# ==========================================
def load_config(config_path="../../config/config.yaml"):
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: No se encontro el config.yaml en: {config_path}")
        return None

# ==========================================
# 2. FUNCION PARA EXTRAER FALTANTES
# ==========================================
def generar_diccionario_faltantes(config):
    print("--- BUSCANDO DATOS HUERFANOS EN BRONZE ---")
    
    ruta_bronze = config["sources"]["raw_airquality_data"]["path"]
    
    df = pd.read_csv(ruta_bronze)
    
    # Buscar filas donde Country es nulo
    df_sin_pais = df[df['Country'].isnull()]
    
    # Extraer las ciudades unicas y convertirlas a minusculas
    ciudades_unicas = df_sin_pais['City'].dropna().str.lower().unique()
    
    print(f"Se encontraron {len(ciudades_unicas)} ciudades unicas sin pais asignado.")
    print("Copia y pega este bloque en clean_excel.py y completa los paises pero no te preocupes profe ya esta todo pegado en el respectivo archivo:")
    
    print("mapeo_paises = {")
    for ciudad in ciudades_unicas:
        print(f'    "{ciudad}": "",')
    print("}")
    
    # Tambien buscamos si hay algun pais sin ciudad (por el nulo solitario que vimos en tu EDA)
    df_sin_ciudad = df[df['City'].isnull()]
    paises_unicos = df_sin_ciudad['Country'].dropna().unique()
    
    if len(paises_unicos) > 0:
        print(f"Ojo, se encontraron {len(paises_unicos)} registros sin Ciudad. Pertenecen a estos paises:")
        for pais in paises_unicos:
            print(f"- {pais}")

    print(f"Aqui hay un problema solo sabemos el pais que es Israel por lo que no podremos saber que lugar o ciudad es, pero aun asi puede aportar sabiendo el pais")

if __name__ == "__main__": #Eso si esto no sirve porque esto lo corro unica y solamente de manera independiente
    # Si lo corres desde la raiz del proyecto usa "config/config.yaml"
    # Si lo corres desde src/transform/ usa "../../config/config.yaml"
    config_dict = load_config(config_path="config/config.yaml") 
    
    if config_dict:
        generar_diccionario_faltantes(config_dict)

        