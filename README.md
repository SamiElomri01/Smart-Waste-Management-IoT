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

🔌 Câblage
(Ajoute ici l'image de ton schéma Fritzing ou le tableau des branchements)

🚀 Comment lancer le projet
Flasher l'ESP32 et les Arduinos avec leurs codes respectifs.

Appairer les HC-05 au Raspberry Pi (sudo rfcomm bind...).

Lancer le broker Mosquitto.

Lancer le script python : python3 cerveau.py.

4. Les étapes pour publier sur GitHub
Connecte-toi à ton compte GitHub et clique sur le bouton New (Nouveau repository).

Donne-lui un nom clair, comme Smart-Waste-Management-IoT.

Coche la case "Add a README file".

Clique sur Create repository.

Tu peux envoyer tes fichiers directement depuis le site web de GitHub (en cliquant sur Add file -> Upload files) en glissant tes dossiers organisés.

N'oublie pas d'aller dans les paramètres du repository (Settings > Collaborators) pour inviter Anas afin qu'il apparaisse comme co-créateur du projet avec toi !
