#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// =================== Wi-Fi Credentials ===================
const char* ssid = "Pavan";        // Your phone hotspot SSID
const char* password = "personal"; // Your phone hotspot password

// =================== Motor Pin Setup =====================
#define ENA D1
#define IN1 D2
#define IN2 D3
#define ENB D5
#define IN3 D6
#define IN4 D7

int speedPWM = 120;                      // Motor speed (0–255)
const unsigned long TURN_DELAY = 600;    // Adjust for exact 90° rotation

ESP8266WebServer server(80);

// Track robot motion states
enum MoveState { IDLE, FORWARD, LEFT_TURN, RIGHT_TURN };
MoveState moveState = IDLE;
unsigned long actionEnd = 0;

// =================== Setup ===============================
void setup() {
  Serial.begin(115200);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.println("Connecting to WiFi...");

  // ✅ USE DHCP (do NOT set static IP on phone hotspot)
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");
  Serial.print("ESP8266 IP Address: ");
  Serial.println(WiFi.localIP());

  // Define HTTP routes
  server.on("/FORWARD", []() { forward(); server.send(200, "text/plain", "FORWARD"); });
  server.on("/LEFT", []() { startTurnLeft(); server.send(200, "text/plain", "LEFT"); });
  server.on("/RIGHT", []() { startTurnRight(); server.send(200, "text/plain", "RIGHT"); });
  server.on("/BLINK", []() { stopMotors(); server.send(200, "text/plain", "STOP"); });
  server.onNotFound([]() { server.send(404, "text/plain", "Invalid Command"); });

  server.begin();
  Serial.println("HTTP server started!");
}

// =================== Main Loop ===========================
void loop() {
  server.handleClient();
  unsigned long now = millis();

  if ((moveState == LEFT_TURN || moveState == RIGHT_TURN) && now >= actionEnd) {
    stopMotors();
    moveState = IDLE;
    Serial.println("Turn complete");
  }
}

// =================== Movement Functions ==================
void forward() {
  Serial.println("FORWARD");
  analogWrite(ENA, speedPWM);
  analogWrite(ENB, speedPWM);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  moveState = FORWARD;
}

void stopMotors() {
  Serial.println("STOP");
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  moveState = IDLE;
}

void startTurnLeft() {
  Serial.println("LEFT");
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, speedPWM);
  analogWrite(ENB, speedPWM);
  moveState = LEFT_TURN;
  actionEnd = millis() + TURN_DELAY;
}

void startTurnRight() {
  Serial.println("RIGHT");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, speedPWM);
  analogWrite(ENB, speedPWM);
  moveState = RIGHT_TURN;
  actionEnd = millis() + TURN_DELAY;
}
