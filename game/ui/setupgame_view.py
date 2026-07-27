from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication,QComboBox,QPushButton
from PySide6.QtCore import Qt,Signal

class SetUpGame(QWidget):
    back_to_menu_request=Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup Game")
        
        # 1. Główny układ poziomy dla całego okna
        main_layout = QHBoxLayout(self)

        # 2. Dynamiczne obliczenie wymiarów (40% szerokości i 70% wysokości ekranu)
        screen = QApplication.primaryScreen().geometry()
        panel_width = int(screen.width() * 0.4)
        panel_height = int(screen.height() * 0.8)

        # 3. Panel konfiguracyjny z nadanym rozmiarem
        self.setuppanel = QWidget()
        self.setuppanel.setObjectName("setuppanel")
        self.setuppanel.setFixedSize(panel_width, panel_height)
        
        # 4. Układ pionowy dla zawartości wewnątrz panelu
        panel_layout = QVBoxLayout(self.setuppanel)
        
        # Przykładowy nagłówek
        self.title_label = QLabel("Konfiguracja Świata")
        self.title_label.setObjectName("setup_title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.difficulty_level_label=QLabel("Wybierz Poziom Trudnosci")
        self.difficulty_level= QComboBox()
        self.difficulty_level
        
        panel_layout.addWidget(self.title_label)
        panel_layout.addWidget(self.difficulty_level_label)
        panel_layout.addWidget(self.difficulty_level)
        # Miejsce na przyszłe kontrolki (suwaki, przyciski wyboru)
        panel_layout.addStretch()
        self.back_to_menu_btn=QPushButton("Menu")
        self.back_to_menu_btn.setObjectName("back_to_menu_btn")
        panel_layout.addWidget(self.back_to_menu_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 5. Dodanie panelu do układu głównego z wymuszonym wyśrodkowaniem
        main_layout.addWidget(self.setuppanel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.back_to_menu_btn.clicked.connect(self.back_to_menu_request.emit)