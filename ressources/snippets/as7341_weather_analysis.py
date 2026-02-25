# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-as7341", "adafruit-blinka"]
# ///
"""
Exemple d'utilisation du spectromètre AS7341 pour l'analyse météorologique.

Catégorie A — Acquisition de données (avancée)
Difficulté : Moyenne (simplifié par la bibliothèque Adafruit)

Ce snippet montre comment:
- Initialiser le spectromètre AS7341
- Lire les 11 canaux spectraux (8 visibles + NIR + clear + flicker)
- Calculer un indice de couvert nuageux (cloud index)
- Estimer l'intensité UV indirecte
- Détecter l'aube/crépuscule par variation spectrale

PERTINENCE MÉTÉO EXCELLENTE :
- Les nuages modifient le spectre lumineux (diffusion bleue)
- Le spectre évolue du lever au coucher du soleil
- Détection UV via canaux violet (415nm) et indigo (445nm)
- Classification conditions : ciel clair / nuageux / orageux
"""

import board
from adafruit_as7341 import AS7341


def init_spectrometer():
    """
    Initialise le spectromètre AS7341.

    Returns:
        AS7341: Instance du spectromètre configuré
    """
    i2c = board.I2C()
    sensor = AS7341(i2c)

    # Configuration optionnelle (la bibliothèque gère les defaults)
    # sensor.atime = 100  # Temps d'intégration
    # sensor.astep = 999  # Nombre de steps
    # sensor.gain = 8     # Gain du capteur

    return sensor


def read_spectrum(sensor):
    """
    Lit tous les canaux spectraux du AS7341.

    Args:
        sensor (AS7341): Instance du spectromètre

    Returns:
        dict: Dictionnaire avec tous les canaux
    """
    return {
        "violet": sensor.channel_415nm,      # 415nm
        "indigo": sensor.channel_445nm,      # 445nm
        "blue": sensor.channel_480nm,        # 480nm
        "cyan": sensor.channel_515nm,        # 515nm
        "green": sensor.channel_555nm,       # 555nm
        "yellow": sensor.channel_590nm,      # 590nm
        "orange": sensor.channel_630nm,      # 630nm
        "red": sensor.channel_680nm,         # 680nm
        "nir": sensor.channel_nir,           # Near Infrared
        "clear": sensor.channel_clear,       # Lumière totale
    }


def calculate_cloud_index(spectrum):
    """
    Calcule un indice de couvert nuageux basé sur le ratio bleu/rouge.

    Les nuages diffusent davantage les courtes longueurs d'onde (bleu)
    que les longues (rouge), ce qui augmente le ratio bleu/rouge.

    Args:
        spectrum (dict): Données spectrales

    Returns:
        dict: Indice et classification
    """
    blue = spectrum["blue"]
    red = spectrum["red"]

    if red == 0:
        cloud_index = 0
    else:
        cloud_index = blue / red

    # Classification basée sur des seuils empiriques
    if cloud_index > 1.3:
        classification = "Très nuageux"
    elif cloud_index > 1.1:
        classification = "Nuageux"
    elif cloud_index > 0.9:
        classification = "Partiellement nuageux"
    else:
        classification = "Ciel clair"

    return {
        "cloud_index": cloud_index,
        "classification": classification
    }


def estimate_uv_index(spectrum):
    """
    Estime l'intensité UV indirecte via les canaux violet et indigo.

    Les canaux 415nm (violet) et 445nm (indigo) sont sensibles aux UV-A.
    Cette estimation est approximative mais utile pour détecter l'exposition.

    Args:
        spectrum (dict): Données spectrales

    Returns:
        dict: Estimation UV et niveau d'exposition
    """
    uv_estimate = (spectrum["violet"] + spectrum["indigo"]) / 2

    # Classification basée sur des seuils relatifs
    if uv_estimate > 800:
        level = "Très élevé"
    elif uv_estimate > 600:
        level = "Élevé"
    elif uv_estimate > 400:
        level = "Modéré"
    elif uv_estimate > 200:
        level = "Faible"
    else:
        level = "Très faible"

    return {
        "uv_estimate": uv_estimate,
        "level": level
    }


def detect_dawn_dusk(spectrum):
    """
    Détecte l'aube ou le crépuscule par variation du ratio violet/rouge.

    Le spectre change rapidement au lever/coucher du soleil.

    Args:
        spectrum (dict): Données spectrales

    Returns:
        dict: Indicateur aube/crépuscule
    """
    violet = spectrum["violet"]
    red = spectrum["red"]

    if red == 0:
        dawn_index = 0
    else:
        dawn_index = violet / red

    is_dawn_dusk = dawn_index > 0.3 and dawn_index < 0.7

    return {
        "dawn_index": dawn_index,
        "is_dawn_dusk": is_dawn_dusk
    }


# Exemple d'utilisation
if __name__ == "__main__":
    import time

    sensor = init_spectrometer()
    print("Station météo - Analyse spectrale AS7341\n")

    while True:
        spectrum = read_spectrum(sensor)
        cloud = calculate_cloud_index(spectrum)
        uv = estimate_uv_index(spectrum)
        dawn = detect_dawn_dusk(spectrum)

        print("=== Analyse Spectrale ===")
        print(f"Lumière totale : {spectrum['clear']}")
        print(f"Bleu : {spectrum['blue']} | Rouge : {spectrum['red']}")
        print()

        print("--- Conditions météo ---")
        print(f"Indice nuageux : {cloud['cloud_index']:.2f}")
        print(f"Classification : {cloud['classification']}")
        print()

        print("--- Estimation UV ---")
        print(f"Intensité UV : {uv['uv_estimate']:.0f}")
        print(f"Niveau : {uv['level']}")
        print()

        print("--- Détection aube/crépuscule ---")
        print(f"Indice : {dawn['dawn_index']:.2f}")
        if dawn['is_dawn_dusk']:
            print("Phase aube/crepuscule detectee")
        print()

        print("-" * 50 + "\n")
        time.sleep(10)
