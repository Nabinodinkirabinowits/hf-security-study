# Hugging Face Security Datasets Study

Estudio cuantitativo y cualitativo de tendencias, adopción y esquemas en los conjuntos de datos de seguridad alojados en Hugging Face.

## Estructura del Proyecto

```text
hf-security-study/
├── data/
│   ├── raw/                 # Metadatos extraídos crudos (.json / .csv)
│   ├── samples/             # Muestras ligeras de filas de datasets clave
│   └── processed/           # Tablas limpias y procesadas listas para análisis
├── notebooks/
│   ├── 01_extraccion_metadatos.ipynb   # Exploración y testing de HfApi
│   ├── 02_eda_tendencias.ipynb        # Análisis de adopción (descargas vs likes, tiempo)
│   └── 03_inspeccion_esquemas.ipynb   # Evaluación de columnas, MITRE, formatos
├── src/
│   ├── __init__.py
│   ├── extractor.py         # Extracción modular de metadatos vía HfApi
│   ├── inspector.py         # Muestreo ligero de esquemas sin clonar repos
│   ├── parser.py            # Categorización por casos de uso
│   ├── visualizer.py        # Generación de gráficos y figuras para reportes
│   └── downloader.py        # Gestor de descarga y verificación del Top 10 curado
├── reports/
│   └── figures/             # Gráficos y visualizaciones generadas
├── requirements.txt         # Dependencias Python
├── .env.example             # Configuración opcional para HF_TOKEN
└── README.md
```

## Primeros Pasos

### 1. Clonar el repositorio
```bash
git clone https://github.com/Nabinodinkirabinowits/hf-security-study.git
cd hf-security-study
```

### 2. Preparar el entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate    # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Extraer metadatos de Hugging Face
```bash
python3 -m src.extractor
```
Esto generará los archivos `data/raw/security_datasets_metadata.csv` y `data/raw/security_datasets_metadata.json`.

### 4. Clasificar y generar gráficos
```bash
python3 -m src.parser
python3 -m src.visualizer
```

### 5. Descargar los Top 10 Datasets Curados
El módulo `src/downloader.py` permite gestionar y descargar los 10 datasets imprescindibles de Ciberseguridad e IA:
```bash
# Ver información, tamaños y estado de descargas
python3 -m src.downloader --info

# Descargar los 9 datasets ligeros (< 1 GB cada uno, ~1.5 GB en total)
python3 -m src.downloader --skip-large

# Descargar todos los 10 datasets completos (~12 GB total)
python3 -m src.downloader --all

# Descargar un dataset individual por número de ranking (ej. #1)
python3 -m src.downloader --index 1
```

---

## Hallazgos Clave y Tendencias

### 1. Likes vs Adopción Real (Descargas)
Los datos demuestran que los **likes no representan el uso real en producción**. Datasets con 0 o 2 likes superan las 10,000 descargas mensuales en pipelines de entrenamiento y evaluación:

![Likes vs Descargas](reports/figures/likes_vs_downloads_correlation.png)

### 2. Dominios Más Utilizados
El ecosistema está dominado ampliamente por dos categorías: **Detección de Vulnerabilidades en Código** y **Safety / Prompt Injection**:

![Distribución por Categorías](reports/figures/categories_distribution.png)

### 3. Top Datasets Más Descargados

![Top Datasets](reports/figures/top_downloads_datasets.png)

