"""
Main entry point for the Pysnake Break game.
Initializes and runs the game, managing the game loop and core components.
"""
import pygame
import sys
import json
import os
import random
from snake import Snake  # Import the Snake class
from brick import Brick  # Import the Brick class
from ball import Ball  # Import the Ball class
from powerup import PowerUp, POWER_UP_TYPES, POWER_UP_SPEED # Import PowerUp related items
from levels import ALL_LEVELS, BRICK_CONFIG # Import level data

# Constants
HIGH_SCORES_FILENAME = "high_scores.json"
MAX_HIGH_SCORES = 5
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30  # Increase FPS a bit for smoother ball movement
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Ball color

# Brick constants
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_PADDING = 5
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = 50
# BRICK_ROWS and BRICK_COLS are now effectively determined by level data

# Ball constants
BALL_RADIUS = 10
BALL_SPEED_X_INITIAL = 4
BALL_SPEED_Y_INITIAL = -4

# Snake movement control
SNAKE_MOVE_INTERVAL = 5  # Move snake every 5 game frames


class Game:
    """
    Encapsulates the entire game state, logic, and main loop for Pysnake Break.

    Manages game initialization, event handling, updates to game objects,
    drawing objects to the screen, and game over conditions.
    """
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"
    HIGH_SCORES_SCREEN = "high_scores_screen"
    LEVEL_SELECTION = "level_selection"

    def __init__(self, width, height, fps):
        """
        Initializes the Game object, Pygame, screen, and game state.
        """
        self.screen_width = width
        self.screen_height = height
        self.fps = fps

        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Pysnake Break")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 74)
        self.restart_font = pygame.font.Font(None, 50)
        self.title_font = pygame.font.Font(None, 90)
        self.menu_option_font = pygame.font.Font(None, 50)

        self.player_snake = None
        self.all_bricks = pygame.sprite.Group()
        self.game_ball = None
        self.power_ups = pygame.sprite.Group()
        
        self.game_over = False
        self.score = 0
        self.snake_move_counter = 0
        
        self.game_state = Game.MAIN_MENU
        self.running = True
        self.previous_game_state = None
        self.high_scores = []
        self.power_up_active = {}
        self.POWER_UP_DURATION = 300 
        self.current_level_index = 0
        
        self.level_selection_rects = {} # For mouse clicks in level selection

        self._load_high_scores()
        # Load initial level structure (level 0) but stay in MAIN_MENU
        self._load_level(load_specific_index=0) 

    def _load_high_scores(self):
        """Loads high scores from the JSON file."""
        if os.path.exists(HIGH_SCORES_FILENAME):
            try:
                with open(HIGH_SCORES_FILENAME, 'r') as f:
                    self.high_scores = json.load(f)
                    if not isinstance(self.high_scores, list): self.high_scores = []
                    self.high_scores = [
                        entry for entry in self.high_scores if isinstance(entry.get("score"), int)
                    ]
                    self.high_scores.sort(key=lambda x: x.get("score", 0), reverse=True)
            except (json.JSONDecodeError, IOError):
                self.high_scores = []
        else:
            self.high_scores = []

    def _save_high_scores(self):
        """Saves the current high scores to the JSON file."""
        try:
            with open(HIGH_SCORES_FILENAME, 'w') as f:
                json.dump(self.high_scores, f, indent=4)
        except IOError:
            print(f"Error: Could not save high scores to {HIGH_SCORES_FILENAME}")

    def _prepare_game_elements(self):
        """Resets positions/states of game elements like snake, ball, power-ups.
           Called when a level (re)starts. Score is handled by caller."""
        snake_start_x = self.screen_width // 2
        snake_start_y = self.screen_height - 50
        if self.player_snake:
            self.player_snake.reset(snake_start_x, snake_start_y)
        else:
            self.player_snake = Snake(snake_start_x, snake_start_y, color=GREEN)

        ball_start_x = self.screen_width // 2
        ball_start_y = self.player_snake.body[0].top - BALL_RADIUS - 5
        if self.game_ball:
            self.game_ball.reset(ball_start_x, ball_start_y)
        else:
            self.game_ball = Ball(
                ball_start_x, ball_start_y, BALL_RADIUS, YELLOW,
                BALL_SPEED_X_INITIAL, BALL_SPEED_Y_INITIAL)
        
        self.snake_move_counter = 0
        self.power_ups.empty()
        self.power_up_active.clear()
        # self.game_over is set by the method that calls _load_level or by game logic

    def _create_bricks_layout(self, level_data):
        """Creates bricks for the given level data."""
        bricks = pygame.sprite.Group()
        num_level_rows = len(level_data)
        num_level_cols = len(level_data[0]) if num_level_rows > 0 else 0

        total_bricks_width = num_level_cols * BRICK_WIDTH + (num_level_cols - 1) * BRICK_PADDING
        dynamic_offset_left = (self.screen_width - total_bricks_width) // 2
        
        for row_idx, row_str in enumerate(level_data):
            for col_idx, char_code in enumerate(row_str):
                if char_code == ' ': continue
                brick_props = BRICK_CONFIG.get(char_code)
                if not brick_props:
                    print(f"Warning: Unknown brick code '{char_code}'. Skipping.")
                    continue

                x = dynamic_offset_left + col_idx * (BRICK_WIDTH + BRICK_PADDING)
                y = BRICK_OFFSET_TOP + row_idx * (BRICK_HEIGHT + BRICK_PADDING)
                color = brick_props['color']
                power_up_type = random.choice(POWER_UP_TYPES) if random.random() < brick_props.get('power_up_chance', 0.0) else None
                bricks.add(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, color, power_up_type))
        return bricks

    def _load_level(self, load_specific_index=-1):
        """Loads a specific level by index, or the next level.
           If load_specific_index is -1, it loads the next level (advancing).
           Resets game elements, sets game_over to False. Score is NOT managed here.
        """
        if load_specific_index != -1:
            self.current_level_index = load_specific_index
        else:  # Advance to next level
            self.current_level_index += 1

        if self.current_level_index >= len(ALL_LEVELS):
            print("All levels completed! Looping back to Level 1.")
            self.current_level_index = 0 
            # Could transition to a "YOU_WIN" state or MAIN_MENU. For now, loops.

        current_level_data = ALL_LEVELS[self.current_level_index]
        self.all_bricks = self._create_bricks_layout(current_level_data)
        self._prepare_game_elements()
        self.game_over = False 

    def _setup_specific_level(self, level_idx):
        """Prepares a specific level, resets score, and sets state to PLAYING."""
        self.score = 0 
        self._load_level(load_specific_index=level_idx)
        self.game_state = Game.PLAYING

    def reset_game(self):
        """Resets game to Level 1, score 0, and sets state to PLAYING."""
        self.score = 0 
        self._load_level(load_specific_index=0)
        self.game_state = Game.PLAYING

    def _draw_main_menu(self, surface):
        surface.fill(BLACK)
        title = self.title_font.render("Pysnake Break", True, WHITE)
        surface.blit(title, title.get_rect(center=(self.screen_width // 2, self.screen_height // 4)))
        
        options = [("1. Start Game", 0), ("2. High Scores", 50), 
                   ("3. Select Level", 100), ("4. Quit", 150)]
        for text, offset_y in options:
            item = self.menu_option_font.render(text, True, WHITE)
            surface.blit(item, item.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + offset_y)))

    def _handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: self.reset_game()
            elif event.key == pygame.K_2: self.game_state = Game.HIGH_SCORES_SCREEN
            elif event.key == pygame.K_3: self.game_state = Game.LEVEL_SELECTION
            elif event.key == pygame.K_4: self.running = False
    
    def _draw_level_selection_screen(self, surface):
        surface.fill(BLACK)
        title = self.title_font.render("Select Level", True, WHITE)
        surface.blit(title, title.get_rect(center=(self.screen_width // 2, self.screen_height // 8)))

        level_font = self.menu_option_font
        start_y = self.screen_height // 4 + 30
        line_height = 50
        items_per_row = 5
        self.level_selection_rects.clear()

        for i, _ in enumerate(ALL_LEVELS):
            level_num_str = f"{i + 1}"
            row, col = divmod(i, items_per_row)
            item_width = self.screen_width // (items_per_row + 1)
            x_pos = (col + 1) * item_width
            y_pos = start_y + row * line_height
            
            text_surface = level_font.render(level_num_str, True, WHITE)
            text_rect = text_surface.get_rect(center=(x_pos, y_pos))
            surface.blit(text_surface, text_rect)
            self.level_selection_rects[i] = text_rect # Store by index

        return_msg = self.font.render("ESC or M for Main Menu", True, WHITE)
        surface.blit(return_msg, return_msg.get_rect(center=(self.screen_width // 2, self.screen_height - 50)))

    def _handle_level_selection_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                self.game_state = Game.MAIN_MENU
            else:
                level_idx = -1
                if pygame.K_1 <= event.key <= pygame.K_9: level_idx = event.key - pygame.K_1
                elif event.key == pygame.K_0 and len(ALL_LEVELS) >= 10: level_idx = 9 
                
                if 0 <= level_idx < len(ALL_LEVELS):
                    self._setup_specific_level(level_idx)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in self.level_selection_rects.items():
                if rect.collidepoint(event.pos):
                    self._setup_specific_level(idx)
                    break

    def _draw_pause_menu(self, surface):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0,0))
        title = self.title_font.render("Paused", True, WHITE)
        surface.blit(title, title.get_rect(center=(self.screen_width // 2, self.screen_height // 4)))
        options = [("1. Resume (P/ESC)", -30), ("2. Restart Level", 30), ("3. Main Menu", 90)]
        for text, offset_y in options:
            item = self.menu_option_font.render(text, True, WHITE)
            surface.blit(item, item.get_rect(center=(self.screen_width//2, self.screen_height//2 + offset_y)))

    def _handle_pause_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_p, pygame.K_ESCAPE]:
                self.game_state = self.previous_game_state or Game.PLAYING
            elif event.key == pygame.K_2: # Restart current level
                current_score, current_idx = self.score, self.current_level_index
                self._load_level(load_specific_index=current_idx)
                self.score = current_score # Preserve score
                self.game_state = Game.PLAYING
            elif event.key == pygame.K_3: # Go to Main Menu
                self.game_state = Game.MAIN_MENU
                self._load_level(load_specific_index=0) # Prepare for potential new game

    def _activate_power_up(self, power_up_type):
        if power_up_type == "wider_paddle": self.player_snake.grow(2)
        elif power_up_type == "slow_ball":
            if not self.power_up_active.get("slow_ball", 0) > 0:
                if not hasattr(self.game_ball, 'original_speed_x'):
                    self.game_ball.original_speed_x = self.game_ball.speed_x
                    self.game_ball.original_speed_y = self.game_ball.speed_y
                self.game_ball.speed_x //= 2
                self.game_ball.speed_y //= 2
                if self.game_ball.speed_x == 0 and self.game_ball.original_speed_x != 0: self.game_ball.speed_x = 1 if self.game_ball.original_speed_x > 0 else -1
                if self.game_ball.speed_y == 0 and self.game_ball.original_speed_y != 0: self.game_ball.speed_y = 1 if self.game_ball.original_speed_y > 0 else -1
            self.power_up_active["slow_ball"] = self.POWER_UP_DURATION

    def _deactivate_power_up(self, power_up_type):
        if power_up_type == "slow_ball" and hasattr(self.game_ball, 'original_speed_x'):
            self.game_ball.speed_x = self.game_ball.original_speed_x
            self.game_ball.speed_y = self.game_ball.original_speed_y
            del self.game_ball.original_speed_x, self.game_ball.original_speed_y

    def _update_power_up_effects(self):
        for type, duration in list(self.power_up_active.items()):
            if duration > 0: self.power_up_active[type] -= 1
            else:
                self._deactivate_power_up(type)
                del self.power_up_active[type]

    def _check_and_add_high_score(self, current_score):
        self.high_scores.append({"name": "PLY", "score": current_score})
        self.high_scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.high_scores = self.high_scores[:MAX_HIGH_SCORES]
        self._save_high_scores()

    def _draw_high_scores_screen(self, surface):
        surface.fill(BLACK)
        title = self.title_font.render("High Scores", True, WHITE)
        surface.blit(title, title.get_rect(center=(self.screen_width // 2, self.screen_height // 8)))
        start_y, line_height = self.screen_height // 4 + 50, 40
        if not self.high_scores:
            no_scores = self.menu_option_font.render("No high scores yet!", True, WHITE)
            surface.blit(no_scores, no_scores.get_rect(center=(self.screen_width // 2, start_y)))
        else:
            for i, entry in enumerate(self.high_scores):
                text = f"{i+1}. {entry.get('name','N/A')} - {entry.get('score',0)}"
                item = self.menu_option_font.render(text, True, WHITE)
                surface.blit(item, item.get_rect(center=(self.screen_width//2, start_y + i * line_height)))
        return_msg = self.font.render("ESC or M for Main Menu", True, WHITE)
        surface.blit(return_msg, return_msg.get_rect(center=(self.screen_width//2, self.screen_height - 50)))

    def _handle_high_scores_input(self, event):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_m]:
            self.game_state = Game.MAIN_MENU

    def handle_input(self, event):
        if event.type == pygame.QUIT: self.running = False; return

        if self.game_state == Game.MAIN_MENU: self._handle_menu_input(event)
        elif self.game_state == Game.LEVEL_SELECTION: self._handle_level_selection_input(event)
        elif self.game_state == Game.HIGH_SCORES_SCREEN: self._handle_high_scores_input(event)
        elif self.game_state == Game.PAUSED: self._handle_pause_input(event)
        elif self.game_state == Game.PLAYING:
            if self.game_over: # This is the brief period after snake dies before state changes to GAME_OVER
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game()
            else:
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_p, pygame.K_ESCAPE]:
                    self.previous_game_state = self.game_state
                    self.game_state = Game.PAUSED
                else: self.player_snake.handle_input(event)
        elif self.game_state == Game.GAME_OVER: # Dedicated GAME_OVER screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game()

    def update(self):
        if self.game_state == Game.PLAYING and not self.game_over:
            self.snake_move_counter += 1
            if self.snake_move_counter >= SNAKE_MOVE_INTERVAL:
                self.player_snake.move()
                self.snake_move_counter = 0
            
            self.power_ups.update(self.screen_height)
            head_rect = self.player_snake.body[0]
            for power_up in list(self.power_ups):
                if head_rect.colliderect(power_up.rect):
                    self._activate_power_up(power_up.type)
                    power_up.kill()
            self._update_power_up_effects()

            points, spawned_pus = self.game_ball.update(
                self.screen_width, self.screen_height, self.player_snake.body, self.all_bricks)
            for pu in spawned_pus: self.power_ups.add(pu)
            self.score += points
            
            if not any(b.is_active for b in self.all_bricks) and self.all_bricks:
                print(f"Level {self.current_level_index + 1} cleared!")
                self._load_level() # Advance to next level
                return 

            if self.player_snake.check_collision_self() or \
               self.player_snake.check_collision_walls(self.screen_width, self.screen_height) or \
               self.game_ball.rect.top > self.screen_height:
                self.game_over = True
                self.game_state = Game.GAME_OVER
                self._check_and_add_high_score(self.score)

    def draw(self):
        if self.game_state == Game.MAIN_MENU: self._draw_main_menu(self.screen)
        elif self.game_state == Game.LEVEL_SELECTION: self._draw_level_selection_screen(self.screen)
        elif self.game_state == Game.HIGH_SCORES_SCREEN: self._draw_high_scores_screen(self.screen)
        elif self.game_state in [Game.PLAYING, Game.GAME_OVER, Game.PAUSED]:
            self.screen.fill(BLACK)
            self.player_snake.draw(self.screen)
            self.all_bricks.draw(self.screen)
            self.game_ball.draw(self.screen)
            self.power_ups.draw(self.screen)
            
            score_display = f"Score: {self.score}  Level: {self.current_level_index + 1}"
            score_text = self.font.render(score_display, True, WHITE)
            self.screen.blit(score_text, (10, 10))

            if self.game_state == Game.GAME_OVER:
                msg = self.game_over_font.render("GAME OVER", True, RED)
                self.screen.blit(msg, msg.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50)))
                restart_msg = self.restart_font.render("Press 'R' to Restart", True, WHITE)
                self.screen.blit(restart_msg, restart_msg.get_rect(center=(self.screen_width//2, self.screen_height//2 + 50)))
            elif self.game_state == Game.PAUSED:
                self._draw_pause_menu(self.screen)
        
        pygame.display.flip()
        self.clock.tick(self.fps)

def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS)
    while game.running:
        for event in pygame.event.get():
            game.handle_input(event)
        game.update()
        game.draw()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

[end of main.py]
