# Email LLM Responder

Email LLM Responder es un sistema automatizado que permite recibir correos electrónicos, analizarlos con un modelo de lenguaje (LLM) y generar respuestas profesionales basadas en el contenido del correo y un prompt predefinido.

El objetivo principal es agilizar las respuestas a consultas mediante inteligencia artificial, aumentando la eficiencia y la calidad de la comunicación en empresas de informática, como **ForgeNEX**.

---

## Características

- **Recepción automática de correos**: Se conecta a un servidor IMAP para recibir correos nuevos.
- **Procesamiento inteligente**: Usa un LLM para analizar el contenido del correo y generar respuestas personalizadas.
- **Envío de respuestas automatizadas**: Utiliza un servidor SMTP para responder profesionalmente a cada correo.
- **Soporte para respuestas en streaming**: Maneja respuestas largas recibidas como fragmentos del LLM.
- **Configuración sencilla**: Todos los parámetros se configuran desde un archivo `config.json`.

---

## Configuración

### Requisitos previos
- Python 3.8 o superior
- Servidor IMAP para recibir correos
- Servidor SMTP para enviar correos
- API de LLM disponible para procesar las respuestas

### Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/forgenex/email-llm-responder.git
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura el archivo `config.json` con tus parámetros:
   ```json
   {
       "IMAP_SERVER": "imap.tu-servidor.com",
       "IMAP_PORT": 993,
       "EMAIL_USER": "tu-correo@dominio.com",
       "EMAIL_PASS": "tu-contraseña",
       "SMTP_SERVER": "smtp.tu-servidor.com",
       "SMTP_PORT": 465,
       "FILTER_KEYWORD": "URGENTE",
       "PROMPT": "Escribe una respuesta profesional al correo que te ha llegado dando información sobre el tema que preguntan. Gracias por confiar en ForgeNEX.",
       "LLM_API_URL": "http://localhost:11434/api/chat",
       "LLM_MODEL": "tu-modelo-llm"
   }
   ```
4. Ejecuta el script principal:
   ```bash
   python emailsrv.py
   ```

---

## Avance privado

1. **Integración con un CRM**
   - Almacenar información del correo en un sistema de gestión de relaciones con clientes (CRM).
   - Asociar respuestas con tickets de soporte.

2. **Respuestas Multilingües**
   - Detectar el idioma del correo y generar respuestas en el mismo idioma.

3. **Análisis Estadístico**
   - Generar métricas como tiempo promedio de respuesta y clasificación de tipos de consultas.

4. **Automatización Avanzada**
   - Implementar triggers para respuestas más específicas basadas en palabras clave.

5. **Integración con Calendarios**
   - Procesar correos para agendar citas o reuniones automáticamente.

---

## Imagen de Respuesta Dummy
![Ilustración del flujo de trabajo del sistema Email LLM Responder](https://i.ibb.co/BNr7XFm/screen.png)

