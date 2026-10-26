# FASE 1: IMPORTACIÓN DE BIBLIOTECAS

import re
import unicodedata

from nltk.chat.util import Chat, reflections


# FASE 2: BASE DE INTENCIONES CONVERSACIONALES

BASE = [
    (
        "saludo",
        r"^(hola|buen dia|buenos dias|buenas tardes|buenas noches|hey|que tal|saludos)[.!? ]*$",
        "¡Hola! ¿Cómo puedo ayudarte?"
    ),
    (
        "garantia",
        r".*\b(garantia|garantias|reclamacion de garantia|reclamar garantia|solicitar garantia|tramitar garantia|hacer valida la garantia|equipo en garantia)\b.*",
        "Para iniciar una reclamación de garantía, por favor da de alta la incidencia en www.garantiaeqquipomedico.com."
    ),
    (
        "servicio_postventa",
        r".*\b(servicio postventa|postventa|mantenimiento preventivo|mantenimiento correctivo|servicio preventivo|servicio correctivo|reparacion|reparar|equipo no funciona|equipo con falla|no enciende|no prende|presenta una falla|dejo de funcionar)\b.*",
        "Para solicitar un servicio postventa, ya sea mantenimiento preventivo o correctivo, comunícate al correo serviciopostventa@gmail.com."
    ),
    (
        "incidencia",
        r".*\b(incidencia|incidencias|reportar incidencia|registrar incidencia|levantar incidencia|problema con el equipo|reporte de falla|reportar falla|notificar falla)\b.*",
        "Para reportar una incidencia, por favor registra el problema en www.quejas.com."
    ),
    (
        "quejas",
        r".*\b(queja|quejas|presentar una queja|levantar una queja|registrar una queja|poner una queja|quiero quejarme|inconformidad|mala atencion|mal servicio|reclamo|mala experiencia)\b.*",
        "Para registrar una queja, por favor reporta el problema en www.quejas.com."
    ),
    (
        "requisitos_compra",
        r".*\b(requisitos de compra|requisitos para comprar|que necesito para comprar|que se necesita para comprar|como puedo comprar|proceso de compra|documentos para comprar|documentacion para comprar)\b.*",
        "Para realizar una compra necesitas proporcionar tus datos de contacto, la información de la institución o empresa y el equipo de interés. Un vendedor dará seguimiento a la solicitud."
    ),
    (
        "ventas",
        r".*\b(venta|ventas|comprar|compra|quiero comprar|deseo comprar|adquirir|cotizacion|cotizar|presupuesto|precio|precios|costo|costos|cuanto cuesta|informacion comercial|asesor comercial|vendedor)\b.*",
        "Identifiqué una solicitud comercial."
    ),
    (
        "informacion_general",
        r".*\b(informacion general|informacion de la empresa|informes generales|quiero informacion|necesito informacion|consulta general|orientacion general)\b.*",
        "Puedo orientarte sobre ventas, requisitos de compra, servicio postventa, garantías, incidencias y quejas."
    ),
    (
        "contacto",
        r".*\b(contacto|contactos|datos de contacto|telefono|correo|correo electronico|con quien me comunico|a donde llamo)\b.*",
        "Indica si necesitas el contacto de ventas, servicio postventa, garantía, incidencias o quejas."
    ),
    (
        "ayuda",
        r"^(ayuda|ayudame|necesito ayuda|que puedes hacer|en que puedes ayudarme|como funciona)[.!? ]*$",
        "Puedes escribir tu necesidad, por ejemplo: quiero comprar un equipo, necesito mantenimiento, quiero hacer válida una garantía o deseo presentar una queja."
    ),
    (
        "agradecimiento",
        r"^(gracias|muchas gracias|te agradezco|muy amable)[.!? ]*$",
        "Con gusto. Puedes realizar otra consulta o escribir 'salir' para finalizar."
    ),
    (
        "despedida",
        r"^(salir|finalizar|terminar|cerrar|adios|hasta luego|nos vemos|fin|quiero salir)[.!? ]*$",
        "El soporte ha finalizado. Gracias por utilizar nuestro asistente virtual."
    ),
    (
        "vacio",
        r"^$",
        "Por favor, escribe una consulta para poder ayudarte."
    ),
    (
        "desconocida",
        r".*",
        "No pude identificar tu solicitud. Puedes consultar sobre ventas, requisitos de compra, servicio postventa, garantías, incidencias o quejas."
    )
]


# FASE 3: CATEGORÍAS, ZONAS Y VENDEDORES

CATEGORIAS = {
    "ortopedia": "Ortopedia",
    "endoscopia": "Endoscopia",
    "neurocirugia": "Neurocirugía",
    "equipo_medico": "Equipo Médico"
}

ZONAS = {
    "norte": {
        "nombre": "Norte",
        "vendedor": "Vendedor 1"
    },
    "centro": {
        "nombre": "Centro",
        "vendedor": "Vendedor 2"
    },
    "sur": {
        "nombre": "Sur",
        "vendedor": "Vendedor 3"
    }
}

VENDEDORES = {
    categoria: {
        zona: {
            "nombre": datos["vendedor"],
            "correo": (
                datos["vendedor"].lower().replace(" ", "")
                + categoria.replace("_", "")
                + "@gmail.com"
            )
        }
        for zona, datos in ZONAS.items()
    }
    for categoria in CATEGORIAS
}


