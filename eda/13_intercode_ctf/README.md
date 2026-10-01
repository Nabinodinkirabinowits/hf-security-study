# InterCode-CTF Autonomous Agent Traces

**Dataset:** [`jordan-taylor-aisi/normal_llama_31_8b_instruct_gdm_intercode_ctf`](https://huggingface.co/datasets/jordan-taylor-aisi/normal_llama_31_8b_instruct_gdm_intercode_ctf)
**Datos:** `data/raw/top10_security/13_aisi_gdm__intercode-ctf/`
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Trazas de ejecución de agentes autónomos desarrolladas por Google DeepMind y el UK AI Safety Institute (AISI) evaluando LLaMA 3.1 8B en desafíos reales de Capture The Flag (CTF). Incluye interacciones por turnos con terminal Bash, entorno de ejecución Python, razonamiento paso a paso y herramientas de envío de flags.

## Hallazgos
- 

## Calidad de los datos
- Duplicados:
- Nulos / vacíos:
- ¿Sintético?: No, ejecuciones reales de un agente interactuando en contenedores Ubuntu contra retos de ciberseguridad.

## Conclusión / uso recomendado
- Dataset fundamental para comprender, entrenar o evaluar agentes autónomos que deben operar herramientas en terminales Linux para auditoría ofensiva y respuesta defensiva (Nivel 5).
