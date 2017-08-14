import configparser
import logging
import os
import time

import telegram
from telegram import ReplyKeyboardMarkup, update, ChatAction
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from model.consignacion import consignacion
from model.retiro import retiro
from model.traslado import traslado
from model.usuario import usuario
from tools import tools

# Cambiamos direccion horaria
os.environ['TZ'] = 'America/Bogota'
time.tzset()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# cargamos la configuración
config = configparser.ConfigParser()
config.read("etc/config.ini")

REGISTRO_P1, REGISTRO_P2, OPCIONES, TRASLADO, RETIRO, CONSIGNACION, CONFIRMACION_TRASLADO, CONFIRMACION_RETIRO, REGISTRO_MOVIMIENTOS = range(
    9)
TOKEN = config['KEYS']['bot_api']


def start(bot, update):
    user = update.message.from_user

    logging.info("Usuario %s ha iniciado una conversación" % user.name)
    # para usuario no registrado
    retorno = REGISTRO_P1

    typing(bot, update)
    us = usuario(user.id)
    user_register = us.verificar_usuario_registrado()

    # Verificacion de si el usuario se encuentra registrado
    if user_register:
        update.message.reply_text('Bienvenid@ %s a MiBanco ' % (user.name))
        show_options(bot, update)
        # Opciones para usuario registrado
        retorno = OPCIONES

    else:
        msg = "Bienvenid@ %s a MiBanco, por lo que veo no estás registrado, ¿Deseas registrarte? *S/N*" % (user.name)
        send_message_MARKDOWN(bot, update, msg)

    return retorno


# REGISTRO  NUEVO USUARIO
def registro_p1(bot, update):
    respuesta = update.message.text
    user = update.message.from_user  # para obtener los datos del usuario

    if respuesta == 'S' or respuesta == 's':
        update.message.reply_text('Ingresa tu email para notificarte todas las acciones realizadas con tu cuenta')
        logging.info("Usuario %s en registro_p1" % user.name)
        return REGISTRO_P2

    else:
        update.message.reply_text('OK, espero serte útil en otra ocasión, Dios te bendiga %s' % (user.name))


def registro_p2(bot, update):
    user = update.message.from_user

    logging.info("Usuario %s en proceso de registro 2" % user.name)

    email = update.message.text

    retorno = OPCIONES

    us = usuario(num_cuenta=user.id, nombre=user.first_name, apellido=user.last_name, email=email)

    typing(bot, update)
    status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], email,
                              "Registrando a MiBanco",
                              "Estamos procesando tus datos, si todo sale bien recibirás un Email confirmando tu registro",
                              True)

    typing(bot, update)
    time.sleep(1)
    if status:
        typing(bot, update)
        registrado = us.registrar()
        if registrado:
            update.message.reply_text("Te hemos enviado un Email para verificar si el Email ingresado es válido")
            msg = "*Tus Datos*\n" \
                  "*Nombre de usuario* : %s \n" \
                  "*Número de Cuenta* : %s \n" \
                  "*Saldo* : $500\n" \
                  "*Email* : %s" % (user.name, user.id, email)

            typing(bot, update)
            tools.send_email(config['SMTP']['email'], config['SMTP']['password'], email,
                             "Bienvenido a MiBanco",
                             "Nos Alegra que hagas parte de este KodeFest t.me/MiBanco_bot", False)

            send_message_MARKDOWN(bot, update, msg)
            logging.info("Usuario %s registrado" % user.name)
            # Opciones
            show_options(bot, update)
        else:
            update.message.reply_text("Ups!, Ocurrió un error en tu registro, no se pudo realizar")
            retorno = ConversationHandler.END
    else:
        update.message.reply_text("No pudimos enviarte el Email, intentalo de nuevo con /start:(")
        retorno = ConversationHandler.END

    return retorno


