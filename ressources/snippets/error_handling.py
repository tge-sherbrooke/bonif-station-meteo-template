# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-blinka"]
# ///
"""
Exemple de gestion d'erreurs robuste pour la station météo.

Catégorie C — Qualité du code
Difficulté : Moyenne

Ce snippet montre comment:
- Gérer les exceptions lors de l'initialisation du capteur
- Gérer les erreurs de lecture I²C
- Implémenter un mécanisme de reconnexion automatique
- Gérer proprement l'interruption clavier (Ctrl+C)
- Logger les erreurs de façon structurée
"""

import time
import logging
from typing import Optional
import board
import adafruit_ahtx0

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('station_meteo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SensorConnectionError(Exception):
    """Exception levée lorsque le capteur ne peut pas être initialisé."""
    pass


class SensorReadError(Exception):
    """Exception levée lors d'une erreur de lecture du capteur."""
    pass


def init_sensor_with_retry(max_retries: int = 3, retry_delay: float = 2.0):
    """
    Initialise le capteur AHT20 avec mécanisme de retry.

    Args:
        max_retries (int): Nombre maximum de tentatives
        retry_delay (float): Délai entre les tentatives (secondes)

    Returns:
        AHTx0: Instance du capteur, ou None si échec

    Raises:
        SensorConnectionError: Si toutes les tentatives échouent
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Tentative {attempt}/{max_retries} d'initialisation du capteur AHT20...")
            i2c = board.I2C()
            sensor = adafruit_ahtx0.AHTx0(i2c)
            logger.info("Capteur AHT20 initialise avec succes")
            return sensor

        except ValueError as e:
            logger.error(f"ERREUR initialisation : {e}")
            if attempt < max_retries:
                logger.info(f"Nouvelle tentative dans {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise SensorConnectionError(
                    f"Impossible d'initialiser le capteur après {max_retries} tentatives"
                ) from e

        except RuntimeError as e:
            logger.error(f"ERREUR I2C : {e}")
            if attempt < max_retries:
                logger.info(f"Nouvelle tentative dans {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                raise SensorConnectionError(
                    f"Erreur I²C persistante après {max_retries} tentatives"
                ) from e


def read_sensor_safe(sensor) -> Optional[dict]:
    """
    Lit les données du capteur avec gestion d'erreurs.

    Args:
        sensor: Instance du capteur AHT20

    Returns:
        dict: Données lues (température, humidité), ou None si erreur

    Raises:
        SensorReadError: Si la lecture échoue
    """
    try:
        temperature = sensor.temperature
        humidity = sensor.relative_humidity

        # Validation des plages de valeurs
        if not (-40 <= temperature <= 120):
            logger.warning(f"ATTENTION Temperature hors plage : {temperature}C")
            raise SensorReadError(f"Température invalide : {temperature}°C")

        if not (0 <= humidity <= 100):
            logger.warning(f"ATTENTION Humidite hors plage : {humidity}%")
            raise SensorReadError(f"Humidité invalide : {humidity}%")

        return {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time()
        }

    except OSError as e:
        logger.error(f"ERREUR I2C lors de la lecture : {e}")
        raise SensorReadError("Erreur de communication I²C") from e

    except RuntimeError as e:
        logger.error(f"ERREUR runtime lors de la lecture : {e}")
        raise SensorReadError("Erreur runtime du capteur") from e


def main_loop_with_error_handling():
    """
    Boucle principale avec gestion d'erreurs complète.

    Gère :
    - Initialisation avec retry
    - Lecture avec gestion d'erreurs
    - Reconnexion automatique si le capteur se déconnecte
    - Interruption propre (Ctrl+C)
    """
    sensor = None
    read_interval = 5.0  # Configurable
    reconnect_attempts = 0
    max_reconnect_attempts = 5

    logger.info("Demarrage de la station meteo...")

    try:
        # Initialisation initiale
        sensor = init_sensor_with_retry()

        logger.info(f"Lecture des donnees toutes les {read_interval}s")
        logger.info("Appuyez sur Ctrl+C pour arrêter proprement\n")

        while True:
            try:
                # Lecture des données
                data = read_sensor_safe(sensor)

                # Affichage (succès de lecture = reset du compteur de reconnexion)
                reconnect_attempts = 0
                print(f"Température : {data['temperature']:.1f}°C")
                print(f"Humidité    : {data['humidity']:.1f}%")
                print()

            except SensorReadError as e:
                logger.error(f"Erreur de lecture : {e}")
                reconnect_attempts += 1

                if reconnect_attempts >= max_reconnect_attempts:
                    logger.critical("Trop d'echecs consecutifs, arret du programme")
                    break

                # Tentative de reconnexion
                logger.info("Tentative de reconnexion au capteur...")
                try:
                    sensor = init_sensor_with_retry(max_retries=2, retry_delay=1.0)
                    logger.info("Reconnexion reussie")
                    reconnect_attempts = 0
                except SensorConnectionError:
                    logger.error("Reconnexion echouee")

            # Délai avant prochaine lecture
            time.sleep(read_interval)

    except KeyboardInterrupt:
        logger.info("\nArret demande par l'utilisateur (Ctrl+C)")

    except SensorConnectionError as e:
        logger.critical(f"Impossible d'initialiser le capteur : {e}")
        logger.info("Vérifiez la connexion I²C avec : i2cdetect -y 1")
        return 1

    except Exception as e:
        logger.critical(f"Erreur inattendue : {e}", exc_info=True)
        return 1

    finally:
        logger.info("Arret propre de la station meteo")

    return 0


if __name__ == "__main__":
    exit(main_loop_with_error_handling())
