import pygame
import cv2
import json
import sys
import argparse
import math
import random
from datetime import datetime
from config import *
from player import Player
from pipe import Pipe

class Game:
    def __init__(self, camera_index=0):
        pygame.init()
        
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Chin-up Flappy Bird")
        self.clock = pygame.time.Clock()
        
        try:
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        except:
            self.font_large = pygame.font.SysFont('Arial', FONT_SIZE_LARGE, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', FONT_SIZE_MEDIUM, bold=True)
            self.font_small = pygame.font.SysFont('Arial', FONT_SIZE_SMALL)
        
        self.state = LOBBY
        self.running = True
        
        self.player = Player(PLAYER_X, GAME_HEIGHT // 2)
        self.camera_index = camera_index
        
        self.pipes = []
        self.last_pipe_time = pygame.time.get_ticks()
        self.current_speed = PIPE_SPEED
        
        self.score = 0
        self.best_score = 0
        
        self.user_id = ""
        self.input_active = True
        
        self.rankings = self.load_rankings()
        
        self.cv_window_name = "Chin-up Detection"
        
        self.particles = []
        self.screen_shake = 0
        self.background_offset = 0
        self.score_saved = False
        
    def load_rankings(self):
        try:
            with open(RANKING_FILE, 'r') as f:
                rankings = json.load(f)
                return sorted(rankings, key=lambda x: x['score'], reverse=True)
        except:
            return []
    
    def save_ranking(self, user_id, score):
        new_entry = {
            'id': user_id,
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.rankings.append(new_entry)
        
        self.rankings = sorted(self.rankings, key=lambda x: x['score'], reverse=True)[:10]
        
        try:
            with open(RANKING_FILE, 'w') as f:
                json.dump(self.rankings, f, indent=2)
        except Exception as e:
            print(f"Failed to save rankings: {e}")
    
    def reset_game(self):
        self.pipes = []
        self.score = 0
        self.current_speed = PIPE_SPEED
        self.player.y = GAME_HEIGHT // 2
        self.player.velocity = 0
        self.last_pipe_time = pygame.time.get_ticks()
        self.score_saved = False
    
    def spawn_pipe(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > PIPE_SPAWN_TIME:
            self.pipes.append(Pipe(GAME_WIDTH))
            self.last_pipe_time = current_time
    
    def update_pipes(self):
        for pipe in self.pipes[:]:
            pipe.update(self.current_speed)
            
            if pipe.check_passed(self.player.x):
                self.score += 1
                self.current_speed += SPEED_INCREASE
                
                self.create_particle_effect(
                    pipe.x + PIPE_WIDTH // 2, 
                    GAME_HEIGHT // 2, 
                    GOLD, 
                    8
                )
                
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
    
    def check_collisions(self):
        if self.player.y <= 0 or self.player.y >= GAME_HEIGHT - PLAYER_SIZE:
            return True
            
        for pipe in self.pipes:
            if pipe.check_collision(self.player.rect):
                return True
                
        return False
    
    def draw_gradient_background(self):
        for y in range(GAME_HEIGHT):
            ratio = y / GAME_HEIGHT
            r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
            g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
            b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (GAME_WIDTH, y))
    
    def draw_clouds(self):
        cloud_positions = [
            (100 + self.background_offset * 0.2, 80),
            (300 + self.background_offset * 0.3, 120),
            (500 + self.background_offset * 0.1, 60),
            (700 + self.background_offset * 0.25, 100)
        ]
        
        for x, y in cloud_positions:
            x = x % (GAME_WIDTH + 200) - 100
            self.draw_cloud(x, y)
    
    def draw_cloud(self, x, y):
        cloud_color = (255, 255, 255, 180)
        pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), 30)
        pygame.draw.circle(self.screen, WHITE, (int(x + 25), int(y - 10)), 25)
        pygame.draw.circle(self.screen, WHITE, (int(x - 25), int(y - 5)), 20)
        pygame.draw.circle(self.screen, WHITE, (int(x + 10), int(y + 15)), 18)
        pygame.draw.circle(self.screen, WHITE, (int(x - 10), int(y + 10)), 22)
    
    def create_particle_effect(self, x, y, color, count=5):
        import random
        for _ in range(count):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vx': random.randint(-5, 5),
                'vy': random.randint(-8, -2),
                'color': color,
                'life': 30
            }
            self.particles.append(particle)
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 30))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(self.screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 3)
    
    def handle_lobby_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.user_id = self.user_id[:-1]
            elif event.key == pygame.K_RETURN:
                if len(self.user_id) == MAX_ID_LENGTH:
                    self.state = PLAYING
                    self.reset_game()
                    if not self.player.init_camera(self.camera_index):
                        print("Camera initialization failed")
            elif event.unicode.isalnum() and len(self.user_id) < MAX_ID_LENGTH:
                self.user_id += event.unicode.upper()
    
    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_ESCAPE:
                self.state = LOBBY
                self.player.cleanup()
                cv2.destroyAllWindows()
    
    def handle_gameover_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.state = PLAYING
                self.reset_game()
                if not self.player.init_camera(self.camera_index):
                    print("Camera initialization failed")
            elif event.key == pygame.K_ESCAPE:
                self.state = LOBBY
                self.user_id = ""
                cv2.destroyAllWindows()
    
    def draw_lobby(self):
        self.draw_gradient_background()
        self.draw_clouds()
        
        title_text = "CHIN-UP FLAPPY BIRD"
        
        for offset in range(8, 0, -2):
            glow_color = (255, 255, 255, 50)
            glow_surface = self.font_large.render(title_text, True, GOLD)
            glow_rect = glow_surface.get_rect(center=(GAME_WIDTH // 2 + offset//2, 120 + offset//2))
            self.screen.blit(glow_surface, glow_rect)
        
        title = self.font_large.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Use chin-ups to control the bird!", True, CYAN)
        subtitle_rect = subtitle.get_rect(center=(GAME_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        input_y = 280
        
        label_text = "ENTER YOUR ID (5 CHARACTERS):"
        label = self.font_medium.render(label_text, True, WHITE)
        label_rect = label.get_rect(center=(GAME_WIDTH // 2, input_y))
        self.screen.blit(label, label_rect)
        
        input_box = pygame.Rect(GAME_WIDTH // 2 - 150, input_y + 50, 300, 60)
        
        shadow_box = pygame.Rect(input_box.x + 3, input_box.y + 3, input_box.width, input_box.height)
        pygame.draw.rect(self.screen, DARK_GRAY, shadow_box, border_radius=10)
        
        pygame.draw.rect(self.screen, WHITE, input_box, border_radius=10)
        pygame.draw.rect(self.screen, GOLD, input_box, 4, border_radius=10)
        
        char_width = 45
        start_x = input_box.centerx - (MAX_ID_LENGTH * char_width) // 2
        
        for i in range(MAX_ID_LENGTH):
            char_rect = pygame.Rect(start_x + i * char_width, input_box.y + 5, char_width - 2, input_box.height - 10)
            
            if i < len(self.user_id):
                pygame.draw.rect(self.screen, LIME_GREEN, char_rect, border_radius=5)
                char_text = self.font_medium.render(self.user_id[i], True, BLACK)
            else:
                pygame.draw.rect(self.screen, LIGHT_GRAY, char_rect, border_radius=5)
                pygame.draw.rect(self.screen, GRAY, char_rect, 2, border_radius=5)
                char_text = self.font_medium.render("_", True, GRAY)
                
            char_text_rect = char_text.get_rect(center=char_rect.center)
            self.screen.blit(char_text, char_text_rect)
        
        instruction_y = input_y + 120
        
        if len(self.user_id) == MAX_ID_LENGTH:
            time_factor = pygame.time.get_ticks() * 0.005
            pulse_scale = 1.0 + 0.1 * abs(math.sin(time_factor))
            instruction_text = "PRESS ENTER TO START!"
            instruction_color = LIME_GREEN
            
            scaled_font = pygame.font.Font(None, int(FONT_SIZE_MEDIUM * pulse_scale))
            instruction = scaled_font.render(instruction_text, True, instruction_color)
        else:
            remaining = MAX_ID_LENGTH - len(self.user_id)
            instruction_text = f"Enter {remaining} more character{'s' if remaining > 1 else ''}"
            instruction = self.font_small.render(instruction_text, True, WHITE)
            
        instruction_rect = instruction.get_rect(center=(GAME_WIDTH // 2, instruction_y))
        self.screen.blit(instruction, instruction_rect)
        
        self.draw_fancy_rankings(GAME_WIDTH - 160, 250)
    
    def draw_game(self):
        self.background_offset -= self.current_speed * 0.5
        
        self.draw_gradient_background()
        self.draw_clouds()
        
        self.update_particles()
        self.draw_particles()
        
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        self.player.draw(self.screen)
        
        score_bg = pygame.Rect(20, 20, 300, 55)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), score_bg, border_radius=12)
        pygame.draw.rect(self.screen, GOLD, score_bg, 4, border_radius=12)
        
        score_text = self.font_large.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (30, 30))
        
        speed_bg = pygame.Rect(20, 85, 250, 45)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), speed_bg, border_radius=10)
        pygame.draw.rect(self.screen, ORANGE, speed_bg, 3, border_radius=10)
        
        speed_text = self.font_medium.render(f"Speed: {self.current_speed:.1f}", True, WHITE)
        self.screen.blit(speed_text, (30, 95))
        
        id_bg = pygame.Rect(20, 140, 280, 45)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), id_bg, border_radius=8)
        pygame.draw.rect(self.screen, CYAN, id_bg, 3, border_radius=8)
        
        id_text = self.font_medium.render(f"Player: {self.user_id}", True, WHITE)
        self.screen.blit(id_text, (30, 150))
        
        pose_bg = pygame.Rect(20, 190, 280, 45)
        if self.player.pose_detected:
            pygame.draw.rect(self.screen, (0, 100, 0, 150), pose_bg, border_radius=8)
            pygame.draw.rect(self.screen, LIME_GREEN, pose_bg, 3, border_radius=8)
            pose_text = self.font_medium.render("Pose: ACTIVE", True, LIME_GREEN)
        else:
            pygame.draw.rect(self.screen, (100, 0, 0, 150), pose_bg, border_radius=8)
            pygame.draw.rect(self.screen, RED, pose_bg, 3, border_radius=8)
            pose_text = self.font_medium.render("Pose: LOST", True, RED)
        
        self.screen.blit(pose_text, (30, 200))
        
        instruction_bg = pygame.Rect(0, GAME_HEIGHT - 60, GAME_WIDTH, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), instruction_bg)
        
        instruction = self.font_medium.render("Use chin-ups to control the bird! Press ESC to quit", True, WHITE)
        instruction_rect = instruction.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 30))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_gameover(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        overlay.set_alpha(200)
        for y in range(GAME_HEIGHT):
            darkness = int(50 + (y / GAME_HEIGHT) * 100)
            pygame.draw.line(overlay, (darkness, 0, 0), (0, y), (GAME_WIDTH, y))
        self.screen.blit(overlay, (0, 0))
        
        time_factor = pygame.time.get_ticks() * 0.003
        
        for offset in range(5, 0, -1):
            shadow_alpha = int(100 - offset * 15)
            game_over_shadow = self.font_large.render("GAME OVER", True, (shadow_alpha, 0, 0))
            shadow_rect = game_over_shadow.get_rect(center=(GAME_WIDTH // 2 + offset, 120 + offset))
            self.screen.blit(game_over_shadow, shadow_rect)
        
        pulse = 1.0 + 0.2 * math.sin(time_factor)
        scaled_font = pygame.font.Font(None, int(FONT_SIZE_LARGE * pulse))
        game_over = scaled_font.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(GAME_WIDTH // 2, 120))
        self.screen.blit(game_over, game_over_rect)
        
        panel_rect = pygame.Rect(GAME_WIDTH // 2 - 200, 180, 400, 200)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, GOLD, panel_rect, 4, border_radius=20)
        
        final_score_text = f"FINAL SCORE: {self.score}"
        final_score = self.font_medium.render(final_score_text, True, GOLD)
        final_score_rect = final_score.get_rect(center=(GAME_WIDTH // 2, 220))
        self.screen.blit(final_score, final_score_rect)
        
        player_text = f"PLAYER: {self.user_id}"
        player = self.font_medium.render(player_text, True, CYAN)
        player_rect = player.get_rect(center=(GAME_WIDTH // 2, 260))
        self.screen.blit(player, player_rect)
        
        if self.score >= 10:
            message = "AMAZING PERFORMANCE!"
            color = GOLD
        elif self.score >= 5:
            message = "GREAT JOB!"
            color = LIME_GREEN
        else:
            message = "KEEP PRACTICING!"
            color = WHITE
            
        message_surface = self.font_small.render(message, True, color)
        message_rect = message_surface.get_rect(center=(GAME_WIDTH // 2, 300))
        self.screen.blit(message_surface, message_rect)
        
        controls_y = 400
        control_bg = pygame.Rect(GAME_WIDTH // 2 - 180, controls_y - 20, 360, 60)
        
        border_color = [int(128 + 127 * math.sin(time_factor + i)) for i in range(3)]
        pygame.draw.rect(self.screen, (0, 0, 0, 150), control_bg, border_radius=15)
        pygame.draw.rect(self.screen, border_color, control_bg, 3, border_radius=15)
        
        restart_text = "Press R to RESTART"
        restart = self.font_small.render(restart_text, True, LIME_GREEN)
        restart_rect = restart.get_rect(center=(GAME_WIDTH // 2, controls_y))
        self.screen.blit(restart, restart_rect)
        
        lobby_text = "Press ESC for LOBBY"
        lobby = self.font_small.render(lobby_text, True, ORANGE)
        lobby_rect = lobby.get_rect(center=(GAME_WIDTH // 2, controls_y + 25))
        self.screen.blit(lobby, lobby_rect)
        
        self.draw_fancy_rankings(GAME_WIDTH - 160, 150)
    
    def draw_fancy_rankings(self, x, y):
        panel_width = 280
        panel_height = 400
        panel_rect = pygame.Rect(x - panel_width//2, y, panel_width, panel_height)
        
        for i in range(panel_height):
            ratio = i / panel_height
            r = int(20 * (1 - ratio) + 50 * ratio)
            g = int(20 * (1 - ratio) + 50 * ratio)
            b = int(60 * (1 - ratio) + 100 * ratio)
            pygame.draw.line(self.screen, (r, g, b), 
                           (panel_rect.left, panel_rect.top + i), 
                           (panel_rect.right, panel_rect.top + i))
        
        pygame.draw.rect(self.screen, GOLD, panel_rect, 4, border_radius=15)
        
        title_text = "TOP SCORES"
        title_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        title = title_font.render(title_text, True, GOLD)
        title_rect = title.get_rect(center=(x, y + 30))
        self.screen.blit(title, title_rect)
        
        for i, ranking in enumerate(self.rankings[:5]):
            rank_y = y + 100 + i * 50
            
            if i == 0:
                medal = "1ST"
                color = GOLD
            elif i == 1:
                medal = "2ND"
                color = SILVER
            elif i == 2:
                medal = "3RD"
                color = (205, 127, 50)
            else:
                medal = f"{i+1}TH"
                color = WHITE
            
            rank_bg = pygame.Rect(x - 130, rank_y - 8, 260, 35)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), rank_bg, border_radius=8)
            pygame.draw.rect(self.screen, color, rank_bg, 3, border_radius=8)
            
            medal_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            medal_text = medal_font.render(medal, True, color)
            self.screen.blit(medal_text, (x - 120, rank_y - 3))
            
            rank_text = f"{ranking['id']}: {ranking['score']}"
            text_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            text = text_font.render(rank_text, True, WHITE)
            self.screen.blit(text, (x - 50, rank_y - 3))
        
        if not self.rankings:
            no_data_font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            no_data = no_data_font.render("No scores yet!", True, WHITE)
            no_data_rect = no_data.get_rect(center=(x, y + 150))
            self.screen.blit(no_data, no_data_rect)
    
    def update_camera(self):
        frame = self.player.update_pose()
        if frame is not None:
            cv2.imshow(self.cv_window_name, frame)
            cv2.moveWindow(self.cv_window_name, GAME_WIDTH + 50, 50)
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif self.state == LOBBY:
                    self.handle_lobby_input(event)
                    
                elif self.state == PLAYING:
                    self.handle_game_input(event)
                    
                elif self.state == GAME_OVER:
                    self.handle_gameover_input(event)
            
            if self.state == PLAYING:
                self.update_camera()
                self.player.update()
                
                self.spawn_pipe()
                self.update_pipes()
                
                if self.check_collisions():
                    self.state = GAME_OVER
                    if not self.score_saved:
                        self.save_ranking(self.user_id, self.score)
                        self.rankings = self.load_rankings()
                        self.score_saved = True
                    self.player.cleanup()
                    cv2.destroyAllWindows()
            
            if self.state == LOBBY:
                self.draw_lobby()
            elif self.state == PLAYING:
                self.draw_game()
            elif self.state == GAME_OVER:
                self.draw_gameover()
            
            pygame.display.flip()
            self.clock.tick(60)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.player.cleanup()
        cv2.destroyAllWindows()
        pygame.quit()

def main():
    parser = argparse.ArgumentParser(description='Chin-up Flappy Bird Game')
    parser.add_argument('--cam', type=int, default=0, help='Camera index (default: 0)')
    args = parser.parse_args()
    
    game = Game(camera_index=args.cam)
    game.run()

if __name__ == "__main__":
    main()
