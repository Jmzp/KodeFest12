import logging
from model.usuario import usuario
from db.connection import connection

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class transaccion:
    def __init__(self, id_transaccion: int = 0, numc_usuario_expedidor: int = 0, numc_usuario_remitente: int = 0,
                 monto_transaccion: float = 0, fecha_inicio_transaccion=None, fecha_fin_transaccion=None,
                 estado_transaccion: str = ''):
        self.id_transaccion = id_transaccion
        self.numc_usuario_expedidor = numc_usuario_expedidor
        self.numc_usuario_remitente = numc_usuario_remitente
        self.monto_transaccion = monto_transaccion if monto_transaccion > 0 else - (monto_transaccion)
        self.fecha_inicio_transaccion = fecha_inicio_transaccion
        self.fecha_fin_transaccion = fecha_fin_transaccion
        self.estado_transaccion = estado_transaccion

    def realizar_transaccion(self):
        retorno = False
        mensaje = ''
        if self.monto_transaccion != 0:
            if self.numc_usuario_expedidor != 0 and self.numc_usuario_remitente != 0:
                us1 = usuario(self.numc_usuario_expedidor)
                us2 = usuario(self.numc_usuario_remitente)
                if us1.cargar_datos():
                    if us2.cargar_datos():
                        con = connection()
                        # Si la transaccion es E -> ESpera, A -> Aceptada, C -> Cancelada
                        output = con.execute(
                            "SELECT id_transaccion, numc_usuario_remitente, monto_transaccion, fecha_inicio_transaccion FROM Transacciones WHERE numc_usuario_expedidor = %s "
                            "AND estado_transaccion = 'E'", [self.numc_usuario_expedidor]).fetchall()

                        if len(output) == 0:
                            saldo_disp = us1.saldo - self.monto_transaccion
                            if saldo_disp < 0:
                                mensaje = "Usted no posee suficiente dinero para realizar la transacción"
                                logging.warning(
                                    "Usuario 1 %s no tiene fondos para realizar la transacción" % self.numc_usuario_expedidor)
                            else:
                                rowcount = con.execute(
                                    "INSERT INTO Transacciones(numc_usuario_expedidor, numc_usuario_remitente, monto_transaccion, fecha_inicio_transaccion)"
                                    "VALUES (%s, %s, %s, %s)",
                                    [self.numc_usuario_expedidor, self.numc_usuario_remitente, self.monto_transaccion,
                                     self.fecha_inicio_transaccion],
                                    True).rowcount
                                if rowcount > 0:
                                    rowcount2 = con.execute("UPDATE Usuarios SET saldo = %s WHERE num_cuenta = %s",
                                                            [saldo_disp, self.numc_usuario_expedidor], True).rowcount
                                    if rowcount2 > 0:
                                        output2 = con.execute(
                                            "SELECT id_transaccion FROM Transacciones WHERE numc_usuario_expedidor = %s "
                                            "AND estado_transaccion = 'E'", [self.numc_usuario_expedidor]).fetchall()
                                        retorno = True
                                        mensaje = output2[0]
                                    else:
                                        mensaje = "Algo salio mal al actualizar tu saldo :("

                        else:
                            self.id_transaccion = output[0]
                            self.numc_usuario_remitente = output[1]
                            self.monto_transaccion = output[2]
                            self.fecha_inicio_transaccion = output[3]
                            mensaje = "Usted tiene una transacción pendiente"
                            logging.warning("Usuario %s tiene una transacción pendiente %s" % (
                            self.numc_usuario_expedidor, self.id_transaccion))

                    else:
                        logging.warning(
                            "Usuario 2 %s invalido para realizar la transacción" % self.numc_usuario_remitente)

                else:
                    logging.warning("Usuario 1 %s invalido para realizar la transacción" % self.numc_usuario_expedidor)

            else:
                logging.error("Usuario invalido, datos no iniciados correctamente")

        else:
            mensaje = "Usted esta tratando de realizar una transacción con un valor de 0"
            logging.warning("Usuario 1 %s esta tratando de realizar una transacción de 0" % self.numc_usuario_expedidor)
        return (retorno, mensaje)

    def actualizar_transaccion(self):
        pass