# OPCIONES PARA USUARIO REGISTRADO
def opciones(bot, update):
    retorno = OPCIONES
    user = update.message.from_user
    op = update.message.text

    if op == 'Traslado':
        logging.info("Usuario %s en Traslado" % user.name)
        retorno = TRASLADO
        typing(bot, update)
        us = usuario(user.id)
        us.cargar_datos()
        resultado = us.verificar_traslado_espera()
        # Si tiene un traslado en espera
        if resultado[0]:
            typing(bot, update)
            status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                      "Confirmación de Traslado",
                                      "El <b>Código</b> de Traslado es : %s" % resultado[1],
                                      True)

            if status:
                send_message_MARKDOWN(bot, update, "Usted tiene un traslado en espera\n\n"
                                                   "Verifique su Email e ingrese el código de verificación del Traslado\n"
                                                   "seguido de *A* -> Aceptar ó \n"
                                                   "*C* -> Cancelar\n"
                                                   "Ejemplo : 1111 - A")

            else:
                send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                                   "Su *Código* de Traslado es : %s" % (us.email, resultado[1]))

            retorno = CONFIRMACION_TRASLADO

        else:
            update.message.reply_text(
                "Por favor ingrese el número de cuenta a la que desea realizarle el traslado y el monto del mismo.\n"
                "Ejemplo : 78128456 - 50")
    if op == 'Retiro':
        logging.info("Usuario %s en Retiro" % user.name)
        retorno = RETIRO
        typing(bot, update)
        us = usuario(user.id)
        us.cargar_datos()
        resultado = us.verificar_retiro_espera()
        # Si tiene un retiro en espera
        if resultado[0]:
            typing(bot, update)
            status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                      "Confirmación de Retiro",
                                      "El <b>Código</b> de confirmación de Retiro es : %s" % resultado[1],
                                      True)

            if status:
                send_message_MARKDOWN(bot, update, "Usted tiene un Retiro en espera\n\n"
                                                   "Verifique su Email e ingrese el código de verificación del Retiro\n"
                                                   "seguido de *A* -> Aceptar ó \n"
                                                   "*C* -> Cancelar\n"
                                                   "Ejemplo : 1111 - A")

            else:
                send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                                   "Su *Código* de confirmación de Retiro es : %s" % (
                                          us.email, resultado[1]))

            retorno = CONFIRMACION_RETIRO
        else:
            update.message.reply_text("Por favor escriba la cantidad de dinero a retirar")

    if op == 'Consignación':
        logging.info("Usuario %s en Consignación" % user.name)
        update.message.reply_text("Ingrese el valor a consignar a su cuenta")
        retorno = CONSIGNACION

    if op == 'Registro Movimientos':
        logging.info("Usuario %s solicitando Registro Movimientos" % user.name)
        typing(bot, update)
        update.message.reply_text("Estoy generando el informe, espera por favor")
        us = usuario(user.id)
        typing(bot, update)
        us.cargar_datos()
        resultado = us.registro_movimientos('res/')
        if resultado[0]:
            typing(bot, update)
            bot.sendDocument(chat_id=update.message.chat.id, document=open('%s' % resultado[1], 'rb'))
            os.remove("%s" % resultado[1])
            logging.info("Usuario %s informe enviado" % user.name)
        else:
            update.message.reply_text("No pude generar el informe, lo siento")

    return retorno


# TRASLADOS
def traslados(bot, update):
    update.message.reply_text("Estoy procesando tú petición...")
    retorno = OPCIONES
    user = update.message.from_user
    msg = update.message.text.replace(" ", "").split("-")

    numc_receptor = msg[0]
    monto = int(msg[1])

    # Se verifica que el usuario receptor se encuentre registrado
    typing(bot, update)
    us = usuario(num_cuenta=user.id)
    us2 = usuario(numc_receptor)
    if us2.verificar_usuario_registrado():

        typing(bot, update)
        us.cargar_datos()
        typing(bot, update)
        tras = traslado(numc_usuario_expedidor=user.id, numc_usuario_receptor=numc_receptor, monto_traslado=monto)
        typing(bot, update)
        tras_result = tras.realizar_traslado()

        if tras_result[0]:
            typing(bot, update)
            status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                      "Confirmación de Traslado",
                                      "El <b>Código</b> de confirmación de Traslado es : %s" % tras_result[1],
                                      True)
            if status:
                send_message_MARKDOWN(bot, update,
                                      "Verifique su Email e ingrese el código de verificación del traslado\n"
                                      "seguido de *A* -> Aceptar ó \n"
                                      "*C* -> Cancelar\n"
                                      "Ejemplo : 1111 - A")
            else:
                send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                                   "Su *Código* de Traslado es : %s" % (us.email, tras_result[1]))

            retorno = CONFIRMACION_TRASLADO

        else:
            logging.info("Usuario sin fondos")
            send_message_MARKDOWN(bot, update,
                                  "Lo sentimos no se pudo realizar el Traslado razón : %s" % tras_result[1])

    else:
        update.message.reply_text("El destinario no se encuentra registrado")

    return retorno


