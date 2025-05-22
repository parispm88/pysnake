"""
Level Editor for Pysnake Break game.
Allows users to create and modify level layouts.
"""
import pygame
import sys
import os
from datetime import datetime # For timestamped filenames

# Adjust path to import from parent directory if levels.py is there
# This assumes editor.py is in the same root directory as levels.py and main.py
try:
    from levels import BRICK_CONFIG
except ImportError:
    print("Warning: levels.py not found or BRICK_CONFIG missing. Using default editor config.")
    # Define a simplified BRICK_CONFIG if levels.py is not accessible
    # Ensure this matches or is compatible with the game's BRICK_CONFIG
    BRICK_CONFIG = {
        'S': {'color': (0, 0, 255), 'editor_char': 'S'},    # Blue
        'H': {'color': (255, 0, 0), 'editor_char': 'H'},    # Red
        'P': {'color': (0, 255, 0), 'editor_char': 'P'},    # Green
        ' ': {'color': (50, 50, 50), 'editor_char': ' '}     # Dark Gray for empty
    }

# Editor constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
EDITOR_ROWS = 10  # Default number of rows in the editor grid
EDITOR_COLS = 10  # Default number of columns in the editor grid
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRID_LINE_COLOR = (100, 100, 100)
UI_TEXT_COLOR = WHITE

# Ensure space is in BRICK_CONFIG for drawing empty cells correctly
if ' ' not in BRICK_CONFIG:
    BRICK_CONFIG[' '] = {'color': (50, 50, 50), 'editor_char': ' '}


