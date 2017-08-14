import logging
import time

from db.connection import connection
from model.usuario import usuario

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Modelo que representa la traslado de la DB
class traslado:
    def __init__(self, id_traslado: int = 0, numc_usuario_expedidor: int = 0, numc_usuario_receptor: int = 0,
                 monto_traslado: int = 0, fecha_inicio_traslado=time.strftime('%Y-%m-%d %H:%M:%S'),
                 fecha_fin_traslado=None,
                 estado_traslado: str = 'E'):
        self.id_traslado = id_traslado
        self.numc_usuario_expedidor = numc_usuario_expedidor
        self.numc_usuario_receptor = numc_usuario_receptor
        self.monto_traslado = monto_traslado if monto_traslado > 0 else - (monto_traslado)
        self.fecha_inicio_traslado = fecha_inicio_traslado
        self.fecha_fin_traslado = fecha_fin_traslado
        self.estado_traslado = estado_traslado

    def realizar_traslado(self):
        retorno = False
        mensaje = ''
        if self.monto_traslado != 0:
            if self.numc_usuario_expedidor != 0 and self.numc_usuario_receptor != 0:
                us1 = usuario(self.numc_usuario_expedidor)
                us2 = usuario(self.numc_usuario_receptor)
                if us1.cargar_datos():
                    if us2.cargar_datos():
                        con = connection()
                        # Si el estado del traslado es E -> ESpera, A -> Aceptada, C -> Cancelada
                        # Solo tomamos una posicion porque solo puede haber una traslado en cola
                        output = con.execute(
                            "SELECT id_traslado, numc_usuario_receptor, monto_traslado, fecha_inicio_traslado FROM Traslados WHERE numc_usuario_expedidor = %s "
                            "AND estado_traslado = 'E'", [self.numc_usuario_expedidor]).fetchall()

                        if len(output) == 0:
                            saldo_disp = us1.saldo - self.monto_traslado
                            if saldo_disp < 0:
                                mensaje = "Usted no posee suficiente dinero para realizar el Traslados"
                                logging.warning(
                                    "Usuario 1 %s no tiene fondos para realizar los traslados" % self.numc_usuario_expedidor)
                            else:
                                rowcount = con.execute(
                                    "INSERT INTO Traslados(numc_usuario_expedidor, numc_usuario_receptor, monto_traslado, fecha_inicio_traslado)"
                                    "VALUES (%s, %s, %s, %s)",
                                    [self.numc_usuario_expedidor, self.numc_usuario_receptor, self.monto_traslado,
                                     self.fecha_inicio_traslado],
                                    True).rowcount
                                if rowcount > 0:
                                    # Solo debe haber un dato
                                    output2 = con.execute(
                                        "SELECT id_traslado FROM Traslados WHERE numc_usuario_expedidor = %s "
                                        "AND estado_traslado = 'E'", [self.numc_usuario_expedidor]).fetchall()[0]
                                    retorno = True
                                    mensaje = output2[0]
                                    logging.info("Traslado en cola con exito a la espera de confirmación"
                                                 " por el usuario %s", self.numc_usuario_expedidor)
                                else:
                                    logging.info("Traslado fallida por el usuario %s",
                                                 self.numc_usuario_expedidor)
                                    mensaje = "Algo salio mal al realizar tu Traslado :("

                        else:
                            output = output[0]
                            self.id_traslado = output[0]
                            self.numc_usuario_receptor = output[1]
                            self.monto_traslado = output[2]
                            self.fecha_inicio_traslado = output[3]
                            mensaje = "Usted tiene un traslado pendiente - %s" % self.id_traslado
                            logging.warning("Usuario %s tiene un traslado pendiente %s" % (
                                self.numc_usuario_expedidor, self.id_traslado))

                    else:
                        logging.warning(
                            "Usuario 2 %s invalido para realizar el traslado" % self.numc_usuario_receptor)

                else:
                    logging.warning("Usuario 1 %s invalido para realizar el traslado" % self.numc_usuario_expedidor)

            else:
                logging.error("Usuario invalido, datos no iniciados correctamente")

        else:
            mensaje = "Usted esta tratando de realizar un traslado con un valor de 0"
            logging.warning("Usuario 1 %s esta tratando de realizar un traslado de 0" % self.numc_usuario_expedidor)
        return (retorno, mensaje)

    def actualizar_traslado(self, estado_traslado):
        retorno = False
        mensaje = ''
        if estado_traslado in ('A', 'C'):

            con = connection()
            output = con.execute("SELECT * FROM Traslados WHERE id_traslado = %s", [self.id_traslado]).fetchall()

            if len(output) == 1:
                output = output[0]
                us = usuario(output[1])
                us2 = usuario(output[2])

                us.cargar_datos()
                us2.cargar_datos()

                logging.info("Actualizando Traslado %s" % self.id_traslado)
                rowcount = con.execute(
                    "UPDATE Traslados SET estado_traslado = %s, fecha_fin_traslado = %s WHERE id_traslado = %s",
                    [estado_traslado, time.strftime('%Y-%m-%d %H:%M:%S'), self.id_traslado], True).rowcount
                if rowcount == 1:
                    if estado_traslado == 'A':

                        logging.info(
                            "Cambiando los saldos de los usuario despues del Traslado %s Aceptado" % self.id_traslado)

                        monto = output[3]
                        saldo_disp_us1 = us.saldo - monto
                        rowcount2 = con.execute("UPDATE Usuarios SET saldo = %s WHERE num_cuenta = %s",
                                                [saldo_disp_us1, us.num_cuenta], True).rowcount

                        saldo_disp_us2 = us2.saldo + monto
                        rowcount3 = con.execute("UPDATE Usuarios SET saldo = %s WHERE num_cuenta = %s",
                                                [saldo_disp_us2, us2.num_cuenta], True).rowcount
                        if rowcount2 == 1 and rowcount3 == 1:
                            retorno = True
                            mensaje = "%s-%s-%s-%s" % (us2.email, monto, us.nombre, us.num_cuenta)
                            logging.info("Traslado aceptado")
                    else:
                        mensaje = "Traslado cancelado"
                        logging.info("Traslado %s cancelado", self.id_traslado)
                else:
                    mensaje = 'Código de Traslado erróneo\nPor favor ingrese el código correcto'
                    logging.info("Código de Traslado erróneo")
            con.close_connection()
        else:
            logging.warning("Estado de traslado Incorrecto")
        return (retorno, mensaje)


if __name__ == '__main__':
    tra = traslado(numc_usuario_expedidor=111111, numc_usuario_receptor=111112, monto_traslado=100)
    print(tra.realizar_traslado())
