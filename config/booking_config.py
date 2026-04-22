import os
from dotenv import load_dotenv


class BookingConfig:
    """
    Singleton que guarda la configuración global de MediBook,
    incluyendo la URL de la base de datos y parámetros de la clínica.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Creamos la instancia por primera vez
            cls._instance = super().__new__(cls)

            # tomamos+ variables de entorno desde .env
            load_dotenv()

            # Configuración de la clínica
            cls._instance.clinic_name = "MediBook Clinic"
            cls._instance.open_hour = 9        # hora de apertura a las 9 am
            cls._instance.close_hour = 19      # hora de cierre a las 7 pm
            cls._instance.slot_minutes = 30    # duración estándar de cita en minutos

         
            cls._instance.db_url = os.getenv("DATABASE_URL")#aqui hacemos la conexion

            
            if not cls._instance.db_url:
                raise ValueError(
                    "DATABASE_URL no está definida en las variables de entorno"
                )

        
        return cls._instance



