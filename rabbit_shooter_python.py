#!/usr/bin/env python3
"""
Rabbit Shooter Game - Python/Pygame Version
Un gioco di tiro ai conigli in 2D con stile 8-bit
"""

import pygame
import random
import math
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

# Inizializzazione di Pygame
pygame.init()
pygame.mixer.init()

# Costanti di gioco
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colori (palette 8-bit)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
PURPLE = (147, 112, 219)
GOLD = (255, 215, 0)
BLUE = (0, 0, 255)

class RabbitType(Enum):
    NORMAL = "normal"
    FAST = "fast"
    BONUS = "bonus"
    SNEAKY = "sneaky"

@dataclass
class RabbitData:
    type: RabbitType
    color: Tuple[int, int, int]
    points: int
    base_speed: float

# Dati dei conigli
RABBIT_TYPES = {
    RabbitType.NORMAL: RabbitData(RabbitType.NORMAL, BROWN, 10, 1.0),
    RabbitType.FAST: RabbitData(RabbitType.FAST, GREEN, 20, 1.5),
    RabbitType.BONUS: RabbitData(RabbitType.BONUS, GOLD, 50, 0.8),
    RabbitType.SNEAKY: RabbitData(RabbitType.SNEAKY, PURPLE, 30, 2.0)
}

class Bullet:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 4
        self.speed = 8
        self.active = True
        
    def update(self):
        # I proiettili sono istantanei nella posizione del click
        self.active = False
        
    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, YELLOW, (self.x - 2, self.y - 2, self.width, self.height))

