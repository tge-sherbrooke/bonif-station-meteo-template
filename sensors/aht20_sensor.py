"""
Module pour la lecture du capteur AHT20.

Ce module fournit une interface basique pour le capteur AHT20.
Version minimale - À améliorer par les étudiants.
"""
import board
import adafruit_ahtx0


def init_sensor():
    """
    Initialise le capteur AHT20 sur le bus I²C.

    Returns:
        AHTx0: Instance du capteur initialisé

    LACUNES :
    - Pas de gestion d'erreur si le capteur n'est pas détecté
    - Pas de vérification de l'adresse I²C
    """
    i2c = board.I2C()
    return adafruit_ahtx0.AHTx0(i2c)


def read_temperature(sensor):
    """
    Lit la température du capteur.

    Args:
        sensor (AHTx0): Instance du capteur

    Returns:
        float: Température en Celsius

    LACUNES :
    - Pas de validation de la plage (-40 à +120°C)
    - Pas de gestion d'erreur de lecture
    """
    return sensor.temperature


def read_humidity(sensor):
    """
    Lit l'humidité relative du capteur.

    Args:
        sensor (AHTx0): Instance du capteur

    Returns:
        float: Humidité relative en pourcentage (0-100%)

    LACUNES :
    - Pas de validation de la plage (0-100%)
    - Pas de gestion d'erreur de lecture
    """
    return sensor.relative_humidity
