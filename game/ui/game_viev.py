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
        self.speed = 100 
        self.angle_speed=180
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
            # 3. Testowy wydruk pozycji
            print(f"Pozycja: x:{self.position['x']}, y:{self.position['y']},Kat:{self.player_visual.rotation()}")
    def move_math_player(self, delta_time,rotation=True):
        
        on_tile_pos_x=0
        
        # Obliczamy, o ile pikseli chcemy się przesunąć w tej klatce (v * delta_time)
        step = self.speed * delta_time
        dir_x=0
        dir_y=0
        kat=self.player_visual.rotation()
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
        # ---- KOLIZJE OŚ X ----   
        if dir_x != 0:
            # 1. Gdzie postać CHCE iść w osi X?
            future_x = self.position['x'] + dir_x * step * (0.7071 if dir_y != 0 else 1.0)
            
            # 2. Przelicz przyszłą pozycję X i obecną pozycję Y na indeksy kafelków
            target_col = int(future_x // self.tilesize)
            current_row = int(self.position['y'] // self.tilesize)
            
            # 3. Sprawdź, czy nie wychodzimy poza ramy tablicy 64x64!
            if 0 <= target_col < self.map_size and 0 <= current_row < self.map_size:
                # 4. Sprawdź, czy na tym kafelku jest podłoga (0)
                if self.level_data[current_row][target_col] == 0:
                    # Sukces! Nie ma ściany, możemy przypisać nową pozycję
                    self.position['x'] = future_x
        # ---- KOLIZJE OŚ Y ----
        if dir_y !=0:
            future_y = self.position['x']+dir_y*step*(0.7071 if dir_x != 0 else 1.0)
            # 2. Przelicz przyszłą pozycję X i obecną pozycję Y na indeksy kafelków
            current_col = int(self.position['x'] // self.tilesize)
            target_row = int(future_y // self.tilesize)
            if 0 <= target_col < self.map_size and 0 <= current_row < self.map_size:
                # 4. Sprawdź, czy na tym kafelku jest podłoga (0)
                if self.level_data[current_row][target_col] == 0:
                # Sukces! Nie ma ściany, możemy przypisać nową pozycję
                    self.position['y'] = future_y
        # if dir_x != 0 and dir_y != 0:
        #     self.position['x']+=dir_x*(step)*0.7071
        #     self.position['y']+=dir_y*(step)*0.7071
        # else:
        #     self.position['x']+=dir_x*(step)
        #     self.position['y']+=dir_y*(step)
        if rotation==True:
            # Rotacja (A - w lewo, D - w prawo)
            angle_step = self.angle_speed * delta_time
            
            if self.keys_pressed[Qt.Key.Key_A]:
                self.player_visual.setRotation(kat - angle_step)
            if self.keys_pressed[Qt.Key.Key_D]:
                self.player_visual.setRotation(kat + angle_step)   
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scene.setSceneRect(0, 0, self.canvas.width(), self.canvas.height())
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
        player_image = player_image.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        #2. Tworzymy nowy obiekt sceny oparty na obrazku
        self.player_visual = QGraphicsPixmapItem(player_image)

        # 3. Ustawiamy środek obrotu i pozycję tak jak wcześniej
        w = self.player_visual.pixmap().width()
        h = self.player_visual.pixmap().height()
        self.player_visual.setTransformOriginPoint(w / 2, h / 2)
        self.player_visual.setPos(self.start_pos, self.start_pos)

        # 4. Dodajemy na scenę
        self.scene.addItem(self.player_visual)
    def gen_worldmap(self):
        self.tilesize=32
        #tesowa plansza
        # self.testowaplansza=[
        #     [1, 1, 1, 1, 1, 1, 1, 1],
        #     [1, 0, 0, 0, 0, 0, 0, 1],
        #     [1, 0, 1, 1, 0, 1, 0, 1],
        #     [1, 0, 0, 0, 0, 0, 0, 1],
        #     [1, 1, 1, 1, 1, 1, 1, 1]
        # ]
        self.testowaplansza=np.random.randint(0, 2, size=(self.map_size, self.map_size))
        # Pętla po wierszach (y)
        for row_idx, row_data in enumerate(self.testowaplansza):
            # Pętla po kolumnach w danym wierszu (x)
            for col_idx, tile_value in enumerate(row_data):
                x_pos=col_idx*self.tilesize
                y_pos=row_idx*self.tilesize
                kafelek=QGraphicsRectItem(0,0,self.tilesize,self.tilesize)
                if tile_value==1:
                    kafelek.setBrush(QBrush(QColor("green")))
                else:
                    kafelek.setBrush(QBrush(QColor("grey")))
                kafelek.setPos(x_pos,y_pos)
                self.scene.addItem(kafelek)