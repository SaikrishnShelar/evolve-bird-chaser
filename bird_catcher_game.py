import pygame
import sys
import random
import math
import os
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Set up the display
WIDTH = 700
HEIGHT = 800
PLAY_AREA_HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bird Catcher Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BIRD_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
]

# Player properties
player_radius = 30
player_x = WIDTH // 2
player_y = PLAY_AREA_HEIGHT // 2
player_speed = 5
player_evolution = 0  # 0: circle, 1: cat, 2: hawk, 3: phoenix

# Trail properties
trail = []
max_trail_length = 20

# Bird properties
bird_width = 40
bird_height = 30
num_birds = 6
bird_animation_frames = 2
bird_animation_speed = 10

# Sparkle properties
sparkles = []
sparkle_duration = 30  # frames

# Power-up properties
power_ups = []
power_up_active = None
power_up_end_time = 0

# Game state
score = 0
game_over = False
victory = False
font = pygame.font.SysFont(None, 36)

# Timer
game_duration = 60  # seconds
start_time = pygame.time.get_ticks()

# Create birds at random positions
birds = []
for i in range(num_birds):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, PLAY_AREA_HEIGHT - 50)
    color = BIRD_COLORS[i % len(BIRD_COLORS)]
    direction = random.choice([-1, 1])
    birds.append({
        'x': x,
        'y': y,
        'color': color,
        'captured': False,
        'frame': 0,
        'frame_counter': 0,
        'direction': direction,
        'offset': 0,
        'offset_direction': random.choice([-1, 1])
    })

# Sound effects
try:
    # Create sounds directory if it doesn't exist
    os.makedirs(os.path.join(os.getcwd(), "sounds"), exist_ok=True)
    
    # Load sound files if they exist, otherwise create placeholders
    sound_files = {
        "capture": "capture.wav",
        "evolve": "evolve.wav",
        "victory": "victory.wav",
        "game_over": "game_over.wav",
        "power_up": "power_up.wav",
        "background": "background.wav"
    }
    
    sounds = {}
    for name, file in sound_files.items():
        path = os.path.join("sounds", file)
        if os.path.exists(path):
            sounds[name] = mixer.Sound(path)
        else:
            # Create a placeholder sound file
            with open(path, "wb") as f:
                # Write a minimal WAV file header
                f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xAC\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            sounds[name] = mixer.Sound(path)
    
    # Start background music
    sounds["background"].play(-1)  # Loop indefinitely
    sound_loaded = True
except:
    sound_loaded = False
    sounds = {}

# Function to create gradient background
def draw_gradient_background():
    # Create a gradient from dark blue to purple
    time_factor = max(0, min(1, remaining_time / game_duration))
    
    for y in range(PLAY_AREA_HEIGHT):
        # Calculate color based on position and time
        r = int(20 + (y / PLAY_AREA_HEIGHT) * 40)
        g = int(10 + (y / PLAY_AREA_HEIGHT) * 20)
        b = int(50 + (y / PLAY_AREA_HEIGHT) * 100)
        
        # Make colors more intense as time runs out
        if time_factor < 0.3:
            r = min(255, int(r * (1.5 - time_factor)))
        
        # Draw a line with the calculated color
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

# Function to create sparkle effect
def create_sparkles(x, y, color):
    for _ in range(20):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        size = random.randint(2, 5)
        lifetime = random.randint(10, sparkle_duration)
        sparkles.append({
            'x': x,
            'y': y,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'lifetime': lifetime
        })

