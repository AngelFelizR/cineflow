# database.py
# Configuración de SQLAlchemy para el Sistema de Biblioteca

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import Config
import urllib

# Crear la base declarativa para los modelos
Base = declarative_base()

class Database:
    """Clase para manejar la conexión con SQLAlchemy"""

    def __init__(self, use_windows_auth=False):
        """
        Inicializa la conexión a la base de datos

        Args:
            use_windows_auth (bool): Usar autenticación de Windows
        """
        # Obtener la URL de conexión desde Config
        connection_url = Config.get_sqlalchemy_url(use_windows_auth)
        # connection_url = r"mssql+pymssql://sa:Pass123!@mssql2025:1433/CineFlow?charset=utf8&tds_version=7.4"

        # Crear el engine
        # echo=True muestra las consultas SQL en consola (útil para debug)
        # echo=False oculta las consultas (para producción)
        self.engine = create_engine(
            connection_url,
            echo=False,  # Cambiar a True para ver las consultas SQL
            pool_pre_ping=True,  # Verifica la conexión antes de usarla
            pool_recycle=3600,  # Recicla conexiones cada hora
        )

        # Crear session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self):
        """
        Retorna una nueva sesión de base de datos

        Returns:
            Session: Objeto de sesión de SQLAlchemy
        """
        return self.SessionLocal()

    def create_tables(self):
        """
        Crea todas las tablas definidas en los modelos
        NOTA: En este proyecto no lo usaremos porque ya creamos las tablas con SQL
        """
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """
        Elimina todas las tablas definidas en los modelos
        ¡CUIDADO! Esto borrará todos los datos
        """
        Base.metadata.drop_all(bind=self.engine)

    def test_connection(self):
        """
        Prueba la conexión a la base de datos

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Intentar crear una sesión y hacer una consulta simple
            session = self.get_session()
            result = session.execute(text("SELECT @@VERSION")).fetchone()
            session.close()

            return (True, f"Conexión exitosa. SQL Server: {result[0][:100]}...")
        except Exception as e:
            return (False, f"Error de conexión: {e}")



# Context manager para sesiones
class SessionContext:
    """
    Context manager para manejar sesiones de forma segura

    Ejemplo de uso:
        with SessionContext() as session:
            libros = session.query(Libro).all()
    """

    def __init__(self, database=None):
        self.database = database or db
        self.session = None

    def __enter__(self):
        self.session = self.database.get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Si hubo una excepción, hacer rollback
            self.session.rollback()
        else:
            # Si todo fue bien, hacer commit
            self.session.commit()

        self.session.close()


# Instancia global de la base de datos
# Por defecto usa Windows Authentication
db = Database(use_windows_auth=False)


if __name__ == "__main__":
    """
    Script de prueba de la configuración de SQLAlchemy
    Ejecutar: python database.py
    """
    print("=" * 80)
    print("CONFIGURACIÓN DE SQLALCHEMY")
    print("=" * 80)

    print(f"\nServidor: {Config.SERVER}")
    print(f"Base de datos: {Config.DATABASE}")
    print(f"TDS_VERSION: {Config.TDS_VERSION}")

    # Probar la conexión
    print("\n" + "=" * 80)
    print("PROBANDO CONEXIÓN CON SQLALCHEMY")
    print("=" * 80)

    success, message = db.test_connection()

    if success:
        print(f"\n[OK] {message}")

        # Mostrar información del engine
        print("\n" + "-" * 60)
        print("Información del Engine:")
        print("-" * 60)
        print(f"URL: {db.engine.url}")
        print(f"Driver: {db.engine.driver}")
        print(f"Pool size: {db.engine.pool.size()}")

    else:
        print(f"\n[ERROR] {message}")
        print("\nVerifica:")
        print("1. Que SQL Server esté corriendo")
        print("2. Que la base de datos CineFlow exista")
        print("3. Que la configuración en config.py sea correcta")

    print("\n" + "=" * 80)
