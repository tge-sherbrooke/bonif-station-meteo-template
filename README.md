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

## Capteurs additionnels

Des capteurs optionnels sont disponibles sur demande pour enrichir votre station :

| Capteur | Fonction | Adresse I²C |
|---------|----------|-------------|
| HTS221 | Température/humidité (validation croisée) | 0x5F |
| AS7341 | Spectromètre 11 canaux (analyse météo) | 0x39 |
| VCNL4200 | Lumière ambiante et proximité | 0x51 |
| Neoslider | Potentiomètre + 4 LEDs NeoPixel RGB | 0x30 |

Pour installer les dépendances des capteurs additionnels :
```bash
uv sync --extra sensors
```

Consultez les exemples dans `ressources/snippets/` pour l'intégration de chaque capteur.

## Améliorations possibles

Ce code est volontairement minimal. Consulter les consignes fournies par votre enseignant pour la liste des améliorations à implémenter.
