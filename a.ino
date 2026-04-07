// ESP32-S3 아날로그 입력(ADC) 예제

// ADC로 사용할 핀 번호 설정
// (ESP32-S3에서는 ADC1 채널을 지원하는 핀을 사용하는 것이 좋습니다. WiFi를 사용할 경우 ADC2 사용에 제약이 있을 수 있습니다.)
// 추천 핀 (ADC1): GPIO 1 ~ 10 등
const int adcPin = 1; 

void setup() {
  // 시리얼 통신 시작 (보드레이트: 115200)
  Serial.begin(115200);
  delay(1000); // 시리얼 모니터가 켜질 시간 확보

  // ADC 해상도 설정 (ESP32-S3는 최대 12비트: 0~4095 해상도를 가집니다)
  analogReadResolution(12);
  
  Serial.println("ESP32-S3 ADC 테스트 시작!");
}

void loop() {
  // 지정한 핀의 아날로그 값 읽어오기
  int adcValue = analogRead(adcPin);

  // 측정된 ADC 값 출력
  Serial.print("ADC 측정값 (0~4095): ");
  Serial.println(adcValue);

  // 대략적인 전압(V)으로 변환 (기준 전압 3.3V 기준)
  // ESP32의 ADC는 완벽히 선형적이지 않으므로(특히 0V와 3.3V 근처), 
  // 정밀한 측정을 위해서는 캘리브레이션 API를 사용하는 것이 좋습니다.
  float voltage = (adcValue / 4095.0) * 3.3;
  
  Serial.print("예상 전압: ");
  Serial.print(voltage);
  Serial.println(" V");
  
  Serial.println("-----------------------");

  // 500ms 대기 후 반복
  delay(500);
}
