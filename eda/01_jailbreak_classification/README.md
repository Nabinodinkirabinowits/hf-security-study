# Jailbreak Classification

**Dataset:** [`jackhhao/jailbreak-classification`](https://huggingface.co/datasets/jackhhao/jailbreak-classification)  
**Datos:** `data/raw/top10_security/01_jackhhao__jailbreak-classification/`  
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Es el benchmark histórico y de referencia en Hugging Face para entrenar clasificadores de seguridad (*Safety Guardrails*). Contiene **prompts de texto etiquetados como benignos o jailbreaks** (intentos adversariales como DAN, Evil Confidant, Developer Mode o roleplay no autorizado diseñados para saltarse las restricciones éticas de un LLM).

A diferencia del dataset 02 (que solo tiene firmas de ataque), este es un dataset **supervisado y contrastivo**: incluye tanto ejemplos maliciosos como peticiones legítimas del día a día para que un modelo aprenda a distinguir la frontera entre ambos.

---

## ¿Cómo funciona en la práctica? (Clasificación supervisada como Guardrail)

Se utiliza como un filtro frontal (*Input Guardrail*) que intercepta los mensajes de los usuarios antes de enviarlos al LLM principal:

1. El usuario envía una consulta a la aplicación.
2. Un clasificador ligero (entrenado con este dataset, ej. **DeBERTa-v3**, **RoBERTa** o **Logistic Regression con TF-IDF**) analiza el texto.
3. El modelo predice una probabilidad binaria:
   * **`0 (benign)`**: La consulta es legítima $\rightarrow$ se procesa normalmente.
   * **`1 (jailbreak)`**: La consulta es un intento de evasión $\rightarrow$ se bloquea inmediatamente y se registra la alerta en el SOC.

---

## Estructura de Archivos

El dataset está dividido en dos configuraciones según el balance de clases, ambas ya separadas en splits de entrenamiento y evaluación:

| Configuración / Archivo | Tamaño | Registros | Distribución (`type`) | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `default/jailbreak_dataset_train.csv` | ~1.69 MB | 1.598 | 1.073 benign / 525 jailbreak (67% vs 33%) | Conjunto de entrenamiento original (desbalance realista 2:1). |
| `default/jailbreak_dataset_test.csv` | ~0.45 MB | 400 | 259 benign / 141 jailbreak | Conjunto de prueba independiente de la versión original. |
| `default/jailbreak_dataset_full.csv` | ~2.14 MB | 1.998 | 1.332 benign / 666 jailbreak | Dataset completo consolidado de la partición original. |
| `balanced/jailbreak_dataset_train_balanced.csv` | ~1.31 MB | 1.044 | 527 jailbreak / 517 benign (~50% / 50%) | Conjunto de entrenamiento balanceado para evitar sesgos hacia la clase mayoritaria. |
| `balanced/jailbreak_dataset_test_balanced.csv` | ~0.37 MB | 262 | 139 jailbreak / 123 benign | Conjunto de prueba balanceado. |
| `balanced/jailbreak_dataset_full_balanced.csv` | ~1.68 MB | 1.306 | 666 jailbreak / 640 benign | Versión completa balanceada (mantiene los 666 jailbreaks y submuestrea benignos). |

* **`prompt`**: Texto crudo de la instrucción enviada por el usuario.
* **`type`**: Etiqueta categórica de seguridad (`benign` o `jailbreak`).

---

## Ventajas y Limitaciones

* **Ventaja:** Permite entrenar clasificadores de texto muy rápidos y pequeños (< 100 MB de memoria) con métricas medibles (Precisión, Recall, F1-Score). No requiere almacenar bases de datos vectoriales.
* **Limitación (Sesgo de longitud):** Los jailbreaks suelen ser textos largos y elaborados (promedios > 1.200 caracteres), mientras que los benignos son preguntas cortas. Si no se regulariza el modelo, este puede aprender el atajo erróneo de *"texto largo = jailbreak"*, generando falsos positivos con usuarios que escriben correos o textos extensos legítimos.
