import logging, time
from db.connection import connection
from tools.tools import createPDF

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class usuario:
    # A -> Activo, I -> Inactivo (Cuenta cancelada)
    def __init__(self, num_cuenta: int = 0, saldo: int = 500, nombre: str = '',
                 apellido: str = '', email: str = '', estado: str = 'A'):
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
                con = connection()
                cursor = con.execute("SELECT * FROM Usuarios WHERE num_cuenta = %s", [self.num_cuenta])
                if cursor != None:
                    # Porque solo nos retorna un usuario
                    output = cursor.fetchall()[0]
                    self.saldo = output[1]
                    self.nombre = output[2]
                    self.apellido = output[3]
                    self.email = output[4]
                    self.estado = output[5]
                else:
                    logging.error("Error interno al cargar datos del usuario")
                retorno = True
                con.close_connection()
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

                    logging.info("Usuario con email %s y numero de cuenta %s insertado correctamente" % (
                        self.email, self.num_cuenta))
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
                logging.warning("El usuario %s no esta registrado" % self.email)
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

    def verificar_traslado_espera(self):
        retorno = False
        id_traslado = 0
        con = connection()
        cursor = con.execute(
            "SELECT id_traslado FROM Traslados WHERE numc_usuario_expedidor = %s "
            "AND estado_traslado = 'E'", [self.num_cuenta])
        if cursor != None:
            output = cursor.fetchall()
            if len(output) == 1:
                output = output[0]
                retorno = True
                id_traslado = output[0]
                logging.info(
                    "Traslado %s en espera" % (output[0]))
            else:
                logging.warning("No existen Traslados en espera de confirmación")
        else:
            logging.error("Error interno al verificar Traslado")
        con.close_connection()
        return (retorno, id_traslado)

    def verificar_retiro_espera(self):
        retorno = False
        id_retiro = 0
        con = connection()
        cursor = con.execute(
            "SELECT id_retiro FROM Retiros WHERE numc_usuario = %s "
            "AND estado_retiro = 'E'", [self.num_cuenta])
        if cursor != None:
            output = cursor.fetchall()
            if len(output) == 1:
                output = output[0]
                retorno = True
                id_retiro = output[0]
                logging.info(
                    "Retiro %s en espera" % (output[0]))
            else:
                logging.warning("No existen Retiros en espera de confirmación")
        else:
            logging.error("Error interno al verificar Retiro")
        con.close_connection()
        return (retorno, id_retiro)

    def registro_movimientos(self, ruta : str = ''):
        retorno = True
        strHTML = '''
            <html>
            <head>
            <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
                text-align: center;    
            }
            </style>
            </head>
            <h2> Usuario %s %s, Número de cuenta %s</h2>
        ''' % (self.nombre, self.apellido if self.apellido != '' else '-', self.num_cuenta)
        strHTMLConsig = '''
        <h2>Consignaciones</h2>
        <table style="width:100%">
        <tr>
            <th>Monto</th>
            <th>Fecha</th>
        </tr>
        '''

        strHTMLRet = '''
                <h2>Retiros</h2>
                <table style="width:100%">
                <tr>
                    <th>Monto</th>
                    <th>Fecha Solicitud</th>
                    <th>Fecha Confirmación</th>
                </tr>
                '''
        strHTMLTras = '''
                    <h2>Traslados (A : Aceptado, C : Cancelado, E : Espera)</h2>
                    <table style="width:100%">
                    <tr>
                        <th>No Cuenta que recibió</th>
                        <th>Monto</th>
                        <th>Fecha Solicitud</th>
                        <th>Fecha Confirmación</th>
                        <th>Estado</th>
                    </tr>
                        '''

        con = connection()
        cursor = con.execute(
            '''
            SELECT con.monto_consig, con.fecha_consig 
            FROM Consignaciones con INNER JOIN Usuarios us ON con.numc_usuario = us.num_cuenta
            WHERE us.num_cuenta = %s
            ''', params=[self.num_cuenta])

        if cursor == None:
            retorno = False

        output = cursor.fetchall()
        for consig in output:
            str_temp = "<tr><td>$%s</td><td>%s</td></tr>" % (consig[0], consig[1])
            strHTMLConsig += str_temp

        strHTML += strHTMLConsig + "</table>"

        cursor = con.execute(
            '''
            SELECT re.monto_retiro, re.fecha_inicio_retiro, re.fecha_fin_retiro
            FROM Retiros re INNER JOIN Usuarios us ON re.numc_usuario = us.num_cuenta
            WHERE us.num_cuenta = %s
            ''', params=[self.num_cuenta])

        if cursor == None:
            retorno = False

        output = cursor.fetchall()
        for ret in output:
            str_temp = "<tr><td>$%s</td><td>%s</td><td>%s</td></tr>" % (ret[0], ret[1], ret[2])
            strHTMLRet += str_temp

        strHTML += strHTMLRet + "</table>"

        cursor = con.execute(
            '''
            SELECT tra.numc_usuario_receptor, tra.monto_traslado, tra.fecha_inicio_traslado, tra.fecha_fin_traslado, tra.estado_traslado
            FROM  Traslados tra INNER JOIN Usuarios us ON tra.numc_usuario_expedidor = us.num_cuenta
            WHERE us.num_cuenta = %s
            ''', params=[self.num_cuenta])

        if cursor == None:
            retorno = False

        output = cursor.fetchall()
        for tras in output:
            str_temp = "<tr><td>%s</td><td>$%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (tras[0], tras[1], tras[2],
                                                                                             tras[3], tras[4])
            strHTMLTras += str_temp

        strHTML += strHTMLTras + "</table>"

        strHTML += "</body></html>"

        nombre_archivo = "%s%s-%s.pdf" % (ruta,self.num_cuenta, time.strftime('%Y-%m-%d_%H:%M:%S'))
        createPDF(strHTML, nombre_archivo)

        con.close_connection()
        return (retorno, nombre_archivo)


if __name__ == '__main__':
    # us = usuario(111111)
    # print(us.verificar_usuario_registrado())
    # us2 = usuario(111113, "sad", 500, "pepito perez")
    # us.cargar_datos()
    us = usuario(101813701)
    us.registro_movimientos()

