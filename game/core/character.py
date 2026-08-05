import math
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap


class Character:
    """Klasa bazowa dla wszystkich bytów poruszających się po mapie (Gracz, Wrogowie, NPC)."""
    def __init__(self, x: float, y: float, sprite_path: str, sprite_size: int = 64, speed: float = 200.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.sprite_size = sprite_size
        
        # Marginesy Hitboxa (domyślne dla postaci)
        self.hitbox_margin_x = 18
        self.hitbox_margin_top = 40
        self.hitbox_margin_bottom = 2

        # Inicjalizacja Grafiki w Qt
        pixmap = QPixmap(sprite_path)
        pixmap = pixmap.scaled(
            self.sprite_size, self.sprite_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.FastTransformation
        )
        self.visual = QGraphicsPixmapItem(pixmap)
        self.visual.setZValue(1) # Postacie są nad podłogą
        
        w = self.visual.pixmap().width()
        h = self.visual.pixmap().height()
        self.visual.setTransformOriginPoint(w / 2.0, h / 2.0)
        self.set_position(self.x, self.y)

    def set_position(self, x: float, y: float):
        """Ustawia logiczne i graficzne położenie postaci."""
        self.x = x
        self.y = y
        self.visual.setPos(self.x, self.y)

    def get_tile_pos(self, tilesize: int) -> tuple[int, int]:
        """Zwraca obecną pozycję kafelkową (Tile X, Tile Y)."""
        return int(self.x // tilesize), int(self.y // tilesize)


class Player(Character):
    """Klasa reprezentująca Gracza sterowanego klawiaturą."""
    def __init__(self, x: float, y: float, sprite_path: str, sprite_size: int = 64, speed: float = 200.0):
        super().__init__(x, y, sprite_path, sprite_size, speed)
        
        self.angle_speed = 180.0
        self.range_view = 8
        self.keys_pressed = {
            Qt.Key.Key_Left: False,
            Qt.Key.Key_Right: False,
            Qt.Key.Key_Up: False,
            Qt.Key.Key_Down: False,
            Qt.Key.Key_A: False,
            Qt.Key.Key_D: False
        }

    def set_key_state(self, key, is_pressed: bool):
        """Aktualizuje stan klawisza sterującego."""
        if key in self.keys_pressed:
            self.keys_pressed[key] = is_pressed

    def update(self, delta_time: float, tile_map, map_size: int, tilesize: int):
        """Główna pętla fizyki gracza: ruch, kolizje, obrót."""
        step = self.speed * delta_time
        dir_x = 0
        dir_y = 0
        kat = self.visual.rotation()

        if self.keys_pressed[Qt.Key.Key_Left]:  dir_x -= 1
        if self.keys_pressed[Qt.Key.Key_Right]: dir_x += 1
        if self.keys_pressed[Qt.Key.Key_Up]:    dir_y -= 1
        if self.keys_pressed[Qt.Key.Key_Down]:  dir_y += 1

        # ---- KOLIZJE OŚ X ----
        if dir_x != 0:
            future_x = self.x + dir_x * step * (0.7071 if dir_y != 0 else 1.0)
            hitbox_top = self.y + self.hitbox_margin_top
            hitbox_bottom = self.y + self.sprite_size - self.hitbox_margin_bottom - 1

            check_x = future_x + (self.sprite_size - self.hitbox_margin_x - 1 if dir_x == 1 else self.hitbox_margin_x)

            target_col = int(check_x // tilesize)
            top_row = int(hitbox_top // tilesize)
            bottom_row = int(hitbox_bottom // tilesize)

            if 0 <= target_col < map_size and 0 <= top_row < map_size and 0 <= bottom_row < map_size:
                if tile_map[top_row][target_col] == 0 and tile_map[bottom_row][target_col] == 0:
                    self.x = future_x

        # ---- KOLIZJE OŚ Y ----
        if dir_y != 0:
            future_y = self.y + dir_y * step * (0.7071 if dir_x != 0 else 1.0)
            hitbox_left = self.x + self.hitbox_margin_x
            hitbox_right = self.x + self.sprite_size - self.hitbox_margin_x - 1

            check_y = future_y + (self.sprite_size - self.hitbox_margin_bottom - 1 if dir_y == 1 else self.hitbox_margin_top)

            target_row = int(check_y // tilesize)
            left_col = int(hitbox_left // tilesize)
            right_col = int(hitbox_right // tilesize)

            if 0 <= target_row < map_size and 0 <= left_col < map_size and 0 <= right_col < map_size:
                if tile_map[target_row][left_col] == 0 and tile_map[target_row][right_col] == 0:
                    self.y = future_y

        # ---- ROTACJA ----
        angle_step = self.angle_speed * delta_time
        if self.keys_pressed[Qt.Key.Key_A]:
            self.visual.setRotation(kat - angle_step)
        if self.keys_pressed[Qt.Key.Key_D]:
            self.visual.setRotation(kat + angle_step)

        # Zaktualizuj pozycję grafiki
        self.visual.setPos(self.x, self.y)


class Enemy(Character):
    """Klasa przeciwnika (do późniejszej rozbudowy AI)."""
    def __init__(self, x: float, y: float, sprite_path: str):
        super().__init__(x, y, sprite_path)


class PassivMob(Character):
    """Klasa biernego moba/zwierzęcia."""
    def __init__(self, x: float, y: float, sprite_path: str):
        super().__init__(x, y, sprite_path)