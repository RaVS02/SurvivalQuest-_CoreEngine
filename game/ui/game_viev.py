import math
import sys
import numpy as np
from PySide6.QtCore import Qt, Signal, QTimer, QElapsedTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QFrame
)
from PySide6.QtGui import QBrush, QPen, QColor, QPixmap

from game.core.character import Player

class GameView(QWidget):
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game View - Core Engine")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.map_size = 64
        self.start_pos = 0

        # --- ZMIENNE ZOOMU MINIMAPY ---
        self.zoom_levels = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]
        self.current_zoom_idx = 0  # Zaczynamy od skali 0.1x

        # --- GŁÓWNY UKŁAD PIONOWY OKNA ---
        main_layout = QVBoxLayout(self)
        
        # Przycisk wyjścia na samej górze
        self.btn_exit = QPushButton("Wróć do Menu (ESC)")
        self.btn_exit.clicked.connect(self.quit_requested.emit)
        main_layout.addWidget(self.btn_exit)

        # --- OBSZAR ROZGRYWKI (PODZIAŁ POZIOMY: CANVA + DASHBOARD) ---
        self.gameplay_area = QWidget()
        gameplay_layout = QHBoxLayout(self.gameplay_area)
        gameplay_layout.setContentsMargins(0, 0, 0, 0) 

        # 1. LEWA STRONA (Widok Gry)
        self.scene = QGraphicsScene()
        self.gen_worldmap()
        self.player = Player(
            x=self.start_pos, 
            y=self.start_pos, 
            sprite_path="./game/assets/MrRzodkiewkaSprite.png"
        )
        self.scene.addItem(self.player.visual)
        self.canvas = QGraphicsView(self.scene)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.canvas.setStyleSheet("background-color: lightgray; border: 2px solid black;")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # Wyłączenie scrollbarów głównego widoku
        self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 2. PRAWA STRONA (Panel Boczny / Dashboard)
        self.dashboard_panel = QWidget()
        self.dashboard_panel.setFixedWidth(300)
        self.dashboard_panel.setStyleSheet("background-color: #2c3e50; border-radius: 4px;")
        
        dashboard_layout = QVBoxLayout(self.dashboard_panel)

        # --- MINIMAPA W RÓŻY WIATRÓW (QGridLayout) ---
        # 1. Tworzymy ramkę zewnętrzną (QFrame), która gwarantuje poprawny border
        self.minimap_frame = QFrame()
        self.minimap_frame.setFixedSize(188, 188) # 180 + 2x2px ramki
        self.minimap_frame.setStyleSheet("background-color: black; border: 4px solid #ecf0f1;")
        
        minimap_layout = QVBoxLayout(self.minimap_frame)
        minimap_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Tworzymy samą minimapę bez własnego bordera
        self.minimap = QGraphicsView(self.scene)
        self.minimap.setFixedSize(180, 180)
        self.minimap.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.minimap.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.minimap.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.minimap.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.minimap.setStyleSheet("background-color: black; border: none;")

        minimap_layout.addWidget(self.minimap)

        # Kontener siatki dla minimapy i liter N, S, W, E
        minimap_box = QWidget()
        compass_grid = QGridLayout(minimap_box)
        compass_grid.setContentsMargins(0, 0, 0, 0)
        compass_grid.setSpacing(4)

        lbl_n = QLabel("N")
        lbl_s = QLabel("S")
        lbl_w = QLabel("W")
        lbl_e = QLabel("E")

        style_direction = "color: #e74c3c; font-weight: bold; font-size: 14px;"
        for lbl in (lbl_n, lbl_s, lbl_w, lbl_e):
            lbl.setStyleSheet(style_direction)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Układanie elementów w siatce (wiersz, kolumna)
        compass_grid.addWidget(lbl_n, 0, 1)          # Góra: Północ
        compass_grid.addWidget(lbl_w, 1, 0)          # Lewo: Zachód
        compass_grid.addWidget(self.minimap_frame, 1, 1) # Środek: Minimapa
        compass_grid.addWidget(lbl_e, 1, 2)          # Prawo: Wschód
        compass_grid.addWidget(lbl_s, 2, 1)          # Dół: Południe

        dashboard_layout.addWidget(minimap_box, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2B. ETYKIETY STATYSTYK I KOORDYNATÓW
        dashboard_layout.addSpacing(10)
        
        self.zoom_label = QLabel("Zoom: 0.1x")
        self.dir_label = QLabel("Kierunek: STOI")
        self.dir_label.setStyleSheet("color: #f1c40f; font-weight: bold; font-size: 14px;")

        self.poz_tile_label = QLabel("Poz: x:0 y:0")
        
        for lbl in (self.zoom_label, self.dir_label, self.poz_tile_label):
            lbl.setStyleSheet("color: white; font-size: 13px;")
            dashboard_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        dashboard_layout.addStretch()

        # Połączenie obszaru gry z panelem bocznym
        gameplay_layout.addWidget(self.canvas, stretch=4)
        gameplay_layout.addWidget(self.dashboard_panel, stretch=1)
        main_layout.addWidget(self.gameplay_area)

        # --- TIMERY I ZMIENNE STANU GRY ---
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.process_movement_player)
        self.game_timer.start(16)

        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()

        # Pełna Mapa Kamera
        # --- EKRAN PEŁNEJ MAPY (Złożony w jeden QWidget) ---
        self.map_screen = QWidget()
        map_layout = QVBoxLayout(self.map_screen)
        
        self.poz_tile_label_fullmap = QLabel("Poz: x:0 y:0")
        self.poz_tile_label_fullmap.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.poz_tile_label_fullmap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        map_layout.addWidget(self.poz_tile_label_fullmap)
        
        self.full_map_view = QGraphicsView(self.scene)
        self.full_map_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.full_map_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.full_map_view.setStyleSheet("background-color: black; border: 2px solid gray;")
        self.full_map_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.full_map_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        map_layout.addWidget(self.full_map_view)
        
        main_layout.addWidget(self.map_screen)
        
        self.map_screen.hide()
        self.is_map_open = False
        
        self.update_minimap_zoom()
        
    def keyPressEvent(self, event):
        # Powrót do menu pod klawiszem ESC
        if event.key() == Qt.Key.Key_Escape:
            self.quit_requested.emit()
            return
            
        # ZOOM MINIMAPY (+ i -) Z LISTY
        if event.key() == Qt.Key.Key_Equal or event.key() == Qt.Key.Key_Plus:
            if self.current_zoom_idx < len(self.zoom_levels) - 1:
                self.current_zoom_idx += 1
                self.update_minimap_zoom()
            return
            
        if event.key() == Qt.Key.Key_Minus:
            if self.current_zoom_idx > 0:
                self.current_zoom_idx -= 1
                self.update_minimap_zoom()
            return
        
        if event.key() == Qt.Key.Key_M:
            self.toggle_full_map()
            return
            
        self.player.set_key_state(event.key(), True)

    def keyReleaseEvent(self, event):
        self.player.set_key_state(event.key(), False)

    def process_movement_player(self):
        delta_time = self.elapsed_timer.elapsed() / 1000.0
        self.elapsed_timer.restart()
        
        # 1. Przekazujemy logikę fizyki do klasy gracza
        self.player.update(delta_time, self.testowaplansza, self.map_size, self.tilesize)
        
        # 2. Kamery śledzą grafikę gracza
        self.update_camera()
        self.minimap.centerOn(self.player.visual)
        
        # 3. Przeliczanie na kafelki i HUD
        tile_x, tile_y = self.player.get_tile_pos(self.tilesize)
        pozycje_tekst = f"Poz: x:{tile_x} y:{tile_y}"
        
        self.poz_tile_label.setText(pozycje_tekst)          
        self.poz_tile_label_fullmap.setText(pozycje_tekst)

        # 4. Wyznaczenie nazwy kierunku na podstawie wciśniętych klawiszy
        dir_text = []
        if self.player.keys_pressed[Qt.Key.Key_Up]:    dir_text.append("N")
        if self.player.keys_pressed[Qt.Key.Key_Down]:  dir_text.append("S")
        if self.player.keys_pressed[Qt.Key.Key_Left]:  dir_text.append("W")
        if self.player.keys_pressed[Qt.Key.Key_Right]: dir_text.append("E")

        kierunek = "".join(dir_text) if dir_text else "STOI"
        self.dir_label.setText(f"Kierunek: {kierunek}")

        # --- TRZYSTANOWA MGŁA WOJNY (ZOPTYMALIZOWANA) ---
        # 1. WYGASZANIE: Cofamy kafelki z poprzedniej klatki do stanu "Półmroku"
        for r, c in self.visible_tiles:
            if self.fog_map[r][c] == 0:  # Upewniamy się, że były widoczne
                self.fog_map[r][c] = 1  # Zmieniamy stan na Pamięć (1)
                mgla = self.fog_items[(r, c)]
                mgla.show()
                mgla.setOpacity(0.7)

        # 2. Czyszczenie zbioru na nową klatkę
        self.visible_tiles.clear()

        # 3. OŚWIETLANIE: Wyliczamy nowe koło widzenia
        zasieg = int(self.player.range_view)

        for wiersz in range(tile_y - zasieg, tile_y + zasieg + 2):
            for kolumna in range(tile_x - zasieg, tile_x + zasieg + 2):
                if 0 <= wiersz < self.map_size and 0 <= kolumna < self.map_size:
                    dystans = math.hypot(wiersz - tile_y - 1, kolumna - tile_x - 1)

                    if dystans <= self.player.range_view:
                        self.fog_map[wiersz][kolumna] = 0
                        mgla = self.fog_items[(wiersz, kolumna)]
                        mgla.setOpacity(0.0)
                        self.visible_tiles.add((wiersz, kolumna))

        print(f"Pozycja: x:{self.player.x:.1f}, y:{self.player.y:.1f}, Kat:{self.player.visual.rotation():.1f}")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)

    def gen_worldmap(self):
        self.tilesize = 32
        
        self.testowaplansza = np.zeros((self.map_size, self.map_size), dtype=int)
        self.fog_map = np.full((self.map_size, self.map_size), 2, dtype=int)
        self.fog_items = {}
        self.visible_tiles = set()
        world_width = self.map_size * self.tilesize
        world_height = self.map_size * self.tilesize
        
        self.scene.setSceneRect(0, 0, world_width, world_height)
        
        self.testowaplansza[0, :] = 1   # Górna ściana
        self.testowaplansza[-1, :] = 1  # Dolna ściana
        self.testowaplansza[:, 0] = 1   # Lewa ściana
        self.testowaplansza[:, -1] = 1  # Prawa ściana
        
        for r in range(3, self.map_size - 3, 4):
            for c in range(3, self.map_size - 3, 4):
                self.testowaplansza[r, c] = 1

        # --- OPTYMALIZACJA TŁA ---
        from PySide6.QtGui import QPainter
        
        background_pixmap = QPixmap(world_width, world_height)
        background_pixmap.fill(QColor("grey"))
        
        painter = QPainter(background_pixmap)
        painter.setBrush(QBrush(QColor("green")))
        painter.setPen(QPen(QColor("darkgreen"), 1))
        
        for row_idx, row_data in enumerate(self.testowaplansza):
            for col_idx, tile_value in enumerate(row_data):
                if tile_value == 1:
                    x_pos = col_idx * self.tilesize
                    y_pos = row_idx * self.tilesize
                    painter.drawRect(x_pos, y_pos, self.tilesize, self.tilesize)
                    
        painter.end() 
        
        self.world_visual = QGraphicsPixmapItem(background_pixmap)
        self.world_visual.setZValue(0)
        self.scene.addItem(self.world_visual)

        # --- RYSOWANIE MGŁY ---
        for row_idx, row_data in enumerate(self.testowaplansza):
            for col_idx, tile_value in enumerate(row_data):
                x_pos = col_idx * self.tilesize
                y_pos = row_idx * self.tilesize
                
                kafelek_mgly = QGraphicsRectItem(0, 0, self.tilesize, self.tilesize)
                kafelek_mgly.setBrush(QBrush(QColor("black")))
                kafelek_mgly.setPen(Qt.PenStyle.NoPen)
                kafelek_mgly.setZValue(2)
                kafelek_mgly.setPos(x_pos, y_pos)
                
                self.scene.addItem(kafelek_mgly)
                self.fog_items[(row_idx, col_idx)] = kafelek_mgly

    def update_camera(self):
        view_w = self.canvas.width()
        view_h = self.canvas.height()
        
        half_w = view_w / 2.0
        half_h = view_h / 2.0
        
        world_w = self.map_size * self.tilesize
        world_h = self.map_size * self.tilesize
        
        player_center_x = self.player.x + (self.player.sprite_size / 2.0)
        player_center_y = self.player.y + (self.player.sprite_size / 2.0)
        
        cam_x = max(half_w, min(player_center_x, world_w - half_w))
        cam_y = max(half_h, min(player_center_y, world_h - half_h))
        
        self.canvas.centerOn(cam_x, cam_y)

    def update_minimap_zoom(self):
        self.minimap.resetTransform()
        zoom_factor = self.zoom_levels[self.current_zoom_idx]
        self.minimap.scale(zoom_factor, zoom_factor)
        self.zoom_label.setText(f"Zoom: {zoom_factor}x")

    def toggle_full_map(self):
        if self.is_map_open == False:
            self.gameplay_area.hide()
            self.map_screen.show()
            self.is_map_open = True
            
            self.full_map_view.resetTransform()
            self.full_map_view.scale(0.25, 0.25) 
            self.full_map_view.centerOn(self.player.visual)
        else:
            self.map_screen.hide()
            self.gameplay_area.show()
            self.is_map_open = False