import time
import logging
from model.usuario import usuario
from db.connection import connection
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class retiro:

    def __init__(self, id_retiro : int = 0, numc_usuario : int = '',
                 monto_retiro : int = 0, fecha_inicio_retiro = time.strftime('%Y-%m-%d %H:%M:%S'), fecha_fin_retiro = None, estado_retiro : str = ''):
        self.id_retiro = id_retiro
        self.numc_usuario = numc_usuario
        self.monto_retiro = monto_retiro if monto_retiro > 0 else - (monto_retiro)
        self.fecha_inicio_retiro = fecha_inicio_retiro
        self.fecha_fin_retiro = fecha_fin_retiro
        self.estado_retiro = estado_retiro



    def realizar_retiro(self):
        retorno = False
        mensaje = ''
        if self.numc_usuario != 0:
            us = usuario(self.numc_usuario)
            if us.cargar_datos():
                con = connection()
                # Si el estado del retiro es E -> ESpera, A -> Aceptada, C -> Cancelada
                # Solo tomamos una posicion porque solo puede haber una retiro en cola
                output = con.execute(
                    "SELECT id_retiro, numc_usuario, monto_retiro, fecha_inicio_retiro FROM Retiros WHERE numc_usuario = %s "
                    "AND estado_retiro = 'E'", [self.numc_usuario]).fetchall()

                if len(output) == 0:
                    saldo_disp = us.saldo - self.monto_retiro
                    if saldo_disp < 0:
                        mensaje = "Usted no posee suficiente dinero para realizar el Retiro"
                        logging.warning(
                            "Usuario 1 %s no tiene fondos para realizar el Retiro" % self.numc_usuario)
                    else:
                        rowcount = con.execute(
                            "INSERT INTO Retiros(numc_usuario,monto_retiro, fecha_inicio_retiro)"
                            "VALUES (%s, %s, %s)",
                            [self.numc_usuario,self.monto_retiro,
                             self.fecha_inicio_retiro],
                            True).rowcount
                        if rowcount > 0:
                            # Solo debe haber un dato
                            output2 = con.execute(
                                "SELECT id_retiro FROM Retiros WHERE numc_usuario = %s "
                                "AND estado_retiro = 'E'", [self.numc_usuario]).fetchall()[0]
                            retorno = True
                            mensaje = output2[0]
                            logging.info("Retiro en cola con exito a la espera de confirmación"
                                         " por el usuario %s", self.numc_usuario)
                        else:
                            logging.info("Retiro fallida por el usuario %s",
                                         self.numc_usuario)
                            mensaje = "Algo salio mal al realizar tu Retiro :("

                else:
                    output = output[0]
                    self.id_retiro = output[0]
                    self.numc_usuario = output[1]
                    self.monto_retiro = output[2]
                    self.fecha_inicio_retiro = output[3]
                    mensaje = "Usted tiene un Retiro pendiente - %s" % self.id_retiro
                    logging.warning("Usuario %s tiene un retiro pendiente %s" % (
                        self.numc_usuario, self.id_retiro))


            else:
                mensaje = "Usuario no registrado"
                logging.error("Usuario no regirstrado %s" % self.numc_usuario )


        else:
            mensaje = "Usuario invalido"
            logging.error("Usuario invalido, datos no iniciados correctamente")

        return (retorno, mensaje)

    def actualizar_retiro(self, estado_retiro):
        retorno = False
        mensaje = ''
        if estado_retiro in ('A', 'C'):

            con = connection()
            output = con.execute("SELECT id_retiro,numc_usuario,monto_retiro FROM Retiros WHERE id_retiro = %s", [self.id_retiro]).fetchall()
            if len(output) == 1:
                output = output[0]
                us = usuario(output[1])
                us.cargar_datos()


                logging.info("Actualizando Retiro %s" % self.id_retiro)
                rowcount = con.execute("UPDATE Retiros SET estado_retiro = %s, fecha_fin_retiro = %s WHERE id_retiro = %s",
                                       [estado_retiro, time.strftime('%Y-%m-%d %H:%M:%S') ,self.id_retiro], True).rowcount
                # Si es igual a 1 es porque se pudo realizar la actualizacion
                if rowcount == 1:
                    if estado_retiro == 'A':

                        logging.info("cambiando los saldos de los usuario despues del Retiro %s Aceptado" % self.id_retiro)

                        monto = output[2]
                        saldo_disp_us1 = us.saldo - monto
                        rowcount2 = con.execute("UPDATE Usuarios SET saldo = %s WHERE num_cuenta = %s",
                                                [saldo_disp_us1, us.num_cuenta], True).rowcount
                        if rowcount2 == 1:
                            retorno = True
                            mensaje = 'Retiro aceptado'
                            logging.info("Retiro aceptado")
                else:
                    mensaje = 'Código de Retiro erróneo'
                    logging.info("Código de Retiro erróneo")
            con.close_connection()
        else:
            logging.warning("Estado de Retiro Incorrecto")
        return  (retorno, mensaje)


if __name__ == '__main__':
    re = retiro(numc_usuario=111111, monto_retiro=20)
    print(re.realizar_retiro())
    print(retiro(id_retiro=8327).actualizar_retiro('A'))
