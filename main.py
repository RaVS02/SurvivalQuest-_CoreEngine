import os
import sys
from pathlib import Path  # Dodane do obsługi ścieżek plików

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon  # Dodane do obsługi ikony aplikacji
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QStackedWidget

from game.ui.game_viev import GameView
from game.ui.menu_view import MenuView
from game.ui.setupgame_view import SetUpGame
from game.ui.settings import Settings
# FIX DLA WINDOWS: Wymusza wyświetlanie własnej ikony na pasku zadań zamiast logo Pythona
if sys.platform == "win32":
    import ctypes

    my_app_id = "moja_gra.pyside6.wersja.1.0"  # Dowolny, unikalny identyfikator tekstowy
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


def load_stylesheet(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return ""


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Survival Quest")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.window_width = screen_geometry.width()
        self.window_height = screen_geometry.height()
        # Ustawia domyślny rozmiar na pełny ekran / rozmiar monitora
        self.resize(self.window_width, self.window_height)
        # 1. Tworzymy kontener na widoki i ustawiamy go jako główny element okna
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 2. Tworzymy widok menu i dodajemy go do kontenera
        self.menu_view = MenuView()
        self.game_view = GameView()
        self.setup_game = SetUpGame()
        self.settings = Settings()
        self.stacked_widget.addWidget(self.menu_view)
        # Trafia na indeks 0
        self.stacked_widget.addWidget(self.game_view)  # Trafia na indeks 1
        self.stacked_widget.addWidget(self.setup_game)
        self.stacked_widget.addWidget(self.settings)
        # 3. Łączymy sygnał kliknięcia "Exit" bezpośrednio z zamknięciem MainWindow
        self.menu_view.exit_button.clicked.connect(self.close)
        self.menu_view.start_game_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(2)
        )
        self.menu_view.load_game_requested.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )  # Powrót do menu po kliknięciu "Start Game" w GameView)
        self.setup_game.back_to_menu_request.connect(lambda: self.stacked_widget.setCurrentIndex(0), self.stacked_widget.setFocus())
        self.game_view.quit_requested.connect(lambda: self.stacked_widget.setCurrentIndex(0), self.stacked_widget.setFocus())
        self.menu_view.settings_requested.connect(lambda:self.stacked_widget.setCurrentIndex(3))
        self.settings.quit_requested.connect(lambda:self.stacked_widget.setCurrentIndex(0))
        self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # USTAWIANIE IKONY: Definiujemy ścieżkę do pliku graficznego
    # Path(__file__).parent oznacza katalog, w którym znajduje się ten skrypt
    icon_path = Path(__file__).parent / "game/assets/app_icon_t.png"

    # Ładujemy ikonę i ustawiamy ją globalnie dla całego programu
    app.setWindowIcon(QIcon(str(icon_path)))

    stylesheet = load_stylesheet("game/config/style.qss")
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()
    app.exec()