class Editor:
    """
    Provides a simple grid-based level editor for Pysnake Break.
    """
    def __init__(self, rows, cols, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT - 100): # Reserve space for UI
        self.rows = rows
        self.cols = cols
        self.screen_width = screen_width
        self.screen_height = screen_height # Grid area height
        self.ui_height = 100 # Height for the UI panel

        self.grid = [[' ' for _ in range(cols)] for _ in range(rows)]
        
        # Use keys from imported BRICK_CONFIG, ensure ' ' is a type
        self.brick_types_map = {str(i+1): char for i, char in enumerate(BRICK_CONFIG.keys()) if char != ' '}
        # Add ' ' as a type that can be selected, e.g., with key '0' or another key
        # For simplicity, let's map '0' to ' '
        self.brick_types_map['0'] = ' ' 
        self.current_brick_char = 'S' # Default to 'S'

        pygame.display.set_caption("Pysnake Break Level Editor")
        # Total screen height includes UI area
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height + self.ui_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24) # For UI text
        self.grid_font = pygame.font.Font(None, 30) # For characters in grid cells

        self.cell_width = self.screen_width // self.cols
        self.cell_height = self.screen_height // self.rows
        
        self.running = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if my < self.screen_height: # Click is within grid area
                    col = mx // self.cell_width
                    row = my // self.cell_height
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        self.grid[row][col] = self.current_brick_char
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Placeholder for exiting to main menu
                    print("ESC pressed - (Placeholder for exiting editor)")
                    # self.running = False # For now, just quit editor
                elif event.key == pygame.K_s:
                    self.save_level_to_file()
                elif event.key == pygame.K_c:
                    self.grid = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
                    print("Grid cleared.")
                
                # Change brick type based on number keys
                # Uses the brick_types_map defined in __init__
                key_char = pygame.key.name(event.key)
                if key_char in self.brick_types_map:
                    self.current_brick_char = self.brick_types_map[key_char]
                    print(f"Selected brick type: {self.current_brick_char}")


    def update(self):
        # Currently no per-frame update logic needed beyond input handling
        pass

    def save_level_to_file(self):
        """Saves the current grid layout to a timestamped file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"level_{timestamp}.txt"
        
        # Sanitize grid: ensure all cells are single characters from BRICK_CONFIG keys
        # If a cell somehow has an invalid char, default to ' '
        valid_chars = set(BRICK_CONFIG.keys())
        sanitized_grid = []
        for r_idx in range(self.rows):
            row_str = ""
            for c_idx in range(self.cols):
                char = self.grid[r_idx][c_idx]
                if char in valid_chars:
                    row_str += char
                else:
                    row_str += ' ' # Default to space if invalid char found
            sanitized_grid.append(row_str)

        # Trim empty rows from the end
        while sanitized_grid and all(c == ' ' for c in sanitized_grid[-1]):
            sanitized_grid.pop()

        # Trim empty columns from the right of all remaining rows
        if sanitized_grid:
            max_cols = 0
            for row_str in sanitized_grid:
                last_brick_idx = -1
                for i, char_code in enumerate(row_str):
                    if char_code != ' ':
                        last_brick_idx = i
                if last_brick_idx > -1: # Check if row is not all spaces
                    max_cols = max(max_cols, last_brick_idx + 1)
            
            if max_cols > 0: # If there's any non-space content
                trimmed_grid_rows = [row_str[:max_cols] for row_str in sanitized_grid]
            else: # Grid is all spaces or empty
                trimmed_grid_rows = [""] # Represent as one empty string row for an empty level
        else: # Grid was initially empty or became empty after row trimming
            trimmed_grid_rows = [""]


        level_name = f"LEVEL_{timestamp}"
        
        try:
            with open(filename, 'w') as f:
                f.write(f"{level_name} = [\n")
                for i, row_str in enumerate(trimmed_grid_rows):
                    f.write(f"    \"{row_str}\"")
                    if i < len(trimmed_grid_rows) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                f.write("]\n")
            save_message = f"Level saved to {filename}"
            print(save_message)
            # Optionally, display this message in the UI for a few seconds
            # For now, we'll update the main instruction text to show last saved file.
            self.last_save_message = save_message 
        except IOError as e:
            error_message = f"Error saving level: {e}"
            print(error_message)
            self.last_save_message = error_message # Display error

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * self.cell_width, r * self.cell_height, 
                                   self.cell_width, self.cell_height)
                
                char_code = self.grid[r][c]
                brick_info = BRICK_CONFIG.get(char_code, BRICK_CONFIG[' ']) # Default to empty
                
                pygame.draw.rect(self.screen, brick_info['color'], rect)
                pygame.draw.rect(self.screen, GRID_LINE_COLOR, rect, 1) # Grid lines

                # Draw character in cell
                char_surface = self.grid_font.render(char_code, True, WHITE)
                char_rect = char_surface.get_rect(center=rect.center)
                self.screen.blit(char_surface, char_rect)

    def draw_ui(self):
        ui_panel_rect = pygame.Rect(0, self.screen_height, self.screen_width, self.ui_height)
        pygame.draw.rect(self.screen, (30, 30, 30), ui_panel_rect) # Dark UI background

        # Display current brick type
        type_text = f"Current: [{self.current_brick_char}] ({BRICK_CONFIG.get(self.current_brick_char, {}).get('color', 'N/A')})"
        type_surface = self.font.render(type_text, True, UI_TEXT_COLOR)
        self.screen.blit(type_surface, (10, self.screen_height + 5)) # Adjusted y for new line

        # Display instructions
        instructions = "Click: Paint | Keys(0-map):Change | S:Save | C:Clear | ESC:Quit"
        instr_surface = self.font.render(instructions, True, UI_TEXT_COLOR)
        self.screen.blit(instr_surface, (10, self.screen_height + 30)) # Adjusted y
        
        # Display brick type selection keys
        key_map_y_start = self.screen_height + 50 # Adjusted y
        selection_texts = []
        current_line_width = 10
        max_line_width = self.screen_width - 20 # Allow some padding

        for key, char_code in self.brick_types_map.items():
            text_part = f"{key}:{char_code} "
            part_surface = self.font.render(text_part, True, UI_TEXT_COLOR)
            if current_line_width + part_surface.get_width() > max_line_width:
                # Move to next line in UI for key map
                key_map_y_start += 15 # Next line y
                current_line_width = 10 # Reset x offset
            
            self.screen.blit(part_surface, (current_line_width, key_map_y_start))
            current_line_width += part_surface.get_width() + 5 # Add some spacing
        
        # Display last save message
        if hasattr(self, 'last_save_message') and self.last_save_message:
            save_msg_surface = self.font.render(self.last_save_message, True, (150, 255, 150)) # Light green
            self.screen.blit(save_msg_surface, (10, self.screen_height + self.ui_height - 25))


    def draw(self):
        self.screen.fill(BLACK) # Fill whole screen including UI area potential border
        self.draw_grid()
        self.draw_ui()
        pygame.display.flip()

    def run_editor_loop(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    editor = Editor(rows=EDITOR_ROWS, cols=EDITOR_COLS)
    editor.run_editor_loop()
    pygame.quit()
    sys.exit()

[end of editor.py]
