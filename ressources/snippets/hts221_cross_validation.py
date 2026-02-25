# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-circuitpython-hts221", "adafruit-blinka"]
# ///
"""
Exemple d'ajout du capteur HTS221 pour validation croisee avec le AHT20 de base.

Categorie A -- Acquisition de donnees
Difficulte : Moyenne

Ce snippet montre comment:
- Initialiser le capteur HTS221 (adresse I2C 0x5F) en complement du AHT20
- Lire temperature et humidite des deux capteurs
- Comparer les valeurs du HTS221 avec celles du AHT20 (capteur de base)
- Detecter les ecarts significatifs entre capteurs
"""

import board
import adafruit_ahtx0
from adafruit_hts221 import HTS221


def init_sensors():
    """
    Initialise les deux capteurs sur le meme bus I2C.

    Returns:
        tuple: (AHTx0, HTS221) instances des capteurs
    """
    i2c = board.I2C()
    aht20 = adafruit_ahtx0.AHTx0(i2c)  # Adresse 0x38 (capteur de base)
    hts221 = HTS221(i2c)                # Adresse 0x5F (capteur ajoute)
    return aht20, hts221


def read_both_sensors(aht20, hts221):
    """
    Lit les donnees des deux capteurs.

    Args:
        aht20: Capteur principal (base)
        hts221: Capteur secondaire (ajoute)

    Returns:
        dict: Dictionnaire avec les mesures des deux capteurs
    """
    return {
        "aht20": {
            "temperature": aht20.temperature,
            "humidity": aht20.relative_humidity
        },
        "hts221": {
            "temperature": hts221.temperature,
            "humidity": hts221.relative_humidity
        }
    }


def compare_sensors(aht20, hts221, temp_threshold=2.0, hum_threshold=5.0):
    """
    Compare les mesures des deux capteurs et detecte les ecarts.

    Args:
        aht20: Capteur principal (base)
        hts221: Capteur secondaire (ajoute)
        temp_threshold (float): Seuil d'alerte temperature (C)
        hum_threshold (float): Seuil d'alerte humidite (%)

    Returns:
        dict: Resultat de la comparaison
    """
    data = read_both_sensors(aht20, hts221)

    temp_diff = abs(data["aht20"]["temperature"] - data["hts221"]["temperature"])
    hum_diff = abs(data["aht20"]["humidity"] - data["hts221"]["humidity"])

    return {
        "data": data,
        "differences": {
            "temperature": temp_diff,
            "humidity": hum_diff
        },
        "alerts": {
            "temperature_alert": temp_diff > temp_threshold,
            "humidity_alert": hum_diff > hum_threshold
        }
    }


# Exemple d'utilisation
if __name__ == "__main__":
    import time

    aht20, hts221 = init_sensors()
    print("Station meteo - Comparaison AHT20 vs HTS221\n")

    while True:
        result = compare_sensors(aht20, hts221)

        print("--- Mesures ---")
        print(f"AHT20  : {result['data']['aht20']['temperature']:.1f}C, "
              f"{result['data']['aht20']['humidity']:.1f}%")
        print(f"HTS221 : {result['data']['hts221']['temperature']:.1f}C, "
              f"{result['data']['hts221']['humidity']:.1f}%")

        print("\n--- Ecarts ---")
        print(f"Temperature : {result['differences']['temperature']:.2f}C")
        print(f"Humidite    : {result['differences']['humidity']:.2f}%")

        if result['alerts']['temperature_alert']:
            print("ALERTE : Ecart temperature eleve entre capteurs !")
        if result['alerts']['humidity_alert']:
            print("ALERTE : Ecart humidite eleve entre capteurs !")

        print("\n" + "-"*50 + "\n")
        time.sleep(5)
