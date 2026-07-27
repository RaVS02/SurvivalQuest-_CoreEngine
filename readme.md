# Mini Gierka w Ramach Nauki Biblioteki 
## Wykorzystane Środowisko

## Opis projektu
Projekt własnego silnika minigier 2D tworzony od zera w Pythonie przy wykorzystaniu frameworka PySide6 (QGraphicsView, QGraphicsScene). Celem projektu jest nauka mechanizmów gamedevu na poziomie "low-level logic" bez użycia gotowych silników typu Unity.

## Zaimplementowane Mechaniki (Silnik)
* **Game Loop i Delta Time:** Ruch niezależny od klatek na sekundę (Frame-Rate Independent) obliczany na podstawie czasu z `QElapsedTimer`.
* **Ruch postaci (Top-Down):** Normalizacja wektorów ruchu po skosie (matematyka pierwiastków) zapobiegająca *strafe-runningowi*.
* **System Kafelkowy (Tilemap):** Proceduralne generowanie mapy 2D oparte na wydajnych wielowymiarowych tablicach z biblioteki `NumPy`.
* **System Kolizji (AABB):** Autorski system detekcji ścian poprzez rzutowanie współrzędnych ekranowych na indeksy tablicy (AABB). Posiada wsparcie dla tzw. *Leading Edge* oraz definiowania logicznych Hitboxów o mniejszych rozmiarach niż Sprite graficzny.
* **Kamera (Viewport):** Płynne śledzenie gracza (`centerOn`) w środowisku większym niż ekran aplikacji.

## Struktura Projektu
```
my_game/
│
├── game/                 
│   ├── core/             # silnik gry (logika, modele)
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── world.py
│   │   └── physics.py
│   │
│   ├── ui/               # warstwa graficzna (PySide6)
│   │   ├── main_window.py
│   │   ├── renderer.py
│   │   └── assets.py
│   │
│   ├── assets/           # grafiki, dźwięki
│   └── config/           # ustawienia gry
│
├── tests/                # testy logiki gry
├── README.md
└── main.py               # punkt startowy
```

## Plan rozwoju
- [x] Podstawy pętli gry i ruchu (Delta Time)
- [x] Renderowanie Sprite'ów i mapy kafelkowej
- [x] System kolizji (Hitboxy) i kamera
- [ ] Złożony system mapy i minimapy
- [ ] Sortowanie głębi (Z-ordering / Y-Sort) dla efektu 2.5D
- [ ] Animacje sprite’ów (Spritesheets)
- [ ] Główne Menu / UI / Ekwipunek
- [ ] System walki i AI przeciwników
- [ ] Zapis / Odczyt stanu gry


## Instalacja
```bash
pip install -r requirements.txt