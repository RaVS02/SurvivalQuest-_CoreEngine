import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton,QLabel,QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from rich import layout
class MenuView(QWidget):
    # Signal to indicate that the "Start Game" button was clicked
    start_game_requested = Signal()
    load_game_requested = Signal()
    settings_requested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Menu View")
        self.setGeometry(100, 100, 400, 300)
          # Set the background color to light gray
        layout = QVBoxLayout()      
        layout.addStretch(1)
        current_dir = os.path.dirname(os.path.abspath(__file__))  # katalog ui/
        game_dir = os.path.dirname(current_dir)                   # katalog game/
        image_path = os.path.join(game_dir, "assets", "app_icon_t.png") # game/assets/app_icon_t.png

        self.image_label = QLabel()
        
        pixmap = QPixmap(image_path)
        pixmap_scaled = pixmap.scaled(400, 400, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap_scaled)
        self.start_button = QPushButton("Start Game")
        self.start_button.setObjectName("start_button")  # Set the object name for the start button
        self.load_button = QPushButton("Resume Game")
        self.load_button.setObjectName("resume_button")  # Set the object name for the
        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("settings_button")  # Set the object name for the settings button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setObjectName("exit_button") # Set the object name for the exit button
        layout.addWidget(self.image_label,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.load_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch(1)
        self.setLayout(layout)
        self.start_button.clicked.connect(self.start_game_requested.emit)
        self.load_button.clicked.connect(self.load_game_requested.emit)
        self.settings_button.clicked.connect(self.settings_requested.emit)
        self.exit_button.clicked.connect(QApplication.instance().quit)
        
        