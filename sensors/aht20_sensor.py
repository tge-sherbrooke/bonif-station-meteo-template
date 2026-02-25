"""
Module pour la lecture du capteur AHT20.

Ce module fournit une interface basique pour le capteur AHT20.
Version minimale - A ameliorer par les etudiants.
"""
import board
import adafruit_ahtx0


def init_sensor():
    """
    Initialise le capteur AHT20 sur le bus I2C.

    Returns:
        AHTx0: Instance du capteur initialise

    LACUNES :
    - Pas de gestion d'erreur si le capteur n'est pas detecte
    - Pas de verification de l'adresse I2C
    """
    i2c = board.I2C()
    return adafruit_ahtx0.AHTx0(i2c)


def read_temperature(sensor):
    """
    Lit la temperature du capteur.

    Args:
        sensor (AHTx0): Instance du capteur

    Returns:
        float: Temperature en Celsius

    LACUNES :
    - Pas de validation de la plage (-40 a +120 C)
    - Pas de gestion d'erreur de lecture
    """
    return sensor.temperature


def read_humidity(sensor):
    """
    Lit l'humidite relative du capteur.

    Args:
        sensor (AHTx0): Instance du capteur

    Returns:
        float: Humidite relative en pourcentage (0-100%)

    LACUNES :
    - Pas de validation de la plage (0-100%)
    - Pas de gestion d'erreur de lecture
    """
    return sensor.relative_humidity
