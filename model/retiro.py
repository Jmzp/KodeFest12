import time
import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class retiro:

    def __init__(self, id_retiro : int = 0, numc_usuario : int = '',
                 monto_retiro : int = 0, fecha_inicio_retiro = time.strftime('%Y-%m-%d %H:%M:%S'), fecha_fin_retiro = None, estado_retiro : str = ''):
        self.id_retiro = id_retiro
        self.numc_usuario = numc_usuario
        self.monto_retiro = monto_retiro
        self.fecha_inicio_retiro = fecha_inicio_retiro
        self.fecha_fin_retiro = fecha_fin_retiro
        self.estado_retiro = estado_retiro