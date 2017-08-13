import time
import os
import configparser
from tools import tools
import logging
import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, update, ChatAction
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from model.usuario import usuario
from model.traslado import traslado

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)

# cargamos la configuración
config = configparser.ConfigParser()
config.read("etc/config.ini")


REGISTRO_P1, REGISTRO_P2, OPCIONES, TRASLADO, RETIRO, PRESTAMO, CONFIRMACION_TRASLADO= range(7)
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
    registrado = us.registrar()
    if registrado:

        msg2 = "Tus Datos\n" \
               "Nombre de usuario : %s \n" \
               "Número de Cuenta : %s \n" \
               "Saldo : $500\n" \
               "Email : %s" % (user.name, user.id, email)

        typing(bot, update)
        status = tools.send_email(config['SMTP']['email'],config['SMTP']['password'], email,
                         "Bienvenido a MiBanco", "Nos Alegra que hagas parte de este KodeFest t.me/MiBanco_bot \n\n\n%s" %msg2, False)

        if status:
            update.message.reply_text("Te hemos enviado un Email con la información registrada")
        else:
            update.message.reply_text("No pudimos enviarte el Email :(")

        msg = "*Tus Datos*\n" \
              "*Nombre de usuario* : %s \n" \
              "*Número de Cuenta* : %s \n" \
              "*Saldo* : $500\n" \
              "*Email* : %s" % (user.name, user.id, email)
        send_message_MARKDOWN(bot, update, msg)
        logging.info("Usuario %s registrado" % user.name)
        # Opciones
        show_options(bot, update)
    else:
        msg = "Ups!, Ocurrió un error en tu registro, no se pudo realizar"
        retorno = ConversationHandler.END

    return retorno



def registro_incorrecto_p1(bot, update):
    user = update.message.from_user

    msg = "%s recuerda responder *S* o *s* en caso afirmativo, *N* o *n* en caso negativo" % user.first_name
    send_message_MARKDOWN(bot,update, msg)

    logging.info("Usuario %s en registro_incorrecto_p1" % user.name)

    return REGISTRO_P1

def registro_incorrecto_p2(bot, update):
    user = update.message.from_user

    update.message.reply_text("%s has ingresado una direccion de correo invalida" %user.first_name)
    logging.info("Usuario %s en registro_incorrecto_p2" % user.name)

    return REGISTRO_P2


def opciones(bot, update):
    retorno = TRASLADO
    user = update.message.from_user
    op = update.message.text

    if op == 'Traslado':
        typing(bot,update)
        us = usuario(user.id)
        us.cargar_datos()
        resultado = us.verificar_traslado_espera()
        if resultado[0]:
            typing(bot, update)
            status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                      "Confirmación de Traslado",
                                      "El <bold>Código</bold> de Traslado es : %s" % resultado[1],
                                      True)
            retorno = CONFIRMACION_TRASLADO
            if status:
                send_message_MARKDOWN(bot, update, "Usted tiene un traslado en espera\n\n"
                                                   "Verifique su Email e ingrese el código de verificación del traslado\n"
                                                   "seguido de *A* -> Aceptar ó \n"
                                                   "*C* -> Cancelar\n"
                                                   "Ejemplo : 1111 - A")

            else:
                send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                                   "Su *Código* de Traslado es : %s" % (us.email, resultado[1]))


        else:
            update.message.reply_text("Por favor ingrese el número de cuenta a la que desea realizarle el traslado y el monto del mismo.\n"
                                  "Ejemplo : 78128456 - 50")
    if op == 'Retiro':
        update.message.reply_text("Por favor escriba la cantidad de dinero a retirar")


    if op == 'Préstamo':
        update.message.reply_text("p")


    logging.info("Usuario %s en opciones" % user.name)

    return retorno