def confirmacion_traslado(bot, update):
    user = update.message.from_user

    logging.info('Usuario %s confirmando el traslado', user.name)

    retorno = OPCIONES

    codigo, estado_traslado = update.message.text.replace(" ", "").split("-")

    tras = traslado(id_traslado=codigo)

    typing(bot, update)
    resultado = tras.actualizar_traslado(estado_traslado)

    if resultado[0]:
        typing(bot, update)
        # Envío de email de notificacion al usuario receptor del traslado
        resultado2 = resultado[1].split("-")
        typing(bot, update)
        status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], resultado2[0],
                                  "Usted ha recibido un Traslado de Dinero",
                                  "El monto recibido es : $%s y fue enviado por %s con número de cuenta %s" %
                                  (resultado2[1], resultado2[2], resultado2[3]),
                                  True)
        if status:
            update.message.reply_text("Email de notificación de Traslado enviado")
        typing(bot, update)
        us = usuario(user.id)
        us.cargar_datos()
        send_message_MARKDOWN(bot, update, "Traslado realizado con éxito\n"
                                           "*Tu nuevo saldo es de* : $%s" % us.saldo)

        show_options(bot, update)
    else:
        update.message.reply_text(resultado[1])
        if estado_traslado in ('C', 'c'):
            show_options(bot, update)
        else:
            retorno = CONFIRMACION_TRASLADO
    return retorno


# RETIROS
def retiros(bot, update):
    update.message.reply_text("Estoy procesando tú petición...")
    retorno = OPCIONES
    user = update.message.from_user
    monto_retirar = int(update.message.text)

    us = usuario(num_cuenta=user.id)
    typing(bot, update)
    us.cargar_datos()

    typing(bot, update)
    # Se crea el retiro
    reti = retiro(numc_usuario=us.num_cuenta, monto_retiro=monto_retirar)
    typing(bot, update)

    retiro_result = reti.realizar_retiro()

    if retiro_result[0]:
        typing(bot, update)
        status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                  "Confirmación de Retiro",
                                  "El <b>Código</b> de confirmación de Retiro es : %s" % retiro_result[1],
                                  True)
        if status:
            send_message_MARKDOWN(bot, update, "Verifique su Email e ingrese el código de verificación del Retiro\n"
                                               "seguido de *A* -> Aceptar ó \n"
                                               "*C* -> Cancelar\n"
                                               "Ejemplo : 1111 - A")
        else:
            send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                               "Su *Código* de Retiro es : %s" % (us.email, retiro_result[1]))

        retorno = CONFIRMACION_RETIRO

    else:
        logging.info("Usuario sin fondos")
        send_message_MARKDOWN(bot, update, "Lo sentimos no se pudo realizar el Retiro razón : %s" % retiro_result[1])

    return retorno


