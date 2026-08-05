class Character:
    def __init__(
        self, 
        defense: float=1.0, 
        magic_resist: float=1.0, 
        lvl: float = 1.0, 
        max_hp: float = 100, 
        max_ap: float = 10.0,
        perks_points=5,
        stamina:float=10.0
        
    ):
        self.max_hp = max_hp
        self.max_ap = max_ap
        self.current_hp = max_hp
        self.current_ap = max_ap
        self.defense = defense
        self.magic_resist = magic_resist
        self.lvl = lvl
        self.perks_points=perks_points
        self.stamina=stamina
        self.critical_chance=0.01
        self.attack_speed=1.0
        # Perki
        self.mele_attack=1.0
        self.range_attack=1.0
        self.magic_attack=1.0
        self.building_speed=1.0
        self.max_eq=10.0
        # Ekwipunek
        self.eq={}
    def __repr__(self) -> str:
        return f"Character(lvl={self.lvl}, hp={self.current_hp}/{self.max_hp}, ap={self.current_ap}/{self.max_ap})"

    def __str__(self) -> str:
        return (f"Postać (Lvl: {self.lvl}) | "
                f"HP: {self.current_hp}/{self.max_hp} 🩸 | "
                f"AP: {self.current_ap}/{self.max_ap} ⚡ | "
                f"Obrona: {self.defense} 🛡️ | "
                f"Odp. na magię: {self.magic_resist} 🔮")
    
class Player(Character):
    def __init__(self, defense=1.0, magic_resist=1.0, lvl = 1, max_hp = 100, max_ap = 10, perks_points=5,mele_attack=2):
        super().__init__(defense=defense, magic_resist=magic_resist, lvl=lvl, max_hp=max_hp, max_ap=max_ap, perks_points=perks_points,mele_attack=mele_attack)
        self.hungry=100
        self.thirst=100
    def upgrade_statistic_point(self, stat: str):
        if self.perks_points>0:
            if stat=="max_hp":
                self.max_hp=self.max_hp+5.0               
            elif stat=="max_ap":
                self.max_ap=self.max_ap+5.0
            elif stat=="stamina":
                self.stamina=self.stamina+5.0
            self.perks_points=self.perks_points-1   
class Enemy(Character):
    def __init__(self, defense=1.0, magic_resist=1.0, lvl = 1, max_hp = 100, max_ap = 10, perks_points=5,mele_attack=1):
        super().__init__(defense=defense, magic_resist=magic_resist, lvl=lvl, max_hp=max_hp, max_ap=max_ap, perks_points=perks_points,mele_attack=mele_attack)

class PassivMob(Character):
    def __init__(self, defense, magic_resist, lvl = 1, max_hp = 100, max_ap = 10, perks_points=5):
        super().__init__(defense=defense, magic_resist=magic_resist, lvl=lvl, max_hp=max_hp, max_ap=max_ap, perks_points=perks_points)



        
if __name__ == "__main__":
    
    print("TEST")
    