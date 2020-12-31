char serialData;

void setup() {
  // put your setup code here, to run once:
  pinMode(7, OUTPUT); // connected to the S terminal of relay
  digitalWrite(7, LOW); //turn relay on
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
    if(Serial.available() > 0)
    {
      serialData = Serial.read();
      Serial.println(serialData);
      
      if(serialData == '1')
      {
        digitalWrite(7, HIGH);
      }
      else if(serialData == '0')
      {
        digitalWrite(7, LOW);
//        delay(3000);
//        digitalWrite(7, LOW);
//        Serial.println("on");
      }
    }  
}
