# EDA de los datasets del Top 10

Una carpeta por dataset. Todo lo que se genera para un dataset (gráficos, tablas, conclusiones)
queda dentro de su carpeta.

```text
eda/
├── 00_general/                 # comparación entre los 10 (ejecutar al final)
├── 01_jailbreak_classification/
│   ├── eda.ipynb               # carga, muestra y explora el dataset
│   ├── figures/                # gráficos que guarda el notebook (save_fig)
│   ├── tables/                 # tablas que guarda el notebook (save_table)
│   │   ├── perfil_columnas.csv
│   │   └── resumen.csv         # una fila; la usa 00_general
│   └── README.md               # hallazgos y conclusiones (a completar)
├── ...
└── 10_nist_cybersecurity/
```

## Cómo se usa

1. Activa el entorno virtual del repo (`.venv`) e instala `requirements.txt`.
2. Abre cualquier `eda.ipynb` (Jupyter o VS Code) y ejecuta todo. El notebook encuentra solo la raíz
   del repo y lee los datos desde `data/raw/top10_security/`; **los datos no se copian aquí**.
3. Las funciones comunes (cargar, perfilar, guardar) están en `src/profiler.py`.

## Datasets grandes

Los notebooks 04, 05, 06, 07 y 10 trabajan con una **muestra aleatoria** (`SAMPLE_N`) para no
cargar cientos de MB en memoria. Súbela o usa `FULL = True` si tu equipo lo permite.
La carpeta `embeddings/` del dataset NIST (~10 GB) no se usa.
