# /// script
# requires-python = ">=3.11"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-blinka", "RPi.GPIO"]
# ///
"""
Station météo basique avec capteur AHT20
Version minimale - À améliorer par les étudiants

LACUNES INTENTIONNELLES :
1. Pas de gestion d'erreurs si le capteur se déconnecte
2. Pas de validation des plages de valeurs
3. Affichage brut sans formatage ni unités claires
4. Pas d'horodatage des mesures
5. Fréquence codée en dur (pas configurable)
6. Pas de gestion de Ctrl+C propre
7. Code monolithique (difficile d'ajouter des capteurs)
8. Documentation minimale
"""
import time
import board
import adafruit_ahtx0


def main():
    """Point d'entrée principal de la station météo."""
    # Initialisation I²C et capteur
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)

    print("Station météo - AHT20")
    print("Ctrl+C pour arrêter")
    print()

    # Boucle de lecture (pas de gestion KeyboardInterrupt)
    while True:
        # Lecture des données (pas de try/except)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity

        # Affichage brut (pas de formatage, pas d'unités claires, pas de timestamp)
        print(f"Température: {temperature}")
        print(f"Humidité: {humidity}")
        print()

        # Délai fixe (pas configurable)
        time.sleep(5)


if __name__ == "__main__":
    main()
