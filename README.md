# Smart-Waste-Management-IoT
📝 Description
Système de tri des déchets 100% automatisé basé sur une architecture réseau hybride. Le système détecte la présence d'un déchet, analyse son taux d'humidité pour déterminer sa nature (Sec/Humide), et actionne le bon moteur de tri.

🏗️ Architecture du Système
Nœud Capteur (ESP32-S3) : Lit les capteurs (Ultrason + Humidité) et diffuse les données en Bluetooth Low Energy (BLE).

Cerveau Central (Raspberry Pi) : Écoute le BLE, applique la logique de tri, envoie les ordres aux moteurs en Bluetooth Classic (SPP), et publie les résultats sur un broker MQTT.

Actionneurs (2x Arduino Uno) : Reçoivent les ordres via modules HC-05 et pilotent les servomoteurs.

⚙️ Matériel Requis
1x Raspberry Pi 4 (ou 3)

1x ESP32-S3

2x Arduino Uno + 2x Modules Bluetooth HC-05

1x Capteur Ultrason HC-SR04

2x Capteurs d'humidité du sol

2x Servomoteurs

## 🔌 Câblage & Connexions (Wiring)

Le projet est divisé en deux parties matérielles distinctes : le nœud capteur (ESP32) et les actionneurs (Arduinos).

### 1. Nœud Capteur (ESP32-S3)
L'ESP32 gère la lecture des capteurs et la transmission BLE.

| Composant | Broche Composant | Broche ESP32-S3 | Remarques / Alimentation |
| :--- | :--- | :--- | :--- |
| **Ultrason (HC-SR04)** | VCC | **5V (VIN / VBUS)** | ⚠️ Nécessite 5V pour fonctionner correctement |
| | GND | GND | Commun |
| | TRIG | **GPIO 18** | |
| | ECHO | **GPIO 16** | |
| **Humidité 1 (Place 1)**| VCC | 3.3V | |
| | GND | GND | Commun |
| | Signal (A0) | **GPIO 4** | Entrée Analogique |
| **Humidité 2 (Place 2)**| VCC | 3.3V | |
| | GND | GND | Commun |
| | Signal (A0) | **GPIO 5** | Entrée Analogique |

---

### 2. Actionneurs (Arduino Uno x2)
*Note : Ce câblage doit être reproduit à l'identique sur les deux cartes Arduino (Place 1 "SAMI" et Place 2 "ANAS").*

| Composant | Broche Composant | Broche Arduino Uno | Remarques / Alimentation |
| :--- | :--- | :--- | :--- |
| **Bluetooth (HC-05)** | VCC | 5V | |
| | GND | GND | Commun |
| | TXD | **Pin 10** | (SoftwareSerial RX) |
| | RXD | **Pin 11** | ⚠️ Utiliser un pont diviseur de tension (1kΩ/2kΩ) |
| **Servomoteur** | VCC (Rouge) | 5V | *Idéalement sur une alimentation 5V externe* |
| | GND (Marron/Noir)| GND | Commun avec l'Arduino |
| | Signal (Jaune) | **Pin 9** | Sortie PWM |

🚀 Comment lancer le projet
Flasher l'ESP32 et les Arduinos avec leurs codes respectifs.

Appairer les HC-05 au Raspberry Pi (sudo rfcomm bind...).

Lancer le broker Mosquitto.

Lancer le script python : python3 cerveau.py.


