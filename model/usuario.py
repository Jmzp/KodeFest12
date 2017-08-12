from db.connection import connection
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class usuario:

    def __init__(self, num_cuenta : int = 0, saldo : float = 0, nombre : str = '',
                 apellido : str = '', email : str = '', estado : str = '' ):
        self.num_cuenta = num_cuenta
        self.saldo = saldo
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.estado = estado


    def cargar_datos(self):
        retorno = False
        if self.num_cuenta != 0:
            if self.verificar_usuario_registrado():
                cursor = connection.execute("SELECT * FROM Usuarios WHERE num_cuenta = %s", [self.num_cuenta])
                if cursor != None:
                    output = cursor.fetchall()
                    for out in output:
                        self.saldo = output[1]
                        self.nombre = output[2]
                        self.apellido = output[3]
                        self.email = output[4]
                        self.estado = output[5]
                retorno = True
                logging.info("Usuario cargado con exito")
        else:
            logging.error("Usuario invalido, datos no iniciados correctamente")
        return retorno


    def registrar(self):
        con = connection()
        retorno = False
        if not self.verificar_usuario_registrado() and not self.verificar_email():
            cursor = con.execute("INSERT INTO Usuarios VALUES (%s, %s, %s, %s, %s ,%s)",
                                   [self.num_cuenta, self.saldo, self.nombre, self.apellido,
                                    self.email, self.estado], True)
            if cursor != None:
                rowcount = cursor.rowcount
                if rowcount > 0:
                    retorno = True
                    logging.info("Usuario con email %s y numero de cuenta %s insertado correctamente" % (self.email, self.num_cuenta))
                else:
                    logging.warning('Error registrando usuario %s' % self.email)

            else:
                logging.error("Error interno al registrar usuario")

        else:
            logging.warning("El usuario o email ya esta registrado")

        con.close_connection()
        return retorno

    def verificar_usuario_registrado(self) -> bool:
        retorno = False
        con = connection()
        cursor = con.execute("SELECT nombre FROM Usuarios WHERE num_cuenta = %s", [self.num_cuenta])
        if cursor != None:
            output = cursor.fetchall()
            if len(output) == 1:
                retorno = True
                logging.info(
                    "Usuario %s ya se encuentra registrado" % (self.num_cuenta))
            else:
                logging.warning("EL usuario %s no esta registrado" % self.email)
        else:
            logging.error("Error interno al verificar usuario")

        con.close_connection()
        return retorno

    def verificar_email(self):
        retorno = False
        con = connection()
        cursor = con.execute("SELECT nombre FROM Usuarios WHERE email = %s", [self.email])
        if cursor != None:
            output = cursor.fetchall()
            if len(output) >= 1:
                retorno = True
                logging.info(
                    "Email %s ya se encuentra registrado" % (self.email))
            else:
                logging.warning("El email %s no esta registrado" % self.email)
        else:
            logging.error("Error interno al verificar usuario")

        con.close_connection()
        return retorno

if __name__ == '__main__':
    us = usuario(111111)
    print(us.verificar_usuario_registrado())
    us2 = usuario(111113, "sad", 500, "pepito perez")
    print(us2.registrar())