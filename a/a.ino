
// ESP32-개발
#include <WiFi.h> // ESP32 WiFi 라이브러리 포함
#include <WiFiClient.h> // ESP32 WiFi 클라이언트 라이브러리 포함

const char* ssid = "Nixdora-main"; // WiFi SSID (네트워크 이름)
const char* password = "aaaaaaaa"; // WiFi 비밀번호

WiFiServer tcpServer(5000); // TCP 서버 객체 생성 (포트 5000)
WiFiClient tcpCleint; // TCP 클라이언트 객체 생성

uint8_t rx_buf[1024]; // 수신 버퍼 (최대 1024 바이트)
uint16_t rx_len = 0; // 수신된 데이터 길이
uint8_t tx_buf[1024]; // 송신 버퍼 (최대 1024 바이트)
uint16_t tx_len = 0; // 송신할 데이터 길이


// ADC로 사용할 핀 번호 설정
// (ESP32-S3에서는 ADC1 채널을 지원하는 핀을 사용하는 것이 좋습니다. WiFi를 사용할 경우 ADC2 사용에 제약이 있을 수 있습니다.)
// 추천 핀 (ADC1): GPIO 1 ~ 10 등
const int audio_adc = 36; // 오디오 신호를 측정할 ADC 핀 번호 (예: GPIO 1)
const int vive_adc = 34; // Vive 신호를 측정할 ADC 핀 번호 (예: GPIO 2)
const int event = 3; // 이벤트 신호를 측정할 GPIO 핀 번호 (예: GPIO 3)
const int event_dac = 4; // 이벤트 신호의 측정 감도를 출력할 DAC 핀 번호 (예: GPIO 4)

void setup() {

  // 시리얼 통신 시작 (보드레이트: 115200)
  Serial.begin(115200); // 시리얼 모니터를 통해 ADC 값을 출력하기 위해 시리얼 통신을 초기화합니다.
  delay(1000); // 시리얼 모니터가 켜질 시간 확보
	Serial.setDebugOutput(true);  // 디버그 출력을 활성화하여 WiFi 연결 상태 등을 시리얼 모니터에 출력할 수 있도록 합니다.
	Serial.println(); // 줄바꿈 출력
  Serial.println("Connecting to WiFi..."); // WiFi 연결 시작 메시지 출력
	
	WiFi.begin(ssid, password); // WiFi 네트워크에 연결을 시도합니다.
	while (WiFi.status() != WL_CONNECTED) { // WiFi 연결이 완료될 때까지 대기합니다.
		delay(500); // 500ms마다 연결 상태를 확인합니다.
		Serial.print("."); // 연결 시도 중임을 나타내기 위해 점을 출력합니다.
	}
	Serial.println(""); // 줄바꿈 출력
	Serial.println("WiFi connected."); // WiFi 연결 성공 메시지 출력
	Serial.print("IP address: "); // 연결된 WiFi 네트워크에서 할당된 IP 주소를 시리얼 모니터에 출력합니다.
	Serial.println(WiFi.localIP()); // 할당된 IP 주소 출력
	tcpServer.begin(); // TCP 서버 시작
	tcpServer.setNoDelay(true); // TCP 서버의 Nagle 알고리즘을 비활성화하여 데이터 전송 지연을 줄입니다.

  // ADC 해상도 설정 (ESP32-S3는 최대 12비트: 0~4095 해상도를 가집니다)
  analogReadResolution(12); // ADC 해상도를 12비트로 설정하여 0~4095 범위의 값을 읽을 수 있도록 합니다.
  
  Serial.println("ESP32-S3 ADC 테스트 시작!"); // 초기 메시지 출력
}

