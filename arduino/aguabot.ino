int pin_sensor = 2; // Pin del sensor de nivel
int pin_rele = 8;   // Pin de control del relé

int valor = 0;
bool modoManual = false; // true si está en control desde la app
unsigned long tiempoEncendido = 0;

void setup() {
  Serial.begin(9600);

  pinMode(pin_sensor, INPUT);
  pinMode(pin_rele, OUTPUT);

  digitalWrite(pin_rele, HIGH); // Relé apagado al inicio

  delay(2000); // ⏳ Tiempo de inicio

  // Mensajes iniciales claros
  Serial.println("USB listo para recibir comandos");
  Serial.println("Sistema listo - Modo automático");
}

void loop() {
  // Leer comandos desde USB
  if (Serial.available()) {
    char comando = Serial.read();

    if (comando == '1') { // Encender manual
      modoManual = true;
      digitalWrite(pin_rele, LOW);
      tiempoEncendido = millis();
      Serial.println("Encendido manual por 5 minutos");
    }
    else if (comando == '0') { // Apagar manual
      modoManual = false;
      digitalWrite(pin_rele, HIGH);
      Serial.println("Apagado manual - Vuelve a automático");
    }
    else if (comando == 'A') { // Volver a automático
      modoManual = false;
      Serial.println("Modo automático activado desde la app");
    }
  }

  // Modo manual con temporizador
  if (modoManual) {
    if (millis() - tiempoEncendido >= 300000) { // 5 minutos
      digitalWrite(pin_rele, HIGH);
      modoManual = false;
      Serial.println("Tiempo manual terminado - Vuelve a automático");
    }
  }
  else {
    // Modo automático
    valor = digitalRead(pin_sensor);
    delay(50); // Evita rebotes de lectura

    if (valor == 0) { // Tanque lleno
      digitalWrite(pin_rele, LOW);
      Serial.println("Tanque lleno - Lámpara encendida");
    }
    else { // Tanque vacío
      digitalWrite(pin_rele, HIGH);
      Serial.println("Tanque vacío - Lámpara apagada");
    }
  }

  delay(500);
}
