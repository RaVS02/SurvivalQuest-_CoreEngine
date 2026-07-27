from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from PySide6.QtCore import Qt, Signal

class Settings(QWidget):
    quit_requested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings View")
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        settings_panel = QWidget()
        settings_panel.setObjectName("settings_panel")
        
        # POPRAWKA 1: Nadajemy panelowi minimalną szerokość, żeby miał ładny, stały kształt
        settings_panel.setMinimumWidth(250)
        
        settings_layout = QVBoxLayout()
        # POPRAWKA 2: Dodajemy wewnętrzne marginesy dla panelu, żeby elementy nie dotykały krawędzi
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_panel.setLayout(settings_layout)
        
        self.sound_lvl_label = QLabel("Poziom Głośności")
        
        # --- UKŁAD: Suwak + Wartość obok siebie ---
        slider_row_layout = QHBoxLayout()
        
        # Dodajemy małe sprężyny po bokach wiersza dla idealnego centrowania
        slider_row_layout.addStretch()
        
        self.sound_lvl_slider = QSlider(Qt.Orientation.Horizontal)
        
        self.sound_lvl_slider.setMinimum(0)
        self.sound_lvl_slider.setMaximum(100)
        self.sound_lvl_slider.setValue(50)
        # POPRAWKA 3: Zmniejszamy szerokość suwaka do 120px, aby zostawić miejsce na tekst
        self.sound_lvl_slider.setFixedWidth(120) 
        
        self.sound_val_label = QLabel(f"{self.sound_lvl_slider.value()}%")
        self.sound_val_label.setObjectName("sound_val_label") 
        # POPRAWKA 4: Stała szerokość etykiety i wyrównanie do lewej, by tekst nie drgał
        self.sound_val_label.setFixedWidth(55)
        self.sound_val_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        slider_row_layout.addWidget(self.sound_lvl_slider)
        # POPRAWKA 5: Dodajemy minimalny odstęp (5px) między suwakiem a cyframi
        slider_row_layout.addSpacing(5)
        slider_row_layout.addWidget(self.sound_val_label)
        
        slider_row_layout.addStretch()
        # ------------------------------------------------
        
        self.back_to_menu_btn = QPushButton("Menu")
        self.back_to_menu_btn.setObjectName("back_to_menu_btn")
        # Opcjonalnie: nadajemy przyciskowi stałą szerokość, by pasował do reszty
        self.back_to_menu_btn.setFixedWidth(100)
        
        self.sound_lvl_slider.valueChanged.connect(self.update_volume_label)
        
        # Układanie elementów w pionie
        settings_layout.addStretch()
        settings_layout.addWidget(self.sound_lvl_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        settings_layout.addSpacing(15) 
        
        settings_layout.addLayout(slider_row_layout)
        
        settings_layout.addSpacing(25) 
        settings_layout.addWidget(self.back_to_menu_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        settings_layout.addStretch()
        
        self.back_to_menu_btn.clicked.connect(self.quit_requested.emit)
        main_layout.addWidget(settings_panel, alignment=Qt.AlignmentFlag.AlignHCenter)

    def update_volume_label(self, value):
        self.sound_val_label.setText(f"{value}%")
