import asyncio
import serial
import time
import json
import paho.mqtt.client as mqtt
from bleak import BleakClient

# --- CONFIGURATION BLUETOOTH ---
MAC_ESP32 = "ADRESS MAC DE ESP"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# NOUVEAU SEUIL : Moins de 3500 = HUMIDE / 3500 et plus = SEC
SEUIL_HUMIDITE = 3500 

# --- VARIABLES GLOBALES ---
etat_capteurs = {"distance": 999.0, "hum1": 4095, "hum2": 4095}
tri_en_cours = False
dernier_affichage = 0  # Chronomètre pour limiter l'affichage à 2 secondes

# --- CONFIGURATION MQTT ---
MQTT_BROKER = "localhost"
TOPIC_CAPTEURS = "smartwaste/capteurs"
TOPIC_TRI = "smartwaste/tri"

print("[INIT] Démarrage du client MQTT...")
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) 
try:
    mqtt_client.connect(MQTT_BROKER, 1883, 60)
    mqtt_client.loop_start()
    print("✅ [INIT] Connecté au Broker MQTT local")
except Exception as e:
    print(f"⚠️ [INIT] Broker MQTT non trouvé : {e}")

# --- CONNEXION AUX 2 ARDUINOS ---
try:
    arduino_sami = serial.Serial("/dev/rfcomm0", 9600, timeout=1)
    print("✅ [INIT] Arduino SAMI (Place 1) connecté")
except:
    arduino_sami = None
    print("❌ [INIT] Impossible de connecter l'Arduino SAMI")

try:
    arduino_anas = serial.Serial("/dev/rfcomm1", 9600, timeout=1)
    print("✅ [INIT] Arduino ANAS (Place 2) connecté")
except:
    arduino_anas = None
    print("❌ [INIT] Impossible de connecter l'Arduino ANAS")

# =====================================================================
# 1. FONCTION DE RÉCEPTION (Affichage toutes les 2 secondes)
# =====================================================================
def reception_capteurs(sender, data):
    global dernier_affichage
    try:
        message = data.decode('utf-8').strip()
        valeurs = message.split(",")
        
        if len(valeurs) == 3:
            # 1. Mise à jour de la mémoire en temps réel
            etat_capteurs["distance"] = float(valeurs[0])
            etat_capteurs["hum1"] = int(valeurs[1])
            etat_capteurs["hum2"] = int(valeurs[2])
            
            # 2. Vérification du chronomètre (Affichage seulement si 2s sont passées)
            maintenant = time.time()
            if maintenant - dernier_affichage >= 2.0:
                dernier_affichage = maintenant
                
                # Traduction en texte (SEC ou HUMIDE) avec le NOUVEAU SEUIL (3500)
                texte_h1 = "SEC" if etat_capteurs["hum1"] >= SEUIL_HUMIDITE else "HUMIDE"
                texte_h2 = "SEC" if etat_capteurs["hum2"] >= SEUIL_HUMIDITE else "HUMIDE"
                
                # Affichage propre dans la console
                print(f"[ÉTAT] Dist: {etat_capteurs['distance']} cm | Place 1: {texte_h1} ({etat_capteurs['hum1']}) | Place 2: {texte_h2} ({etat_capteurs['hum2']})")
                
                # Envoi MQTT (Avec le texte inclus)
                payload = json.dumps({
                    "distance": etat_capteurs["distance"],
                    "h1_val": etat_capteurs["hum1"], "h1_etat": texte_h1,
                    "h2_val": etat_capteurs["hum2"], "h2_etat": texte_h2
                })
                mqtt_client.publish(TOPIC_CAPTEURS, payload)
                
    except Exception as e:
        pass

# =====================================================================
# 2. LOGIQUE DE TRI (Les Moteurs)
# =====================================================================
async def executer_tri(place):
    global tri_en_cours
    tri_en_cours = True 
    
    print(f"\n==========================================")
    print(f"🛑 OBJET DÉTECTÉ À LA PLACE {place} !")
    print(f"⏱️ Attente de 1 seconde pour vérification...")
    
    await asyncio.sleep(1) 
    
    if place == 1:
        hum = etat_capteurs["hum1"]
        if hum >= SEUIL_HUMIDITE:
            print(f"➡️ VERDICT PLACE 1 : SEC ({hum}) -> Moteur SAMI : DROITE")
            if arduino_sami: arduino_sami.write(b'DROIT\n')
            mqtt_client.publish(TOPIC_TRI, '{"moteur":"SAMI", "nature":"SEC", "action":"DROITE"}')
        else:
            print(f"➡️ VERDICT PLACE 1 : HUMIDE ({hum}) -> Moteur SAMI : GAUCHE")
            if arduino_sami: arduino_sami.write(b'GAUCHE\n')
            mqtt_client.publish(TOPIC_TRI, '{"moteur":"SAMI", "nature":"HUMIDE", "action":"GAUCHE"}')

    elif place == 2:
        hum = etat_capteurs["hum2"]
        if hum >= SEUIL_HUMIDITE:
            print(f"➡️ VERDICT PLACE 2 : SEC ({hum}) -> Moteur ANAS : GAUCHE")
            if arduino_anas: arduino_anas.write(b'GAUCHE\n')
            mqtt_client.publish(TOPIC_TRI, '{"moteur":"ANAS", "nature":"SEC", "action":"GAUCHE"}')
        else:
            print(f"➡️ VERDICT PLACE 2 : HUMIDE ({hum}) -> Moteur ANAS : DROITE")
            if arduino_anas: arduino_anas.write(b'DROIT\n')
            mqtt_client.publish(TOPIC_TRI, '{"moteur":"ANAS", "nature":"HUMIDE", "action":"DROITE"}')

    await asyncio.sleep(2.5) 
    print("✅ Tri terminé. Reprise de la détection...")
    print("==========================================\n")
    
    tri_en_cours = False 

# =====================================================================
# 3. BOUCLE PRINCIPALE
# =====================================================================
async def main():
    print(f"🔍 Connexion BLE à l'ESP32 ({MAC_ESP32})...")
    try:
        async with BleakClient(MAC_ESP32) as client:
            print("✅ Connecté ! Lancement du système (Seuil Humidité < 3500).\n")
            await client.start_notify(CHARACTERISTIC_UUID, reception_capteurs)
            
            while True:
                await asyncio.sleep(0.1)
                
                if not tri_en_cours:
                    dist = etat_capteurs["distance"]
                    if 1.0 <= dist <= 10.0:
                        asyncio.create_task(executer_tri(1))
                    elif 10.0 < dist <= 20.0:
                        asyncio.create_task(executer_tri(2))

    except Exception as e:
        print(f"❌ Erreur BLE : {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nArrêt manuel du programme.")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        if arduino_sami: arduino_sami.close()
        if arduino_anas: arduino_anas.close()