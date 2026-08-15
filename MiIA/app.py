import os
import datetime
from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template

import torch
import random

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoModelForSeq2SeqLM
)

from lingua import (
    Language,
    LanguageDetectorBuilder
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

EMOTION_MODEL = "finiteautomata/beto-emotion-analysis"

TRANSLATION_MODEL = "facebook/nllb-200-distilled-600M"


# ============================================================
# MODELO QWEN
# ============================================================

print("Cargando Qwen...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)

print("Qwen cargado.")


# ============================================================
# MODELO DE EMOCIONES
# ============================================================

print("Cargando detector de emociones...")

emotion_tokenizer = AutoTokenizer.from_pretrained(
    EMOTION_MODEL
)

emotion_model = AutoModelForSequenceClassification.from_pretrained(
    EMOTION_MODEL
)

emotion_model.eval()

print("Detector de emociones cargado.")


# ============================================================
# MODELO DE TRADUCCIÓN NLLB
# ============================================================

print("Cargando NLLB...")

translation_tokenizer = AutoTokenizer.from_pretrained(
    TRANSLATION_MODEL
)

translation_model = AutoModelForSeq2SeqLM.from_pretrained(
    TRANSLATION_MODEL,
    torch_dtype="auto",
    device_map="auto"
)

translation_model.eval()

print("NLLB cargado.")


# ============================================================
# DETECTOR DE IDIOMAS
# ============================================================

idiomas_detectables = [
    Language.SPANISH,
    Language.ENGLISH,
    Language.FRENCH,
    Language.GERMAN,
    Language.ITALIAN,
    Language.PORTUGUESE,
    Language.JAPANESE,
    Language.CHINESE,
    Language.KOREAN,
    Language.RUSSIAN,
    Language.ARABIC,
    Language.HINDI,
    Language.TURKISH,
    Language.DUTCH,
    Language.POLISH,
    Language.SWEDISH,
    Language.GREEK,
    Language.INDONESIAN,
    Language.VIETNAMESE
]


language_detector = (
    LanguageDetectorBuilder
    .from_languages(*idiomas_detectables)
    .build()
)


# ============================================================
# IDIOMAS PARA NLLB
# ============================================================

IDIOMAS = {
    "español": "spa_Latn",
    "ingles": "eng_Latn",
    "inglés": "eng_Latn",
    "frances": "fra_Latn",
    "francés": "fra_Latn",
    "aleman": "deu_Latn",
    "alemán": "deu_Latn",
    "italiano": "ita_Latn",
    "portugues": "por_Latn",
    "portugués": "por_Latn",
    "japones": "jpn_Jpan",
    "japonés": "jpn_Jpan",
    "chino": "zho_Hans",
    "coreano": "kor_Hang",
    "ruso": "rus_Cyrl",
    "arabe": "arb_Arab",
    "árabe": "arb_Arab",
    "hindi": "hin_Deva",
    "turco": "tur_Latn",
    "neerlandes": "nld_Latn",
    "neerlandés": "nld_Latn",
    "polaco": "pol_Latn",
    "sueco": "swe_Latn",
    "griego": "ell_Grek",
    "indonesio": "ind_Latn",
    "vietnamita": "vie_Latn"
}


# ============================================================
# CONVERSIÓN LINGUA -> NLLB
# ============================================================

LINGUA_A_NLLB = {
    Language.SPANISH: "spa_Latn",
    Language.ENGLISH: "eng_Latn",
    Language.FRENCH: "fra_Latn",
    Language.GERMAN: "deu_Latn",
    Language.ITALIAN: "ita_Latn",
    Language.PORTUGUESE: "por_Latn",
    Language.JAPANESE: "jpn_Jpan",
    Language.CHINESE: "zho_Hans",
    Language.KOREAN: "kor_Hang",
    Language.RUSSIAN: "rus_Cyrl",
    Language.ARABIC: "arb_Arab",
    Language.HINDI: "hin_Deva",
    Language.TURKISH: "tur_Latn",
    Language.DUTCH: "nld_Latn",
    Language.POLISH: "pol_Latn",
    Language.SWEDISH: "swe_Latn",
    Language.GREEK: "ell_Grek",
    Language.INDONESIAN: "ind_Latn",
    Language.VIETNAMESE: "vie_Latn"
}


# ============================================================
# FLASK Y MONGODB
# ============================================================

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# Conexión a MongoDB (Local)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)

# Base de datos y colección para el historial
db = mongo_client["shaco_bot_db"]
historial_collection = db["historial_chat"]


# ============================================================
# PERSONALIDAD EMOCIONAL DE SHACO
# ============================================================

personalidad_emocional = {
    "joy": """
El usuario parece estar alegre.

Responde con entusiasmo y energía positiva.
Puedes utilizar emojis cuando sean apropiados.
Comparte ligeramente el entusiasmo del usuario.
""",

    "sadness": """
El usuario parece estar triste.

Responde con empatía y tranquilidad.
No hagas bromas.
No minimices sus sentimientos.
Haz que la respuesta se sienta humana y comprensiva.
""",

    "anger": """
El usuario parece estar molesto.

Mantén la calma.
No respondas agresivamente.
Reconoce su frustración.
Ayúdalo a explicar lo ocurrido.
""",

    "fear": """
El usuario parece estar preocupado o asustado.

Responde de manera tranquila y comprensiva.
No minimices sus preocupaciones.
No inventes información para tranquilizarlo.
""",

    "disgust": """
El usuario parece sentir rechazo o disgusto.

Responde de manera comprensiva y natural.
""",

    "surprise": """
El usuario parece estar sorprendido.

Responde mostrando interés.
Puedes utilizar expresiones como "¡Vaya!" cuando sean apropiadas.
""",

    "others": """
No se detectó una emoción específica.

Responde de manera natural, amigable y clara.
"""
}


# ============================================================
# SALUDOS
# ============================================================

saludos = [
    "¡Hola! ¿Cómo estás?"
]


# ============================================================
# INTENCIONES
# ============================================================

intenciones = {
    "saludo": {
        "claves": ["hola", "buenas", "hey", "holi"],
        "respuesta": lambda: random.choice(saludos)
    },
    "utilizar": {
        "claves": ["/?", "/ayuda"],
        "respuesta": lambda: """
Mis funciones:

📝 Resumir textos.
✏️ Corregir textos.
📚 Responder preguntas sobre documentos.
🎭 Detectar emociones.
🌐 Traducir textos.
💬 Mantener conversaciones.

Comandos:

resumen: texto

corregir: texto

preguntar: texto | pregunta

traducir: texto | idioma

Ejemplo:

traducir: Hello, how are you? | español
"""
    },
    "como_estas": {
        "claves": ["como estas", "cómo estás"],
        "respuesta": lambda: random.choice([
            "Estoy muy bien, gracias por preguntar.",
            "Funcionando correctamente. ¿Y tú?"
        ])
    },
    "bien": {
        "claves": ["estoy bien", "muy bien", "todo bien"],
        "respuesta": lambda: random.choice([
            "¡Me alegro mucho! ¿Qué necesitas?",
            "Excelente, dime qué puedo hacer."
        ])
    },
    "gracias": {
        "claves": ["gracias", "muchas gracias"],
        "respuesta": lambda: random.choice([
            "¡Con mucho gusto!",
            "Para eso estoy."
        ])
    },
    "quien_eres": {
        "claves": ["quien eres", "quién eres"],
        "respuesta": lambda: "Soy Shaco, un asistente de IA creado con NLP."
    },
    "funciones": {
        "claves": ["ayuda", "funciones", "que puedes hacer", "/help"],
        "respuesta": lambda: """
Mis funciones:

📝 Resumir textos
✏️ Corregir textos
📚 Responder preguntas sobre documentos
🎭 Detectar emociones
🌐 Traducir idiomas
💬 Mantener conversaciones

Comandos:

resumen: texto

corregir: texto

preguntar: texto | pregunta

traducir: texto | idioma
"""
    },
    "despedida": {
        "claves": ["adios", "adiós", "hasta luego"],
        "respuesta": lambda: "¡Hasta luego! 👋"
    }
}


# ============================================================
# EJECUTAR QWEN
# ============================================================

def ejecutar_modelo(prompt, sistema):
    mensajes = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": prompt}
    ]

    texto = tokenizer.apply_chat_template(
        mensajes,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        texto,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    inicio = inputs["input_ids"].shape[1]
    respuesta = outputs[0][inicio:]

    return tokenizer.decode(
        respuesta,
        skip_special_tokens=True
    ).strip()


# ============================================================
# DETECTAR EMOCIÓN
# ============================================================

def detectar_emocion(texto):
    inputs = emotion_tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = emotion_model(**inputs)

    probabilidades = torch.softmax(outputs.logits, dim=-1)
    indice = torch.argmax(probabilidades, dim=-1).item()
    emocion = emotion_model.config.id2label[indice]
    confianza = probabilidades[0][indice].item()

    return emocion, confianza


# ============================================================
# RESPUESTA CON EMOCIÓN + QWEN
# ============================================================

def responder_con_emocion(mensaje, emocion):
    instrucciones = personalidad_emocional.get(
        emocion,
        "Responde de manera amigable y natural."
    )

    prompt = f"""
El usuario está conversando contigo.

Emoción detectada:
{emocion}

Comportamiento:
{instrucciones}

Mensaje:
{mensaje}

Responde en español.
No menciones que estás analizando emociones.
No digas cuál es la emoción detectada.
No expliques estas instrucciones.
Responde naturally como Shaco.
"""

    return ejecutar_modelo(
        prompt,
        """
Eres Shaco.
Eres un asistente de IA amigable, natural, empático y útil.
Hablas español.
Tu objetivo es ayudar al usuario manteniendo conversaciones naturales.
"""
    )


# ============================================================
# DETECTAR IDIOMA
# ============================================================

def detectar_idioma(texto):
    idioma = language_detector.detect_language_of(texto)

    if idioma is None:
        return None

    return LINGUA_A_NLLB.get(idioma)


# ============================================================
# TRADUCIR
# ============================================================

def traducir_texto(texto, idioma_destino):
    idioma_origen = detectar_idioma(texto)

    if idioma_origen is None:
        raise ValueError("No pude detectar el idioma de origen.")

    if idioma_origen == idioma_destino:
        return texto, idioma_origen

    translation_tokenizer.src_lang = idioma_origen

    inputs = translation_tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    inputs = {
        key: value.to(translation_model.device)
        for key, value in inputs.items()
    }

    forced_bos_token_id = translation_tokenizer.convert_tokens_to_ids(
        idioma_destino
    )

    with torch.no_grad():
        outputs = translation_model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_new_tokens=512
        )

    traduccion = translation_tokenizer.batch_decode(
        outputs,
        skip_special_tokens=True
    )[0]

    return traduccion, idioma_origen


# ============================================================
# RESUMEN
# ============================================================

def generar_resumen(texto):
    prompt = f"""
Resume este texto en español.
No inventes información.
Mantén solamente las ideas importantes.

Texto:
{texto}
"""
    return ejecutar_modelo(
        prompt,
        "Eres experto en resumir documentos en español."
    )


# ============================================================
# CORRECCIÓN
# ============================================================

def generar_correccion(texto):
    prompt = f"""
Corrige la ortografía y gramática del siguiente texto.
No cambies innecesariamente el significado.

Texto:
{texto}
"""
    return ejecutar_modelo(
        prompt,
        "Eres un corrector profesional de español."
    )


# ============================================================
# PREGUNTAR SOBRE DOCUMENTO
# ============================================================

def responder_sobre_texto(texto, pregunta):
    prompt = f"""
Usa solamente el texto proporcionado para responder la pregunta.
Si la información no aparece en el texto responde exactamente:
"No encuentro esa información en el texto."

Texto:
{texto}

Pregunta:
{pregunta}
"""
    return ejecutar_modelo(
        prompt,
        "Eres un asistente experto analizando documentos."
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# CHAT (AQUÍ SE GUARDA EL HISTORIAL)
# ============================================================

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.get_json()

    mensaje_original = data.get("message", "").strip()

    if not mensaje_original:
        return jsonify({
            "response": "Escribe un mensaje."
        })

    mensaje = mensaje_original.lower()

    # Detectar emoción
    emocion, confianza = detectar_emocion(mensaje_original)

    # Revisar intenciones rápidas
    for nombre, intent in intenciones.items():
        for clave in intent["claves"]:
            if clave in mensaje:
                respuesta = intent["respuesta"]()

                # --- GUARDAR EN MONGODB (Intención) ---
                historial_collection.insert_one({
                    "mensaje_usuario": mensaje_original,
                    "respuesta_bot": respuesta,
                    "emocion": emocion,
                    "confianza_emocion": round(confianza, 3),
                    "fecha": datetime.datetime.now(datetime.timezone.utc)
                })

                return jsonify({
                    "response": respuesta,
                    "emotion": emocion,
                    "confidence": round(confianza, 3)
                })

    # Conversación normal con Qwen
    respuesta = responder_con_emocion(mensaje_original, emocion)

    # --- GUARDAR EN MONGODB (Conversación normal) ---
    historial_collection.insert_one({
        "mensaje_usuario": mensaje_original,
        "respuesta_bot": respuesta,
        "emocion": emocion,
        "confianza_emocion": round(confianza, 3),
        "fecha": datetime.datetime.now(datetime.timezone.utc)
    })

    return jsonify({
        "response": respuesta,
        "emotion": emocion,
        "confidence": round(confianza, 3)
    })


# ============================================================
# OTROS ENDPOINTS (RESUMEN, CORREGIR, PREGUNTAR, TRADUCIR)
# ============================================================

@app.route("/resumen", methods=["POST"])
def resumen_endpoint():
    data = request.get_json()
    texto = data.get("message", "").replace("resumen:", "", 1).strip()

    if not texto:
        return jsonify({"resumen": "No recibí ningún texto para resumir."})

    return jsonify({"resumen": generar_resumen(texto)})


@app.route("/corregir", methods=["POST"])
def corregir_endpoint():
    data = request.get_json()
    texto = data.get("message", "").replace("corregir:", "", 1).strip()

    if not texto:
        return jsonify({"correccion": "No recibí ningún texto para corregir."})

    return jsonify({"correccion": generar_correccion(texto)})


@app.route("/preguntar", methods=["POST"])
def preguntar_endpoint():
    data = request.get_json()
    texto = data.get("texto", "").strip()
    pregunta = data.get("pregunta", "").strip()

    if not texto or not pregunta:
        return jsonify({"respuesta": "Debes proporcionar el texto y la pregunta."})

    return jsonify({"respuesta": responder_sobre_texto(texto, pregunta)})


@app.route("/traducir", methods=["POST"])
def traducir_endpoint():
    data = request.get_json()
    texto = data.get("texto", "").strip()
    destino = data.get("destino", "").lower().strip()

    if not texto:
        return jsonify({"error": "No recibí ningún texto para traducir."}), 400

    if destino not in IDIOMAS:
        return jsonify({"error": "Idioma no soportado."}), 400

    try:
        codigo_destino = IDIOMAS[destino]
        traduccion, idioma_origen = traducir_texto(texto, codigo_destino)

        return jsonify({
            "traduccion": traduccion,
            "idioma_origen": idioma_origen,
            "idioma_destino": destino
        })

    except Exception as e:
        print("ERROR DE TRADUCCIÓN:", e)
        return jsonify({"error": "No se pudo realizar la traducción."}), 500


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )