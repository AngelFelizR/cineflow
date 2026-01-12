# config.py
# Configuración de la conexión a SQL Server para el Sistema de Biblioteca

import os

class Config:
    """Configuración de la conexión a SQL Server"""

    # Configuración del servidor
    # Opciones comunes:
    # - 'localhost' para instancia por defecto
    # - 'localhost\\SQLEXPRESS' para SQL Server Express
    # - '.' para instancia local por defecto
    SERVER = 'mssql2025'  # Configurado para el servidor especificado
    PORT = 1433  # Puerto por defecto para SQL Server

    DATABASE = 'CineFlow'

    # Autenticación SQL Server
    USERNAME = 'sa'  # Usuario SQL Server
    PASSWORD = 'Pass123!'  # CAMBIAR ESTO - Nunca dejar contraseñas en texto plano en producción

    CHARSET = 'utf8'
    TDS_VERSION = '7.4'

    @staticmethod
    def get_connection_string():
        """
        Retorna la cadena de conexión apropiada.
        Para pymssql, se usa directamente en la URL de SQLAlchemy.

        Returns:
            str: Cadena de conexión
        """
        # Autenticación SQL Server
        return (
            f"server={Config.SERVER};"
            f"port={Config.PORT};"
            f"database={Config.DATABASE};"
            f"user={Config.USERNAME};"
            f"password={Config.PASSWORD};"
        )
            

    @staticmethod
    def get_sqlalchemy_url():
        """
        Retorna la URL de conexión para SQLAlchemy usando pymssql

        Returns:
            str: URL de conexión para SQLAlchemy
        """
        
        # Construir la URL para pymssql
        url = (
            f"mssql+pymssql://{Config.USERNAME}:{Config.PASSWORD}@{Config.SERVER}:{Config.PORT}/{Config.DATABASE}"
            f"?charset={Config.CHARSET}&tds_version={Config.TDS_VERSION}"
        )
        return url

    @staticmethod
    def verificar_drivers_disponibles():
        """
        Verifica y muestra los drivers disponibles.
        Nota: Esta función estaba orientada a ODBC; para pymssql no es necesaria.
        """
        print("\nDrivers no aplicables para pymssql, ya que no usa ODBC.")
        return []

    @staticmethod
    def test_connection():
        """
        Prueba la conexión a SQL Server usando pymssql

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            import pymssql
        except ImportError:
            return (False, "pymssql no está instalado. Add the dependency in the default.nix file.")

        try:
            conn = pymssql.connect(
                server=f"{Config.SERVER}:{Config.PORT}",
                user=Config.USERNAME,
                password=Config.PASSWORD,
                database=Config.DATABASE,
                charset=Config.CHARSET,
                tds_version=Config.TDS_VERSION
            )

            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return (True, f"Conexión exitosa usando SQL Server Authentication\nVersión: {version[:100]}...")

        except pymssql.Error as e:
            error_msg = str(e)
            return (False, f"Error de conexión: {error_msg}")


# Configuración para desarrollo
class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    DEBUG = True
    TESTING = False


# Configuración para producción
class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    DEBUG = False
    TESTING = False

    # En producción, usar variables de entorno
    SERVER = os.environ.get('DB_SERVER', 'mssql2025')
    PORT = int(os.environ.get('DB_PORT', '1433'))
    DATABASE = os.environ.get('DB_NAME', 'CineFlow')
    USERNAME = os.environ.get('DB_USER', 'sa')
    PASSWORD = os.environ.get('DB_PASSWORD', 'Pass123!')
    CHARSET = os.environ.get('DB_CHARSET', 'utf8')
    TDS_VERSION = os.environ.get('DB_TDS_VERSION', '7.4')


# Configuración por defecto
config = DevelopmentConfig()


if __name__ == "__main__":
    """
    Script de prueba de configuración
    Ejecutar: python config.py
    """
    print("=" * 80)
    print("CONFIGURACIÓN DE CONEXIÓN A SQL SERVER")
    print("=" * 80)

    print(f"\nServidor: {Config.SERVER}:{Config.PORT}")
    print(f"Base de datos: {Config.DATABASE}")
    print(f"Usuario: {Config.USERNAME}")

    # Imprimir la URL de SQLAlchemy al iniciar
    print("\nURL de SQLAlchemy:")
    print(Config.get_sqlalchemy_url())

    # Verificar drivers disponibles (adaptado)
    Config.verificar_drivers_disponibles()

    # Probar conexión con SQL Auth (ya que Windows Auth no está implementada)
    print("\n" + "=" * 80)
    print("PROBANDO CONEXIÓN CON SQL SERVER AUTHENTICATION")
    print("=" * 80)

    success, message = Config.test_connection()

    if success:
        print(f"\n[OK] {message}")
    else:
        print(f"\n[ERROR] {message}")
        print("\nSugerencias:")
        print("1. Verifica que SQL Server esté corriendo")
        print("2. Verifica el nombre del servidor y puerto")
        print("3. Verifica las credenciales de usuario y contraseña")
        print("4. Asegúrate de que pymssql esté instalado y configurado correctamente")