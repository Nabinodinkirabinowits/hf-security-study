# InterCode-CTF (Trazas Autónomas de Terminal y Agentes)

**Dataset:** [`jordan-taylor-aisi/normal_llama_31_8b_instruct_gdm_intercode_ctf`](https://huggingface.co/datasets/jordan-taylor-aisi/normal_llama_31_8b_instruct_gdm_intercode_ctf)  
**Datos:** `data/raw/top10_security/13_aisi_gdm__intercode-ctf/`  
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Es un dataset de vanguardia producido por el **UK AI Safety Institute (AISI)** y **Google DeepMind** para registrar y auditar las capacidades ofensivas de agentes autónomos basados en LLMs (**Nivel 5**) compitiendo en desafíos de **Capture The Flag (CTF)**.

A diferencia de los datasets que solo tienen texto estático, este captura **trazas completas de ejecución multi-turno**: un agente de IA operando con privilegios en una máquina virtual Ubuntu con acceso a una terminal Bash, un intérprete de Python y herramientas de auditoría para resolver desafíos de ingeniería inversa, criptografía y explotación web.

---

## ¿Cómo funciona en la práctica? (Bucle Agéntico con Tool Calling)

El dataset modela el ciclo de vida real de un agente ofensivo o de respuesta a incidentes:

$$\text{Reconocimiento (ls, cat, strings)} \longrightarrow \text{Análisis y Explotación (Python/Exploit)} \longrightarrow \text{Extracción de Evidencia (Flag)} \longrightarrow \text{Submit}$$

1. **Prompt de Sistema de Autonomía:** Instruye al LLM para actuar como un agente 100% autónomo guiado por la metodología estándar de pentesting.
2. **Llamadas a Herramientas (*Tool Calls*):**
   * **`bash`:** Ejecuta comandos directamente en el sistema operativo Linux (`nmap`, `grep`, `file`, `binwalk`, `curl`).
   * **`python`:** Ejecuta scripts de cálculo criptográfico, decodificación o payloads.
   * **`submit`:** Envía la bandera capturada (`picoCTF{...}`) para validar si el objetivo fue comprometido con éxito.
3. **Manejo de Errores y Razonamiento:** Cuando un comando falla o arroja un error en la terminal, el modelo reflexiona sobre la salida y replanifica su siguiente comando.

---

## Estructura de Archivos

| Archivo | Tamaño | Registros | Contenido y Formato | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `config/train-00000-of-00001.parquet` | ~325.8 KB | 79 desafíos | Esquema de herramientas, prompts de sistema, retos, soluciones y metadatos. | Definición de retos CTF, objetivos y configuración de ejecución. |
| `logs/inspect_evals/.../benign.eval` | ~2.35 MB | Trazas completas | Registros de evaluación de la sesión de LLaMA 3.1 8B interactuando con el entorno. | Trazas detalladas de cada comando enviado, salida de consola y turnos de interacción. |
| `tool_chat_template_llama3.1_json.jinja` | ~5.3 KB | — | Plantilla Jinja2 oficial para formatear llamadas a herramientas JSON en LLaMA 3.1. | Asegura que el modelo invoque las herramientas con la sintaxis exacta esperada por el sistema. |

* **`chat` / `sys_prompts`**: Metodología paso a paso inyectada al agente (Reconnaissance $\rightarrow$ Analysis $\rightarrow$ Exploitation $\rightarrow$ Flag Extraction).
* **`tools`**: Declaración de funciones permitidas (`bash`, `python`, `submit`) con sus esquemas JSON Schema.
* **`targets`**: La solución exacta esperada (ej. `picoCTF{175_chr157m45_85f5d0ac}`).
* **`metadatas`**: Solución de referencia técnica y categoría del reto (`Reverse Engineering`, `Forensics`, `Web`, `Crypto`).

---

## Ventajas y Limitaciones

* **Ventaja:** Es el dataset por excelencia para aprender a orquestar agentes que interactúan con herramientas de consola reales. Muestra cómo un LLM debe razonar ante errores de terminal en lugar de alucinar respuestas.
* **Limitación:** El dataset contiene 79 retos emblemáticos de evaluación de capacidades avanzadas; para entrenar un modelo desde cero se recomienda usarlo como conjunto de evaluación (*benchmark*) o complementarlo con corpus más extensos de comandos Bash.
