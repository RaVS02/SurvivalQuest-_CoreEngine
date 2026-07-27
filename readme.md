# Mini Gierka w Ramach Nauki Biblioteki 
## Wykorzystane Środowisko

## Opis
Krótki opis gry: mechanika, cel, klimat.

## Funkcje
- Sterowanie postacią
- Kolizje
- Przeciwnicy
- Punkty / HP
- Animacje

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
- [ ] System kolizji
- [ ] Animacje sprite’ów
- [ ] Menu startowe
- [ ] Zapis stanu gry
- [ ] Dźwięki

## Mechaniki Gry

### 🔹 1. **Ruch gracza**
- prędkość  
- kierunek  
- ograniczenia mapy  

### 🔹 2. **Kolizje**
- z mapą  
- z przeciwnikami  
- z obiektami  

### 🔹 3. **AI przeciwników**
- patrol  
- pogoń  
- atak  

### 🔹 4. **Fizyka**
- grawitacja  
- tarcie  
- skoki  

### 🔹 5. **UI**
- HUD  
- HP  
- punkty  

### 🔹 6. **Loop gry**
- update  
- render  
- input 

## Instalacja
```bash
pip install -r requirements.txt