# Function to draw a bird
def draw_bird(bird):
    x, y = bird['x'], bird['y']
    color = bird['color']
    frame = bird['frame']
    direction = bird['direction']
    
    # Bird body
    pygame.draw.ellipse(screen, color, (x - bird_width//2, y - bird_height//2, bird_width, bird_height))
    
    # Bird head
    head_radius = bird_height // 3
    head_x = x + direction * (bird_width//2 - head_radius//2)
    pygame.draw.circle(screen, color, (head_x, y - bird_height//6), head_radius)
    
    # Bird eye
    eye_x = head_x + direction * (head_radius//2)
    pygame.draw.circle(screen, BLACK, (eye_x, y - bird_height//4), 3)
    
    # Bird wings (animated)
    wing_y = y + (5 if frame == 0 else -5)
    wing_points = [
        (x, y),
        (x - direction * (bird_width//4), wing_y - bird_height//2),
        (x + direction * (bird_width//4), wing_y - bird_height//2)
    ]
    pygame.draw.polygon(screen, color, wing_points)

# Function to draw the player based on evolution level
def draw_player(x, y, evolution):
    if evolution == 0:  # Circle (default)
        pygame.draw.circle(screen, RED, (x, y), player_radius)
    
    elif evolution == 1:  # Cat
        # Cat body (circle)
        pygame.draw.circle(screen, (200, 100, 100), (x, y), player_radius)
        
        # Cat ears
        pygame.draw.polygon(screen, (200, 100, 100), [
            (x - player_radius//2, y - player_radius),
            (x - player_radius, y - player_radius*1.5),
            (x, y - player_radius)
        ])
        pygame.draw.polygon(screen, (200, 100, 100), [
            (x + player_radius//2, y - player_radius),
            (x + player_radius, y - player_radius*1.5),
            (x, y - player_radius)
        ])
        
        # Cat eyes
        pygame.draw.circle(screen, BLACK, (x - player_radius//2, y - player_radius//4), 4)
        pygame.draw.circle(screen, BLACK, (x + player_radius//2, y - player_radius//4), 4)
        
        # Cat mouth
        pygame.draw.line(screen, BLACK, (x - player_radius//3, y + player_radius//3), 
                        (x + player_radius//3, y + player_radius//3), 2)
    
    elif evolution == 2:  # Hawk
        # Hawk body
        pygame.draw.circle(screen, (139, 69, 19), (x, y), player_radius)
        
        # Hawk wings
        pygame.draw.polygon(screen, (120, 60, 10), [
            (x, y),
            (x - player_radius*1.5, y),
            (x - player_radius, y - player_radius//2)
        ])
        pygame.draw.polygon(screen, (120, 60, 10), [
            (x, y),
            (x + player_radius*1.5, y),
            (x + player_radius, y - player_radius//2)
        ])
        
        # Hawk beak
        pygame.draw.polygon(screen, (255, 200, 0), [
            (x, y),
            (x - player_radius//3, y + player_radius//3),
            (x + player_radius//3, y + player_radius//3)
        ])
        
        # Hawk eyes
        pygame.draw.circle(screen, BLACK, (x - player_radius//3, y - player_radius//4), 3)
        pygame.draw.circle(screen, BLACK, (x + player_radius//3, y - player_radius//4), 3)
    
    elif evolution == 3:  # Phoenix
        # Phoenix body
        pygame.draw.circle(screen, (255, 100, 0), (x, y), player_radius)
        
        # Phoenix flame aura
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            end_x = x + math.cos(angle) * (player_radius * 1.5)
            end_y = y + math.sin(angle) * (player_radius * 1.5)
            mid_x = x + math.cos(angle) * (player_radius * 1.2)
            mid_y = y + math.sin(angle) * (player_radius * 1.2)
            
            # Draw flame
            pygame.draw.polygon(screen, (255, 200, 0), [
                (x, y),
                (mid_x + random.randint(-5, 5), mid_y + random.randint(-5, 5)),
                (end_x, end_y)
            ])
        
        # Phoenix eyes
        pygame.draw.circle(screen, (255, 255, 255), (x - player_radius//3, y - player_radius//4), 4)
        pygame.draw.circle(screen, (255, 255, 255), (x + player_radius//3, y - player_radius//4), 4)
        pygame.draw.circle(screen, (0, 0, 0), (x - player_radius//3, y - player_radius//4), 2)
        pygame.draw.circle(screen, (0, 0, 0), (x + player_radius//3, y - player_radius//4), 2)

# Function to spawn power-up
def spawn_power_up():
    if random.random() < 0.005 and not power_ups and not power_up_active:  # 0.5% chance per frame
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, PLAY_AREA_HEIGHT - 50)
        power_ups.append({
            'type': "speed" if random.random() < 0.5 else "invincibility",
            'x': x,
            'y': y,
            'radius': 15,
            'color': (255, 215, 0)  # Gold color
        })

# Game loop
clock = pygame.time.Clock()
running = True
sound_played = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Calculate remaining time
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    remaining_time = max(0, game_duration - elapsed_time)
    
    if not game_over and remaining_time > 0:
        # Check if power-up is active
        if power_up_active:
            if pygame.time.get_ticks() > power_up_end_time:
                # Power-up expired
                if power_up_active == "speed":
                    player_speed = 5 + player_evolution
                power_up_active = None
        
        # Handle key presses for movement
        keys = pygame.key.get_pressed()
        current_speed = player_speed
        
        if keys[pygame.K_LEFT] and player_x - current_speed > player_radius:
            player_x -= current_speed
        if keys[pygame.K_RIGHT] and player_x + current_speed < WIDTH - player_radius:
            player_x += current_speed
        if keys[pygame.K_UP] and player_y - current_speed > player_radius:
            player_y -= current_speed
        if keys[pygame.K_DOWN] and player_y + current_speed < PLAY_AREA_HEIGHT - player_radius:
            player_y += current_speed
        
        # Add current position to trail
        if player_evolution == 3:  # Phoenix leaves flame trail
            trail.append((player_x, player_y))
            if len(trail) > max_trail_length:
                trail.pop(0)
        
        # Update bird animations and positions
        for bird in birds:
            if not bird['captured']:
                # Update animation frame
                bird['frame_counter'] += 1
                if bird['frame_counter'] >= bird_animation_speed:
                    bird['frame'] = (bird['frame'] + 1) % bird_animation_frames
                    bird['frame_counter'] = 0
                
                # Move bird side to side
                bird['offset'] += 0.5 * bird['offset_direction']
                if abs(bird['offset']) > 20:
                    bird['offset_direction'] *= -1
                
                # Update bird position
                bird['x'] += bird['offset_direction'] * 0.5
                
                # Keep birds within bounds
                if bird['x'] < 50:
                    bird['x'] = 50
                    bird['offset_direction'] *= -1
                elif bird['x'] > WIDTH - 50:
                    bird['x'] = WIDTH - 50
                    bird['offset_direction'] *= -1
        
        # Update and check for power-up collisions
        for power_up in power_ups[:]:
            # Check if player collects power-up
            distance = ((player_x - power_up['x']) ** 2 + (player_y - power_up['y']) ** 2) ** 0.5
            if distance < player_radius + power_up['radius']:
                power_ups.remove(power_up)
                power_up_active = power_up['type']
                power_up_end_time = pygame.time.get_ticks() + 5000  # 5 seconds
                
                if power_up['type'] == "speed":
                    player_speed *= 2
                
                if sound_loaded:
                    try:
                        sounds["power_up"].play()
                    except:
                        pass
        
        # Check for bird captures
        for bird in birds:
            if not bird['captured']:
                # Check if player overlaps with bird
                distance = ((player_x - bird['x']) ** 2 + (player_y - bird['y']) ** 2) ** 0.5
                
                if distance < player_radius + bird_width // 2:
                    bird['captured'] = True
                    score += 50
                    create_sparkles(bird['x'], bird['y'], bird['color'])
                    
                    # Check for evolution
                    birds_captured = sum(1 for b in birds if b['captured'])
                    
                    if birds_captured == 2 and player_evolution < 1:
                        player_evolution = 1  # Evolve to cat
                        player_speed = 6  # Slightly faster
                        if sound_loaded:
                            try:
                                sounds["evolve"].play()
                            except:
                                pass
                    
                    elif birds_captured == 4 and player_evolution < 2:
                        player_evolution = 2  # Evolve to hawk
                        player_speed = 7
                        if sound_loaded:
                            try:
                                sounds["evolve"].play()
                            except:
                                pass
                    
                    elif birds_captured == 6 and player_evolution < 3:
                        player_evolution = 3  # Evolve to phoenix
                        player_speed = 8
                        if sound_loaded:
                            try:
                                sounds["evolve"].play()
                            except:
                                pass
                    
                    if sound_loaded:
                        try:
                            sounds["capture"].play()
                        except:
                            pass
        
        # Check if all birds are captured
        if all(bird['captured'] for bird in birds):
            game_over = True
            victory = True
            
            if sound_loaded and not sound_played:
                try:
                    sounds["victory"].play()
                    sound_played = True
                except:
                    pass
        
        # Spawn power-ups
        spawn_power_up()
    
    # Check if time is up
    if remaining_time <= 0 and not game_over:
        game_over = True
        victory = False
        
        if sound_loaded and not sound_played:
            try:
                sounds["game_over"].play()
                sound_played = True
            except:
                pass
    
    # Draw gradient background
    draw_gradient_background()
    
    # Draw trail for phoenix
    for i, (trail_x, trail_y) in enumerate(trail):
        # Make trail fade out
        alpha = int(255 * (i / max_trail_length))
        radius = int(player_radius * 0.7 * (i / max_trail_length))
        
        # Draw flame trail with transparency
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 100, 0, alpha), (radius, radius), radius)
        screen.blit(s, (trail_x - radius, trail_y - radius))
    
    # Update and draw sparkles
    for sparkle in sparkles[:]:
        sparkle['x'] += sparkle['dx']
        sparkle['y'] += sparkle['dy']
        sparkle['lifetime'] -= 1
        
        if sparkle['lifetime'] <= 0:
            sparkles.remove(sparkle)
        else:
            # Draw sparkle with fading effect
            alpha = int(255 * (sparkle['lifetime'] / sparkle_duration))
            sparkle_color = sparkle['color'] + (alpha,)
            s = pygame.Surface((sparkle['size'] * 2, sparkle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, sparkle_color, (sparkle['size'], sparkle['size']), sparkle['size'])
            screen.blit(s, (sparkle['x'] - sparkle['size'], sparkle['y'] - sparkle['size']))
    
    # Draw the birds
    for bird in birds:
        if not bird['captured']:
            draw_bird(bird)
    
    # Draw power-ups
    for power_up in power_ups:
        pygame.draw.circle(screen, power_up['color'], (power_up['x'], power_up['y']), power_up['radius'])
        
        # Draw icon based on power-up type
        if power_up['type'] == "speed":
            # Draw lightning bolt
            pygame.draw.line(screen, BLACK, (power_up['x'] - 5, power_up['y'] - 5), 
                            (power_up['x'] + 5, power_up['y'] + 5), 2)
            pygame.draw.line(screen, BLACK, (power_up['x'] + 5, power_up['y'] - 5), 
                            (power_up['x'] - 5, power_up['y'] + 5), 2)
        elif power_up['type'] == "invincibility":
            # Draw shield shape
            pygame.draw.circle(screen, BLACK, (power_up['x'], power_up['y']), 7, 2)
    
    # Draw the player
    draw_player(player_x, player_y, player_evolution)
    
    # Draw UI background at bottom
    pygame.draw.rect(screen, (50, 50, 50), (0, PLAY_AREA_HEIGHT, WIDTH, HEIGHT - PLAY_AREA_HEIGHT))
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, PLAY_AREA_HEIGHT + 30))
    
    # Draw timer
    timer_text = font.render(f"Time: {remaining_time}s", True, WHITE)
    screen.blit(timer_text, (WIDTH - 150, PLAY_AREA_HEIGHT + 30))
    
    # Draw evolution status
    evolution_names = ["Circle", "Cat", "Hawk", "Phoenix"]
    evolution_text = font.render(f"Form: {evolution_names[player_evolution]}", True, WHITE)
    screen.blit(evolution_text, (WIDTH // 2 - 70, PLAY_AREA_HEIGHT + 30))
    
    # Draw active power-up
    if power_up_active:
        power_up_text = font.render(f"Power-up: {power_up_active.capitalize()}", True, (255, 215, 0))
        screen.blit(power_up_text, (20, PLAY_AREA_HEIGHT + 70))
    
    # Draw game over message
    if game_over:
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        if victory:
            message = "Victory! All birds captured!"
        else:
            message = "Game Over! Time's up!"
        
        # Draw main message
        game_over_text = font.render(message, True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(game_over_text, text_rect)
        
        # Draw final score
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        screen.blit(final_score_text, final_score_rect)
        
        # Draw restart instruction
        restart_text = font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
        screen.blit(restart_text, restart_rect)
        
        # Check for restart
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game
            player_evolution = 0
            player_speed = 5
            player_x = WIDTH // 2
            player_y = PLAY_AREA_HEIGHT // 2
            score = 0
            game_over = False
            victory = False
            sound_played = False
            trail = []
            sparkles = []
            power_ups = []
            power_up_active = None
            
            # Reset birds
            birds = []
            for i in range(num_birds):
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, PLAY_AREA_HEIGHT - 50)
                color = BIRD_COLORS[i % len(BIRD_COLORS)]
                direction = random.choice([-1, 1])
                birds.append({
                    'x': x,
                    'y': y,
                    'color': color,
                    'captured': False,
                    'frame': 0,
                    'frame_counter': 0,
                    'direction': direction,
                    'offset': 0,
                    'offset_direction': random.choice([-1, 1])
                })
            
            # Reset timer
            start_time = pygame.time.get_ticks()
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()