def confirmacion_retiro(bot, update):
    user = update.message.from_user

    logging.info('Usuario %s confirmando el retiro', user.name)

    retorno = OPCIONES

    codigo, estado_retiro = update.message.text.replace(" ", "").split("-")

    ret = retiro(id_retiro=codigo)

    typing(bot, update)
    resultado = ret.actualizar_retiro(estado_retiro)

    if resultado[0]:
        typing(bot, update)
        us = usuario(user.id)
        us.cargar_datos()

        send_message_MARKDOWN(bot, update, "Retiro realizado con éxito\n"
                                           "*Tu nuevo saldo es de* : $%s" % us.saldo)
        show_options(bot, update)
    else:
        update.message.reply_text(resultado[1])
        if estado_retiro == 'C':
            show_options(bot, update)
        else:
            retorno = CONFIRMACION_RETIRO
    return retorno


# CONSIGNACIONES
def consignaciones(bot, update):
    update.message.reply_text("Estoy procesando tú petición...")
    retorno = OPCIONES
    user = update.message.from_user
    valor = int(update.message.text)

    consig = consignacion(numc_usuario=user.id, monto_consig=valor)
    typing(bot, update)
    resultado = consig.realizar_consignacion()

    if resultado[0]:
        send_message_MARKDOWN(bot, update, "Consignación realizada con éxito\n"
                                           "*Tu nuevo saldo es de* : $%s" % resultado[1])
    else:
        update.message.reply_text("No he podido procesar tu consignación : %s" % resultado[1])

    return retorno


# ERRORES EN INGRESO DE DATOS
def registro_incorrecto_p1(bot, update):
    user = update.message.from_user

    msg = "%s recuerda responder *S* o *s* en caso afirmativo, *N* o *n* en caso negativo" % user.first_name
    send_message_MARKDOWN(bot, update, msg)

    logging.info("Usuario %s en registro_incorrecto_p1" % user.name)

    return REGISTRO_P1


def registro_incorrecto_p2(bot, update):
    user = update.message.from_user

    update.message.reply_text("%s has ingresado una direccion de correo invalida" % user.first_name)
    logging.info("Usuario %s en registro_incorrecto_p2" % user.name)

    return REGISTRO_P2


def retiro_incorrecto(bot, update):
    user = update.message.from_user

    update.message.reply_text("%s has ingresado una cantidad inválida" % user.first_name)
    logging.info("Usuario %s en retiro_incorrecto" % user.name)

    return RETIRO


def opciones_incorrecto(bot, update):
    update.message.reply_text("Opción incorrecta, por favor haga uso del teclado")
    show_options(bot, update)
    return OPCIONES


def traslado_incorrecto(bot, update):
    update.message.reply_text("Formato incorrecto")
    update.message.reply_text(
        "Por favor ingrese el número de cuenta a la que desea realizarle el traslado y el monto del mismo.\n"
        "Ejemplo : 78128456 - 50")

    return TRASLADO


def confirmacionT_incorrecto(bot, update):
    update.message.reply_text("Formato incorrecto")
    send_message_MARKDOWN(bot, update, "Ingrese el código de verificación del Traslado\n"
                                       "seguido de *A* -> Aceptar ó \n"
                                       "*C* -> Cancelar\n"
                                       "Ejemplo : 1111 - A")

    return CONFIRMACION_TRASLADO


def confirmacionR_incorrecto(bot, update):
    update.message.reply_text("Formato incorrecto")
    send_message_MARKDOWN(bot, update, "Ingrese el código de verificación del Retiro\n"
                                       "seguido de *A* -> Aceptar ó \n"
                                       "*C* -> Cancelar\n"
                                       "Ejemplo : 1111 - A")
    return CONFIRMACION_RETIRO


def consig_incorrecto(bot, update):
    update.message.reply_text("Valor inválido")
    update.message.reply_text("Ingrese el valor a consignar a su cuenta")

    return CONSIGNACION


# OTROS COMANDOS
def micuenta(bot, update):
    typing(bot, update)
    user = update.message.from_user
    us = usuario(user.id)
    typing(bot, update)
    if us.verificar_usuario_registrado():
        typing(bot, update)
        us.cargar_datos()
        msg = "*Tus Datos*\n" \
              "*Nombre de usuario* : %s \n" \
              "*Número de Cuenta* : %s \n" \
              "*Saldo* : $%s\n" \
              "*Email* : %s" % (us.nombre + " " + us.apellido, us.num_cuenta, us.saldo, us.email)
        send_message_MARKDOWN(bot, update, msg)
        logging.info("Mi cuenta cargada del usuario %s cargados con exito ", user.id)
    else:
        msg = "Lo siento, *no estás registrado*"
        send_message_MARKDOWN(bot, update, msg)

    show_options(bot, update)
    return OPCIONES


