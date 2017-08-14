import smtplib
import logging
from weasyprint import HTML
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Herramientas varias
def send_email(correo_from_send: str, password: str, correo_to_send: str, asunto: str, mensaje: str,
               is_html: bool) -> bool:
    # Si se puede enviar el email entonces el status permanecera siendo True
    status = True

    fromaddr = correo_from_send
    toaddr = correo_to_send
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = asunto
    if is_html:

        body = mensaje
        msg.attach(MIMEText(body.encode('utf-8'), 'html', 'UTF-8'))

    else:
        body = mensaje
        msg.attach(MIMEText(body, 'plain', 'UTF-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Login
        try:
            server.login(fromaddr, password)
            text = msg.as_string()
            # Send message
            try:
                server.sendmail(fromaddr, toaddr, text)
            except Exception as err:  # try to avoid catching Exception unless you have too , http://stackoverflow.com/questions/984526/correct-way-of-handling-exceptions-in-python
                status = False
                logging.error("\nOcurrio un error inesperado al enviar el email : %s" % err)
            finally:
                server.quit()
        except smtplib.SMTPAuthenticationError as err:
            server.quit()
            status = False
            logging.error("\nOcurrio un error al tratar de autenticarse en el servidor SMPT : %s " % err)

    except smtplib.socket.gaierror as err:
        status = False
        logging.error("\nOcurrio un error al tratar crear el cliente SMTP : %s " % err)

    return status


def createPDF(strHTML, ruta_namePDF):
    HTML(string=strHTML).write_pdf(ruta_namePDF)
