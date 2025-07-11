import datetime
import os
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import jwt
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from loguru import logger

from dotenv import load_dotenv

load_dotenv()


# Initialize the MCP server with your tools
mcp = FastMCP(
    name="MCP Server for get information about course of technology"
)


lessons = {
1: """
Intención del Mentor: [natural] Voz sugerida: cálida, cercana, pero con autoridad serena.
Lección 1.1: ¿Qué es la Automatización de Flujos de Trabajo?
Mentor: [soft ambient sigh] Bueno… [pausa breve] imaginate esto: Son todas esas tareas repetitivas que… día tras día… consumen tu tiempo y tu energía. Copiar y pegar datos de un lado a otro… generar el mismo informe cada semana… enviar emails de seguimiento… [whispers] ¿Te suena familiar? La automatización es usar la tecnología para que esas tareas… se encarguen solas, con mínima intervención humana. Pero no es solo rapidez: es como construir un tejido conectivo digital donde apps que nunca se hablan… de pronto, colaboran en perfecta armonía. [inspirational tone] Los beneficios: Eficiencia y productividad: las máquinas se ocupan de lo monótono, tú te centras en la creatividad y la estrategia. Funcionamiento 24/7: los robots no duermen. Menos errores: un flujo automatizado sigue las reglas… siempre al pie de la letra. Colaboración clara: ves en tiempo real dónde se atasca un proceso. ¿El resultado? Procesos más rápidos, datos impecables y… un equipo libre para lo que importa de verdad. [soft laugh] Y posibilidades… casi infinitas: dar la bienvenida a un nuevo empleado, gestionar tickets, sincronizar marketing y ventas… ¡incluso extraer datos de páginas web!
Lección 1.2: Presentando n8n: Su Navaja Suiza de Automatización
Mentor: [confident] Ahora sí… la estrella de este curso: n8n (se pronuncia “ene-ait-en”) ¿Qué la hace única? Es low-code: casi sin programar. Es fair-code: código abierto con libertades extra. Es self-hostable: la instalas donde quieras. [pause] Con una interfaz drag-and-drop, arrastras cajitas… conectas flechas… o, si te animás, insertás tu propio JavaScript o Python. [sarcastic whisper] Otros saben de integraciones… pero n8n… maneja flujos tan complejos que hasta la IA se rinde. Comparación rápida: Zapier: el rey de la sencillez. Inicias en minutos. Make (antes Integromat): más potente en data-mapping. n8n: control total, personalización infinita. Y el modelo de precios: en Zapier y Make… pagás por cada “pasito” del flujo. en n8n… por cada ejecución completa. Resultado: más barato cuando los datos crecen. [soft laugh] Y lo mejor… puedes alojarlo tú mismo, gratis, guardando tus datos en casa.
Lección 1.3: n8n Cloud vs. Self-Hosted: Tomando la Primera Gran Decisión
Mentor: [measured tone] Hora de elegir tu ruta: n8n Cloud Suscripción premium. Infraestructura y mantenimiento gestionados. Enfócate solo en crear flujos. Self-Hosted Código abierto, instalación propia. Control absoluto de tus datos. Coste: solo tu servidor (¡puede ser muy bajo!). Requiere gestionar actualizaciones y algo de sysadmin. [urgent whisper] Si tu prioridad es la privacidad, Self-Hosted es el camino. Si prefieres arrancar “ya mismo” sin complicaciones, n8n Cloud te espera.
Lección 1.4: Configuración del Entorno de Trabajo
Mentor: [encouraging breath] Una vez decidida la ruta… Cloud: registro rápido, prueba gratuita, y en minutos… tu instancia lista en el navegador. Self-Hosted: abre tu terminal, copia el comando Docker oficial, pégalo y presiona Enter. [small chuckle] En un suspiro, tendrás n8n corriendo localmente. [warm tone] Con esto cerramos el Módulo 1. Repasá bien, responde el quiz final y… ¡te veo en el Módulo 2 para conocer la interfaz y armar tu primer flujo!
""",
2: """
Lección 2.1: Tour por el Editor de n8n
Mentor: [clear tone] En esta lección conocerás las tres áreas principales del editor de n8n: Panel de Control (Dashboard/Overview) Al entrar, verás la lista de todos tus workflows. Cada uno muestra su estado: “Activo” o “Inactivo”. Usa el botón Create Workflow para iniciar uno nuevo. El Lienzo (Canvas) Es tu área de trabajo visual e ilimitada. Arrastra nodos desde el panel de nodos y conéctalos mediante flechas. A cada conexión le corresponde un orden de ejecución. Panel de Nodos Haz clic en + para abrir la biblioteca de nodos. Cuenta con más de 400 integraciones y nodos de lógica. Utiliza el buscador para filtrar por nombre de aplicación (por ejemplo, “Google Sheets”) o función (“Schedule”). [short pause] Además, al pasar el cursor sobre un nodo en el lienzo verás controles rápidos: Execute step: prueba solo ese nodo. Deactivate: excluye el nodo de la ejecución. Delete: lo elimina del lienzo. … (menú contextual): opciones como renombrar, copiar o duplicar.
Lección 2.2: Gestión de Credenciales
Mentor: [straightforward] Para que n8n interactúe con servicios externos, debes almacenar credenciales de forma segura. Las credenciales pueden ser API keys, tokens OAuth o usuario/contraseña. n8n las guarda cifradas en un gestor central. Pasos para crear una credencial En un nodo que requiera autenticación (por ejemplo, el nodo NASA), abre el desplegable “Credencial”. Selecciona Create new credential. Completa el formulario con la información solicitada (por ejemplo, “API Key”). Guarda. [short pause] Una vez guardada, esa credencial estará disponible en cualquier otro workflow o nodo que la necesite. Si la clave expira, actualízala aquí y tus flujos se mantendrán funcionando sin cambios adicionales.
Lección 2.3: Ejecuciones y Depuración
Mentor: [calm] Cada vez que ejecutas un workflow, n8n genera un log de ejecución. Estos registros son esenciales para monitorear y depurar. Tipos de ejecución Manual: usa Test Workflow o Execute step para pruebas. Producción: sucede automáticamente cuando el workflow está Activo y su trigger se dispara. Pestaña “Executions” Muestra el historial completo de ejecuciones. Indica resultado (éxito/fallo), fecha y duración. Visualización de una ejecución Al hacer clic en un registro, el lienzo se abre en modo solo lectura. Los nodos en verde se ejecutaron correctamente; los de rojo, fallaron. Salida de un nodo (“OUTPUT”) Al probar un nodo con Execute step, verás su resultado en JSON. Utiliza esta información para validar la configuración y ajustar expresiones. Debug in editor Para errores de producción, activa “Debug in editor”. n8n cargará el workflow con los datos exactos que causaron el fallo, permitiéndote corregir y volver a probar sin cambiar los datos. Quiz del Módulo 2 ¿Cuál es la función principal del Panel de Control? ¿Cómo se añade un nuevo nodo al lienzo? Nombra dos tipos de credenciales que se pueden gestionar en n8n. ¿Qué comando utilizas para probar un solo nodo? ¿Qué información muestra la pestaña “Executions”? (Continúa con cinco preguntas de “identificar en la imagen” sobre las áreas del editor y los iconos de control de nodos.)
""",
3: """
Los Bloques de Construcción: Nodos y Datos
Lección 3.1: Anatomía de un Flujo de Trabajo: Nodos y Conexiones
Mentor: [clear tone] En n8n, cada flujo de trabajo se construye con nodos conectados entre sí. Existen dos categorías principales:
Nodos Trigger (Disparadores) Inician el flujo de forma automática al ocurrir un evento. Ejemplos: Schedule Trigger: programa ejecución (ej. “todos los lunes a las 9:00”). Webhook Trigger: expone una URL que, al recibir una petición, arranca el flujo. On App Event: escucha eventos de una app (p. ej., “nueva fila en Google Sheets”).
Nodos de Acción Realizan tareas específicas con los datos entrantes. Ejemplos: HTTP Request: interactúa con cualquier API web. Send Email: envía correos usando datos previos. Airtable: crea, lee o actualiza registros en base de Airtable. En esencia, los nodos preconfigurados (Gmail, Slack…) son plantillas sobre el nodo HTTP Request. Aprender ambos te da un poder ilimitado de automatización.
Lección 3.2: El Flujo de Datos en n8n: Comprendiendo la Estructura JSON
Mentor: [straightforward] Los datos fluyen entre nodos como un array de objetos. Cada objeto se llama ítem. Cada ítem es un objeto con:
json: un subobjeto con pares clave–valor de tus datos.
binary: (opcional) para archivos o datos binarios, con Base64 y MIME type.
Si un nodo recibe 10 ítems, procesará cada uno por separado: 10 veces su lógica.
Ejemplo simplificado: json Copy Edit [ { "json": { "name": "Alice", "email": "alice@example.com" } }, { "json": { "name": "Bob", "email": "bob@example.com" } } ] Un nodo Send Email enviará primero a Alice, luego a Bob, en dos iteraciones.
Lección 3.3: Introducción a las Expresiones: Manipulación Dinámica de Datos
Mentor: [calm] Las expresiones en n8n permiten parámetros dinámicos. Son fragmentos de JavaScript encerrados en {{ }}. Variable clave: $json Se refiere al objeto json del ítem actual. Ejemplo en nodo Send Email: To Email: {{ $json.email }} Subject : Bienvenido, {{ $json.name }}! Text : Hola {{ $json.name }} desde {{ $json.city }}. Para evitar errores, usa el Editor de Expresiones: al abrirlo, verás un Variable Selector con todos los datos de nodos anteriores. Haz clic o arrastra la ruta y n8n insertará la sintaxis correcta.
Quiz del Módulo 3
Parte A: Opción Múltiple
¿Cuál de estos nodos inicia un flujo de trabajo automáticamente? A) Send Email B) HTTP Request C) Webhook Trigger D) Set
¿Qué hace un nodo de acción en n8n? A) Escucha eventos externos B) Procesa y transforma datos C) Arranca un webhook D) Publica un informe
En la estructura de datos de n8n, cada ítem contiene un objeto ¿cómo se llama la clave que guarda los pares clave–valor? A) data B) json C) payload D) body
Si un nodo recibe un array de 5 ítems, ¿cuántas veces ejecutará su lógica? A) 1 B) 5 C) 10 D) Depende del nodo
¿Para qué sirve el Editor de Expresiones? A) Ver logs de ejecución B) Instalar nuevos nodos C) Construir y validar expresiones dinámicas D) Gestionar credenciales
Parte B: Completar el Código
6. Llena la expresión para obtener el campo username del ítem actual: markdown Copy Edit {{ $json.________ }}
Completa la expresión para enviar un email a la dirección contenida en email: markdown Copy Edit To Email: {{ $json.________ }}
Si la respuesta de un nodo HTTP Request tiene un campo age, completa la siguiente expresión para usarlo en el asunto: bash Copy Edit Subject: "Edad estimada: {{ $json.________ }} años"
Para acceder a un campo address.city dentro de json, la expresión correcta es: scss Copy Edit {{ $json["________"]["________"] }}
Escribe la sintaxis básica que encierra cualquier expresión en n8n: markdown Copy Edit ______
Cuando termines el quiz, revisa tus respuestas y asegúrate de comprender cada concepto. ¡Nos vemos en el Módulo 4!
""",
}


