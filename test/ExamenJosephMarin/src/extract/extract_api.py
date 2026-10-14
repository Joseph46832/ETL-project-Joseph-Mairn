import os
import pandas as pd
import kagglehub
import yaml

# ==========================================
# 1 FUNCION PARA LEER EL CONFIG.YAML
def load_config(config_path="../../config/config.yaml"):
    """Lee el archivo YAML de configuracion."""
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: No se encontro el config.yaml en la ruta: {config_path}")
        return None

# ==========================================
# 2. FUNCION DE EXTRACCION
# ==========================================
def extraccion_desde_API(config):
    print("Iniciando extraccion desde Kaggle API")
    
    # Obtenemos la ruta de destino desde el config.yaml
    carpeta_destino = config["path"]["bronze_dir"]
    
    # Nombre del nuevo dataset de calidad del aire en Kaggle
    el_dataset = "hasibalmuzdadid/global-air-pollution-dataset"
    
    # Descargamos la ruta
    path = kagglehub.dataset_download(el_dataset)
    print(f"Dataset descargado temporalmente en: {path}")

    # Listamos los archivos descargados
    archivos = os.listdir(path)
    print(f"Archivos encontrados: {archivos}")
    
    # Buscamos el primer archivo que termine en '.csv'
    csv_file = [f for f in archivos if f.endswith('.csv')][0]
    
    # Unimos la ruta de la carpeta con el nombre del archivo para crear full_path
    full_path = os.path.join(path, csv_file)

    # Cargar usando pandas
    df = pd.read_csv(full_path)
    print(f"Extraccion exitosa. Registros cargados: {len(df)}")
    print("\nPrimeros 5 registros:")
    print(df.head())
    
    # Aseguramos que la carpeta bronze exista antes de guardar
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Guardar en la capa bronze como datos crudos (Nombre actualizado)
    output_path = os.path.join(carpeta_destino, "calidad_aire_raw.csv")

    # Guarda el DataFrame como CSV (index=False es para evitar columnas extras )
    df.to_csv(output_path, index=False)
    print(f"Datos guardados en la capa Bronze: {output_path}")
    
    # Retornamos la ruta para que main.py se la pase a la Transformacion
    return output_path

# ==========================================
# BLOQUE DE PRUEBA LOCAL
# ==========================================
if __name__ == "__main__":

    config_dict = load_config(config_path="config/config.yaml") 
    
    if config_dict:
        ruta = extraccion_desde_API(config_dict)
        print(f"Prueba finalizada. El archivo quedo en: {ruta}")