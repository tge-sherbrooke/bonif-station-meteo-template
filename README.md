# Station meteo - Code de base

Station meteo basique utilisant un capteur AHT20 sur Raspberry Pi 5.

## Installation

1. Cloner ce depot
2. Installer les dependances avec `uv` :
   ```bash
   uv sync
   ```

## Utilisation

Lancer la station meteo :
```bash
uv run main.py
```

## Materiel requis

- Raspberry Pi 5 avec Raspberry Pi OS Lite
- Capteur AHT20 (temperature et humidite)
- Cable STEMMA QT pour connexion I2C

## Configuration I2C

S'assurer que I2C est active :
```bash
sudo raspi-config nonint do_i2c 0
```

Verifier la detection du capteur (adresse 0x38) :
```bash
i2cdetect -y 1
```

## Fonctionnalites

- Lecture de la temperature (C)
- Lecture de l'humidite relative (%)
- Affichage console

## Ameliorations possibles

Ce code est volontairement minimal. Consulter les consignes fournies par votre enseignant pour la liste des ameliorations a implementer.