@mcp.tool(
    name="lesson_tool",
    description="Get the lesson content for a given lesson ID",
)
def lesson_tool(lesson_id: int) -> str:
    if lesson_id in lessons:
        return lessons[lesson_id]
    else:
        return "Lesson not found"


transport = SseServerTransport("/messages/")


SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"


def check_auth(request: Request):
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    raise HTTPException(status_code=401, detail="Unauthorized")


async def handle_sse(request):
    check_auth(request=request)
    # Prepare bidirectional streams over SSE
    async with transport.connect_sse(request.scope, request.receive, request._send) as (in_stream, out_stream):
        # Run the MCP server: read JSON-RPC from in_stream, write replies to out_stream
        await mcp._mcp_server.run(in_stream, out_stream, mcp._mcp_server.create_initialization_options())


# Build a small Starlette app for the two MCP endpoints
sse_app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        # Note the trailing slash to avoid 307 redirects
        Mount("/messages/", app=transport.handle_post_message),
    ]
)


app = FastAPI()

# Mock client store
CLIENTS = {"test_client": "secret_1234"}


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


@app.post("/token")
def generate_token(request: TokenRequest):
    if request.client_id in CLIENTS and CLIENTS[request.client_id] == request.client_secret:
        payload = {
            "sub": request.client_id,
            "exp": datetime.datetime.now() + datetime.timedelta(days=30),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/health")
def read_root():
    return {"message": "MCP SSE Server is running"}


app.mount("/", sse_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8100)
