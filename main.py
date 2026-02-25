# /// script
# requires-python = ">=3.11"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-blinka"]
# ///
"""
Station meteo basique avec capteur AHT20
Version minimale - A ameliorer par les etudiants

LACUNES INTENTIONNELLES :
1. Pas de gestion d'erreurs si le capteur se deconnecte
2. Pas de validation des plages de valeurs
3. Affichage brut sans formatage ni unites claires
4. Pas d'horodatage des mesures
5. Frequence codee en dur (pas configurable)
6. Pas de gestion de Ctrl+C propre
7. Code monolithique (difficile d'ajouter des capteurs)
8. Documentation minimale
"""
import time
import board
import adafruit_ahtx0


def main():
    """Point d'entree principal de la station meteo."""
    # Initialisation I2C et capteur
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)

    print("Station meteo - AHT20")
    print("Ctrl+C pour arreter")
    print()

    # Boucle de lecture (pas de gestion KeyboardInterrupt)
    while True:
        # Lecture des donnees (pas de try/except)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity

        # Affichage brut (pas de formatage, pas d'unites claires, pas de timestamp)
        print(f"Temperature: {temperature}")
        print(f"Humidite: {humidity}")
        print()

        # Delai fixe (pas configurable)
        time.sleep(5)


if __name__ == "__main__":
    main()
