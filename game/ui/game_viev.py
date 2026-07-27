import sys
from PySide6.QtCore import Qt, Signal, QTimer, QElapsedTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGraphicsView, QGraphicsScene,QGraphicsRectItem
from PySide6.QtGui import QBrush, QPen, QColor
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem
import numpy as np
class GameView(QWidget):
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game View - Core Engine")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.map_size=64
        self.start_pos=500
        self.sprite_size = 64
        self.speed = 200 
        self.angle_speed=180
        # Ile pikseli odcinamy z lewej i prawej strony (żeby łatwiej wchodzić w korytarze)
        self.hitbox_margin_x = 18 
        # Ile pikseli odcinamy z góry (głowa ignoruje ściany)
        self.hitbox_margin_top = 40 
        # Ile pikseli odcinamy z dołu (żeby stopy nie były na samym brzegu obrazka)
        self.hitbox_margin_bottom = 2
        # GŁÓWNY UKŁAD
        main_layout = QVBoxLayout(self)
        
        # PRZYCISK POWROTU DO MENU
        self.btn_exit = QPushButton("Wróć do Menu (ESC)")
        self.btn_exit.clicked.connect(self.quit_requested.emit)
        main_layout.addWidget(self.btn_exit)

        # SCENA I WIDOK GRY (CANVAS)
        self.scene = QGraphicsScene()
        self.gen_worldmap()
        #self.square()
        self.gen_sprites()
        self.canvas = QGraphicsView(self.scene)
        self.canvas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.canvas.setStyleSheet("background-color: lightgray; border: none;")
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        main_layout.addWidget(self.canvas)

        # --- MIEJSCE NA TWOJĄ INICJALIZACJĘ TIMERA I DELTA TIME ---
        # 1. Utwórz self.game_timer (QTimer) i podepnij go pod self.process_movement
        self.game_timer=QTimer()
        self.game_timer.timeout.connect(self.process_movement_player)
        self.game_timer.start(16)
        # 2. Utwórz self.elapsed_timer (QElapsedTimer) i od razu go wystartuj
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        # --- ZMIENNE STANU GRY ---
        self.keys_pressed = {
            # ruch x y
            Qt.Key.Key_Left: False,
            Qt.Key.Key_Right: False,
            Qt.Key.Key_Up: False,
            Qt.Key.Key_Down: False,
            #rotacja kat lewo/prawo
            Qt.Key.Key_A:False,
            Qt.Key.Key_D:False
        }
        # Pamiętaj, że teraz prędkość to piksele na sekundę!
        self.position={'x':self.start_pos,'y':self.start_pos}
        
    def keyPressEvent(self, event):
        # Powrót do menu pod klawiszem ESC
        if event.key() == Qt.Key.Key_Escape:
            self.quit_requested.emit()
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
            # 3. Testowy wydruk pozycji
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
            # Gdzie postać chce iść (z uwzględnieniem normalizacji skosów)
            future_x = self.position['x'] + dir_x * step * (0.7071 if dir_y != 0 else 1.0)
            
            # Aplikujemy marginesy X (Krawędź Wiodąca Hitboxa)
            if dir_x == 1: 
                # Idziemy w prawo -> Prawy bok hitboxa
                check_x = future_x + self.sprite_size - self.hitbox_margin_x - 1
            else:          
                # Idziemy w lewo -> Lewy bok hitboxa
                check_x = future_x + self.hitbox_margin_x
                
            # W osi X sprawdzamy kolizję na wysokości stóp postaci!
            check_y = self.position['y'] + self.sprite_size - self.hitbox_margin_bottom - 5
            
            # Tłumaczenie na indeksy kafelków
            target_col = int(check_x // self.tilesize)
            current_row = int(check_y // self.tilesize)
            
            # Weryfikacja ze ścianami na mapie
            if 0 <= target_col < self.map_size and 0 <= current_row < self.map_size:
                if self.testowaplansza[current_row][target_col] == 0:
                    self.position['x'] = future_x

        # ---- KOLIZJE OŚ Y ----
        if dir_y != 0:
            # UWAGA NA POPRAWKĘ: Dodajemy do self.position['y']!
            future_y = self.position['y'] + dir_y * step * (0.7071 if dir_x != 0 else 1.0)
            
            # Aplikujemy marginesy Y (Krawędź Wiodąca Hitboxa)
            if dir_y == 1: 
                # Idziemy w dół -> Sprawdzamy stopy (Dół hitboxa)
                check_y = future_y + self.sprite_size - self.hitbox_margin_bottom - 1
            else: 
                # Idziemy w górę -> Sprawdzamy czubek hitboxa (np. brzuch/klatkę, ucinając głowę)
                check_y = future_y + self.hitbox_margin_top
            
            # W osi Y sprawdzamy kolizję dokładnie na środku szerokości postaci
            check_x = self.position['x'] + (self.sprite_size / 2)
            
            # Tłumaczenie na indeksy kafelków (pamiętaj o odpowiedniej kolejności!)
            target_row = int(check_y // self.tilesize)
            current_col = int(check_x // self.tilesize)
            
            # Weryfikacja ze ścianami na mapie
            if 0 <= current_col < self.map_size and 0 <= target_row < self.map_size:
                # W tablicy NumPy najpierw podajemy Wiersz (Y), potem Kolumnę (X)!
                if self.testowaplansza[target_row][current_col] == 0:
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
                    
                kafelek.setPos(x_pos, y_pos)
                self.scene.addItem(kafelek)
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