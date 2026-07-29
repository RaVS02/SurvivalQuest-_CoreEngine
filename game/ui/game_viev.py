import math
import sys
import numpy as np
from PySide6.QtCore import Qt, Signal, QTimer, QElapsedTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem,QFrame
)
from PySide6.QtGui import QBrush, QPen, QColor, QPixmap
class GameView(QWidget):
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game View - Core Engine")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # --- ZMIENNE KONFIGURACYJNE GRY ---
        self.map_size = 128
        self.start_pos = 500
        self.sprite_size = 64
        self.speed = 400 
        self.angle_speed = 180
        self.range_view=8
        # Marginesy Hitboxa
        self.hitbox_margin_x = 18
        self.hitbox_margin_top = 40 
        self.hitbox_margin_bottom = 2

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
        self.gen_sprites()

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
        
        # TUTAJ BYŁ BŁĄD! Dodajemy minimap_frame, a nie minimap!
        compass_grid.addWidget(self.minimap_frame, 1, 1) 
        
        compass_grid.addWidget(lbl_e, 1, 2)          # Prawo: Wschód
        compass_grid.addWidget(lbl_s, 2, 1)          # Dół: Południe

        dashboard_layout.addWidget(minimap_box, alignment=Qt.AlignmentFlag.AlignCenter)

        # 2B. ETYKIETY STATYSTYK I KOORDYNATÓW
        dashboard_layout.addSpacing(10)
        
        self.zoom_label = QLabel("Zoom: 0.1x")
        self.dir_label = QLabel("Kierunek: STOI")
        self.dir_label.setStyleSheet("color: #f1c40f; font-weight: bold; font-size: 14px;")

        # self.tile_x_label = QLabel("Tile X: 0")
        # self.tile_y_label = QLabel("Tile Y: 0")
        # self.px_x_label = QLabel("Px X: 0")
        # self.px_y_label = QLabel("Px Y: 0")
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

        self.keys_pressed = {
            Qt.Key.Key_Left: False,
            Qt.Key.Key_Right: False,
            Qt.Key.Key_Up: False,
            Qt.Key.Key_Down: False,
            Qt.Key.Key_A: False,
            Qt.Key.Key_D: False
        }

        self.position = {'x': self.start_pos, 'y': self.start_pos}
        # Pełna Mapa Kamera
        # --- EKRAN PEŁNEJ MAPY (Złożony w jeden QWidget) ---
        # 1. Tworzymy nasze "pudełko" na ekran mapy (pamiętaj o dodaniu self.!)
        self.map_screen = QWidget()
        
        # 2. Wkładamy do pudełka pionowe przegródki (Layout pionowy)
        map_layout = QVBoxLayout(self.map_screen)
        
        # 3. Tworzymy tekst koordynatów i wrzucamy do pierwszej górnej przegródki
        self.poz_tile_label_fullmap = QLabel("Poz: x:0 y:0")
        self.poz_tile_label_fullmap.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.poz_tile_label_fullmap.setAlignment(Qt.AlignmentFlag.AlignCenter) # Wyśrodkowanie
        map_layout.addWidget(self.poz_tile_label_fullmap)
        
        # 4. Tworzymy kamerę mapy i wrzucamy do drugiej przegródki (pod tekstem)
        self.full_map_view = QGraphicsView(self.scene)
        self.full_map_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.full_map_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.full_map_view.setStyleSheet("background-color: black; border: 2px solid gray;")
        # --- NOWE: Blokada kradzieży kliknięć i włączenie rączki do przesuwania ---
        self.full_map_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.full_map_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        map_layout.addWidget(self.full_map_view)
        
        # 5. Teraz CAŁE nasze zorganizowane pudełko wrzucamy do głównego okna gry
        main_layout.addWidget(self.map_screen)
        
        # Domyślnie chowamy całe pudełko (a nie tylko samą mapę)
        self.map_screen.hide()
        self.is_map_open = False
        
        # Aplikujemy początkowy poziom zoomu
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
        
        if event.key()==Qt.Key.Key_M:
            self.toggle_full_map()
            return
        
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed[key] = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed[key] = False

    def process_movement(self):
        # 1. Pobierz czas (delta_time w sekundach)
        delta_time = self.elapsed_timer.elapsed() / 1000.0
        self.elapsed_timer.restart()
        
        # 2. Oblicz ruch
        self.move_math(delta_time)
        self.rect_item.setPos(self.position['x'],self.position['y'])
        # Rotacja
        self.rect_item.rotation()
        # 3. Testowy wydruk pozycji
        print(f"Pozycja: x:{self.position['x']}, y:{self.position['y']},Kat:{self.rect_item.rotation()}")

    def move_math(self, delta_time):
        # Obliczamy, o ile pikseli chcemy się przesunąć w tej klatce (v * delta_time)
        step = self.speed * delta_time
        dir_x=0
        dir_y=0
        kat=self.rect_item.rotation()
        # Oś Pozioma (X) - Niezależne IFy!
        if self.keys_pressed[Qt.Key.Key_Left]:
            #self.position['x'] -= step
            dir_x-=1
        if self.keys_pressed[Qt.Key.Key_Right]:
            #self.position['x'] += step
            dir_x+=1
        # Oś Pionowa (Y) - Niezależne IFy!
        if self.keys_pressed[Qt.Key.Key_Up]:
            #self.position['y'] -= step
            dir_y-=1
        if self.keys_pressed[Qt.Key.Key_Down]:
            #self.position['y'] += step
            dir_y+=1
        if dir_x != 0 and dir_y != 0:
            self.position['x']+=dir_x*(step)*0.7071
            self.position['y']+=dir_y*(step)*0.7071
        else:
            self.position['x']+=dir_x*(step)
            self.position['y']+=dir_y*(step)
        # Rotacja (A - w lewo, D - w prawo)
        angle_step = self.angle_speed * delta_time
        
        if self.keys_pressed[Qt.Key.Key_A]:
            self.rect_item.setRotation(kat - angle_step)
        if self.keys_pressed[Qt.Key.Key_D]:
            self.rect_item.setRotation(kat + angle_step)
    def process_movement_player(self):
            # 1. Pobierz czas (delta_time w sekundach)
            delta_time = self.elapsed_timer.elapsed() / 1000.0
            self.elapsed_timer.restart()
            
            # 2. Oblicz ruch
            self.move_math_player(delta_time,False)
            self.player_visual.setPos(self.position['x'],self.position['y'])
            # Rotacja
            self.player_visual.rotation()
            self.update_camera()
            # 5. Przesuń kamerę MINIMAPY za graczem!
            self.minimap.centerOn(self.player_visual)
            # --- AKTUALIZACJA INTERFEJSU (HUD) ---
            # 1. Przeliczanie pikseli na pozycję w kafelkach (Tile Coords)
            tile_x = int(self.position['x'] // self.tilesize)
            tile_y = int(self.position['y'] // self.tilesize)

            pozycje_tekst = f"Poz: x:{tile_x} y:{tile_y}"
            
            self.poz_tile_label.setText(pozycje_tekst)          # Panel boczny
            self.poz_tile_label_fullmap.setText(pozycje_tekst)

            # 3. Wyznaczenie nazwy kierunku na podstawie wciśniętych klawiszy
            dir_text = []
            if self.keys_pressed[Qt.Key.Key_Up]:    dir_text.append("N")
            if self.keys_pressed[Qt.Key.Key_Down]:  dir_text.append("S")
            if self.keys_pressed[Qt.Key.Key_Left]:  dir_text.append("W")
            if self.keys_pressed[Qt.Key.Key_Right]: dir_text.append("E")

            kierunek = "".join(dir_text) if dir_text else "STOI"
            self.dir_label.setText(f"Kierunek: {kierunek}")
            # --- TRZYSTANOWA MGŁA WOJNY (ZOPTYMALIZOWANA) ---

            # 1. WYGASZANIE: Cofamy kafelki z poprzedniej klatki do stanu "Półmroku"
            for r, c in self.visible_tiles:
                if self.fog_map[r][c] == 0:  # Upewniamy się, że były widoczne
                    self.fog_map[r][c] = 1  # Zmieniamy stan na Pamięć (1)
                    mgla = self.fog_items[(r, c)]

                    # Jeśli używałeś wcześniej .hide(), upewnij się że mgła znowu jest włączona!
                    mgla.show()

                    # Ustawiamy półmrok (np. 70% czerni)
                    mgla.setOpacity(0.7)

            # 2. Czyszczenie zbioru na nową klatkę
            self.visible_tiles.clear()

            # 3. OŚWIETLANIE: Wyliczamy nowe koło widzenia
            zasieg = int(self.range_view)

            for wiersz in range(tile_y - zasieg, tile_y + zasieg + 2):
                for kolumna in range(tile_x - zasieg, tile_x + zasieg + 2):
                    # Sprawdzamy granice mapy
                    if 0 <= wiersz < self.map_size and 0 <= kolumna < self.map_size:
                        # Liczymy dystans Pitagorasem
                        dystans = math.hypot(wiersz - tile_y-1, kolumna - tile_x-1)

                        if dystans <= self.range_view:
                            # Gracz to widzi: Stan = 0
                            self.fog_map[wiersz][kolumna] = 0
                            mgla = self.fog_items[(wiersz, kolumna)]

                            # Całkowicie rozpraszamy mgłę nad tym kafelkiem
                            mgla.setOpacity(0.0)

                            # Zapisujemy do zbioru, aby wygasić to w następnej klatce!
                            self.visible_tiles.add((wiersz, kolumna))

            print(f"Pozycja: x:{self.position['x']}, y:{self.position['y']},Kat:{self.player_visual.rotation()}")

    def move_math_player(self, delta_time, rotation=True):
        # 1. Wyliczenie podstawowego kroku
        step = self.speed * delta_time
        dir_x = 0
        dir_y = 0
        kat = self.player_visual.rotation()

        # 2. Odczyt klawiszy (Kierunki)
        if self.keys_pressed[Qt.Key.Key_Left]:  dir_x -= 1
        if self.keys_pressed[Qt.Key.Key_Right]: dir_x += 1
        if self.keys_pressed[Qt.Key.Key_Up]:    dir_y -= 1
        if self.keys_pressed[Qt.Key.Key_Down]:  dir_y += 1

        # ---- KOLIZJE OŚ X ----
        if dir_x != 0:
            future_x = self.position['x'] + dir_x * step * (0.7071 if dir_y != 0 else 1.0)

            # W osi X wyznaczamy pionowe granice naszego Hitboxa (Obecne Y)
            hitbox_top = self.position['y'] + self.hitbox_margin_top
            hitbox_bottom = self.position['y'] + self.sprite_size - self.hitbox_margin_bottom - 1

            # Aplikujemy marginesy X (Krawędź Wiodąca)
            if dir_x == 1:
                check_x = future_x + self.sprite_size - self.hitbox_margin_x - 1
            else:
                check_x = future_x + self.hitbox_margin_x

            # Tłumaczenie na indeksy kafelków (Sprawdzamy GÓRĘ i DÓŁ krawędzi)
            target_col = int(check_x // self.tilesize)
            top_row = int(hitbox_top // self.tilesize)
            bottom_row = int(hitbox_bottom // self.tilesize)

            # Jeśli oba sprawdzane rogi są na bezpiecznej podłodze (0) -> Ruch jest dozwolony
            if 0 <= target_col < self.map_size and 0 <= top_row < self.map_size and 0 <= bottom_row < self.map_size:
                if self.testowaplansza[top_row][target_col] == 0 and self.testowaplansza[bottom_row][target_col] == 0:
                    self.position['x'] = future_x

        # ---- KOLIZJE OŚ Y ----
        if dir_y != 0:
            future_y = self.position['y'] + dir_y * step * (0.7071 if dir_x != 0 else 1.0)

            # W osi Y wyznaczamy poziome granice naszego Hitboxa (Obecne X)
            hitbox_left = self.position['x'] + self.hitbox_margin_x
            hitbox_right = self.position['x'] + self.sprite_size - self.hitbox_margin_x - 1

            # Aplikujemy marginesy Y (Krawędź Wiodąca)
            if dir_y == 1:
                check_y = future_y + self.sprite_size - self.hitbox_margin_bottom - 1
            else:
                check_y = future_y + self.hitbox_margin_top

            # Tłumaczenie na indeksy kafelków (Sprawdzamy LEWY i PRAWY róg krawędzi)
            target_row = int(check_y // self.tilesize)
            left_col = int(hitbox_left // self.tilesize)
            right_col = int(hitbox_right // self.tilesize)

            # Jeśli oba sprawdzane rogi są na bezpiecznej podłodze (0) -> Ruch jest dozwolony
            if 0 <= target_row < self.map_size and 0 <= left_col < self.map_size and 0 <= right_col < self.map_size:
                if self.testowaplansza[target_row][left_col] == 0 and self.testowaplansza[target_row][right_col] == 0:
                    self.position['y'] = future_y

        # ---- ROTACJA (OPCJONALNA) ----
        if rotation:
            angle_step = self.angle_speed * delta_time
            if self.keys_pressed[Qt.Key.Key_A]:
                self.player_visual.setRotation(kat - angle_step)
            if self.keys_pressed[Qt.Key.Key_D]:
                self.player_visual.setRotation(kat + angle_step)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        #self.scene.setSceneRect(0, 0, self.canvas.width(), self.canvas.height())
    def square(self):
        """funcja do generowania kwadracika/postaci testowej """
    # 2. Tworzymy prostokąt (lokalne wymiary: szerokość 32, wysokość 32)
        self.rect_item = QGraphicsRectItem(0, 0, 32, 32)
        self.rect_item.setTransformOriginPoint(16, 16)
        # 3. Stylizujemy prostokąt (czerwone wypełnienie, czarna ramka)
        self.rect_item.setBrush(QBrush(QColor("red")))
        self.rect_item.setPen(QPen(QColor("black"), 1))
    
        # 4. Ustalamy pozycję prostokąta na scenie (X=0, Y=0)
        self.rect_item.setPos(self.start_pos, self.start_pos)
        # 5. Dodajemy obiekt do sceny
        self.scene.addItem(self.rect_item)    
    def gen_sprites(self):
        """ Tworzenie Gracza ze sprita"""
        # 1. Ładujemy obrazek z dysku (pamiętaj o prawidłowej ścieżce!)
        player_image = QPixmap("./game/assets/MrRzodkiewkaSprite.png")

        # Opcjonalnie: Jeśli obrazek jest za duży/za mały, możemy go przeskalować.
        # Używamy FastTransformation, aby utrzymać ostre krawędzie w Pixel Arcie (zapobiega rozmyciu).
        player_image = player_image.scaled(self.sprite_size, self.sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        #2. Tworzymy nowy obiekt sceny oparty na obrazku
        self.player_visual = QGraphicsPixmapItem(player_image)
        self.player_visual.setZValue(1)
        # 3. Ustawiamy środek obrotu i pozycję tak jak wcześniej
        w = self.player_visual.pixmap().width()
        h = self.player_visual.pixmap().height()
        self.player_visual.setTransformOriginPoint(w / 2, h / 2)
        self.player_visual.setPos(self.start_pos, self.start_pos)

        # 4. Dodajemy na scenę
        self.scene.addItem(self.player_visual)
    def gen_worldmap(self):
        self.tilesize = 32
        
        # 1. Tworzymy pustą mapę wypełnioną zerami (podłoga / szary)
        # Rozmiar mapy pobierany jest z self.map_size
        self.testowaplansza = np.zeros((self.map_size, self.map_size), dtype=int)
        self.fog_map = np.full((self.map_size, self.map_size), 2, dtype=int)
        self.fog_items = {}
        self.visible_tiles = set()
        world_width = self.map_size * self.tilesize
        world_height = self.map_size * self.tilesize
        
        # Mówimy Qt, jak gigantyczny jest nasz świat!
        self.scene.setSceneRect(0, 0, world_width, world_height)
        # 2. Budujemy zewnętrzne ściany (ramka wokół mapy)
        self.testowaplansza[0, :] = 1   # Górna ściana
        self.testowaplansza[-1, :] = 1  # Dolna ściana
        self.testowaplansza[:, 0] = 1   # Lewa ściana
        self.testowaplansza[:, -1] = 1  # Prawa ściana
        
        # 3. Dodajemy wewnętrzne przeszkody (kolumny do testowania kolizji)
        # Stawiamy klocek w co czwartym kafelku, omijając brzegi
        for r in range(3, self.map_size - 3, 4):
            for c in range(3, self.map_size - 3, 4):
                self.testowaplansza[r, c] = 1

        # 4. Pętla rysująca kafle na scenie Qt
        for row_idx, row_data in enumerate(self.testowaplansza):
            for col_idx, tile_value in enumerate(row_data):
                x_pos = col_idx * self.tilesize
                y_pos = row_idx * self.tilesize
                
                # Tworzymy kafel od (0,0) do (tilesize, tilesize)
                kafelek = QGraphicsRectItem(0, 0, self.tilesize, self.tilesize)
                kafelek.setZValue(0)
                if tile_value == 1:
                    # Ściana / Przeszkoda (zielona)
                    kafelek.setBrush(QBrush(QColor("green")))
                    # Opcjonalnie dodaj ramkę, żeby ściany nie zlewały się w jedną masę
                    kafelek.setPen(QPen(QColor("darkgreen"), 1))
                else:
                    # Wolna ścieżka (szara)
                    kafelek.setBrush(QBrush(QColor("grey")))
                    kafelek.setPen(QPen(QColor("darkgray"), 1))
                kafelek_mgly= QGraphicsRectItem(0, 0, self.tilesize, self.tilesize)
                kafelek_mgly.setBrush(QBrush(QColor("black")))
                kafelek_mgly.setZValue(2)
                kafelek.setPos(x_pos, y_pos)
                kafelek_mgly.setPos(x_pos, y_pos)
                self.scene.addItem(kafelek)
                self.scene.addItem(kafelek_mgly)
                self.fog_items[(row_idx, col_idx)] = kafelek_mgly
    def update_camera(self):
        # 1. Pobierz wymiary widoku (okna)
        view_w = self.canvas.width()
        view_h = self.canvas.height()
        
        half_w = view_w / 2.0
        half_h = view_h / 2.0
        
        # 2. Całkowite wymiary świata w pikselach
        world_w = self.map_size * self.tilesize
        world_h = self.map_size * self.tilesize
        
        # 3. Pozycja gracza (środek jego sprite'a)
        player_center_x = self.position['x'] + (self.sprite_size / 2.0)
        player_center_y = self.position['y'] + (self.sprite_size / 2.0)
        
        # 4. Obliczamy Cam_X z ograniczeniem (clamping)
        # Przykład w czystym Pythonie: max(half_w, min(player_center_x, world_w - half_w))
        cam_x = max(half_w, min(player_center_x, world_w - half_w))
        cam_y = max(half_h, min(player_center_y, world_h - half_h))
        
        # 5. Ustawiamy kamerę na wyliczony punkt
        self.canvas.centerOn(cam_x, cam_y)
    def update_minimap_zoom(self):
        # Resetujemy skalę do bazowego 1.0
        self.minimap.resetTransform()
        
        # Pobieramy mnożnik z listy
        zoom_factor = self.zoom_levels[self.current_zoom_idx]
        
        # Aplikujemy nową skalę
        self.minimap.scale(zoom_factor, zoom_factor)
        
        # Aktualizujemy tekst
        self.zoom_label.setText(f"Zoom: {zoom_factor}x")
    def toggle_full_map(self):
        if self.is_map_open == False:
            self.gameplay_area.hide()
            self.map_screen.show()
            self.is_map_open = True
            
            # Resetujemy skalę, oddalamy widok i centrujemy na graczu
            self.full_map_view.resetTransform()
            self.full_map_view.scale(0.25, 0.25) 
            self.full_map_view.centerOn(self.player_visual)
        else:
            self.map_screen.hide()
            self.gameplay_area.show()
            self.is_map_open = False