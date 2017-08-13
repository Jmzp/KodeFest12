import time
import os
import logging
from model.usuario import usuario
from db.connection import connection


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class consignacion:

    def __init__(self, id_consignacion : int = 0, numc_usuario : int = '',
                 monto_consig : int = 0, fecha_consig = time.strftime('%Y-%m-%d %H:%M:%S')):
        self.id_consignacion = id_consignacion
        self.numc_usuario = numc_usuario
        self.monto_consig = monto_consig if monto_consig > 0 else - (monto_consig)
        self.fecha_consig = fecha_consig


    def realizar_consignacion(self):
        retorno = False
        mensaje = ''
        if self.numc_usuario != 0:
            us = usuario(self.numc_usuario)
            if us.cargar_datos():
                con = connection()

                rowcount = con.execute("INSERT INTO Consignaciones(numc_usuario, monto_consig, fecha_consig)"
                            "VALUES (%s, %s, %s)",
                            [self.numc_usuario, self.monto_consig, self.fecha_consig], True).rowcount
                if rowcount > 0:

                    #Se actualiza el saldo del usuario
                    saldo_act = us.saldo + self.monto_consig
                    rowcount2 = con.execute("UPDATE Usuarios SET saldo = %s WHERE num_cuenta = %s",
                                            [saldo_act, us.num_cuenta], True).rowcount
                    if rowcount2 == 1:
                        mensaje = saldo_act
                        logging.info("Consignación realizada con éxito por %s" % self.numc_usuario)
                        retorno = True


                else:
                    logging.info("Consignación fallida por el usuario %s", self.numc_usuario)
                    mensaje = "Algo salió mal al realizar su Consignación :("

            else:
                mensaje = "Usuario no registrado"
                logging.error("Usuario no registrado %s" % self.numc_usuario )


        else:
            mensaje = "Usuario inválido"
            logging.error("Usuario inválido, datos no iniciados correctamente")

        return (retorno, mensaje)



if __name__ == '__main__':
    con = consignacion(numc_usuario=111111, monto_consig=20)
    print(con.realizar_consignacion())

