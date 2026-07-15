#include <SoftwareSerial.h>
#include <Servo.h>

// HC-05 branché sur TX=10 et RX=11
SoftwareSerial BT(10, 11);
Servo monMoteur;

const int ANGLE_REPOS = 90;   // Au centre (Trappe fermée)
const int ANGLE_DROIT = 30;   // Rotation à droite
const int ANGLE_GAUCHE = 150; // Rotation à gauche

void setup() {
  Serial.begin(9600); 
  BT.begin(9600); 
  monMoteur.attach(9); // Servomoteur sur la broche 9

  monMoteur.write(ANGLE_REPOS); 
  
  Serial.println("=====================================");
  Serial.println(" ARDUINO PRET : Attente de commande...");
  Serial.println("=====================================");
}

void loop() {
  if (BT.available()) {
    String commande = BT.readStringUntil('\n');
    commande.trim();

    Serial.print(">> Ordre reçu : ");
    Serial.println(commande);

    if (commande == "DROIT") {
      Serial.println("-> Mouvement : DROITE");
      monMoteur.write(ANGLE_DROIT);
      delay(2000); // Temps pour que le déchet tombe
      monMoteur.write(ANGLE_REPOS); // Retour au centre
      delay(500); 
    } 
    else if (commande == "GAUCHE") {
      Serial.println("-> Mouvement : GAUCHE");
      monMoteur.write(ANGLE_GAUCHE);
      delay(2000); 
      monMoteur.write(ANGLE_REPOS); 
      delay(500); 
    }
  }
}