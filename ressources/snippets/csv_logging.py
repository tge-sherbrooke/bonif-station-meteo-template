# /// script
# requires-python = ">=3.9"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-blinka"]
# ///
"""
Exemple de journalisation des données dans un fichier CSV.

Catégorie B — Traitement et logique
Difficulté : Faible

Ce snippet montre comment:
- Créer un fichier CSV avec en-têtes
- Horodater les mesures (format ISO 8601)
- Enregistrer les données de façon persistante
- Gérer la rotation des fichiers (nouveau fichier par jour)
"""

import csv
import time
from datetime import datetime
from pathlib import Path
import board
import adafruit_ahtx0


class CSVDataLogger:
    """
    Gestionnaire de journalisation CSV pour la station météo.
    """

    def __init__(self, data_dir: str = "data", rotation: str = "daily"):
        """
        Initialise le logger CSV.

        Args:
            data_dir (str): Répertoire de stockage des fichiers CSV
            rotation (str): Stratégie de rotation ("none", "daily", "weekly")
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.rotation = rotation
        self.current_file = None
        self.csv_writer = None
        self.file_handle = None

    def _get_filename(self) -> Path:
        """
        Génère le nom du fichier CSV selon la stratégie de rotation.

        Returns:
            Path: Chemin du fichier CSV
        """
        if self.rotation == "none":
            return self.data_dir / "meteo_data.csv"

        elif self.rotation == "daily":
            date_str = datetime.now().strftime("%Y-%m-%d")
            return self.data_dir / f"meteo_data_{date_str}.csv"

        elif self.rotation == "weekly":
            week_str = datetime.now().strftime("%Y-W%W")
            return self.data_dir / f"meteo_data_{week_str}.csv"

        else:
            raise ValueError(f"Rotation '{self.rotation}' non supportée")

    def _ensure_file_open(self):
        """
        S'assure que le fichier CSV est ouvert et prêt à écrire.
        Crée le fichier et les en-têtes si nécessaire.
        """
        target_file = self._get_filename()

        # Si le fichier a changé (rotation), fermer l'ancien
        if self.current_file != target_file:
            if self.file_handle:
                self.file_handle.close()

            # Vérifier si le fichier existe déjà (pour savoir si on écrit les en-têtes)
            file_exists = target_file.exists()

            # Ouvrir le nouveau fichier en mode append
            self.file_handle = open(target_file, 'a', newline='')
            self.csv_writer = csv.writer(self.file_handle)
            self.current_file = target_file

            # Écrire les en-têtes si c'est un nouveau fichier
            if not file_exists:
                self._write_headers()

    def _write_headers(self):
        """Écrit les en-têtes du fichier CSV."""
        headers = ["timestamp", "timestamp_iso", "temperature_c", "humidity_percent"]
        self.csv_writer.writerow(headers)
        self.file_handle.flush()

    def log_data(self, temperature: float, humidity: float):
        """
        Enregistre une mesure dans le fichier CSV.

        Args:
            temperature (float): Température en Celsius
            humidity (float): Humidité relative en pourcentage
        """
        self._ensure_file_open()

        # Horodatage
        timestamp_unix = time.time()
        timestamp_iso = datetime.fromtimestamp(timestamp_unix).isoformat()

        # Écriture de la ligne
        self.csv_writer.writerow([
            timestamp_unix,
            timestamp_iso,
            f"{temperature:.2f}",
            f"{humidity:.2f}"
        ])

        # Forcer l'écriture sur disque
        self.file_handle.flush()

    def close(self):
        """Ferme proprement le fichier CSV."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            self.current_file = None


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)
    logger = CSVDataLogger(data_dir="data", rotation="daily")

    print("Station météo - Journalisation CSV")
    print(f"Fichier : {logger._get_filename()}")
    print("Ctrl+C pour arrêter\n")

    try:
        while True:
            # Lecture des données
            temperature = sensor.temperature
            humidity = sensor.relative_humidity

            # Enregistrement dans le CSV
            logger.log_data(temperature, humidity)

            # Affichage console
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Temp: {temperature:.1f}C | Hum: {humidity:.1f}% | Enregistre")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")

    finally:
        logger.close()
        print("Fichier CSV ferme proprement")
