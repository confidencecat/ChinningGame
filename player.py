import pygame
import cv2
import mediapipe as mp
import numpy as np
from config import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
        try:
            original_bird = pygame.image.load(BIRD_IMAGE)
            self.image = pygame.transform.scale(original_bird, (PLAYER_SIZE, PLAYER_SIZE))
        except:
            self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.image.fill(YELLOW)
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.cap = None
        self.camera_active = False
        
        self.shoulder_center_y = GAME_HEIGHT // 2
        self.pose_detected = False
        
    def init_camera(self, camera_index=0):
        try:
            self.cap = cv2.VideoCapture(camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.camera_active = True
            return True
        except:
            print(f"Failed to initialize camera {camera_index}")
            return False
    
    def update_pose(self):
        if not self.camera_active or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            
            screen_y = int(shoulder_center_y * GAME_HEIGHT)
            
            if self.pose_detected:
                self.shoulder_center_y = self.shoulder_center_y * 0.8 + screen_y * 0.2
            else:
                self.shoulder_center_y = screen_y
                self.pose_detected = True
            
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            center_x = int(shoulder_center_x * CAMERA_WIDTH)
            center_y = int(shoulder_center_y * CAMERA_HEIGHT)
            cv2.circle(frame, (center_x, center_y), 10, (0, 255, 0), -1)
        else:
            self.pose_detected = False
            
        return frame
    
    def update(self):
        if self.pose_detected:
            target_y = self.shoulder_center_y
            self.y = self.y * 0.9 + target_y * 0.1
        else:
            self.velocity += GRAVITY
            self.y += self.velocity
        
        if self.y < 0:
            self.y = 0
            self.velocity = 0
        elif self.y > GAME_HEIGHT - PLAYER_SIZE:
            self.y = GAME_HEIGHT - PLAYER_SIZE
            self.velocity = 0
            
        self.rect.y = int(self.y)
    
    def jump(self):
        if not self.pose_detected:
            self.velocity = JUMP_STRENGTH
    
    def draw(self, screen):
        shadow_offset = 3
        shadow_rect = pygame.Rect(self.x + shadow_offset, int(self.y) + shadow_offset, PLAYER_SIZE, PLAYER_SIZE)
        pygame.draw.ellipse(screen, (50, 50, 50, 100), shadow_rect)
        
        angle = max(-30, min(30, self.velocity * 3))
        rotated_image = pygame.transform.rotate(self.image, angle)
        rotated_rect = rotated_image.get_rect(center=(self.x + PLAYER_SIZE//2, int(self.y) + PLAYER_SIZE//2))
        screen.blit(rotated_image, rotated_rect)
        
        if hasattr(self, 'flap_animation'):
            self.flap_animation += 1
        else:
            self.flap_animation = 0
            
        if self.flap_animation % 20 < 10:
            wing_color = (255, 255, 255, 150)
            wing_points = [
                (self.x - 10, int(self.y) + PLAYER_SIZE//2),
                (self.x - 5, int(self.y) + PLAYER_SIZE//2 - 8),
                (self.x + 5, int(self.y) + PLAYER_SIZE//2 - 5),
                (self.x, int(self.y) + PLAYER_SIZE//2 + 5)
            ]
            pygame.draw.polygon(screen, WHITE, wing_points)
        
        indicator_x, indicator_y = 50, 50
        
        pygame.draw.circle(screen, WHITE, (indicator_x, indicator_y), 20)
        pygame.draw.circle(screen, BLACK, (indicator_x, indicator_y), 20, 3)
        
        if self.pose_detected:
            pygame.draw.circle(screen, LIME_GREEN, (indicator_x, indicator_y), 15)
            check_points = [
                (indicator_x - 6, indicator_y),
                (indicator_x - 2, indicator_y + 4),
                (indicator_x + 6, indicator_y - 4)
            ]
            pygame.draw.lines(screen, WHITE, False, check_points, 3)
        else:
            pygame.draw.circle(screen, RED, (indicator_x, indicator_y), 15)
            pygame.draw.line(screen, WHITE, (indicator_x - 6, indicator_y - 6), (indicator_x + 6, indicator_y + 6), 3)
            pygame.draw.line(screen, WHITE, (indicator_x + 6, indicator_y - 6), (indicator_x - 6, indicator_y + 6), 3)
        
    def cleanup(self):
        if self.cap:
            self.cap.release()