class Rabbit:
    def __init__(self, x: float, y: float, rabbit_type: RabbitType):
        self.x = x
        self.y = y
        self.rabbit_data = RABBIT_TYPES[rabbit_type]
        self.width = 40
        self.height = 40
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.alive = True
        self.direction_change_timer = 0
        
    def update(self, game_speed_multiplier: float):
        if not self.alive:
            return
            
        # Movimento con velocità aumentata
        speed = self.rabbit_data.base_speed * game_speed_multiplier
        self.x += self.vx * speed
        self.y += self.vy * speed
        
        # Rimbalzo sui bordi
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.vx = -self.vx
            self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
            
        if self.y <= 60 or self.y >= SCREEN_HEIGHT - self.height - 60:
            self.vy = -self.vy
            self.y = max(60, min(SCREEN_HEIGHT - self.height - 60, self.y))
        
        # Cambio direzione casuale
        self.direction_change_timer += 1
        if self.direction_change_timer > 120:  # Ogni 2 secondi circa
            if random.random() < 0.3:  # 30% di probabilità
                self.vx = random.uniform(-3, 3)
                self.vy = random.uniform(-3, 3)
                self.direction_change_timer = 0
    
    def draw(self, screen):
        if not self.alive:
            return
            
        # Corpo del coniglio
        pygame.draw.rect(screen, self.rabbit_data.color, (self.x, self.y, self.width, self.height))
        
        # Orecchie
        ear_width = 8
        ear_height = 16
        pygame.draw.rect(screen, self.rabbit_data.color, 
                        (self.x + 6, self.y - 12, ear_width, ear_height))
        pygame.draw.rect(screen, self.rabbit_data.color, 
                        (self.x + 26, self.y - 12, ear_width, ear_height))
        
        # Occhi
        pygame.draw.rect(screen, WHITE, (self.x + 8, self.y + 8, 6, 6))
        pygame.draw.rect(screen, WHITE, (self.x + 26, self.y + 8, 6, 6))
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 10, 2, 2))
        pygame.draw.rect(screen, BLACK, (self.x + 28, self.y + 10, 2, 2))
        
        # Naso
        pygame.draw.rect(screen, (255, 105, 180), (self.x + 17, self.y + 20, 6, 4))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        return self.get_rect().collidepoint(mouse_pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🐰 Rabbit Shooter - Stile 8-bit")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Stato di gioco
        self.game_state = "menu"  # "menu", "playing", "game_over"
        self.score = 0
        self.high_score = self.load_high_score()
        self.time_left = 60.0
        self.game_speed_multiplier = 1.0
        
        # Oggetti di gioco
        self.rabbits: List[Rabbit] = []
        self.bullets: List[Bullet] = []
        
        # Timer per spawn conigli
        self.spawn_timer = 0
        
        self.running = True
        
    def load_high_score(self) -> int:
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def start_game(self):
        self.game_state = "playing"
        self.score = 0
        self.time_left = 60.0
        self.game_speed_multiplier = 1.0
        self.rabbits = []
        self.bullets = []
        self.spawn_timer = 0
        
        # Spawn conigli iniziali
        for _ in range(6):
            self.spawn_rabbit()
    
    def spawn_rabbit(self):
        rabbit_type = random.choice(list(RabbitType))
        x = random.randint(50, SCREEN_WIDTH - 90)
        y = random.randint(100, SCREEN_HEIGHT - 150)
        self.rabbits.append(Rabbit(x, y, rabbit_type))
    
    def update_game_speed(self):
        self.game_speed_multiplier = (self.score // 150) + 1
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        if self.game_state != "playing":
            return
            
        # Crea proiettile istantaneo
        bullet = Bullet(mouse_pos[0], mouse_pos[1])
        
        # Controlla collisioni immediate con i conigli
        for rabbit in self.rabbits:
            if rabbit.alive and rabbit.is_clicked(mouse_pos):
                rabbit.alive = False
                self.score += rabbit.rabbit_data.points
                break
    
    def update(self):
        if self.game_state != "playing":
            return
            
        # Aggiorna timer
        self.time_left -= 1/60
        if self.time_left <= 0:
            self.game_state = "game_over"
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        
        # Aggiorna velocità di gioco
        self.update_game_speed()
        
        # Aggiorna conigli
        for rabbit in self.rabbits:
            rabbit.update(self.game_speed_multiplier)
        
        # Rimuovi conigli morti
        self.rabbits = [r for r in self.rabbits if r.alive]
        
        # Spawn nuovi conigli
        self.spawn_timer += 1
        if self.spawn_timer > 180 and len(self.rabbits) < 8:  # Ogni 3 secondi
            self.spawn_rabbit()
            self.spawn_timer = 0
    
    def draw_menu(self):
        self.screen.fill(DARK_GREEN)
        
        # Titolo
        title = self.font_large.render("🐰 RABBIT SHOOTER", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Sottotitolo
        subtitle = self.font_medium.render("Spara ai conigli! Velocità aumenta ogni 150 punti!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Record
        high_score_text = self.font_medium.render(f"Record: {self.high_score}", True, GOLD)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Istruzioni
        instructions = [
            "CLICCA sui conigli per sparare!",
            "Conigli Marroni: 10 punti",
            "Conigli Verdi: 20 punti", 
            "Conigli Viola: 30 punti",
            "Conigli Dorati: 50 punti",
            "",
            "Premi SPAZIO per iniziare"
        ]
        
        for i, instruction in enumerate(instructions):
            color = WHITE if instruction != "" else WHITE
            text = self.font_small.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 30))
            self.screen.blit(text, text_rect)
    
    def draw_game(self):
        self.screen.fill(DARK_GREEN)
        
        # Disegna griglia 8-bit
        for x in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (0, 80, 0), (x, 60), (x, SCREEN_HEIGHT - 60), 1)
        for y in range(60, SCREEN_HEIGHT - 60, 40):
            pygame.draw.line(self.screen, (0, 80, 0), (0, y), (SCREEN_WIDTH, y), 1)
        
        # HUD
        score_text = self.font_medium.render(f"Punteggio: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (20, 20))
        
        time_text = self.font_medium.render(f"Tempo: {int(self.time_left)}s", True, RED)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(time_text, time_rect)
        
        speed_text = self.font_medium.render(f"Velocità: x{self.game_speed_multiplier:.1f}", True, BLUE)
        speed_rect = speed_text.get_rect()
        speed_rect.topright = (SCREEN_WIDTH - 20, 20)
        self.screen.blit(speed_text, speed_rect)
        
        # Disegna conigli
        for rabbit in self.rabbits:
            rabbit.draw(self.screen)
        
        # Disegna mirino
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, RED, (mouse_pos[0] - 10, mouse_pos[1]), (mouse_pos[0] + 10, mouse_pos[1]), 2)
        pygame.draw.line(self.screen, RED, (mouse_pos[0], mouse_pos[1] - 10), (mouse_pos[0], mouse_pos[1] + 10), 2)
    
    def draw_game_over(self):
        self.screen.fill((40, 0, 0))  # Rosso scuro
        
        # Game Over
        game_over_text = self.font_large.render("GAME OVER!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Punteggio finale
        final_score_text = self.font_medium.render(f"Punteggio Finale: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(final_score_text, final_score_rect)
        
        # Record
        high_score_text = self.font_medium.render(f"Record: {self.high_score}", True, GOLD)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, 320))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Nuovo record?
        if self.score >= self.high_score and self.score > 0:
            new_record_text = self.font_medium.render("🎉 NUOVO RECORD! 🎉", True, GREEN)
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH//2, 360))
            self.screen.blit(new_record_text, new_record_rect)
        
        # Istruzioni
        restart_text = self.font_small.render("Premi SPAZIO per rigiocare o ESC per uscire", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        while self.running:
            # Gestione eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_state == "menu" or self.game_state == "game_over":
                            self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        if self.game_state == "game_over":
                            self.game_state = "menu"
                        else:
                            self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Click sinistro
                        self.handle_click(event.pos)
            
            # Aggiornamento
            self.update()
            
            # Disegno
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.draw_game()
            elif self.game_state == "game_over":
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    print("🐰 Avvio Rabbit Shooter...")
    print("Assicurati di avere pygame installato: pip install pygame")
    
    try:
        game = Game()
        game.run()
    except pygame.error as e:
        print(f"Errore pygame: {e}")
        print("Installa pygame con: pip install pygame")
    except KeyboardInterrupt:
        print("\nGioco interrotto dall'utente")
    except Exception as e:
        print(f"Errore inaspettato: {e}")

if __name__ == "__main__":
    main()