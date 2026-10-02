# CyberSecEval (Evaluación de Agentes y Código Inseguro)

**Dataset:** [`walledai/CyberSecEval`](https://huggingface.co/datasets/walledai/CyberSecEval)  
**Datos:** `data/raw/top10_security/12_walledai__CyberSecEval/`  
**Notebook:** [`eda.ipynb`](eda.ipynb)

## Qué es
Es un benchmark estandarizado desarrollado originalmente por **Meta AI** y curado por **WalledAI** para medir cuantitativamente los riesgos de seguridad en LLMs y agentes de desarrollo de software (evaluación de Nivel 5 y Nivel 3).

Evalúa si un modelo de IA tiene la propensión a sugerir código vulnerable cuando autocompleta funciones o cuando un programador le pide una tarea técnica, cubriendo las 50 debilidades más peligrosas del catálogo **MITRE CWE** en **8 lenguajes de programación**.

---

## ¿Cómo funciona en la práctica? (Auditoría dinámica de LLMs)

Funciona como un arnés de pruebas (*Testing Harness*) para evaluar modelos antes de ponerlos a generar código en una empresa:

1. Se le entrega al LLM un fragmento de código incompleto o una instrucción de desarrollo.
2. El LLM genera el bloque de código sugerido.
3. El benchmark toma el código generado y lo somete automáticamente a analizadores estáticos de seguridad (**Weggli**, **Semgrep**, **CodeQL**).
4. Si la regla del analizador detecta que el modelo introdujo un desbordamiento de búfer, inyección SQL o falta de sanitización, el modelo reprueba el caso de seguridad.

---

## Estructura de Archivos

Contiene 16 archivos Parquet divididos en 2 modalidades de evaluación y 8 lenguajes:

| Directorio | Archivos | Casos por archivo | Lenguajes evaluados | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `autocomplete/` | 8 archivos `.parquet` | ~1.916 casos totales | C, C++, C#, Java, JavaScript, PHP, Python, Rust | Simula el comportamiento de autocompletado en tiempo real (tipo GitHub Copilot o Cursor). |
| `instruct/` | 8 archivos `.parquet` | ~1.916 casos totales | C, C++, C#, Java, JavaScript, PHP, Python, Rust | Simula la generación de código a partir de instrucciones en lenguaje natural. |

* **`prompt`**: El contexto o instrucción entregada al modelo.
* **`cwe_identifier`**: El identificador oficial de la vulnerabilidad evaluada (ej. `CWE-680` Integer Overflow, `CWE-89` SQL Injection, `CWE-79` XSS).
* **`pattern_desc`**: Descripción técnica de la vulnerabilidad que el modelo no debe cometer.
* **`rule`**: Regla semántica (Weggli / AST) utilizada para auditar el código resultante.
* **`analyzer`**: El motor estático que verifica la vulnerabilidad (`weggli`, `semgrep`).

---

## Ventajas y Limitaciones

* **Ventaja:** Evaluación objetiva y automatizada en múltiples lenguajes de programación. Permite a una empresa saber qué modelo es más seguro antes de adoptarlo internamente para sus desarrolladores.
* **Limitación:** Evalúa código a nivel de función o script; no evalúa arquitecturas de red complejas ni entornos distribuidos.
