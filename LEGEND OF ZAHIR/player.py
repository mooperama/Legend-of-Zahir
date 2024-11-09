import pygame
from bullets import *
from config_settings import *
from bullets import*

class Player(pygame.sprite.Sprite):
    """
    Player class representing the main character in the game.
    """

    def __init__(self, game, x, y):
        """
        Initialize the Player object.
        
        Args:
        game (Game): The main game object.
        x (int): Initial x-coordinate of the player (in tile units).
        y (int): Initial y-coordinate of the player (in tile units).
        """
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.allsprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0  # Change in x position per frame
        self.y_change = 0  # Change in y position per frame

        self.facing = 'down'  # Direction the player is facing
        self.animation_loop = 0
        self.animation_speed = 0.1  # Adjust this to control animation speed
        self.last_update = pygame.time.get_ticks()

        # Create animation dictionaries
        self.animations = {
            'down': [self.game.character_spritesheet.get_sprite(3, 3, 15, 26),
                     self.game.character_spritesheet.get_sprite(24, 3, 15, 26)],
            'up': [self.game.character_spritesheet.get_sprite(87, 3, 15, 26),
                   self.game.character_spritesheet.get_sprite(108, 3, 15, 26)],
            'left': [self.game.character_spritesheet.get_sprite(131, 3, 11, 29),
                     self.game.character_spritesheet.get_sprite(151, 3, 11, 30)],
            'right': [self.game.character_spritesheet.get_sprite(46, 3, 11, 29),
                      self.game.character_spritesheet.get_sprite(68, 3, 11, 30)]
        }
        
        # Scale all animation frames
        for direction in self.animations:
            self.animations[direction] = [pygame.transform.scale(img, (30, 48)) 
                                          for img in self.animations[direction]]
        
        self.image = self.animations['down'][0]  # Set initial image
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.ammo_system = AmmoSystem()

        # Player stats
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.exp = 0
        self.knowledge_points = 0  # Add this line
        self.level = 1

        # Add light halo properties
        self.light_radius = 10  # Radius of the light halo
        self.light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.update_light_mask()

        self.experience = 0
        self.level = 1
        self.experience_to_next_level = 100  # Adjust this value as needed
        self.attack_power = 10  # Initial attack power
        self.max_health = 100  # Initial max health
        self.health = self.max_health

    def update(self):
        """
        Update the player's state each frame.
        """
        self.movement()  # Handle player movement
        
        # Only animate if the player is moving
        if self.x_change != 0 or self.y_change != 0:
            self.animate()  # Update player animation
        
        self.collide_enemy()  # Check for collisions with enemies

        # Apply movement
        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        # Reset movement changes
        self.x_change = 0
        self.y_change = 0

        #ammo system for bullets
        self.ammo_system.update()
        
        # Check for reload key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.ammo_system.start_reload()

        # Update light mask position
        self.update_light_mask()

    def update_light_mask(self):
        """
        Update the light mask surface based on the player's position.
        """
        self.light_surface.fill((0, 0, 0, 255))  # Fill with opaque black
        pygame.draw.circle(self.light_surface, (0, 0, 0, 0), 
                           (self.rect.centerx, self.rect.centery), self.light_radius)
    
    def draw(self, surface):
        """
        Draw the player and apply the light mask to the game surface.
        
        Args:
        surface (pygame.Surface): The surface to draw on.
        """
        # Draw the player
        surface.blit(self.image, self.rect)

        # Apply the light mask
        surface.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    def movement(self):
        """
        Handle player movement based on keyboard input.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            #camera movement 
            for sprite in self.game.allsprites:
                sprite.rect.x += PLAYER_SPEED
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_d]:
            #camera movement 
            for sprite in self.game.allsprites:
                sprite.rect.x -= PLAYER_SPEED        
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_w]:
            #camera movement 
            for sprite in self.game.allsprites:
                sprite.rect.y += PLAYER_SPEED
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_s]:
            #camera movement 
            for sprite in self.game.allsprites:
                sprite.rect.y -= PLAYER_SPEED
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

    def collide_blocks(self, direction):
        """
        Handle collisions with block sprites.
        
        Args:
        direction (str): The direction of movement ('x' or 'y').
        """
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    #camera focused
                    for sprite in self.game.allsprites: 
                        sprite.rect.x += PLAYER_SPEED

                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    #camera focused
                    for sprite in self.game.allsprites:
                        sprite.rect.x -= PLAYER_SPEED

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    #camera focused
                    for sprite in self.game.allsprites:
                        sprite.rect.y += PLAYER_SPEED

                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    #camera focused
                    for sprite in self.game.allsprites:
                        sprite.rect.y -= PLAYER_SPEED

    def animate(self):
        """
        Update the player's animation.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.animation_loop = (self.animation_loop + 1) % len(self.animations[self.facing])
            self.image = self.animations[self.facing][self.animation_loop]

        # If not moving, show the first frame of the current direction
        if self.x_change == 0 and self.y_change == 0:
            self.image = self.animations[self.facing][0]

    def collide_enemy(self):
        """
        Handle collisions with enemy sprites.
        """
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.health -= 1
            if self.health <= 0:
                self.kill()

    def shoot(self, target_pos):
        """Modified shoot method to use ammo system."""
        if self.ammo_system.can_shoot():
            pos = pygame.math.Vector2(self.rect.center)
            target = pygame.math.Vector2(target_pos)
            direction = (target - pos).normalize()
            
            Bullet(self.game, pos.x, pos.y, direction)
            self.ammo_system.shoot()
            return True
        return False
    
    def draw_health_bar(self, surface):
        """
        Draw the player's health bar on the given surface.
        
        Args:
        surface (pygame.Surface): The surface to draw on.
        """
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, RED, (10, 10, 200, 20))
        pygame.draw.rect(surface, GREEN, (10, 10, 200 * health_ratio, 20))

    def draw_exp_bar(self, surface):
        """
        Draw the player's experience bar on the given surface.
        
        Args:
        surface (pygame.Surface): The surface to draw on.
        """
        exp_ratio = self.exp / (self.level * 100)  # Assuming 100 exp points per level
        pygame.draw.rect(surface, WHITE, (10, 40, 200, 20))
        pygame.draw.rect(surface, YELLOW, (10, 40, 200 * exp_ratio, 20))

    def draw_stats(self, screen):
        """Draw player stats including health bar, exp bar, and ammo counter."""
        # Constants for positioning and sizing
        BAR_WIDTH = 200
        BAR_HEIGHT = 20
        MARGIN = 10
        LEFT_OFFSET = 10
        TOP_OFFSET = 10
        
        # Create smaller font for stats
        small_font = pygame.font.Font('LEGEND OF ZAHIR/assets/fonts/nokiafc22.ttf', 14)
        
        # Health Bar
        health_y = TOP_OFFSET
        health_outline = pygame.Rect(LEFT_OFFSET, health_y, BAR_WIDTH, BAR_HEIGHT)
        health_fill = pygame.Rect(LEFT_OFFSET, health_y, BAR_WIDTH * (self.health / self.max_health), BAR_HEIGHT)
        
        # Draw health bar background and fill
        pygame.draw.rect(screen, (100, 0, 0), health_outline)  # Dark red background
        pygame.draw.rect(screen, RED, health_fill)  # Health fill
        pygame.draw.rect(screen, WHITE, health_outline, 2)  # White border
        
        # Draw player name on left side of health bar
        name_text = small_font.render(self.name, True, WHITE)
        name_rect = name_text.get_rect(midleft=(LEFT_OFFSET + 5, health_y + BAR_HEIGHT//2))
        screen.blit(name_text, name_rect)
        
        # Draw HP counter next to health bar
        hp_text = small_font.render(f"{self.health}/{self.max_health}", True, WHITE)
        hp_rect = hp_text.get_rect(midleft=(LEFT_OFFSET + BAR_WIDTH + 5, health_y + BAR_HEIGHT//2))
        screen.blit(hp_text, hp_rect)
        
        # Experience Bar
        exp_y = health_y + BAR_HEIGHT + MARGIN
        exp_outline = pygame.Rect(LEFT_OFFSET, exp_y, BAR_WIDTH, BAR_HEIGHT)
        exp_percentage = min(1, self.experience / self.experience_to_next_level)
        exp_fill = pygame.Rect(LEFT_OFFSET, exp_y, BAR_WIDTH * exp_percentage, BAR_HEIGHT)
        
        pygame.draw.rect(screen, (0, 0, 100), exp_outline)
        pygame.draw.rect(screen, BLUE, exp_fill)
        pygame.draw.rect(screen, WHITE, exp_outline, 2)
        
        exp_text = small_font.render(f"Level {self.level} - EXP: {self.experience}/{self.experience_to_next_level}", True, WHITE)
        exp_text_rect = exp_text.get_rect(midleft=(LEFT_OFFSET + BAR_WIDTH + 5, exp_y + BAR_HEIGHT//2))
        screen.blit(exp_text, exp_text_rect)
        
        # Knowledge Points with smaller text
        kp_y = exp_y + BAR_HEIGHT + MARGIN
        kp_text = small_font.render(f"KP: {self.knowledge_points}", True, WHITE)
        kp_rect = kp_text.get_rect(topleft=(LEFT_OFFSET, kp_y))
        screen.blit(kp_text, kp_rect)
        
        # Ammo Display
        ammo_y = kp_y + BAR_HEIGHT + MARGIN
        mag_width = BAR_WIDTH
        mag_height = BAR_HEIGHT
        
        # Magazine background
        mag_rect = pygame.Rect(LEFT_OFFSET, ammo_y, mag_width, mag_height)
        pygame.draw.rect(screen, (40, 40, 40), mag_rect)  # Darker background
        pygame.draw.rect(screen, (70, 70, 70), mag_rect, 2)  # Border
        
        # Calculate bullet dimensions
        bullet_width = (mag_width - 20) // self.ammo_system.magazine_size
        bullet_margin = 2
        bullet_height = mag_height - 6
        
        # Draw ammo slots
        for i in range(self.ammo_system.magazine_size):
            bullet_x = LEFT_OFFSET + 10 + (bullet_width + bullet_margin) * i
            bullet_y = ammo_y + 3
            bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
            
            # Color each bullet slot
            if i < self.ammo_system.current_ammo:
                color = (255, 165, 0)  # Bright orange for loaded bullets
            else:
                color = (80, 80, 80)  # Darker gray for empty slots
            
            pygame.draw.rect(screen, color, bullet_rect)
            
            # Draw separator after each bullet except the last one
            if i < self.ammo_system.magazine_size - 1:
                separator_x = bullet_x + bullet_width + bullet_margin//2
                pygame.draw.line(screen, (70, 70, 70),
                            (separator_x, ammo_y + 3),
                            (separator_x, ammo_y + mag_height - 3))
        
        # Reload status
        if self.ammo_system.reloading:
            reload_text = small_font.render("RELOADING...", True, (255, 50, 50))
            reload_rect = reload_text.get_rect(midleft=(LEFT_OFFSET + mag_width + 5, ammo_y + mag_height//2 + BAR_HEIGHT))
            screen.blit(reload_text, reload_rect)
        elif self.ammo_system.current_ammo == 0:
            empty_text = small_font.render("Press R to reload", True, (255, 50, 50))
            empty_rect = empty_text.get_rect(midleft=(LEFT_OFFSET + mag_width + 5, ammo_y + mag_height//2 + BAR_HEIGHT))
            screen.blit(empty_text, empty_rect)
        
        # Attack Power
        attack_y = ammo_y + mag_height + MARGIN
        attack_text = small_font.render(f"ATK: {self.attack_power}", True, WHITE)
        attack_rect = attack_text.get_rect(topleft=(LEFT_OFFSET, attack_y))
        screen.blit(attack_text, attack_rect)

    def gain_experience(self, amount):
        self.experience += amount
        # Check if the player has enough experience to level up
        while self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)  # Increase exp needed for next level
        self.attack_power += 1  # Increase attack power on level up
        self.max_health += 10  # Increase max health on level up
        self.health = self.max_health  # Restore health to full on level up
        print(f"Level up! You are now level {self.level}")