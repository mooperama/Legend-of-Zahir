import pygame
from bullets import *
from config_settings import *

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
            'down': [self.game.character_spritesheet.get_sprite(128, 0, 15, 15),
                     self.game.character_spritesheet.get_sprite(0, 0, 15, 15),
                     self.game.character_spritesheet.get_sprite(15, 0, 15, 15)],
            'up': [self.game.character_spritesheet.get_sprite(145, 0, 15, 15),
                   self.game.character_spritesheet.get_sprite(65, 0, 15, 15),
                   self.game.character_spritesheet.get_sprite(80, 0, 15, 15)],
            'left': [self.game.character_spritesheet.get_sprite(95, 0, 15, 15),
                     self.game.character_spritesheet.get_sprite(112, 0, 15, 15)],
            'right': [self.game.character_spritesheet.get_sprite(32, 0, 15, 15),
                      self.game.character_spritesheet.get_sprite(48, 0, 15, 15)]
        }
        
        # Scale all animation frames
        for direction in self.animations:
            self.animations[direction] = [pygame.transform.scale(img, (TILESIZE, TILESIZE)) 
                                          for img in self.animations[direction]]
        
        self.image = self.animations['down'][0]  # Set initial image
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Player stats
        self.health = 100
        self.max_health = 100
        self.attack_power = 10
        self.exp = 0
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
        """
        Create a bullet sprite moving towards the target position.
        
        Args:
        target_pos (tuple): The (x, y) coordinates of the target.
        """
        direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
        Bullet(self.game, self.rect.centerx, self.rect.centery, direction)

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

    def draw_stats(self, surface):
        """
        Draw the player's stats (level and attack power) on the given surface.
        
        Args:
        surface (pygame.Surface): The surface to draw on.
        """
        font = pygame.font.Font(None, 24)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        attack_text = font.render(f"Attack: {self.attack_power}", True, WHITE)
        surface.blit(level_text, (10, 70))
        surface.blit(attack_text, (10, 100))

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