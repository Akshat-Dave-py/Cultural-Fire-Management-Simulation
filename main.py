"""
Module: main.py
Description: An educational Pygame simulation illustrating traditional 
             Indigenous cultural fire management (mosaic burning) principles 
             to maintain healthy country and protect biodiversity.
Author: Swinburne Student Final Project
"""

import random
import sys
import pygame

# Initialize Pygame
pygame.init()

# Constants (Increased window height to prevent overlap)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 5
CELL_SIZE = 95
GRID_OFFSET_X = 160
GRID_OFFSET_Y = 100

# Colors (RGB)
COLOR_BG = (245, 239, 230)      # Soft earthy background
COLOR_TEXT = (50, 40, 30)
COLOR_HEALTHY = (76, 153, 0)    # Green: Healthy Country
COLOR_OVERGROWN = (184, 134, 11) # Ochre/Brown: Overgrown Brush (High Fire Risk)
COLOR_BURNT = (100, 100, 100)   # Charcoal: Recently Cool-Burned
COLOR_GRID_LINE = (210, 195, 175)

# Setup Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Caring for Country: Cultural Fire Management")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 32)


class LandPatch:
    """Represents a discrete zone of land (Country) that changes state 
    based on environmental factors and cultural management actions.
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col
        # Start with a higher chance of being overgrown so the game is immediately active
        self.state = random.choices(['healthy', 'overgrown'], weights=[35, 65])[0]
        self.recovery_timer = 0

    def update(self):
        """Updates the ecological lifecycle of the land patch over time."""
        if self.state == 'burnt':
            self.recovery_timer += 1
            # After a few ticks, burnt land regenerates into healthy country
            if self.recovery_timer > 6:
                self.state = 'healthy'
                self.recovery_timer = 0
        elif self.state == 'healthy':
            # Healthy land slowly becomes overgrown with dry brush over time
            if random.random() < 0.04:
                self.state = 'overgrown'

    def apply_cool_burn(self):
        """Applies a controlled traditional cool burn to overgrown land 
        to clear fuel and stimulate new growth.
        """
        if self.state == 'overgrown':
            self.state = 'burnt'
            return True
        return False


class Game:
    """Manages the overall game state, user interactions, scoring, 
    and rendering logic for the educational simulation.
    """
    def __init__(self):
        self.grid = [[LandPatch(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.score = 0
        self.biodiversity_health = 100
        self.turns_remaining = 30
        self.game_over = False
        self.message = "Goal: Click Overgrown (OVE) brown patches to apply Cultural Cool Burns!"

    def handle_click(self, pos):
        """Handles mouse clicks on the grid to perform management actions."""
        if self.game_over:
            return

        x, y = pos
        if (GRID_OFFSET_X <= x <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
                GRID_OFFSET_Y <= y <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            
            col = (x - GRID_OFFSET_X) // CELL_SIZE
            row = (y -
                    GRID_OFFSET_Y) // CELL_SIZE

            patch = self.grid[row][col]
            if patch.apply_cool_burn():
                self.score += 20
                self.biodiversity_health = min(100, self.biodiversity_health + 4)
                self.message = f"Cool burn applied at ({row+1}, {col+1})! Fuel cleared safely."
            else:
                if patch.state == 'healthy':
                    self.message = f"Patch ({row+1}, {col+1}) is already Healthy (HEA). Leave it be!"
                else:
                    self.message = f"Patch ({row+1}, {col+1}) is recovering (BUR). Let it regenerate."

            self.turns_remaining -= 1
            if self.turns_remaining <= 0:
                self.game_over = True
                self.message = "Simulation Complete! Great job caring for Country."

    def update_simulation(self):
        """Updates all land patches periodically."""
        if self.game_over:
            return
        
        overgrown_count = 0
        for row in self.grid:
            for patch in row:
                patch.update()
                if patch.state == 'overgrown':
                    overgrown_count += 1

        # If too many patches are left overgrown, country health degrades (wildfire risk)
        if overgrown_count >= 10:
            self.biodiversity_health = max(0, self.biodiversity_health - 2)
            if self.biodiversity_health <= 0:
                self.game_over = True
                self.message = "Wildfire outbreak due to excessive fuel loads! Game Over."

    def draw(self, surface):
        """Renders all game UI elements, grid cells, scores, and status messages."""
        surface.fill(COLOR_BG)

        # Title Section
        title_surf = font_large.render("Caring for Country: Cultural Fire Management", True, COLOR_TEXT)
        surface.blit(title_surf, (20, 20))

        subtitle_surf = font.render("Simulating Indigenous mosaic burning to prevent wildfires and protect biodiversity.", True, (90, 80, 70))
        surface.blit(subtitle_surf, (20, 50))

        # Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                patch = self.grid[r][c]
                x = GRID_OFFSET_X + c * CELL_SIZE
                y = GRID_OFFSET_Y + r * CELL_SIZE

                if patch.state == 'healthy':
                    color = COLOR_HEALTHY
                elif patch.state == 'overgrown':
                    color = COLOR_OVERGROWN
                else:
                    color = COLOR_BURNT

                pygame.draw.rect(surface, color, (x, y, CELL_SIZE - 6, CELL_SIZE - 6), border_radius=10)
                pygame.draw.rect(surface, COLOR_GRID_LINE, (x, y, CELL_SIZE - 6, CELL_SIZE - 6), 2, border_radius=10)

                # Text inside box: HEA = Healthy, OVE = Overgrown, BUR = Burnt/Regenerating
                label_text = patch.state[:3].upper()
                state_label = font.render(label_text, True, (255, 255, 255))
                surface.blit(state_label, (x + 28, y + 36))

        # Stats Panel (Nicely spaced out below the grid so nothing overlaps)
        stat_y = 600
        score_text = font.render(f"Score: {self.score}", True, COLOR_TEXT)
        health_text = font.render(f"Country Health: {self.biodiversity_health}%", True, COLOR_TEXT)
        turns_text = font.render(f"Turns Left: {self.turns_remaining}", True, COLOR_TEXT)
        
        surface.blit(score_text, (40, stat_y))
        surface.blit(health_text, (260, stat_y))
        surface.blit(turns_text, (560, stat_y))

        # Status Message Box at the very bottom
        msg_surf = font.render(self.message, True, (140, 40, 20))
        surface.blit(msg_surf, (40, 640))


def main():
    """Main application loop."""
    game = Game()
    simulation_timer = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)

        # Periodic background simulation update
        simulation_timer += 1
        if simulation_timer >= 60:  # Roughly once per second
            game.update_simulation()
            simulation_timer = 0

        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()