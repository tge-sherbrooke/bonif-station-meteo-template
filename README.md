# Station météo - Code de base

Station météo basique utilisant un capteur AHT20 sur Raspberry Pi.

## Prérequis

Installer `uv` (gestionnaire de paquets Python) :
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

## Installation

1. Cloner ce dépôt
2. Installer les dépendances avec `uv` :
   ```bash
   uv sync
   ```

## Utilisation

Lancer la station météo :
```bash
uv run main.py
```

## Matériel requis

- Raspberry Pi avec Raspberry Pi OS Lite
- Capteur AHT20 (température et humidité)
- Câble STEMMA QT pour connexion I²C

## Configuration I²C

S'assurer que I²C est activé :
```bash
sudo raspi-config nonint do_i2c 0
```

Vérifier la détection du capteur (adresse 0x38) :
```bash
sudo i2cdetect -y 1
```

## Fonctionnalités

- Lecture de la température (°C)
- Lecture de l'humidité relative (%)
- Affichage console

## Améliorations possibles

Ce code est volontairement minimal. Consulter les consignes fournies par votre enseignant pour la liste des améliorations à implémenter.
