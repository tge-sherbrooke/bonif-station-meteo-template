# /// script
# requires-python = ">=3.11"
# dependencies = ["adafruit-circuitpython-ahtx0", "adafruit-blinka", "paho-mqtt"]
# ///
"""
Exemple de publication MQTT des donnees capteur vers un broker.

Categorie B -- Traitement et logique
Difficulte : Moyenne

Ce snippet montre comment:
- Se connecter a un broker MQTT (ex. test.mosquitto.org)
- Publier les donnees de temperature et humidite en JSON
- Gerer les erreurs de connexion et de publication
- Se deconnecter proprement
"""

import json
import time

import board
import adafruit_ahtx0
import paho.mqtt.client as mqtt


# Configuration MQTT
BROKER_HOST = "test.mosquitto.org"
BROKER_PORT = 1883
TOPIC = "station-meteo/capteurs"


def create_mqtt_client():
    """
    Cree et configure un client MQTT.

    Returns:
        mqtt.Client: Client MQTT configure
    """
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    return client


def publish_sensor_data(client, temperature, humidity):
    """
    Publie les donnees capteur au format JSON sur le topic MQTT.

    Args:
        client (mqtt.Client): Client MQTT connecte
        temperature (float): Temperature en Celsius
        humidity (float): Humidite relative en pourcentage
    """
    payload = json.dumps({
        "temperature_c": round(temperature, 2),
        "humidity_pct": round(humidity, 2),
        "timestamp": time.time(),
    })
    result = client.publish(TOPIC, payload)
    result.wait_for_publish()


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation capteur
    i2c = board.I2C()
    sensor = adafruit_ahtx0.AHTx0(i2c)

    # Connexion MQTT
    client = create_mqtt_client()
    try:
        client.connect(BROKER_HOST, BROKER_PORT)
        client.loop_start()
        print(f"Connecte a {BROKER_HOST}:{BROKER_PORT}")
        print(f"Topic : {TOPIC}")
        print("Ctrl+C pour arreter\n")

        while True:
            temperature = sensor.temperature
            humidity = sensor.relative_humidity
            publish_sensor_data(client, temperature, humidity)
            print(f"Publie : {temperature:.1f}C, {humidity:.1f}%")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nArret demande par l'utilisateur")

    finally:
        client.loop_stop()
        client.disconnect()
        print("Deconnexion MQTT propre")
