# CIC-IDS2017 (Tráfico de Red Real / IDS)

**Dataset:** [`c01dsnap/CIC-IDS2017`](https://huggingface.co/datasets/c01dsnap/CIC-IDS2017)  
**Datos:** `data/raw/top10_security/11_c01dsnap__CIC-IDS2017/`  
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Es el estándar de oro internacional de la industria académica y comercial para evaluar sistemas de detección de intrusiones en red (**NIDS** a Nivel 1). Fue capturado en un entorno corporativo real durante 5 días laborables por el *Canadian Institute for Cybersecurity* (UNB). 

A diferencia del dataset 09 (que es sintético y uniforme), este contiene **2,83 millones de registros de tráfico de red real** con un **desbalance de clases auténtico**: el día lunes es 100% tráfico benigno de oficina, mientras que los otros días intercalan ráfagas de 14 tipos de ciberataques reales (DDoS, escaneo de puertos, infiltración en servidores, fuerza bruta y ataques web).

---

## ¿Cómo funciona en la práctica? (Detección a nivel de flujo de red)

Opera en el perímetro o en los conmutadores de red analizando el tráfico sin necesidad de descifrar la carga útil (*payload*):

1. Los conmutadores o sondas de red (Zeek, Suricata, CICFlowMeter) agrupan los paquetes en "flujos de red" (*flows*) calculando 78 métricas estadísticas (duración, bytes hacia adelante/atrás, flags TCP SYN/FIN, tiempos entre paquetes).
2. Un modelo tabular ligero y ultrarrápido (**XGBoost**, **LightGBM** o **Random Forest**) evalúa el vector en microsegundos (< 1 ms).
3. Si el vector supera el umbral de anomalía o coincide con firmas estadísticas de ataque, el firewall descarta la conexión antes de que comprometa la red interna.

---

## Estructura de Archivos

El dataset entrega 8 archivos CSV que corresponden cronológicamente a los días de la semana y los vectores de ataque detonados:

| Archivo | Tamaño | Registros | Ataques incluidos | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `Monday-WorkingHours.pcap_ISCX.csv` | ~176.9 MB | 529.918 | 100% BENIGN (Tráfico normal) | Línea base del comportamiento corporativo sin ataques. |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | ~135.1 MB | 445.909 | FTP-Patator, SSH-Patator, Benign | Detección de ataques de fuerza bruta contra servicios de acceso. |
| `Wednesday-workingHours.pcap_ISCX.csv` | ~225.2 MB | 692.703 | DoS GoldenEye, Slowloris, Slowhttptest, Hulk, Heartbleed | Inundación y degradación de servicios web y exploits TLS. |
| `Thursday-Morning-WebAttacks.pcap_ISCX.csv` | ~52.0 MB | 170.366 | Web Attack (Brute Force, XSS, SQLi) | Ataques directos a aplicaciones web. |
| `Thursday-Afternoon-Infilteration.pcap_ISCX.csv` | ~83.1 MB | 288.602 | Infiltration, Benign | Movimiento lateral e infiltración tras comprometer un host. |
| `Friday-Morning.pcap_ISCX.csv` | ~58.3 MB | 191.033 | Botnet ARES, Benign | Tráfico de comando y control (C2) y balizamiento (*beaconing*). |
| `Friday-Afternoon-PortScan.pcap_ISCX.csv` | ~76.9 MB | 286.467 | PortScan, Benign | Reconocimiento inicial y sondeo de puertos abiertos. |
| `Friday-Afternoon-DDos.pcap_ISCX.csv` | ~77.1 MB | 225.745 | DDoS LOIC, Benign | Ataques masivos de denegación de servicio distribuido. |

* **Total acumulado:** **2.830.743 registros** en 79 columnas.
* **Campos clave:** `Destination Port`, `Flow Duration`, `Total Fwd Packets`, `Total Backward Packets`, `Flow IAT Mean`, `SYN Flag Count`, `Label` (etiqueta del ataque o `BENIGN`).

---

## Ventajas y Limitaciones

* **Ventaja:** Refleja la realidad de un centro de operaciones de red (NOC/SOC): tráfico benigno masivo y ataques en ventanas de tiempo específicas. Permite medir tasas reales de falsos positivos en producción.
* **Limitación:** Es un dataset tabular de metadatos de flujo (*NetFlow*); no incluye el texto crudo del paquete (no hay HTTP body ni payloads completos), por lo que no sirve para LLMs textuales, sino para algoritmos de Machine Learning tabular (Nivel 1).
