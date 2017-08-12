from db.connection import connection
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)


class usuario:

    def __init__(self, num_cuenta : int = 0, contrasena : str = '', saldo : float = 0, nombre : str = '',
                 apellido : str = '', edad : int = 0,cc : str = '', email : str = '', estado : str = '' ):
        self.num_cuenta = num_cuenta
        self.saldo = saldo
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.cc = cc
        self.email = email
        self.estado = estado


    def registrar(self):
        con = connection()
        retorno = False
        if not self.verificar_usuario_registrado():
            rowcount = con.execute('INSERT INTO Usuarios VALUES (%s, %s, %s, %s, %s ,%s, %s ,%s)',
                        [self.num_cuenta, self.saldo, self.nombre, self.apellido, self.edad,
                         self.cc, self.email, self.estado], True, 'DDL')
            if rowcount not in ('Error', 'Invalido') and rowcount > 0:
                retorno = True
                logging.info("Usuario con email %s y numero de cuenta %s insertado correctamente" % (self.email, self.num_cuenta))
            else:
                logging.warning('Error registrando usuario %s' % self.email)
        else:
            logging.warning("EL usuario con email %s ya esta registrado" % self.email)

        return retorno

    def verificar_usuario_registrado(self) -> bool:
        retorno = False
        con = connection()
        output = con.execute('SELECT nombre FROM Usuarios WHERE num_cuenta = %s', [self.num_cuenta])
        if len(output) == 1:
            retorno = True
            logging.info(
                "Usuario con email %s y numero de cuenta %s ya se encuentra registrado" % (self.email, self.num_cuenta))
        else:
            logging.warning("EL usuario con email %s no esta registrado" % self.email)

        return  retorno

if __name__ == '__main__':
    us = usuario(111111)
    print(us.verificar_usuario_registrado())
    us2 = usuario(111112, "sad", 500, "pepito perez")
    print(us2.registrar())