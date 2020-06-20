#include <Arduino.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <String.h>

// Update these with values suitable for your network.
byte mac[] = {0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED};
IPAddress server(192, 168, 1, 116); //server IP
IPAddress ip(192, 168, 1, 117);
IPAddress dns(192, 168, 1, 254);
char subscribeTopic[] = "result/arduino0";
char publishTopic[] = "localCode/arduino0";
boolean served = false;

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived [topic:");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  served = true;
}

EthernetClient ethClient;
PubSubClient client(ethClient);

void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("arduino0"))
      Serial.println("connected");
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(9600);

  Ethernet.begin(mac, ip, dns);
  // Allow the hardware to sort itself out
  delay(1500);

  client.setServer(server, 1883);
  client.setCallback(callback);

  while (!client.connected())
    reconnect();

  client.subscribe(subscribeTopic);
}

void loop()
{
  client.publish(publishTopic, "3 5");
  Serial.println("Published");
  while (served == false)
  {
    client.loop();
    delay(2000);
  }

  served = false;
}
