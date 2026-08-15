# 🎭 Shaco Bot - Asistente de IA Multimodal

Shaco es un asistente conversacional inteligente desarrollado en **Python** y **Flask**. Integra modelos avanzados de Hugging Face para generación de lenguaje, análisis de sentimientos, detección de idiomas y traducción automática, registrando todo el historial de conversación en **MongoDB**.

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

* **Python 3.10** o superior.
* **MongoDB Community Server** (corriendo localmente en `mongodb://localhost:27017`).
* **Git** (opcional).

---

 Instrucciones de Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd shaco_bot
```

### 2. Crear y activar un entorno virtual (Recomendado)
* **En Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **En macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

> ⚠️ *Nota:* Al ejecutar la aplicación por primera vez, PyTorch y Transformers descargarán automáticamente los modelos necesarios (`Qwen2.5`, `BETO` y `NLLB-200`). Asegúrate de contar con espacio suficiente en disco y conexión a Internet.

---

 Configuración de la Base de Datos

1. Inicia el servicio de **MongoDB Community**:
   * **Windows:** Se ejecuta automáticamente como servicio.
   * **macOS / Linux:** `brew services start mongodb-community` o `sudo systemctl start mongod`.
2. No necesitas crear tablas ni bases de datos manualmente. MongoDB creará la base de datos `shaco_bot_db` y la colección `historial_chat` automáticamente al enviar el primer mensaje.

---

 Ejecución del Proyecto

Para iniciar el servidor de Flask, ejecuta:

```bash
python app.py
```

Abre tu navegador web e ingresa a:
👉 `http://localhost:8000`

---

 Guía de Uso y Comandos

Puedes interactuar con Shaco escribiendo directamente en la casilla del chat o utilizando los comandos estructurados:

1. Conversación General y Emocional
Solo escribe cualquier mensaje. Shaco analizará tu estado de ánimo (alegría, tristeza, enojo, etc.) y responderá adaptando su personalidad.

* **Ejemplo:** `¡Hola Shaco! ¿Cómo estás hoy?`

---
 2. Resumir Textos
Usa el prefijo `resumen:` seguido del texto que deseas condensar.

* **Sintaxis:** `resumen: <texto_largo>`
* **Ejemplo:**
  ```text
  resumen: La inteligencia artificial es un campo de la informática que se enfoca en crear sistemas capaces de realizar tareas que requerirían inteligencia humana.
  ```

---

 3. Corregir Ortografía y Gramática
Usa el prefijo `corregir:` seguido del texto a revisar.

* **Sintaxis:** `corregir: <texto_con_errores>`
* **Ejemplo:**
  ```text
  corregir: ola k ase como estas oi me siento vian
  ```

---

 4. Hacer Preguntas sobre un Documento
Usa el prefijo `preguntar:` especificando el texto fuente y la pregunta separados por una barra vertical (`|`).

* **Sintaxis:** `preguntar: <texto_base> | <tu_pregunta>`
* **Ejemplo:**
  ```text
  preguntar: La reunión se llevará a cabo el viernes a las 3 PM en la sala B. | ¿A qué hora es la reunión?
  ```

---
 5. Traducir Textos
Usa el prefijo `traducir:` indicando el texto y el idioma de destino separados por una barra vertical (`|`).

* **Sintaxis:** `traducir: <texto_a_traducir> | <idioma_destino>`
* **Idiomas soportados:** español, inglés, francés, alemán, italiano, portugués, japonés, chino, coreano, ruso, árabe, hindi, turco, neerlandés, polaco, sueco, griego, indonesio, vietnamita.
* **Ejemplo:**
  ```text
  traducir: Hello, I hope you are having a wonderful day | español
  ```

---

 6. Menú de Ayuda
Escribe `/?`, `/ayuda` o `ayuda` para desplegar en pantalla la lista rápida de funciones y sintaxis.