def traslados(bot, update):
    retorno = OPCIONES
    user = update.message.from_user
    msg = update.message.text.replace(" ","").split("-")

    numc_receptor = msg[0]
    monto = int(msg[1])

    # Se verifica que el usuario receptor se encuentre registrado
    typing(bot, update)
    us = usuario(num_cuenta=user.id)
    us2 = usuario(numc_receptor)
    if us2.verificar_usuario_registrado():

        typing(bot, update)
        us.cargar_datos()
        typing(bot,update)
        tras = traslado(numc_usuario_expedidor=user.id, numc_usuario_receptor=numc_receptor, monto_traslado=monto)
        typing(bot, update)
        tras_result = tras.realizar_traslado()

        if tras_result [0]:
            typing(bot, update)
            status = tools.send_email(config['SMTP']['email'], config['SMTP']['password'], us.email,
                                      "Confirmación de Traslado",
                                      "El <bold>Código</bold> de Traslado es : %s" % tras_result[1],
                                      True)
            if status:
                send_message_MARKDOWN(bot,update,"Verifique su Email e ingrese el código de verificación del traslado\n"
                                      "seguido de *A* -> Aceptar ó \n"
                                             "*C* -> Cancelar\n"
                                             "Ejemplo : 1111 - A" )
            else:
                send_message_MARKDOWN(bot, update, "Lo sentimos no pudimos enviar el Email a %s.\n" \
                                                  "Su *Código* de Traslado es : %s" % (us.email,tras_result[1]))

            retorno = CONFIRMACION_TRASLADO

        else:
            logging.info("Usuario sin fondos")
            send_message_MARKDOWN(bot, update, "Lo sentimos no se pudo realizar el Traslado razón : %s" % tras_result[1])

    else:
        update.message.reply_text("El destinario no se encuentra registrado")

    return retorno



def confirmacion_traslado(bot, update):
    user = update.message.from_user

    logging.info('Usuario %s confirmando el traslado', user.name)

    retorno = OPCIONES

    codigo, estado_traslado = update.message.text.replace(" ","").split("-")

    tras = traslado(id_traslado=codigo)

    typing(bot,update)
    resultado = tras.actualizar_traslado(estado_traslado)

    if resultado[0]:
        update.message.reply_text("Traslado realizado con éxito")
        show_options(bot,update)
    else:
        update.message.reply_text("Código de traslado erróneo \n"
                                  "Por favor ingrese el código correcto")
        retorno = CONFIRMACION_TRASLADO
    return retorno


def retiro(bot, update):
    pass



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
              "*Saldo* : %s\n" \
              "*Email* : %s" % (us.nombre + " " + us.apellido, us.num_cuenta, us.saldo, us.email)
        send_message_MARKDOWN(bot, update, msg)
    else:
        msg ="Lo siento, *no estás registrado*"
        send_message_MARKDOWN(bot, update, msg)

    show_options(bot, update)
    return OPCIONES



def error(bot, update : update, error):
    logger.warning('Update "%s" causo el error "%s"' % (update, error))

def cancelar(bot, update: update):
    '''user = update.message.from_user
    logger.info("Usuario %s cancelo la conversación." % user.first_name)
    # Removemos el teclado personalizado y mostramos el normal

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    time.sleep(1)

    update.message.reply_text('Hasta luego %s :)' % user.first_name,
                              reply_markup=ReplyKeyboardRemove())'''

    return ConversationHandler.END


def show_options(bot, update):
    keyboard = [['Traslado', 'Retiro'], ['Préstamo', "/micuenta"]]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.message.chat.id,
                     text="¿Qué deseas hacer?",
                     reply_markup=reply_markup, one_time_keyboard=True)


def send_message_MARKDOWN(bot, update, msg : str):
    bot.send_message(chat_id=update.message.chat.id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN)

def typing(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

def main():

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            REGISTRO_P1: [RegexHandler('^(S|N|s|n)$', registro_p1),  RegexHandler('^.*?$', registro_incorrecto_p1)],
            #MessageHandler.filters(Filters.text)
            REGISTRO_P2: [RegexHandler('^[a-z0-9]+[_a-z0-9\.-]*[a-z0-9]+@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', registro_p2),
                          RegexHandler('^.*?$', registro_incorrecto_p2)],

            OPCIONES: [RegexHandler('^(Traslado|Retiro|Préstamo)$', opciones)],

            TRASLADO: [RegexHandler('^\d+\s?\-\s?\d+$', traslados)],

            CONFIRMACION_TRASLADO: [RegexHandler('^\d+\s?-\s?(A|a|C|c)$', confirmacion_traslado)],

            RETIRO:[RegexHandler('^\d+$', retiro)]

        },


        fallbacks=[CommandHandler('cancel', cancelar), CommandHandler("micuenta", micuenta)]
    )

    dp.add_handler(conv_handler)

    # log errores
    dp.add_error_handler(error)

    # Iniciamos el bot
    #updater.start_polling()

    PORT = int(os.environ.get('PORT', '5000'))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)

    updater.bot.set_webhook("https://kodefest12.herokuapp.com/" + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()