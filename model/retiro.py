
class retiro:

    def __init__(self, id_retiro : int = 0, numc_usuario : int = '',
                 monto_retiro : float = 0, fecha_inicio_retiro = None, fecha_fin_retiro = None, estado_retiro : str = ''):
        self.id_retiro = id_retiro
        self.numc_usuario = numc_usuario
        self.monto_retiro = monto_retiro
        self.fecha_inicio_retiro = fecha_inicio_retiro
        self.fecha_fin_retiro = fecha_fin_retiro
        self.estado_retiro = estado_retiro