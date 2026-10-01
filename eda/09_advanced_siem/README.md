# Advanced SIEM Dataset

**Dataset:** [`darkknight25/Advanced_SIEM_Dataset`](https://huggingface.co/datasets/darkknight25/Advanced_SIEM_Dataset)
**Datos:** `data/raw/top10_security/09_darkknight25__Advanced_SIEM_Dataset/`
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
100 000 eventos de seguridad **sintéticos** que imitan logs de un SIEM (firewall, IDS, autenticación, endpoint, red, nube, IoT, IA).

## Hallazgos
- **Estructura híbrida:** Combina logs crudos en formato CEF (`raw_log`) con metadatos técnicos y telemetría analítica anidada (`advanced_metadata`, `behavioral_analytics`).
- **Mapeo a MITRE ATT&CK:** Alertas y descripciones etiquetadas con técnicas y tácticas del atacante.
- **Distribución de severidades:** Muestra una dispersión relativamente uniforme entre severidades (info, low, medium, high, critical, emergency), típica de generadores sintéticos.

## Calidad de los datos
- Duplicados: 0 duplicados en `event_id` (UUID único por registro).
- Nulos / vacíos: Columnas específicas de evento (como IPs o puertos) tienen nulos condicionales según el tipo de log (`event_type`).
- ¿Sintético?: Sí, 100% generado sintéticamente para pruebas de concepto y pipelines de SOC sin exponer PII corporativa.

## Conclusión / uso recomendado
- Adecuado para prototipado de parsers SIEM, clasificación de texto de logs crudos y triage inicial asistido por LLMs (Nivel 3).
- Para detección de intrusiones en tráfico de red real (Nivel 1 con XGBoost/Isolation Forest), se recomienda complementar con datasets con desbalance de clases realista como `CIC-IDS2017`.
