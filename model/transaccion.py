

class transaccion:

    def __init__(self, id_transaccion : int = 0, numc_usuario_expedidor : int = 0, numc_usuario_remitente : int = 0,
                 monto_transaccion : float = 0, fecha_inicio_transaccion = None, fecha_fin_transaccion = None, estado_transaccion : str = ''):
        self.id_transaccion = id_transaccion
        self.numc_usuario_expedidor = numc_usuario_expedidor
        self.numc_usuario_remitente = numc_usuario_remitente
        self.monto_transaccion = monto_transaccion
        self.fecha_inicio_transaccion = fecha_inicio_transaccion
        self.fecha_fin_transaccion = fecha_fin_transaccion
        self.estado_transaccion = estado_transaccion