void loop() {

	if (tcpServer.hasClient()) { // TCP 서버에 새로운 클라이언트가 연결되었는지 확인합니다.
		if (!tcpCleint || !tcpCleint.connected()) {  // 현재 클라이언트가 없거나 연결이 끊어진 경우에만 새로운 클라이언트를 수락합니다.
			tcpCleint = tcpServer.available(); // 새로운 클라이언트를 수락합니다.
			Serial.println("accept new Connection ..."); // 새로운 클라이언트가 연결되었음을 시리얼 모니터에 출력합니다.
			}
			
		else { // 이미 클라이언트가 연결되어 있는 경우, 새로운 연결을 거부합니다.
			WiFiClient temp = tcpServer.available(); temp.stop(); // 새로운 클라이언트를 수락한 후 즉시 연결을 종료하여 거부합니다.
			Serial.println("reject new Connection ...");  // 새로운 클라이언트가 연결을 시도했지만 이미 다른 클라이언트가 연결되어 있어서 거부되었음을 시리얼 모니터에 출력합니다.
			}
	}
	
	if (!tcpCleint || !tcpCleint.connected()) { // 현재 클라이언트가 없거나 연결이 끊어진 경우, TCP 통신을 처리하지 않고 루프를 계속 진행합니다.
		delay(100); return; // 클라이언트가 없거나 연결이 끊어진 경우, 100ms 대기 후 루프를 계속 진행합니다. 이렇게 하면 CPU 사용량을 줄이고 불필요한 통신 처리를 방지할 수 있습니다.
	}
	
	
	while(tcpCleint.connected()) { // 클라이언트가 연결되어 있는 동안 통신을 처리합니다.
	  // 지정한 핀의 아날로그 값 읽어오기
  int adcValue = analogRead(audio_adc); // ADC 값을 읽어옵니다. 이 값은 0에서 4095 사이의 정수입니다 (12비트 해상도).

  // 측정된 ADC 값 출력
  Serial.print("ADC 측정값 (0~4095): "); // ADC 값을 시리얼 모니터에 출력합니다.
  Serial.println(adcValue); // ADC 값은 0에서 4095 사이의 정수입니다.

  // 대략적인 전압(V)으로 변환 (기준 전압 3.3V 기준)
  // ESP32의 ADC는 완벽히 선형적이지 않으므로(특히 0V와 3.3V 근처), 
  // 정밀한 측정을 위해서는 캘리브레이션 API를 사용하는 것이 좋습니다.
  float voltage = (adcValue / 4095.0) * 3.3; // ADC 값을 0~4095 범위에서 0~3.3V 범위로 변환합니다.

  

		if (tcpCleint.available()) { // 클라이언트로부터 데이터가 수신되었는지 확인합니다.
			while (tcpCleint.available()) { // 클라이언트로부터 수신된 데이터를 모두 읽어옵니다.
				rx_buf[rx_len] = tcpCleint.read(); // 클라이언트로부터 한 바이트씩 데이터를 읽어와 수신 버퍼에 저장합니다.
				rx_len++; // 수신된 데이터 길이를 증가시킵니다.
			}
			Serial.write(rx_buf, rx_len); rx_len = 0; // 수신된 데이터를 시리얼 모니터에 출력한 후, 수신 버퍼 길이를 초기화합니다.
		}
		
			while (tx_len <= sizeof(tx_buf)/sizeof(uint8_t)) { // 시리얼 모니터로부터 입력된 데이터를 모두 읽어옵니다.
			  Serial.print("송신 전압: "); // 변환된 전압 값을 시리얼 모니터에 출력합니다.
  			Serial.print(adcValue); // 전압 값은 0V에서 3.3V 사이의 실수입니다.
  			Serial.println(" V"); // 단위로 "V"를 출력합니다.
				Serial.println("-----------------------"); // 구분선 출력
				tx_buf[tx_len] = voltage; tx_len++; // 시리얼 모니터로부터 한 바이트씩 데이터를 읽어와 송신 버퍼에 저장하고, 송신 데이터 길이를 증가시킵니다.
			}
		tcpCleint.write(tx_buf, tx_len); tx_len = 0; // 송신 버퍼에 저장된 데이터를 클라이언트로 전송한 후, 송신 버퍼 길이를 초기화합니다.
		
		delay(1000); // 클라이언트와의 통신을 처리한 후, 1ms 대기하여 CPU 사용량을 줄입니다. 너무 짧은 간격으로 설정하면 CPU 사용량이 높아질 수 있습니다.
	}
  // 500ms 대기 후 반복
  delay(500); // 500ms마다 ADC 값을 읽고 출력하도록 설정합니다. 너무 짧은 간격으로 설정하면 시리얼 모니터가 너무 빠르게 업데이트되어 읽기 어려울 수 있습니다.
}
