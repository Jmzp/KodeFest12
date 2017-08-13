import mysql.connector
import sys
from mysql.connector import errorcode




class connection:
    def __init__(self, hostname : str = "localhost", database : str = "dbMy", user : str = "root",
                 password : str = ""):
        self.config = {
            'host': hostname,
            'port': 3306,
            'database': database,
            'user': user,
            'password': password,
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
        }
        self.cnx = None
        self.connect()


    def connect(self) -> bool:
        sucess = False
        try:
            # Desentranamos el diccionario y cada elemetno se convierte en un parametro
            self.cnx = mysql.connector.connect(**self.config)
            sucess = True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("\nAlgo ha salido mal con tu usuario o contraseña : ",err,file=sys.stderr)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("\nLa base de datos no existe : ",err,file=sys.stderr)
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                print("\nOcurrio un error al tratar de conectarse al host : ",err,file=sys.stderr)
            else:
                print("\nAlgo salio mal : " , err,file=sys.stderr)
        return sucess


    def close_connection(self):
        if self.cnx != None:
            self.cnx.close()
        else:
            print("La conexión no se ha iniciado, no puede ser cerrada",file=sys.stderr)


    '''
        Ejcutamos una sentencia al servidor de bases de datos, se pasan los parametros respectivos.
    '''
    def execute(self, str_query: str, params: [] = (), commit: bool = False):
        output = None
        try:
            if self.cnx == None:
                print("\nPrimero debe iniciar una conexion valida, antes de poder consultar", file=sys.stderr)
            else:
                cursor = self.cnx.cursor()
                cursor.execute(str_query, params=params)
                if commit:
                    self.cnx.commit()
                output = cursor
        except mysql.connector.Error as err:
            print("\nOcurrió un error al procesar la petición : " + str_query + "\n El error es : ", err,
                  file=sys.stderr)

        return output

    def call_procedure(self, name : str, parameters : list = [], commit : bool = True):
        try:
            if self.cnx is not None:
                cursor = self.cnx.cursor()
                cursor.callproc(name, parameters)
                if commit:
                    self.cnx.commit()
                output = cursor.stored_results()
                cursor.close()
                return output
            else:
                print("Error en la clase conexion, No ha iniciado una conexion")
                return None
        except mysql.connector.Error as e:
            print("Ocurrio un error en la sentencia, ",e)
            return None


if __name__ == "__main__":
    Con = connection()
    resultado = Con.execute("SELECT * FROM Versiculos")
    print(resultado)







