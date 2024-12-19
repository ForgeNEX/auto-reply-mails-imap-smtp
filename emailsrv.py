import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
import requests
import json
import os
import time

# Ruta del archivo de configuración
CONFIG_FILE = "config.json"
# Archivo para almacenar IDs procesados
PROCESSED_IDS_FILE = "processed_ids.json"

# Cargar configuración
try:
    with open(CONFIG_FILE, "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print(f"Error: Archivo '{CONFIG_FILE}' no encontrado.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: No se pudo parsear '{CONFIG_FILE}': {e}")
    exit(1)

IMAP_SERVER = config.get("IMAP_SERVER")
IMAP_PORT = config.get("IMAP_PORT", 993)
EMAIL_USER = config.get("EMAIL_USER")
EMAIL_PASS = config.get("EMAIL_PASS")
SMTP_SERVER = config.get("SMTP_SERVER")
SMTP_PORT = config.get("SMTP_PORT", 465)  # Cambiar a 465 para SSL
FILTER_KEYWORD = config.get("FILTER_KEYWORD", "URGENTE")
PROMPT = config.get("PROMPT", "Escribe una respuesta profesional al correo que te ha llegado dando informacion sobre el tema que preguntan.")
LLM_API_URL = config.get("LLM_API_URL")
LLM_MODEL = config.get("LLM_MODEL")

# Cargar IDs procesados
if os.path.exists(PROCESSED_IDS_FILE):
    with open(PROCESSED_IDS_FILE, "r") as f:
        processed_ids = json.load(f)
else:
    processed_ids = []

# Guardar IDs procesados
def save_processed_ids():
    with open(PROCESSED_IDS_FILE, "w") as f:
        json.dump([str(id) for id in processed_ids], f)

# Conexión al servidor IMAP
def connect_to_email():
    try:
        print(f"Conectando al servidor IMAP: {IMAP_SERVER}:{IMAP_PORT}")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("Conexión IMAP exitosa.")
        return mail
    except Exception as e:
        print(f"Error al conectar al servidor IMAP: {e}")
        return None

# Leer correos y filtrar por palabra clave
def read_and_filter_emails():
    mail = connect_to_email()
    if not mail:
        return []

    try:
        print("Seleccionando bandeja de entrada.")
        mail.select("inbox")  # Selecciona la bandeja de entrada
        status, messages = mail.search(None, "UNSEEN")  # Buscar solo correos no leídos
        if status != "OK":
            print("Error al buscar correos.")
            return []

        email_ids = messages[0].split()
        print(f"Número total de correos no leídos: {len(email_ids)}")
        filtered_emails = []

        for email_id in email_ids:
            email_id_str = email_id.decode()  # Convertir ID a cadena para manipular
            if email_id_str in processed_ids:
                print(f"Correo ID {email_id_str} ya procesado, saltando.")
                continue  # Saltar correos ya procesados

            print(f"Fetching correo ID: {email_id_str}")
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                print(f"Error al obtener el correo con ID {email_id_str}.")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg.get("Subject", ""))[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    print(f"Asunto del correo: {subject}")

                    if subject and FILTER_KEYWORD.lower() in subject.lower():
                        print(f"Correo con ID {email_id_str} coincide con el filtro.")
                        filtered_emails.append({
                            "id": email_id_str,
                            "subject": subject,
                            "from": msg.get("From"),
                            "body": get_email_body(msg)
                        })
                        processed_ids.append(email_id_str)
        save_processed_ids()
        return filtered_emails

    except Exception as e:
        print(f"Error al leer correos: {e}")
        return []
    finally:
        mail.logout()

# Obtener el cuerpo del correo
def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    return part.get_payload(decode=True).decode()
                except Exception as e:
                    print(f"Error al decodificar el cuerpo del correo: {e}")
                    pass
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            try:
                return msg.get_payload(decode=True).decode()
            except Exception as e:
                print(f"Error al decodificar el cuerpo del correo: {e}")
                pass
    return ""

# Enviar correos con SMTP
def send_email(to_address, subject, body):
    try:
        print(f"Conectando al servidor SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:  # Cambiar a SMTP_SSL con timeout
            server.set_debuglevel(1)  # Habilitar depuración SMTP
            server.login(EMAIL_USER, EMAIL_PASS)
            msg = MIMEText(body)
            msg["From"] = EMAIL_USER
            msg["To"] = to_address
            msg["Subject"] = subject
            server.sendmail(EMAIL_USER, to_address, msg.as_string())
            print(f"Correo enviado a {to_address}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

# Procesar correo con el LLM
def process_email_with_prompt(email_body):
    try:
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": email_body}
            ]
        }
        print("Enviando solicitud al LLM...")
        with requests.post(LLM_API_URL, json=payload, stream=True) as response:
            response.raise_for_status()
            print("Procesando respuesta del LLM...")
            full_response = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        part = json.loads(line)
                        if "message" in part and "content" in part["message"]:
                            full_response += part["message"]["content"]
                        if part.get("done", False):
                            break
                    except json.JSONDecodeError as e:
                        print(f"Error decodificando fragmento del LLM: {e}")
                        continue
            return full_response if full_response else "No se pudo generar una respuesta."
    except Exception as e:
        print(f"Error al procesar correo con LLM: {e}")
        return "No se pudo procesar el correo."

# Ciclo principal para verificar correos periódicamente
def main_loop():
    while True:
        print("Iniciando verificación de correos...")
        emails = read_and_filter_emails()
        if emails:
            print("Correos filtrados:")
            for email in emails:
                print(f"De: {email['from']}\nAsunto: {email['subject']}\nCuerpo: {email['body']}\n")
                response = process_email_with_prompt(email['body'])
                send_email(email['from'], f"Re: {email['subject']}", response)
        else:
            print("No se encontraron correos que coincidan con el filtro.")
        time.sleep(300)  # Esperar 5 minutos

if __name__ == "__main__":
    main_loop()