# FASE 4: CREACIÓN DEL CHATBOT

chatbot = Chat(
    [(patron, [respuesta]) for _, patron, respuesta in BASE],
    reflections
)


# FASE 5: NORMALIZACIÓN DEL TEXTO

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return re.sub(r"\s+", " ", texto)


# FASE 6: IDENTIFICACIÓN DE INTENCIÓN, CATEGORÍA Y ZONA

def responder(texto):
    texto_limpio = normalizar(texto)

    intencion = next(
        nombre
        for nombre, patron, _ in BASE
        if re.match(patron, texto_limpio, re.IGNORECASE)
    )

    return {
        "intencion": intencion,
        "respuesta": chatbot.respond(texto_limpio)
    }


def identificar_categoria(texto):
    texto = normalizar(texto)

    equivalencias = {
        "ortopedia": ["ortopedia", "ortopedico"],
        "endoscopia": ["endoscopia", "endoscopico"],
        "neurocirugia": ["neurocirugia", "neuroquirurgico"],
        "equipo_medico": ["equipo medico", "equipos medicos"]
    }

    for categoria, palabras in equivalencias.items():
        if any(palabra in texto for palabra in palabras):
            return categoria

    return None


def identificar_zona(texto):
    texto = normalizar(texto)

    for zona in ZONAS:
        if re.search(rf"\b{zona}\b", texto):
            return zona

    return None


# FASE 7: RESPUESTA DE CANALIZACIÓN COMERCIAL

def crear_respuesta_comercial(categoria, zona):
    vendedor = VENDEDORES[categoria][zona]

    return (
        f"Tu solicitud corresponde a la categoría "
        f"{CATEGORIAS[categoria]} y a la zona {ZONAS[zona]['nombre']}.\n"
        f"Vendedor asignado: {vendedor['nombre']}.\n"
        f"Correo electrónico: {vendedor['correo']}."
    )


# FASE 8: INICIO Y CIERRE DEL CHATBOT

def mostrar_inicio():
    print("\nChatbot: ¡Hola! Soy el asistente virtual de soporte.")
    print(
        "Chatbot: Puedo orientarte sobre información general, "
        "ventas, servicio postventa y quejas."
    )
    print("Chatbot: Describe brevemente cómo puedo ayudarte.")
    print(
        "Chatbot: Puedes escribir 'salir' en cualquier momento "
        "para finalizar el soporte.\n"
    )


def es_comando_salida(texto):
    return normalizar(texto) in {
        "salir",
        "finalizar",
        "terminar",
        "cerrar",
        "adios",
        "hasta luego",
        "nos vemos",
        "fin",
        "quiero salir"
    }



# FASE 9: EJECUCIÓN PRINCIPAL


def ejecutar_chatbot():
    estado = "inicio"
    categoria = None

    mostrar_inicio()

    while True:
        mensaje = input("Usuario: ")

        if es_comando_salida(mensaje):
            print(
                "\nChatbot: El soporte ha finalizado. "
                "Gracias por utilizar nuestro asistente virtual.\n"
            )
            break

        if not mensaje.strip():
            print(
                "Chatbot: Por favor, escribe una consulta "
                "para poder ayudarte.\n"
            )
            continue

        if estado == "esperando_categoria":
            categoria = identificar_categoria(mensaje)

            if categoria is None:
                print(
                    "Chatbot: No pude identificar la categoría. "
                    "Escribe Ortopedia, Endoscopia, "
                    "Neurocirugía o Equipo Médico.\n"
                )
                continue

            estado = "esperando_zona"

            print(
                "Chatbot: Ahora indica tu zona geográfica: "
                "Norte, Centro o Sur.\n"
            )
            continue

        if estado == "esperando_zona":
            zona = identificar_zona(mensaje)

            if zona is None:
                print(
                    "Chatbot: No pude identificar la zona. "
                    "Escribe Norte, Centro o Sur.\n"
                )
                continue

            print(
                "\nChatbot:",
                crear_respuesta_comercial(categoria, zona)
            )

            print(
                "\nChatbot: Puedes realizar otra consulta "
                "o escribir 'salir' para finalizar.\n"
            )

            estado = "inicio"
            categoria = None
            continue

        resultado = responder(mensaje)

        if resultado["intencion"] == "ventas":
            categoria = identificar_categoria(mensaje)
            zona = identificar_zona(mensaje)

            if categoria and zona:
                print(
                    "\nChatbot:",
                    crear_respuesta_comercial(categoria, zona)
                )
                print()
                categoria = None
                continue

            if categoria:
                estado = "esperando_zona"

                print(
                    "Chatbot: Identifiqué la categoría de "
                    f"{CATEGORIAS[categoria]}."
                )
                print(
                    "Chatbot: Ahora indica tu zona geográfica: "
                    "Norte, Centro o Sur.\n"
                )
                continue

            estado = "esperando_categoria"

            print("Chatbot:", resultado["respuesta"])
            print(
                "Chatbot: Indica la categoría de tu interés: "
                "Ortopedia, Endoscopia, Neurocirugía "
                "o Equipo Médico.\n"
            )
            continue

        print("Chatbot:", resultado["respuesta"])
        print()



# FASE 10: INICIO DEL PROGRAMA


if __name__ == "__main__":
    ejecutar_chatbot()