def help(bot, update):
    send_message_MARKDOWN(bot, update,
                          "Con *MiBanco* puedes crear una cuenta y así realizar traslados, retiros, y mucho más. "
                          "Además no te preocupes MiBanco te avisará cada vez que realices un traslado o retiro vía Email "
                          "para que lo confirmes o canceles.\n\n"
                          "Los *comandos* son los siguientes:\n\n"
                          "/start - Iniciar bot y mostrar opciones\n"
                          "/micuenta - Muestra los datos de tu cuenta\n"
                          "/help - Te muestra los comandos a usar\n"
                          "/cancel - Cancelas la operación actual\n\n"
                          "Las *operaciones* que puedes realizar son:\n\n"
                          "- Traslados\n"
                          "- Retiros\n"
                          "- Consignaciones\n"
                          "- Obtener registro de movimientos en pdf")

    show_options(bot, update)
    return OPCIONES


def cancelar(bot, update: update):
    user = update.message.from_user
    update.message.reply_text('Hasta luego %s' % user.first_name)

    return ConversationHandler.END


# OTRAS FUNCIONES
def show_options(bot, update):
    keyboard = [['Traslado', 'Retiro'], ['Consignación', 'Registro Movimientos'], ['/start'],
                ['/micuenta', '/help', '/cancel']]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.message.chat.id,
                     text="¿Qué deseas hacer?",
                     reply_markup=reply_markup, one_time_keyboard=True)


def send_message_MARKDOWN(bot, update, msg: str):
    bot.send_message(chat_id=update.message.chat.id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN)


def typing(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)


def error(bot, update: update, error):
    logger.warning('Update "%s" causo el error "%s"' % (update, error))


def main():
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            REGISTRO_P1: [RegexHandler('^(S|N|s|n)$', registro_p1),
                          MessageHandler(Filters.text, registro_incorrecto_p1)],

            REGISTRO_P2: [
                RegexHandler('^[a-z0-9]+[_a-z0-9\.-]*[a-z0-9]+@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', registro_p2),
                MessageHandler(Filters.text, registro_incorrecto_p2)],

            OPCIONES: [RegexHandler('^(Traslado|Retiro|Consignación|Registro Movimientos)$', opciones),
                       MessageHandler(Filters.text, opciones_incorrecto)],

            TRASLADO: [RegexHandler('^\d+\s?\-\s?\d+$', traslados), MessageHandler(Filters.text, traslado_incorrecto)],

            CONFIRMACION_TRASLADO: [RegexHandler('^\d+\s?-\s?(A|a|C|c)$', confirmacion_traslado),
                                    MessageHandler(Filters.text, confirmacionT_incorrecto)],

            RETIRO: [RegexHandler('^\d+$', retiros), MessageHandler(Filters.text, retiro_incorrecto)],

            CONFIRMACION_RETIRO: [RegexHandler('^\d+\s?-\s?(A|a|C|c)$', confirmacion_retiro),
                                  MessageHandler(Filters.text, confirmacionR_incorrecto)],

            CONSIGNACION: [RegexHandler('^\d+$', consignaciones), MessageHandler(Filters.text, consig_incorrecto)],

        },

        fallbacks=[CommandHandler('cancel', cancelar), CommandHandler("micuenta", micuenta),
                   CommandHandler("help", help)]
    )

    dp.add_handler(conv_handler)

    # log errores
    dp.add_error_handler(error)

    # Iniciamos el bot
    # updater.start_polling()

    PORT = int(os.environ.get('PORT', '5000'))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)

    updater.bot.set_webhook("https://kodefest12.herokuapp.com/" + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
