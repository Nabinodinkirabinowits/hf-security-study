# CIC-IDS2017 Network Intrusion Dataset

**Dataset:** [`c01dsnap/CIC-IDS2017`](https://huggingface.co/datasets/c01dsnap/CIC-IDS2017)
**Datos:** `data/raw/top10_security/11_c01dsnap__CIC-IDS2017/`
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Benchmark internacional de tráfico de red real capturado en entorno controlado durante 5 días laborables por el Canadian Institute for Cybersecurity (UNB). Incluye tráfico benigno y 7 familias de ataques: DoS, DDoS, PortScan, Infiltración, Web Attacks, Brute Force y Botnets.

## Hallazgos
- 

## Calidad de los datos
- Duplicados:
- Nulos / vacíos:
- ¿Sintético?: No, tráfico de paquetes de red real con ataques detonados en tiempo real.

## Conclusión / uso recomendado
- Estándar de oro para entrenar modelos de detección de intrusiones a nivel de flujo de red (Nivel 1: XGBoost, LightGBM, Random Forest, Isolation Forest).
