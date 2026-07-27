import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtCore import QTimer
# Importujemy QGraphicsView i QGraphicsScene dla canvy
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap

class GameView(QWidget):
    quit_requested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Game View")
        self.setGeometry(100, 100, 800, 600)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # --- 1. GŁÓWNY UKŁAD OKNA ---
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # --- 2. PASEK MENU (GÓRNY) ---
        menu_bar = QWidget()
        menu_bar.setObjectName("menu_bar")
        menu_layout = QHBoxLayout()
        menu_bar.setLayout(menu_layout)
        
        btn_save = QPushButton("Zapisz grę")
        btn_load = QPushButton("Wczytaj grę")
        btn_exit = QPushButton("Wyjście")
        btn_exit.clicked.connect(self.quit_requested.emit)
        
        menu_layout.addWidget(btn_save)
        menu_layout.addWidget(btn_load)
        menu_layout.addStretch()
        menu_layout.addWidget(btn_exit)
        
        main_layout.addWidget(menu_bar)
        
        # --- 3. OBSZAR ROZGRYWKI (Poziomy: Canvas + Dashboard) ---
        gameplay_area = QWidget()
        gameplay_layout = QHBoxLayout()
        gameplay_area.setLayout(gameplay_layout)
        
        # --- PODMIANA: Canvas jako QGraphicsView ---
        self.scene = QGraphicsScene()
        self.canvas = QGraphicsView(self.scene)
        # Początkowe wartości, które resizeEvent zaraz po uruchomieniu nadpisze realnymi wymiarami
        self.scene_width = 1800
        self.scene_height = 1600

        self.canvas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.canvas.setStyleSheet("background-color: lightgray; border: none;")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        
        # Dashboard (Panel boczny)
        self.game_dashboard = QWidget()
        
        # --- 4. WYPEŁNIANIE PANELU BOCZNEGO (Dashboard) ---
        dashboard_layout = QVBoxLayout()
        self.game_dashboard.setLayout(dashboard_layout)
        self.game_dashboard.setObjectName("game_dashboard")
        
        lbl_stats = QLabel("STATYSTYKI POSTACI")
        lbl_stats.setStyleSheet("color:black;")
        lbl_stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_attack = QPushButton("Atak")
        btn_defend = QPushButton("Obrona")
        btn_inventory = QPushButton("Ekwipunek")
        self.x_pos_label=QLabel("x:")
        self.y_pos_label=QLabel("y:")
        self.y_pos_label.setStyleSheet("color:black;")
        self.x_pos_label.setStyleSheet("color:black;")
        # Testowy przycisk do spawnowania obiektów
        btn_spawn_test = QPushButton("Spawn Sprite")
        # Wywołanie z przykładową ścieżką (zmień na własny plik)
        btn_spawn_test.clicked.connect(lambda: self.spawn_object("game/assets/mr_orange.png"))
        
        dashboard_layout.addWidget(lbl_stats)
        dashboard_layout.addWidget(btn_attack)
        dashboard_layout.addWidget(btn_defend)
        dashboard_layout.addWidget(btn_spawn_test) # Dodajemy przycisk testowy
        dashboard_layout.addWidget(self.x_pos_label)
        dashboard_layout.addWidget(self.y_pos_label)
        dashboard_layout.addStretch()
        dashboard_layout.addWidget(btn_inventory)
        
        # Dodawanie składowych do obszaru rozgrywki
        gameplay_layout.addWidget(self.canvas, 5)
        gameplay_layout.addWidget(self.game_dashboard, 1)
        
        main_layout.addWidget(gameplay_area)
        
        # Słownik przechowujący stan klawiszy (True = wciśnięty, False = puszczony)
        self.keys_pressed = {
            Qt.Key.Key_Left: False,
            Qt.Key.Key_Right: False,
            Qt.Key.Key_Up: False,
            Qt.Key.Key_Down: False
        }

        self.speed = 5  # Prędkość Twojej postaci

        # Timer, który co 16 milisekund (około 60 FPS) będzie wywoływał funkcję ruchu
        # # Upewnij się, że masz import QTimer na górze pliku lub zaimportuj tutaj
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.process_movement)
        self.game_timer.start(16)

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed[key] = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed[key] = False
    def spawn_object(self, path, x=None, y=None):
        """Tworzy nowy obiekt graficzny (sprite) na canvie."""
        # 1. Wczytujemy plik graficzny
        pixmap = QPixmap(path)
        
        # Awaryjne zabezpieczenie: jeśli plik nie istnieje, tworzy pusty czerwony kwadrat
        if pixmap.isNull():
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.red)
            
        # 2. Tworzymy element graficzny dla sceny
        sprite_item = QGraphicsPixmapItem(pixmap)
        
        # Obliczamy wymiary sprite'a
        w = sprite_item.pixmap().width()
        h = sprite_item.pixmap().height()

        # Ustawiamy punkt zakotwiczenia na środku obrazka (przydatne do obrotów)
        sprite_item.setTransformOriginPoint(w / 2, h / 2)

        # Jeśli x lub y nie zostały podane, generujemy postać na środku sceny
        if x is None:
            x = (self.scene_width / 2) - (w / 2)
        if y is None:
            y = (self.scene_height / 2) - (h / 2)

        # 3. Ustawiamy pozycję startową X i Y na canvie
        sprite_item.setPos(x, y)
        
        # 4. Dodajemy obiekt do sceny (naszej canvy)
        self.scene.addItem(sprite_item)
        
        # Zwracamy obiekt, jeśli będziesz chciał nim później sterować
        self.player = sprite_item
        print(f"w:{self.player.pixmap().width()},h:{self.player.pixmap().height()}")
        self.setFocus()

    def process_movement(self):
        dx = 0
        dy = 0

        if self.keys_pressed[Qt.Key.Key_Left]:
            dx -= self.speed
        if self.keys_pressed[Qt.Key.Key_Right]:
            dx += self.speed
        if self.keys_pressed[Qt.Key.Key_Up]:
            dy -= self.speed
        if self.keys_pressed[Qt.Key.Key_Down]:
            dy += self.speed

        # NORMALIZACJA SKOSÓW: Jeśli poruszamy się w obu osiach jednocześnie
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Jeśli jakikolwiek klawisz jest wciśnięty, przesuwamy obiekt
        if dx != 0 or dy != 0:
            self.move_object(dx, dy)

    def move_object(self, dx, dy):
        if hasattr(self, 'player') and self.player:
            current_x = self.player.x()
            current_y = self.player.y()
            
            p_width = self.player.pixmap().width()
            p_height = self.player.pixmap().height()
            
            new_x = current_x + dx
            new_y = current_y + dy
            
            # CZYSTE GRANICE: Sprawdzamy pozycję względem dynamicznych zmiennych sceny
            if 0 <= new_x <= (self.scene_width - p_width):
                current_x = new_x
                
            if 0 <= new_y <= (self.scene_height - p_height):
                current_y = new_y
                
            self.x_pos_label.setText(f"x:{int(current_x)}")
            self.y_pos_label.setText(f"y:{int(current_y)}")
            
            self.player.setPos(current_x, current_y)
    def resizeEvent(self, event):
        """Automatycznie aktualizuje rozmiar sceny, gdy zmienia się rozmiar okna."""
        super().resizeEvent(event)
        
        # Pobieramy realną szerokość i wysokość całego widgetu canvas
        self.scene_width = self.canvas.width()
        self.scene_height = self.canvas.height()
        
        # Aktualizujemy obszar wirtualnej sceny do pełnych wymiarów szarego pola
        self.scene.setSceneRect(0, 0, self.scene_width, self.scene_height)

