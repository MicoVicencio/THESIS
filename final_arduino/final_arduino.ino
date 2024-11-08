#define BLYNK_TEMPLATE_ID "TMPL6SXs9qykp"
#define BLYNK_TEMPLATE_NAME "Esp32"
#define BLYNK_AUTH_TOKEN "LduZDw9669CeWfGNk0sx7yy1xFaBkYb6"
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <SPI.h>
#include <MFRC522.h>  // Include the MFRC522 library

// Wi-Fi cre  entials
const char* ssid = "MICOVICENCIO";   
const char* password = "micopogi";    

// Blynk configuration
BlynkTimer timer;
const int relayPin = 13; // Relay GPIO pin
bool relayState = false;  // Relay state
const int buzzerPin = 17;     // Buzzer GPIO pin (connected to D5)

// RFID setup
#define RST_PIN 22    // Reset pin
#define SS_PIN 21     // Slave select pin (SDA)
MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

// Define valid UIDs to match (make sure these match the exact RFID card UIDs)
String validHexCodes[] = {
  "43bfc28", "3321c28", "d3741829", "a337729", 
  "837fde28", "23bc1228", "f3a4e428", "638b3729", 
  "537e7729", "236db26", "f7bb1e3"
};
const int validUIDCount = sizeof(validHexCodes) / sizeof(validHexCodes[0]);

// Timeout variables
unsigned long relayTimeout = 10800000;
unsigned long lastValidUIDTime = 0;  // To track when the last valid UID was scanned
String lastValidUID = "";  // Store the last valid UID

void setup() {
  Serial.begin(115200);

  // Initialize the relay pin and set its initial state
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);  // Start with relay OFF
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);  // Start with buzzer OFF

  // Initialize the MFRC522 RFID module
  SPI.begin(); 
  mfrc522.PCD_Init();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());  // Print the local IP address
  
  // Connect to Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);

  // Sync relay state with Blynk on startup
  Blynk.virtualWrite(V0, relayState);  // Sync the relay state to the Blynk app
}

void loop() {
  // Handle Blynk tasks
  Blynk.run();
  timer.run();  // Run the timer for Blynk

  // Check for relay timeout
  if (relayState && millis() - lastValidUIDTime > relayTimeout) {
    digitalWrite(relayPin, HIGH);  // Turn off relay
    relayState = false;
    lastValidUID = "";  // Reset the last valid UID
    Blynk.virtualWrite(V0, relayState);  // Sync Blynk button state
    Serial.println("Relay turned off due to timeout.");
  }

  // Look for new RFID cards
  if (mfrc522.PICC_IsNewCardPresent()) {
    if (mfrc522.PICC_ReadCardSerial()) {
      // Get the UID of the card and convert it to hex
      String hexCode = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        hexCode += String(mfrc522.uid.uidByte[i], HEX);
      }

      Serial.print("Received Hex Code: ");
      Serial.println(hexCode);
      Serial.println("Lab A");
      // Activate buzzer when card is tapped
      digitalWrite(buzzerPin, HIGH);  // Turn on the buzzer
      delay(100);                     // Buzz for a short duration
      digitalWrite(buzzerPin, LOW);   // Turn off the buzzer

      // Check if the hex code matches one of the valid UIDs
      bool isValid = false;
      for (int i = 0; i < validUIDCount; i++) {
        if (hexCode.equalsIgnoreCase(validHexCodes[i])) {
          isValid = true;
          break;
        }
      }

      // If valid and matches the last valid UID or relay is off, toggle relay
      if (isValid) {
        if (!relayState || hexCode == lastValidUID) {
          relayState = !relayState;  // Toggle relay state
          digitalWrite(relayPin, relayState ? LOW : HIGH);  // Activate or deactivate relay
          lastValidUIDTime = millis();  // Reset timeout timer
          lastValidUID = hexCode;  // Store this as the last valid UID
          Blynk.virtualWrite(V0, relayState);  // Sync Blynk button state

          if (relayState) {
            Serial.println("Relay turned ON.");
          } else {
            Serial.println("Relay turned OFF.");
            lastValidUID = "";  // Clear last valid UID when turning off
          }
        }
      } else {
        Serial.println("Hex code did not match.");
      }

      mfrc522.PICC_HaltA();  // Halt PICC (card)
    }
  }

  // Optional delay for stability
  delay(100);
}

// Blynk Virtual Pin (V0) to toggle the relay from the Blynk app
BLYNK_WRITE(V0) {
  int pinValue = param.asInt();
  if (pinValue == 1) {
    digitalWrite(relayPin, LOW);
    relayState = true;
    lastValidUIDTime = millis();  // Reset the timeout
    Serial.println("Admin on");
    // Activate buzzer when card is tapped
      digitalWrite(buzzerPin, HIGH);  // Turn on the buzzer
      delay(100);                     // Buzz for a short duration
      digitalWrite(buzzerPin, LOW);   // Turn off the buzzer
  } else {
    digitalWrite(relayPin, HIGH);
    relayState = false;
    lastValidUID = "";  // Clear last valid UID
    Serial.println("Admin off");
    // Activate buzzer when card is tapped
      digitalWrite(buzzerPin, HIGH);  // Turn on the buzzer
      delay(100);                     // Buzz for a short duration
      digitalWrite(buzzerPin, LOW);   // Turn off the buzzer
  }

  // Sync the relay state with Blynk after it changes
  Blynk.virtualWrite(V0, relayState);  // Update Blynk switch state to match relay state
}
