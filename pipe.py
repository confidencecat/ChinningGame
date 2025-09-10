import pygame
import random
from config import *

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, GAME_HEIGHT - PIPE_GAP - 100)
        self.width = PIPE_WIDTH
        self.passed = False
        
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.height)
        self.bottom_rect = pygame.Rect(
            self.x, 
            self.height + PIPE_GAP, 
            self.width, 
            GAME_HEIGHT - (self.height + PIPE_GAP)
        )
    
    def update(self, speed):
        self.x -= speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, screen):
        shadow_offset = 5
        shadow_top = pygame.Rect(self.x + shadow_offset, shadow_offset, self.width, self.height)
        shadow_bottom = pygame.Rect(
            self.x + shadow_offset, 
            self.height + PIPE_GAP + shadow_offset, 
            self.width, 
            GAME_HEIGHT - (self.height + PIPE_GAP)
        )
        pygame.draw.rect(screen, DARK_GRAY, shadow_top)
        pygame.draw.rect(screen, DARK_GRAY, shadow_bottom)
        
        for i in range(self.width):
            color_ratio = i / self.width
            r = int(PIPE_GREEN[0] * (1 - color_ratio) + PIPE_HIGHLIGHT[0] * color_ratio)
            g = int(PIPE_GREEN[1] * (1 - color_ratio) + PIPE_HIGHLIGHT[1] * color_ratio)
            b = int(PIPE_GREEN[2] * (1 - color_ratio) + PIPE_HIGHLIGHT[2] * color_ratio)
            pygame.draw.line(screen, (r, g, b), 
                           (self.x + i, 0), 
                           (self.x + i, self.height))
        
        for i in range(self.width):
            color_ratio = i / self.width
            r = int(PIPE_GREEN[0] * (1 - color_ratio) + PIPE_HIGHLIGHT[0] * color_ratio)
            g = int(PIPE_GREEN[1] * (1 - color_ratio) + PIPE_HIGHLIGHT[1] * color_ratio)
            b = int(PIPE_GREEN[2] * (1 - color_ratio) + PIPE_HIGHLIGHT[2] * color_ratio)
            pygame.draw.line(screen, (r, g, b), 
                           (self.x + i, self.height + PIPE_GAP), 
                           (self.x + i, GAME_HEIGHT))
        
        pygame.draw.rect(screen, PIPE_DARK, self.top_rect, 4)
        pygame.draw.rect(screen, PIPE_DARK, self.bottom_rect, 4)
        
        cap_height = 40
        cap_width = self.width + 20
        
        top_cap = pygame.Rect(
            self.x - 10, 
            self.height - cap_height, 
            cap_width, 
            cap_height
        )
        pygame.draw.rect(screen, PIPE_HIGHLIGHT, top_cap)
        pygame.draw.line(screen, WHITE, (top_cap.left, top_cap.top), (top_cap.right, top_cap.top), 3)
        pygame.draw.line(screen, WHITE, (top_cap.left, top_cap.top), (top_cap.left, top_cap.bottom), 3)
        pygame.draw.line(screen, PIPE_DARK, (top_cap.right-1, top_cap.top), (top_cap.right-1, top_cap.bottom), 3)
        pygame.draw.line(screen, PIPE_DARK, (top_cap.left, top_cap.bottom-1), (top_cap.right, top_cap.bottom-1), 3)
        
        bottom_cap = pygame.Rect(
            self.x - 10, 
            self.height + PIPE_GAP, 
            cap_width, 
            cap_height
        )
        pygame.draw.rect(screen, PIPE_HIGHLIGHT, bottom_cap)
        pygame.draw.line(screen, WHITE, (bottom_cap.left, bottom_cap.top), (bottom_cap.right, bottom_cap.top), 3)
        pygame.draw.line(screen, WHITE, (bottom_cap.left, bottom_cap.top), (bottom_cap.left, bottom_cap.bottom), 3)
        pygame.draw.line(screen, PIPE_DARK, (bottom_cap.right-1, bottom_cap.top), (bottom_cap.right-1, bottom_cap.bottom), 3)
        pygame.draw.line(screen, PIPE_DARK, (bottom_cap.left, bottom_cap.bottom-1), (bottom_cap.right, bottom_cap.bottom-1), 3)
        
        rivet_positions = [
            (self.x + self.width//4, self.height - cap_height//2),
            (self.x + 3*self.width//4, self.height - cap_height//2),
            (self.x + self.width//4, self.height + PIPE_GAP + cap_height//2),
            (self.x + 3*self.width//4, self.height + PIPE_GAP + cap_height//2)
        ]
        
        for pos in rivet_positions:
            pygame.draw.circle(screen, PIPE_DARK, pos, 4)
            pygame.draw.circle(screen, GRAY, pos, 3)
            pygame.draw.circle(screen, WHITE, (pos[0]-1, pos[1]-1), 2)
    
    def check_collision(self, player_rect):
        return (self.top_rect.colliderect(player_rect) or 
                self.bottom_rect.colliderect(player_rect))
    
    def is_off_screen(self):
        return self.x + self.width < 0
    
    def check_passed(self, player_x):
        if not self.passed and self.x + self.width < player_x:
            self.passed = True
            return True
        return False
