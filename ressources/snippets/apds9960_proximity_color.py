# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-apds9960", "adafruit-circuitpython-ahtx0", "adafruit-blinka"]
# ///
"""
Exemple d'ajout du capteur APDS-9960 pour la detection de proximite et couleur.

Categorie A -- Acquisition de donnees
Difficulte : Moyenne

Ce snippet montre comment:
- Initialiser le capteur APDS-9960 (adresse I2C 0x39) en complement du AHT20
- Activer les modes proximite et couleur
- Lire la valeur de proximite (0-255)
- Lire les donnees de couleur (rouge, vert, bleu, clair)
- Afficher les mesures combinees des deux capteurs
"""

import board
import adafruit_ahtx0
from adafruit_apds9960.apds9960 import APDS9960


def init_sensors():
    """
    Initialise les deux capteurs sur le meme bus I2C.

    Returns:
        tuple: (AHTx0, APDS9960) instances des capteurs
    """
    i2c = board.I2C()
    aht20 = adafruit_ahtx0.AHTx0(i2c)     # Adresse 0x38 (capteur de base)
    apds = APDS9960(i2c)                    # Adresse 0x39 (capteur ajoute)
    apds.enable_proximity = True
    apds.enable_color = True
    return aht20, apds


def read_apds9960(apds):
    """
    Lit les donnees du capteur APDS-9960.

    Args:
        apds: Instance du capteur APDS9960

    Returns:
        dict: Dictionnaire avec proximite et couleurs (rouge, vert, bleu, clair)
    """
    r, g, b, c = apds.color_data
    return {
        "proximity": apds.proximity,
        "red": r,
        "green": g,
        "blue": b,
        "clear": c,
    }


def read_both_sensors(aht20, apds):
    """
    Lit les donnees des deux capteurs.

    Args:
        aht20: Capteur principal (base)
        apds: Capteur secondaire (ajoute)

    Returns:
        dict: Dictionnaire avec les mesures des deux capteurs
    """
    apds_data = read_apds9960(apds)
    return {
        "aht20": {
            "temperature": aht20.temperature,
            "humidity": aht20.relative_humidity,
        },
        "apds9960": apds_data,
    }


# Exemple d'utilisation
if __name__ == "__main__":
    import time

    aht20, apds = init_sensors()
    print("Station meteo - AHT20 + APDS-9960\n")

    while True:
        data = read_both_sensors(aht20, apds)

        print("--- AHT20 ---")
        print(f"Temperature : {data['aht20']['temperature']:.1f}C")
        print(f"Humidite    : {data['aht20']['humidity']:.1f}%")

        print("\n--- APDS-9960 ---")
        print(f"Proximite : {data['apds9960']['proximity']}")
        print(f"Rouge     : {data['apds9960']['red']}")
        print(f"Vert      : {data['apds9960']['green']}")
        print(f"Bleu      : {data['apds9960']['blue']}")
        print(f"Clair     : {data['apds9960']['clear']}")

        print("\n" + "-" * 50 + "\n")
        time.sleep(5)
