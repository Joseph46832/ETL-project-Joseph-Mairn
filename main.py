import os
import logging
import yaml
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS
# ==========================================
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# ==========================================
# 2. FUNCIÓN PRINCIPAL DEL ORQUESTADOR
# ==========================================
def main():
    logging.info("=== INICIANDO PIPELINE ETL (MEDALLION ARCHITECTURE) ===")
    
    # 1. Cargar la configuración global desde config.yaml
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        logging.error(f"No se encontró el archivo de configuración en: {config_path}")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logging.info("Configuración cargada exitosamente desde config.yaml.")
    except Exception as e:
        logging.critical(f"Error crítico al leer el config.yaml: {e}")
        return

    # 2. Extracción (Capa Bronze)
    logging.info("--- ETAPA 1: EXTRACCIÓN (BRONZE) ---")
    try:
        from src.extract import extract_api as extractor
        
        # Ejecutamos la función de extracción que descarga el dataset y genera el archivo raw
        ruta_bronze = extractor.extraccion_desde_API(config)
        logging.info(f"Capa Bronze completada con éxito. Archivo raw en: {ruta_bronze}")
        
        # Leemos el dataframe crudo para pasarlo a la siguiente etapa
        df_bronze = pd.read_csv(ruta_bronze)
    except Exception as e:
        logging.error(f"Error crítico durante la etapa de extracción (Bronze): {e}")
        return

    # 3. Transformación (Capa Silver)
    logging.info("--- ETAPA 2: TRANSFORMACIÓN Y LIMPIEZA (SILVER) ---")
    try:
        from src.transform import clean_excel as limpieza
        
        ruta_silver = limpieza.limpiar_datos(df_bronze, config)
        df_silver = pd.read_csv(ruta_silver)
        logging.info(f"Capa Silver procesada exitosamente. Datos limpios en: {ruta_silver}")
    except Exception as e:
        logging.error(f"Error durante la transformación a Silver: {e}")
        return

    # 4. Carga e Integración (Capa Gold / Data Marts)
    logging.info("--- ETAPA 3: CARGA Y DATA MARTS (GOLD) ---")
    try:
        from src.transform import gold_data as integrar
        
        if hasattr(integrar, 'construir_data_marts'):
            integrar.construir_data_marts(df_silver, config)
        elif hasattr(integrar, 'integrar_datos'):
            integrar.integrar_datos(df_silver, config)
            
        logging.info("Capa Gold procesada exitosamente. Data Marts generados.")
    except Exception as e:
        logging.error(f"Error durante la generación de la capa Gold: {e}")
        return

    logging.info("=== PIPELINE ETL FINALIZADO CON ÉXITO ===")

if __name__ == "__main__":
    main()