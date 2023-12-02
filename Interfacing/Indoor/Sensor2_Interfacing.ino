#include <SDS011.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <ThingSpeak.h>

Adafruit_AHTX0 aht;

float p25, p10, temperature, humidity;
int error;
int datapointnumber=0;

SDS011 sds;

char ssid[] = "ROG Phone 7 series_7960"; // SSID of the WiFi Network
char password[] = "11111111"; // PWD of the WiFi Network

int writeChannelID = 2341776 ; // Channel ID
char writeAPIKey[] = "XMCV8GFBCWDPTGCL"; // Write API Key

WiFiClient wifiClient;

void setup() {

  Serial.begin(9600); // Initialize serial monitor

  ThingSpeak.begin(wifiClient);

  WiFi.begin(ssid, password); // Initialising the WiFi connection
  while (WiFi.status() != WL_CONNECTED) // Waiting till the WiFi is connected
  {
    Serial.println("Connecting to WiFi...");
    delay(1000);
  }

  // Initialize the SoftwareSerial port
  sds.begin(16,17);

  while (!aht.begin()) {
    Serial.println("Could not find a valid AHT10 sensor, check wiring!");
    // while (1);
  }

}

void loop() {
  sensors_event_t humidity_event, temperature_event;
  
  if (aht.getEvent(&humidity_event, &temperature_event)) {
    Serial.print("Temperature: ");
    temperature=temperature_event.temperature;
    Serial.print(temperature);
    Serial.print(" °C, Humidity: ");
    humidity=humidity_event.relative_humidity;
    Serial.print(humidity);
    Serial.println(" %");
  } else {
    Serial.println("Failed to read from AHT10 sensor!");
  }

  error = sds.read(&p25, &p10);

  p25=p25*1.3586309233786342+8.986988938804878;

  p10=p10*1.7734262357652464+70.12370821420492;

  if (!error) {
    Serial.print("P2.5 value: ");
    Serial.println(p25);
    Serial.print("P10 value: ");
    Serial.println(p10);
  } else {
    Serial.println("Error reading data from SDS011 sensor.");
  }

  // int x=ThingSpeak.writeField(writeChannelID, 1, temperature, writeAPIKey);
  // if(x != 200){
  //   Serial.println("Problem updating temperature channel. HTTP error code " + String(x));
  // }
  // delay(15000);

  // x=ThingSpeak.writeField(writeChannelID, 2, humidity, writeAPIKey);
  // if(x != 200){
  //   Serial.println("Problem updating humidity channel. HTTP error code " + String(x));
  // }
  // delay(15000);
  
  // x = ThingSpeak.writeField(writeChannelID, 3, p25, writeAPIKey);
  // if(x != 200){
  //   Serial.println("Problem updating pm2.5 channel. HTTP error code " + String(x));
  // }
  // delay(15000);

  // x = ThingSpeak.writeField(writeChannelID, 4, p10, writeAPIKey);
  // if(x != 200){
  //   Serial.println("Problem updating pm10 channel. HTTP error code " + String(x));
  // }
  // delay(15000); // Wait for a few seconds before reading again

  float values[] = {temperature, humidity, p25, p10};
  int numFields = sizeof(values) / sizeof(values[0]);
  ThingSpeak.setField(1, temperature);
  ThingSpeak.setField(2, humidity);
  ThingSpeak.setField(3, p25);
  ThingSpeak.setField(4, p10);
  int status = ThingSpeak.writeFields(writeChannelID, writeAPIKey);
  if (status == 200) {
    datapointnumber=datapointnumber+1;
    Serial.print("Data ");
    Serial.print(datapointnumber);
    Serial.println(" sent successfully!");
  } else {
    Serial.println("Problem updating ThingSpeak channel. HTTP error code " + String(status));
  }
  delay(60000);
}