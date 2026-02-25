# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-seesaw", "adafruit-circuitpython-ahtx0", "adafruit-blinka"]
# ///
"""
Exemple d'affichage visuel avec le Neoslider (LEDs NeoPixel RGB).

Catégorie D — Interface (avancée)
Difficulté : Élevée

Ce snippet montre comment:
- Initialiser le Neoslider (potentiomètre + 4 NeoPixels)
- Mapper des valeurs de température/humidité à des couleurs
- Créer des animations visuelles selon les conditions météo
- Utiliser le slider comme contrôle (seuils d'alarme)

ATTENTION : Nécessite la bibliothèque adafruit-circuitpython-seesaw
"""

import time
import board
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ahtx0


class WeatherDisplay:
    """
    Affichage visuel des conditions météo sur Neoslider.
    """

    def __init__(self):
        """Initialise le Neoslider et le capteur AHT20."""
        i2c = board.I2C()

        # Initialiser le Neoslider (adresse I²C 0x30)
        self.neoslider = Seesaw(i2c, addr=0x30)

        # Initialiser le capteur AHT20
        self.sensor = adafruit_ahtx0.AHTx0(i2c)

        # Nombre de pixels (4 sur le Neoslider)
        self.num_pixels = 4

        # Configuration des couleurs
        self.off = (0, 0, 0)

    def temperature_to_color(self, temp: float) -> tuple:
        """
        Convertit une température en couleur RGB.

        Gradient :
        - Bleu froid : < 15°C
        - Vert : 15-20°C
        - Jaune : 20-25°C
        - Orange : 25-30°C
        - Rouge chaud : > 30°C

        Args:
            temp (float): Température en Celsius

        Returns:
            tuple: Couleur RGB (r, g, b) entre 0-255
        """
        if temp < 15:
            # Bleu froid
            return (0, 0, 255)
        elif temp < 20:
            # Gradient bleu → vert
            ratio = (temp - 15) / 5
            return (0, int(255 * ratio), int(255 * (1 - ratio)))
        elif temp < 25:
            # Gradient vert → jaune
            ratio = (temp - 20) / 5
            return (int(255 * ratio), 255, 0)
        elif temp < 30:
            # Gradient jaune → orange
            ratio = (temp - 25) / 5
            return (255, int(255 * (1 - ratio * 0.5)), 0)
        else:
            # Rouge chaud
            return (255, 0, 0)

    def humidity_to_brightness(self, humidity: float) -> float:
        """
        Convertit l'humidité en niveau de luminosité.

        Plus l'humidité est élevée, plus les LEDs sont brillantes.

        Args:
            humidity (float): Humidité relative (0-100%)

        Returns:
            float: Multiplicateur de luminosité (0.2-1.0)
        """
        # Limiter entre 20% et 100% de luminosité
        return 0.2 + (humidity / 100) * 0.8

    def apply_brightness(self, color: tuple, brightness: float) -> tuple:
        """
        Applique un facteur de luminosité à une couleur.

        Args:
            color (tuple): Couleur RGB (r, g, b)
            brightness (float): Facteur de luminosité (0.0-1.0)

        Returns:
            tuple: Couleur ajustée
        """
        return tuple(int(c * brightness) for c in color)

    def set_all_pixels(self, color: tuple):
        """
        Définit la même couleur pour tous les pixels.

        Args:
            color (tuple): Couleur RGB (r, g, b)
        """
        for i in range(self.num_pixels):
            self.neoslider.pixel_set(i, color)
        self.neoslider.pixel_show()

    def animated_fill(self, color: tuple, delay: float = 0.1):
        """
        Remplit progressivement les pixels avec une couleur.

        Args:
            color (tuple): Couleur RGB (r, g, b)
            delay (float): Délai entre chaque pixel (secondes)
        """
        for i in range(self.num_pixels):
            self.neoslider.pixel_set(i, color)
            self.neoslider.pixel_show()
            time.sleep(delay)

    def breathing_effect(self, color: tuple, cycles: int = 2, duration: float = 2.0):
        """
        Effet de respiration (fade in/out) avec une couleur.

        Args:
            color (tuple): Couleur de base RGB (r, g, b)
            cycles (int): Nombre de cycles de respiration
            duration (float): Durée d'un cycle complet (secondes)
        """
        steps = 20
        step_delay = duration / (steps * 2)

        for _ in range(cycles):
            # Fade in
            for i in range(steps + 1):
                brightness = i / steps
                adjusted_color = self.apply_brightness(color, brightness)
                self.set_all_pixels(adjusted_color)
                time.sleep(step_delay)

            # Fade out
            for i in range(steps, -1, -1):
                brightness = i / steps
                adjusted_color = self.apply_brightness(color, brightness)
                self.set_all_pixels(adjusted_color)
                time.sleep(step_delay)

    def display_weather(self):
        """
        Affiche les conditions météo actuelles sur les LEDs.
        """
        # Lecture des données
        temperature = self.sensor.temperature
        humidity = self.sensor.relative_humidity

        # Calcul de la couleur et luminosité
        color = self.temperature_to_color(temperature)
        brightness = self.humidity_to_brightness(humidity)
        final_color = self.apply_brightness(color, brightness)

        # Affichage
        self.set_all_pixels(final_color)

        return temperature, humidity, final_color


# Exemple d'utilisation
if __name__ == "__main__":
    display = WeatherDisplay()

    print("Station météo - Affichage visuel Neoslider")
    print("Les LEDs indiquent :")
    print("  - Couleur : Température (bleu=froid, rouge=chaud)")
    print("  - Luminosité : Humidité (sombre=sec, brillant=humide)")
    print("\nCtrl+C pour arrêter\n")

    try:
        # Animation de démarrage
        print("Animation de demarrage...")
        display.animated_fill((50, 50, 255), delay=0.15)
        time.sleep(0.5)
        display.set_all_pixels(display.off)
        time.sleep(0.5)

        # Boucle principale
        while True:
            temp, hum, color = display.display_weather()

            print(f"Température : {temp:.1f}°C | Humidité : {hum:.1f}% | "
                  f"Couleur RGB : {color}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")

    finally:
        # Éteindre les LEDs proprement
        display.set_all_pixels(display.off)
        print("LEDs eteintes")
