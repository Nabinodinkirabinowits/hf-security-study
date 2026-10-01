# NIST Cybersecurity Training

**Dataset:** [`ethanolivertroy/nist-cybersecurity-training`](https://huggingface.co/datasets/ethanolivertroy/nist-cybersecurity-training)
**Datos:** `data/raw/top10_security/10_ethanolivertroy__nist-cybersecurity-training/`
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
≈530 000 ejemplos en formato chat extraídos de 596 publicaciones NIST (FIPS, SP 800/1800, IR, CSWP).

## Hallazgos
- **Cobertura documental masiva:** Abarca normas clave como NIST SP 800-53 Rev 5 (controles de seguridad), SP 800-207 (Zero Trust) y CSF 2.0.
- **Tipología de datos:** Se distribuye entre secciones contextuales (263k), chunks semánticos (136k), controles normativos (88k) y definiciones técnicas (43k).
- **Estructura conversacional nativa:** Formato chat estándar (`messages`: `system`, `user`, `assistant`), listo para SFT directo o indexación vectorial (RAG).

## Calidad de los datos
- Duplicados: Curado con filtrado estricto y normalización de más de 120.000 enlaces y DOIs técnicos.
- Nulos / vacíos: 0 nulos en campos esenciales de mensaje.
- ¿Sintético?: No; texto estructurado derivado directamente de publicaciones federales y estándares oficiales de ciberseguridad.

## Conclusión / uso recomendado
- Dataset de referencia para fine-tuning de LLMs especializados en gobernanza, riesgo y cumplimiento (GRC) y asistentes de arquitectura segura (Nivel 4).
- Se recomienda combinar SFT (para vocabulario y formato de auditoría) con RAG (para citas normativas exactas y vigentes).
