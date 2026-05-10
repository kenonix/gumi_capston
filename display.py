import customtkinter as ctk # modern UI 라이브러리인 customtkinter 임포트
import tkinter as tk # 기본 GUI 도구인 tkinter 임포트
import math # 수학 연산을 위한 math 모듈 임포트
import time # 시간 관련 처리를 위한 time 모듈 임포트
import random # 랜덤 값 생성을 위한 random 모듈 임포트
from datetime import datetime # 현재 시간 획득을 위한 datetime 임포트

# GUI 외관 모드(Light) 및 기본 테마 색상(Blue) 설정
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

class NoiseMonitorApp(ctk.CTk): # CTk 클래스를 상속받는 메인 앱 클래스 정의
    def __init__(self): # 클래스 초기화 함수
        super().__init__() # 부모 클래스 초기화 호출

        # 메인 윈도우의 타이틀, 초기 크기 및 최소 크기 설정
        self.title("스마트 홈 소음 모니터링 시스템")
        self.geometry("1100x800") # 사이드바를 포함한 넉넉한 가로 너비
        self.minsize(1000, 750) # 창이 너무 작아지지 않도록 최소 크기 고정
        
        # 앱 내에서 사용할 상태 변수들 초기화
        self.monitor_state = "NORMAL" # 현재 감지 상태 (NORMAL, BABY_ALERT, IMPACT_ALERT)
        self.crying_start_time = None # 아기 울음 시작 시간 기록용
        self.wave_phase = 0 # 파동 애니메이션의 위상 변수
        self.theme_mode = "light" # 현재 테마 모드 (light/dark)
        
        # 가상의 센서 데이터 목록 정의
        self.sensors = [
            {"id": 0, "name": "아기방 센서", "icon": "👶", "status": "NORMAL"},
            {"id": 1, "name": "거실 센서", "icon": "🛋️", "status": "NORMAL"},
            {"id": 2, "name": "현관 센서", "icon": "🚪", "status": "IMPACT_ALERT"}
        ]
        self.current_sensor_index = 0 # 현재 선택된 센서의 인덱스
        self.sensor_card_widgets = [] # 센서 카드 위젯들을 저장할 리스트 (최적화용)
        
        # 테마별 색상 팔레트 정의 (배경색, 텍스트색, 파동색 등)
        self.palettes = {
            "light": {
                "window_bg": "#F8FAFC", # 윈도우 전체 배경
                "card_bg": "#FFFFFF", # 카드 위젯 배경
                "sidebar_bg": "#F1F5F9", # 사이드바 배경
                "NORMAL": {"bg": "#F0F9FF", "text": "#0369A1", "wave": "#38BDF8"}, # 평온 상태 색상
                "BABY_ALERT": {"bg": "#FFFBEB", "text": "#B45309", "wave": "#FBBF24"}, # 아기 울음 상태 색상
                "IMPACT_ALERT": {"bg": "#FEF2F2", "text": "#B91C1C", "wave": "#F87171"} # 충격 감지 상태 색상
            },
            "dark": {
                "window_bg": "#0F172A",
                "card_bg": "#1E293B",
                "sidebar_bg": "#1E293B",
                "NORMAL": {"bg": "#0C4A6E", "text": "#7DD3FC", "wave": "#0EA5E9"},
                "BABY_ALERT": {"bg": "#78350F", "text": "#FDE68A", "wave": "#F59E0B"},
                "IMPACT_ALERT": {"bg": "#7F1D1D", "text": "#FECACA", "wave": "#EF4444"}
            }
        }

        self._setup_ui() # UI 구성 요소 배치 함수 호출
        self._update_time() # 시계 및 데이터 업데이트 루프 시작
        self._animate() # 파동 애니메이션 루프 시작

    def _setup_ui(self): # UI를 구성하고 배치하는 함수
        self.configure(fg_color=self.palettes[self.theme_mode]["window_bg"]) # 메인 배경색 설정
        
        # 메인 그리드 레이아웃 설정 (0번 열: 사이드바, 1번 열: 메인 콘텐츠)
        self.grid_columnconfigure(0, weight=0, minsize=260) # 사이드바 열 고정
        self.grid_columnconfigure(1, weight=1) # 콘텐츠 열 가변 너비
        self.grid_rowconfigure(0, weight=1) # 전체 행 높이 가변

        # --- A. 왼쪽 사이드바 영역 프레임 설정 ---
        self.sidebar = ctk.CTkFrame(self, fg_color=self.palettes[self.theme_mode]["sidebar_bg"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew") # 좌측 상하좌우 꽉 차게 배치
        
        # 사이드바 상단 헤더 프레임 (타이틀 + 추가 버튼)
        self.sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_header.pack(pady=(40, 20), padx=20, fill="x")
        
        # 사이드바 상단 레이블 (SENSORS)
        ctk.CTkLabel(self.sidebar_header, text="SENSORS", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64748B").pack(side="left")
        
        # 센서 추가 버튼 (+)
        self.add_sensor_btn = ctk.CTkButton(
            self.sidebar_header, text="+", width=30, height=30, corner_radius=8,
            fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(size=18, weight="bold"),
            command=self._add_sensor # 센서 추가 함수 연결
        )
        self.add_sensor_btn.pack(side="right")
        
        # 센서 카드들이 들어갈 컨테이너 프레임
        self.sensor_cards_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sensor_cards_frame.pack(fill="both", expand=True, padx=10)
        
        self._render_sidebar_sensors() # 센서 카드 목록 렌더링

        # --- B. 오른쪽 메인 콘텐츠 영역 프레임 설정 ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew") # 우측 배치
        self.main_area.grid_columnconfigure(0, weight=1) # 내부 열 확장 설정
        self.main_area.grid_rowconfigure(1, weight=1, minsize=550) # 중앙 콘텐츠 높이 확보

        # --- B1. 메인 영역 상단 헤더 프레임 ---
        self.header_frame = ctk.CTkFrame(self.main_area, fg_color="transparent", height=60)
        self.header_frame.grid(row=0, column=0, padx=40, pady=(30, 0), sticky="ew")
        
        # 앱 타이틀 로고/텍스트
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="🏠 Gumi Smart Monitor", 
            font=ctk.CTkFont(family="Inter", size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        # 테마 변경 스위치 (Light/Dark)
        self.theme_toggle = ctk.CTkSwitch(
            self.header_frame, 
            text="다크 모드", 
            command=self._toggle_theme,
            font=ctk.CTkFont(family="Inter", size=14)
        )
        self.theme_toggle.pack(side="right")

        # --- B2. 메인 콘텐츠 대형 컨테이너 ---
        self.main_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.main_container.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=3, minsize=350) # 상단 큰 카드 비율
        self.main_container.grid_rowconfigure(1, weight=1, minsize=140) # 하단 작은 카드 비율

        # 중앙 상태 표시 대형 카드 설정
        self.status_card = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.palettes[self.theme_mode]["card_bg"], 
            corner_radius=40, border_width=1,
            border_color="#E2E8F0" if self.theme_mode == "light" else "#334155"
        )
        self.status_card.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        # 상태에 따라 배경색이 변하는 내부 프레임
        self.status_bg_frame = ctk.CTkFrame(
            self.status_card, 
            fg_color=self.palettes[self.theme_mode][self.monitor_state]["bg"], 
            corner_radius=35
        )
        self.status_bg_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 상태 메시지 레이블 (예: 평온한 상태입니다)
        self.status_msg = ctk.CTkLabel(
            self.status_bg_frame, text="평온한 상태입니다", 
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
            text_color=self.palettes[self.theme_mode][self.monitor_state]["text"]
        )
        self.status_msg.pack(pady=(40, 0))

        # 디지털 시계 레이블
        self.time_label = ctk.CTkLabel(
            self.status_bg_frame, text="00:00:00",
            font=ctk.CTkFont(family="Inter", size=80, weight="bold"),
            text_color=self.palettes[self.theme_mode][self.monitor_state]["text"]
        )
        self.time_label.pack(pady=(0, 10))

        # 파동 애니메이션을 그릴 캔버스 객체
        self.canvas = tk.Canvas(
            self.status_bg_frame, bg=self.palettes[self.theme_mode][self.monitor_state]["bg"], 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        # 하단 2개 위젯 배치를 위한 그리드 프레임
        self.bottom_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_grid.grid(row=1, column=0, sticky="nsew")
        self.bottom_grid.grid_columnconfigure(0, weight=1, uniform="bottom_widgets") # 동일 비율
        self.bottom_grid.grid_columnconfigure(1, weight=1, uniform="bottom_widgets") # 동일 비율
        self.bottom_grid.grid_rowconfigure(0, weight=1)

        # 하단 위젯 공통 파라미터
        widget_params = {
            "fg_color": self.palettes[self.theme_mode]["card_bg"],
            "corner_radius": 40, "border_width": 1,
            "border_color": "#E2E8F0" if self.theme_mode == "light" else "#334155"
        }

        # 아기 상태 요약 위젯
        self.baby_widget = ctk.CTkFrame(self.bottom_grid, **widget_params)
        self.baby_widget.grid(row=0, column=0, padx=(0, 15), sticky="nsew") # 오른쪽 패딩으로 간격 유지
        self.baby_widget.grid_columnconfigure(1, weight=1)
        self.baby_widget.grid_rowconfigure(0, weight=1)
        self.baby_icon = ctk.CTkLabel(self.baby_widget, text="👶", font=ctk.CTkFont(size=60))
        self.baby_icon.grid(row=0, column=0, padx=(30, 15))
        self.baby_text_frame = ctk.CTkFrame(self.baby_widget, fg_color="transparent")
        self.baby_text_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=10) # 오른쪽 여백으로 둥근 모서리 보호
        self.baby_title_label = ctk.CTkLabel(self.baby_text_frame, text="아기 상태", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8")
        self.baby_title_label.pack(anchor="sw", pady=(25, 0))
        self.baby_val = ctk.CTkLabel(self.baby_text_frame, text="평온함", font=ctk.CTkFont(size=22, weight="bold"))
        self.baby_val.pack(anchor="nw", pady=(0, 20))

        # 층간 소음 요약 위젯
        self.noise_widget = ctk.CTkFrame(self.bottom_grid, **widget_params)
        self.noise_widget.grid(row=0, column=1, padx=(15, 0), sticky="nsew") # 왼쪽 패딩으로 간격 유지
        self.noise_widget.grid_columnconfigure(1, weight=1)
        self.noise_widget.grid_rowconfigure(0, weight=1)
        self.noise_icon = ctk.CTkLabel(self.noise_widget, text="👣", font=ctk.CTkFont(size=60))
        self.noise_icon.grid(row=0, column=0, padx=(30, 15))
        self.noise_text_frame = ctk.CTkFrame(self.noise_widget, fg_color="transparent")
        self.noise_text_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 30), pady=10) # 오른쪽 여백으로 둥근 모서리 보호
        self.noise_title_label = ctk.CTkLabel(self.noise_text_frame, text="층간 소음", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94A3B8")
        self.noise_title_label.pack(anchor="sw", pady=(25, 0))
        self.noise_val = ctk.CTkLabel(self.noise_text_frame, text="32 dB", font=ctk.CTkFont(size=26, weight="bold"))
        self.noise_val.pack(anchor="nw", pady=(0, 20))

        # --- B3. 하단 상태 제어 버튼 바 ---
        self.control_bar = ctk.CTkFrame(self.main_area, fg_color=self.palettes[self.theme_mode]["card_bg"], corner_radius=20, height=60)
        self.control_bar.grid(row=2, column=0, pady=(0, 30), padx=40)
        
        # 버튼으로 강제 상태 변경 (시뮬레이션용)
        states = [("평온(Normal)", "NORMAL"), ("아기 울음(Baby)", "BABY_ALERT"), ("충격(Impact)", "IMPACT_ALERT")]
        for label, s_name in states:
            btn = ctk.CTkButton(
                self.control_bar, text=label, width=120, height=40, corner_radius=15,
                command=lambda s=s_name: self.set_state(s),
                fg_color="#F1F5F9" if self.theme_mode == "light" else "#334155",
                text_color="#1E293B" if self.theme_mode == "light" else "#F8FAFC",
                hover_color="#E2E8F0" if self.theme_mode == "light" else "#475569"
            )
            btn.pack(side="left", padx=10, pady=10)

    def _render_sidebar_sensors(self): # 사이드바의 센서 카드들을 렌더링하거나 업데이트하는 함수
        # 센서 개수와 위젯 개수가 맞지 않으면 전체 다시 렌더링 (추가/삭제 시)
        if len(self.sensors) != len(self.sensor_card_widgets):
            for widget in self.sensor_cards_frame.winfo_children():
                widget.destroy()
            self.sensor_card_widgets = [] # 리스트 초기화
            
            for i, sensor in enumerate(self.sensors):
                is_active = (i == self.current_sensor_index)
                bg_color = "#3B82F6" if is_active else ("#E2E8F0" if self.theme_mode == "light" else "#334155")
                text_color = "white" if is_active else ("#1E293B" if self.theme_mode == "light" else "#F8FAFC")
                
                # 카드 프레임
                card = ctk.CTkFrame(self.sensor_cards_frame, fg_color=bg_color, corner_radius=15, height=60)
                card.pack(fill="x", pady=5)
                card.pack_propagate(False)
                card.bind("<Button-1>", lambda e, idx=i: self._select_sensor(idx))
                
                # 이모지 레이블
                icon_lbl = ctk.CTkLabel(card, text=sensor["icon"], font=ctk.CTkFont(size=24), cursor="hand2")
                icon_lbl.pack(side="left", padx=(15, 10))
                icon_lbl.bind("<Button-1>", lambda e, idx=i: self._change_sensor_emoji(idx))
                
                # 이름 레이블
                name_lbl = ctk.CTkLabel(card, text=sensor["name"], font=ctk.CTkFont(size=14, weight="bold"), text_color=text_color, cursor="hand2")
                name_lbl.pack(side="left", anchor="w")
                name_lbl.bind("<Button-1>", lambda e, idx=i: self._select_sensor(idx))
                
                # 삭제 버튼
                del_btn = ctk.CTkButton(
                    card, text="✕", width=24, height=24, fg_color="transparent", 
                    text_color="#EF4444" if not is_active else "white", 
                    hover_color="#FEE2E2" if not is_active else "#EF4444",
                    command=lambda idx=i: self._delete_sensor(idx)
                )
                del_btn.pack(side="right", padx=(0, 5))

                # 수정 버튼
                edit_btn = ctk.CTkButton(
                    card, text="✏️", width=24, height=24, fg_color="transparent", 
                    text_color=text_color, hover_color="#60A5FA" if is_active else "#94A3B8",
                    command=lambda idx=i: self._rename_sensor(idx)
                )
                edit_btn.pack(side="right", padx=2)
                
                # 위젯들을 딕셔너리로 저장하여 나중에 업데이트 가능하게 함
                self.sensor_card_widgets.append({
                    "card": card, "icon": icon_lbl, "name": name_lbl, 
                    "del_btn": del_btn, "edit_btn": edit_btn
                })
        else:
            # 개수가 같으면 파괴하지 않고 속성만 업데이트 (깜빡임 방지 최적화)
            for i, sensor in enumerate(self.sensors):
                is_active = (i == self.current_sensor_index)
                bg_color = "#3B82F6" if is_active else ("#E2E8F0" if self.theme_mode == "light" else "#334155")
                text_color = "white" if is_active else ("#1E293B" if self.theme_mode == "light" else "#F8FAFC")
                
                w = self.sensor_card_widgets[i]
                w["card"].configure(fg_color=bg_color)
                w["icon"].configure(text=sensor["icon"])
                w["name"].configure(text=sensor["name"], text_color=text_color)
                w["del_btn"].configure(
                    text_color="#EF4444" if not is_active else "white",
                    hover_color="#FEE2E2" if not is_active else "#EF4444"
                )
                w["edit_btn"].configure(text_color=text_color)

    def _add_sensor(self): # 새로운 센서를 추가하는 함수
        dialog = ctk.CTkInputDialog(text="새 센서 이름을 입력하세요:", title="센서 추가")
        name = dialog.get_input()
        if name:
            # 기본 이모지와 함께 새로운 센서 객체 생성
            new_id = len(self.sensors)
            self.sensors.append({"id": new_id, "name": name, "icon": "📡", "status": "NORMAL"})
            self._render_sidebar_sensors() # 사이드바 갱신

    def _delete_sensor(self, index): # 센서를 삭제하는 함수
        if len(self.sensors) <= 1: # 최소 한 개의 센서는 유지
            return
        
        # 삭제 확인 (간단하게 구현)
        self.sensors.pop(index)
        
        # 현재 선택된 센서가 삭제된 경우 인덱스 조정
        if self.current_sensor_index >= len(self.sensors):
            self.current_sensor_index = len(self.sensors) - 1
        elif self.current_sensor_index == index:
            self.current_sensor_index = 0 # 첫 번째 센서로 강제 이동
            
        self._select_sensor(self.current_sensor_index) # 화면 갱신

    def _select_sensor(self, index): # 특정 센서를 선택하는 함수
        self.current_sensor_index = index # 현재 인덱스 업데이트
        sensor = self.sensors[index] # 선택된 센서 정보 획득
        self.set_state(sensor["status"]) # 센서의 마지막 상태로 화면 전환
        self._render_sidebar_sensors() # 사이드바 강조 표시 갱신

    def _change_sensor_emoji(self, index): # 센서 이모지를 변경하는 입력창 실행
        dialog = ctk.CTkInputDialog(text="새로운 이모지를 입력하세요:", title="센서 이모지 변경")
        new_emoji = dialog.get_input()
        if new_emoji:
            self.sensors[index]["icon"] = new_emoji[0] if len(new_emoji) > 0 else self.sensors[index]["icon"]
            self._render_sidebar_sensors()

    def _rename_sensor(self, index): # 센서 이름을 변경하는 입력창 실행
        dialog = ctk.CTkInputDialog(text="새로운 센서 이름을 입력하세요:", title="센서 이름 변경")
        new_name = dialog.get_input()
        if new_name:
            self.sensors[index]["name"] = new_name
            self._render_sidebar_sensors()

    def _toggle_theme(self): # 테마(Light/Dark) 토글 함수
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        ctk.set_appearance_mode(self.theme_mode) # 라이브러리 전체 테마 적용
        palette = self.palettes[self.theme_mode] # 현재 모드 팔레트 선택
        self.configure(fg_color=palette["window_bg"]) # 배경색 즉각 반영
        self.sidebar.configure(fg_color=palette["sidebar_bg"]) # 사이드바 색상 반영
        
        # 주요 위젯들 색상 수동 업데이트
        card_color = palette["card_bg"]
        border_color = "#E2E8F0" if self.theme_mode == "light" else "#334155"
        self.status_card.configure(fg_color=card_color, border_color=border_color)
        self.baby_widget.configure(fg_color=card_color, border_color=border_color)
        self.noise_widget.configure(fg_color=card_color, border_color=border_color)
        self.control_bar.configure(fg_color=card_color)
        
        self.set_state(self.monitor_state) # 현재 상태 UI 색상 다시 입히기
        self._render_sidebar_sensors() # 사이드바 카드 색상 다시 입히기

    def set_state(self, new_state): # 앱의 감지 상태를 변경하는 핵심 함수
        self.monitor_state = new_state # 새로운 상태 저장
        self.sensors[self.current_sensor_index]["status"] = new_state # 해당 센서 데이터에도 반영
        palette = self.palettes[self.theme_mode][new_state] # 상태 전용 색상 선택
        
        # UI 요소들 색상 업데이트
        self.status_bg_frame.configure(fg_color=palette["bg"])
        self.canvas.configure(bg=palette["bg"])
        self.status_msg.configure(text_color=palette["text"])
        self.time_label.configure(text_color=palette["text"])
        
        # 각 상태에 따른 메시지 및 기본 수치 설정
        if new_state == "NORMAL":
            self.status_msg.configure(text="평온한 상태입니다")
            self.baby_icon.configure(text="👶")
            self.baby_val.configure(text="평온함")
            self.noise_icon.configure(text="👣")
            self.noise_val.configure(text="32 dB")
            self.crying_start_time = None
        elif new_state == "BABY_ALERT":
            self.status_msg.configure(text="아기 울음 감지!")
            self.baby_icon.configure(text="😭")
            self.baby_val.configure(text="울음 감지")
            self.crying_start_time = time.time() # 울음 시작 시간 기록
        elif new_state == "IMPACT_ALERT":
            self.status_msg.configure(text="큰 충격 발생!")
            self.noise_icon.configure(text="⚠️")
            self.noise_val.configure(text="75 dB")

    def _update_time(self): # 시계 및 센서 수치(초당 평균)를 업데이트하는 루프 함수
        current_time = datetime.now().strftime("%H:%M:%S") # 현재 시간 포맷팅
        self.time_label.configure(text=current_time) # 시계 레이블 업데이트
        
        # 상태에 따른 데시벨 수치 1초마다 랜덤 시뮬레이션
        if self.monitor_state == "NORMAL":
            db = random.randint(28, 34)
            self.noise_val.configure(text=f"{db} dB")
            self.baby_val.configure(text="평온함")
        elif self.monitor_state == "BABY_ALERT":
            if self.crying_start_time:
                elapsed = int(time.time() - self.crying_start_time) # 울음 경과 시간 계산
                mins, secs = divmod(elapsed, 60)
                db = random.randint(58, 72)
                self.baby_val.configure(text=f"감지: {mins:02d}:{secs:02d} | {db} dB")
        elif self.monitor_state == "IMPACT_ALERT":
            db = random.randint(75, 92)
            self.noise_val.configure(text=f"{db} dB")

        self.after(1000, self._update_time) # 1000ms(1초) 후 재귀 호출

    def _draw_waves(self): # 캔버스에 파동 애니메이션을 그리는 핵심 함수 (30 FPS)
        self.canvas.delete("wave") # 기존 파형 제거
        width = self.canvas.winfo_width() # 현재 캔버스 너비
        height = self.canvas.winfo_height() # 현재 캔버스 높이
        if width <= 1 or height <= 1: return # 크기가 너무 작으면 그리기 건너뜀

        center_y = height / 2 # 파동의 수직 중심축
        palette = self.palettes[self.theme_mode][self.monitor_state] # 현재 상태 색상

        if self.monitor_state == "NORMAL": # 평온 상태: 우아하고 부드러운 다중 사인 파형
            for i in range(3):
                points = []
                phase_mult = 1.0 - (i * 0.15)
                color = palette["wave"]
                for x in range(0, width + 20, 15):
                    # 수학적 사인 함수를 이용한 부드러운 곡선 계산
                    y = center_y + math.sin(x * 0.007 + self.wave_phase * phase_mult + i) * (35 - i * 8)
                    points.extend([x, y])
                self.canvas.create_line(points, fill=color, width=4-i, smooth=True, tags="wave")

        elif self.monitor_state == "BABY_ALERT": # 아기 울음 상태: 강렬하고 노이즈 섞인 격렬한 파형
            points = []
            for x in range(0, width + 10, 8):
                # 베이스 파동에 빠른 위상의 사인 변동성을 추가하여 울음소리 형상화
                variation = math.sin(x * 0.2 + self.wave_phase * 10) * 20
                y = center_y + math.sin(x * 0.05 + self.wave_phase * 5) * 50 + variation
                points.extend([x, y])
            self.canvas.create_line(points, fill=palette["wave"], width=4, smooth=True, tags="wave")

        elif self.monitor_state == "IMPACT_ALERT": # 충격 상태: 역동적으로 움직이는 둥근 막대 그래프
            bar_w, gap = 20, 15 # 막대 너비 및 간격 설정
            num_bars = width // (bar_w + gap) # 그릴 수 있는 막대 개수 계산
            for i in range(num_bars):
                x = i * (bar_w + gap) + gap + (bar_w / 2) # 막대 중심 위치
                base_h = abs(math.sin(i * 0.5 + self.wave_phase * 6)) # 사인파 기반의 기본 높이 리듬
                random_factor = random.uniform(0.6, 1.0) # 약간의 랜덤 변동성 추가
                h = height * 0.7 * base_h * random_factor # 실제 픽셀 높이 계산
                h = max(h, 25) # 최소 높이 보장
                
                # 두꺼운 선에 라운드 캡을 씌워 둥근 막대 구현
                self.canvas.create_line(
                    x, height - 10, x, height - h, 
                    fill=palette["wave"], width=bar_w, 
                    capstyle="round", tags="wave"
                )

    def _animate(self): # 애니메이션 위상을 업데이트하고 다시 그리기를 트리거하는 루프
        self.wave_phase += 0.08 # 위상값 증가시켜 파동 이동
        self._draw_waves() # 파형 다시 그리기
        self.after(30, self._animate) # 약 33 FPS를 위한 30ms 대기 후 호출

if __name__ == "__main__": # 스크립트 직접 실행 시
    app = NoiseMonitorApp() # 앱 인스턴스 생성
    app.mainloop() # Tkinter 메인 이벤트 루프 시작
