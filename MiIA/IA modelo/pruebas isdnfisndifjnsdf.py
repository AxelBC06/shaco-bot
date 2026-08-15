import random
import torch
from difflib import ndiff
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

print("Cargando modelo de resumen...")

# Carga única del tokenizer y el modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)

# ==========================
# FUNCIÓN DE RESUMEN (captura multi-línea con '.' para terminar)
# ==========================
def resumen():
    print("Pega el texto. Escribe una línea con solo un punto (.) para finalizar:\n")

    lineas = []
    while True:
        linea = input()
        if linea.strip() == ".":
            break
        lineas.append(linea)

    texto = "\n".join(lineas).strip()
    if not texto:
        return "No se proporcionó texto para resumir."

    prompt = f"""
Resume el siguiente texto en español.

Reglas:
- No inventes información.
- Conserva únicamente las ideas principales.
- Escribe un resumen claro y natural.
- El resumen debe ocupar aproximadamente un 25% del tamaño del texto original.

Texto:
{texto}
"""

    mensajes = [
        {"role": "system", "content": "Eres un experto en resumir textos."},
        {"role": "user", "content": prompt}
    ]

    # Construir el texto que se tokenizará (NO imprimirlo)
    text = tokenizer.apply_chat_template(
        mensajes,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=250
        )

    # Para modelos causales: outputs contiene prompt + generación.
    # Extraemos solo los ids generados (después de la longitud del input).
    input_len = inputs["input_ids"].shape[1]
    generated_ids = outputs[0][input_len:]

    resumen_generado = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    ).strip()

    return resumen_generado


# ==========================
# FUNCIÓN CORRECTOR (sin recargar modelo)
# ==========================
def corrector():
    print("Cargando modelo... (la primera vez puede tardar)")

    texto = input("Escribe un texto con errores:\n").strip()
    if not texto:
        print("No se proporcionó texto.")
        return

    prompt = f"""Corrige únicamente la ortografía y la gramática del siguiente texto.
No cambies el significado.
No expliques nada.
Devuelve solo el texto corregido.

Texto:
{texto}
"""

    mensajes = [
        {"role": "system", "content": "Eres un corrector profesional de español."},
        {"role": "user", "content": prompt},
    ]

    text = tokenizer.apply_chat_template(
        mensajes,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300
        )

    # Extraer solo la parte generada (sin el prompt)
    input_len = inputs["input_ids"].shape[1]
    generated_ids = outputs[0][input_len:]

    respuesta = tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    ).strip()

    print("\n--- TEXTO CORREGIDO ---")
    print(respuesta)

    original = texto.split()
    nuevo = respuesta.split()

    resultado = []
    for diff in ndiff(original, nuevo):
        if diff.startswith("- "):
            resultado.append(f"[❌{diff[2:]}]")
        elif diff.startswith("+ "):
            resultado.append(f"[✔{diff[2:]}]")
        elif diff.startswith("  "):
            resultado.append(diff[2:])

    print("\n--- CAMBIOS DESTACADOS ---")
    print(" ".join(resultado))


# ==========================
# RESPUESTAS VARIABLES
# ==========================
saludos = [
    "¡Hola! ¿Cómo estás?",
    "¡Bienvenido! ¿En qué puedo ayudarte?",
    "¡Hola! Me alegra hablar contigo."
]

# ==========================
# INTENCIONES
# ==========================
nlp = {
    "resumen": {
        "claves": ["resumen"],
        "respuesta": resumen
    },
    "corrector": {
        "claves": ["corrector", "corregir", "corrige"],
        "respuesta": corrector
    }
}

intenciones = {
    "saludo": {
        "claves": ["hola", "buenas", "hey", "holi"],
        "respuesta": lambda: random.choice(saludos)
    },
    "como_estas": {
        "claves": ["como estas", "cómo estás"],
        "respuesta": lambda: random.choice([
            "Estoy muy bien, gracias por preguntar. ¿Y tú?",
            "Todo funciona correctamente. ¿Cómo estás tú?"
        ])
    },
    "bien": {
        "claves": ["estoy bien", "muy bien", "todo bien"],
        "respuesta": lambda: random.choice([
            "¡Me alegro mucho!",
            "Excelente 😊",
            "Qué bueno."
        ])
    },
    "mal": {
        "claves": ["estoy mal", "triste", "cansado"],
        "respuesta": lambda: random.choice([
            "Lamento escuchar eso. Espero que todo mejore.",
            "Ánimo, espero que pronto te sientas mejor."
        ])
    },
    "gracias": {
        "claves": ["gracias", "muchas gracias"],
        "respuesta": lambda: random.choice([
            "¡Con mucho gusto!",
            "Para eso estoy.",
            "No hay de qué."
        ])
    },
    "quien_eres": {
        "claves": ["quien eres", "quién eres"],
        "respuesta": lambda: "Soy Shaco, un chatbot especializado en Procesamiento de Lenguaje Natural."
    },
    "nombre": {
        "claves": ["como te llamas", "cómo te llamas", "tu nombre"],
        "respuesta": lambda: "Puedes llamarme Shaco."
    },
    "funciones": {
        "claves": ["que puedes hacer", "qué puedes hacer", "ayuda", "funciones"],
        "respuesta": lambda: """
Puedo ayudarte con:

📝 Resumir textos.
✍️ Corregir ortografía.
😊 Detectar sentimientos.
❓ Responder preguntas sobre un texto.
🌐 Detectar y traducir idiomas.

También puedo mantener una conversación básica contigo.
"""
    },
    "despedida": {
        "claves": ["adios", "adiós", "hasta luego", "nos vemos"],
        "respuesta": lambda: random.choice([
            "¡Hasta luego!",
            "Que tengas un excelente día.",
            "Fue un gusto hablar contigo."
        ])
    }
}

# ==========================
# FUNCIONES PRINCIPALES
# ==========================
def responder(mensaje):
    mensaje = mensaje.lower()
    for nombre, datos in intenciones.items():
        if any(clave in mensaje for clave in datos["claves"]):
            return datos["respuesta"]()
    return "No entendí tu mensaje. Puedes preguntarme qué puedo hacer."


def nl(mensaje):
    mensaje = mensaje.lower()
    # Primero buscar en nlp (resumen, corrector)
    for nombre, datos in nlp.items():
        if any(clave in mensaje for clave in datos["claves"]):
            return datos["respuesta"]()
    # Si no es intención de nlp, delega a responder()
    return responder(mensaje)


# ==========================
# CHAT
# ==========================
print("="*50)
print(" Hola, soy Shaco.")
print("Puedo conversar contigo y realizar tareas de NLP.")
print("Escribe 'adiós' para terminar.")
print("="*50)

while True:
    mensaje = input("\nTú: ")

    # Ignorar entradas vacías (evita respuestas "No entendí..." al pulsar ENTER)
    if mensaje.strip() == "":
        continue

    respuesta = nl(mensaje)
    # Si la respuesta es una función (resumen/corrector), ejecutarla
    if callable(respuesta):
        salida = respuesta()
        # Algunas funciones imprimen por sí mismas (corrector), otras devuelven texto (resumen)
        if salida is not None:
            print("\nBot:", salida)
    else:
        print("\nBot:", respuesta)

    lower_msg = mensaje.lower()
    if any(x in lower_msg for x in ["adios", "adiós", "hasta luego"]):
        break
