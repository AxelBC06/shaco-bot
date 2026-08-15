
window.onload = () => {

    add(
        "🎭 Bienvenido. Soy Shaco. Usa /help para ver mis funciones.",
        "ai"
    );

};


const m = document.getElementById("messages");

const t = document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");


sendButton.onclick = send;


// ============================================================
// ENTER PARA ENVIAR
// ============================================================

t.addEventListener(
    "keydown",
    e => {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            send();

        }

    }
);


// ============================================================
// ENVIAR MENSAJE
// ============================================================

async function send() {

    let txt = t.value.trim();

    if (!txt) return;


    add(
        txt,
        "user"
    );


    t.value = "";


    let endpoint = "/chat";

    let body = {
        message: txt
    };


    let lower = txt.toLowerCase().trim();


    // ========================================================
    // RESUMEN
    // ========================================================

    if (lower.startsWith("resumen:")) {

        endpoint = "/resumen";

        body = {

            message: txt

        };

    }


    // ========================================================
    // CORREGIR
    // ========================================================

    else if (lower.startsWith("corregir:")) {

        endpoint = "/corregir";

        body = {

            message: txt

        };

    }


    // ========================================================
    // PREGUNTAR
    // ========================================================

    else if (lower.startsWith("preguntar:")) {

        endpoint = "/preguntar";


        let contenido =
            txt.substring(
                "preguntar:".length
            ).trim();


        let partes =
            contenido.split("|");


        if (partes.length < 2) {

            add(
                "Formato: preguntar: texto | pregunta",
                "ai"
            );

            return;

        }


        let texto =
            partes.shift().trim();


        let pregunta =
            partes.join("|").trim();


        if (!texto || !pregunta) {

            add(
                "Debes proporcionar el texto y la pregunta.",
                "ai"
            );

            return;

        }


        body = {

            texto: texto,

            pregunta: pregunta

        };

    }


    // ========================================================
    // TRADUCIR
    // ========================================================

    else if (lower.startsWith("traducir:")) {

        endpoint = "/traducir";


        let contenido =
            txt.substring(
                "traducir:".length
            ).trim();


        let partes =
            contenido.split("|");


        if (partes.length < 2) {

            add(
                "Formato: traducir: texto | idioma",
                "ai"
            );

            return;

        }


        let texto =
            partes.shift().trim();


        let destino =
            partes.join("|").trim();


        if (!texto || !destino) {

            add(
                "Debes indicar el texto y el idioma de destino.",
                "ai"
            );

            return;

        }


        body = {

            texto: texto,

            destino: destino

        };

    }


    // ========================================================
    // PETICIÓN AL SERVIDOR
    // ========================================================

    try {

        let r = await fetch(

            endpoint,

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(body)

            }

        );


        let d;


        try {

            d = await r.json();

        }

        catch {

            throw new Error(
                "El servidor no devolvió JSON válido."
            );

        }


        if (!r.ok) {

            throw new Error(

                d.error
                ||
                d.response
                ||
                "HTTP " + r.status

            );

        }


        // ====================================================
        // RESUMEN
        // ====================================================

        if (endpoint === "/resumen") {

            add(

                d.resumen
                ||
                "No se pudo generar el resumen.",

                "ai"

            );

        }


        // ====================================================
        // CORRECCIÓN
        // ====================================================

        else if (endpoint === "/corregir") {

            add(

                d.correccion
                ||
                "No se pudo corregir el texto.",

                "ai"

            );

        }


        // ====================================================
        // PREGUNTAR
        // ====================================================

        else if (endpoint === "/preguntar") {

            add(

                d.respuesta
                ||
                "No se pudo obtener una respuesta.",

                "ai"

            );

        }


        // ====================================================
        // TRADUCCIÓN
        // ====================================================

        else if (endpoint === "/traducir") {

            add(

                d.traduccion
                ||
                "No se pudo realizar la traducción.",

                "ai"

            );


            // Mostrar información de idiomas

            if (
                d.idioma_origen &&
                d.idioma_destino
            ) {

                add(

                    `🌐 ${d.idioma_origen} → ${d.idioma_destino}`,

                    "translation"

                );

            }

        }


        // ====================================================
        // CHAT NORMAL
        // ====================================================

        else {

            add(

                d.response
                ||
                "No recibí una respuesta de Shaco.",

                "ai"

            );


            // ================================================
            // EMOCIÓN
            // ================================================

            if (
                d.emotion &&
                typeof d.confidence === "number"
            ) {

                const nombres = {

                    joy:
                        "alegría",

                    sadness:
                        "tristeza",

                    anger:
                        "enojo",

                    fear:
                        "miedo",

                    disgust:
                        "disgusto",

                    surprise:
                        "sorpresa",

                    others:
                        "neutral"

                };


                let emocion =
                    nombres[d.emotion]
                    ||
                    d.emotion;


                let porcentaje =
                    Math.round(
                        d.confidence * 100
                    );


                add(

                    `🎭 Emoción detectada: ${emocion} (${porcentaje}%)`,

                    "emotion"

                );

            }

        }

    }

    catch (error) {

        console.error(
            "Error:",
            error
        );


        add(

            "❌ " +
            (
                error.message
                ||
                "Ocurrió un error al comunicarse con Shaco."
            ),

            "ai"

        );

    }

}


// ============================================================
// AGREGAR MENSAJE AL CHAT
// ============================================================

function add(x, c) {

    let div =
        document.createElement("div");


    div.className =
        "msg " + c;


    div.textContent =
        x;


    m.appendChild(div);


    m.scrollTop =
        m.scrollHeight;

}

