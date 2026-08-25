import streamlit as st
import google.generativeai as genai

# Configuración de la página web
st.set_page_config(
    page_title="Tutor Virtual LOGO! Siemens",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Tutor Virtual: PLC Siemens LOGO!")
st.subheader("Asistente interactivo para automatización industrial y LOGO! Soft Comfort")

# Configuración en la barra lateral
with st.sidebar:
    st.header("⚙️ Configuración")
    
    api_key = st.text_input(
        "Clave API de Gemini", 
        type="password",
        help="Obtén tu clave gratis en Google AI Studio"
    )
    
    # Modelo actualizado a la versión actual exigida por la API
    model_name = st.selectbox(
        "Modelo:",
        ["gemini-3.6-flash", "gemini-2.5-flash"],
        index=0
    )
    
    st.subheader("🎓 Modo de Aprendizaje")
    pedagogy = st.radio(
        "Estilo de respuesta:",
        ["Guiado / Socrático (Te hace preguntas y da pistas)", "Directo (Explicaciones técnicas y soluciones directas)"]
    )

# Definición de Prompts de Sistema
PROMPTS = {
    "Guiado / Socrático (Te hace preguntas y da pistas)": """
    Eres "LogoBot", un tutor pedagógico de automatización industrial especializado en PLC LOGO! Siemens (0BA7, 0BA8, 8.3, 8.4) y LOGO! Soft Comfort.
    REGLA CLAVE: No des la respuesta del programa de inmediato. Haz preguntas guía al usuario para que razone las entradas (I), salidas (Q), temporizadores y lógica FBD/LADDER por sí mismo.
    """,
    "Directo (Explicaciones técnicas y soluciones directas)": """
    Eres "LogoBot", un consultor técnico experto en PLC LOGO! Siemens y LOGO! Soft Comfort.
    REGLA CLAVE: Da respuestas estructuradas indicando entradas (I), salidas (Q), bloques recomendados (RS, TON, TOF, etc.) y la explicación del flujo lógico paso a paso.
    """
}

# Inicialización del historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

# Guardar la configuración anterior para detectar cambios
if "last_model" not in st.session_state:
    st.session_state.last_model = model_name
if "last_pedagogy" not in st.session_state:
    st.session_state.last_pedagogy = pedagogy

# Reiniciar sesión si el usuario cambia el modelo o el modo
if st.session_state.last_model != model_name or st.session_state.last_pedagogy != pedagogy:
    st.session_state.chat_session = None
    st.session_state.last_model = model_name
    st.session_state.last_pedagogy = pedagogy

# Mostrar historial de conversación
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de texto del usuario
if user_prompt := st.chat_input("Escribe tu duda sobre LOGO! (ej: ¿Qué es LOGO!?)..."):
    if not api_key:
        st.error("👈 Por favor, ingresa tu API Key de Gemini en el menú lateral de la izquierda para comenzar.")
    else:
        # Registrar y mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generar respuesta con Gemini
        with st.chat_message("assistant"):
            with st.spinner("LogoBot está procesando la respuesta..."):
                try:
                    # Configurar la API y crear el modelo en cada mensaje para evitar desincronización
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=PROMPTS[pedagogy]
                    )
                    
                    # Convertir historial al formato requerido por Gemini
                    gemini_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(user_prompt)
                    bot_response = response.text
                    
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")