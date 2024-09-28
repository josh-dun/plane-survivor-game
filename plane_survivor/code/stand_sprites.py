from settings import * 
from support import load_food_images, load_images_directly
from move_sprites import Bullet, Meteor, UFO

class Food(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.radius = 30
        self.player = player
        self.color = "darkgrey"
        self.food_type = "normal"

        self.images = load_food_images(self.radius, self.radius)
        self.image = load_images_directly(f"{self.food_type}_food", self.radius, self.radius)
        self.mask = pygame.mask.from_surface(self.image)
        self.generate_food_pos()

    def generate_food_pos(self):
        self.x = random.randint(0, WIDTH - self.radius)
        self.y = random.randint(UI_HEIGHT, HEIGHT - self.radius)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        while self.collide_player():
            self.x = random.randint(0, WIDTH - self.radius)
            self.y = random.randint(UI_HEIGHT, HEIGHT - self.radius)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def collide_player(self):
        return pygame.sprite.collide_mask(self, self.player)

    def collide_obstacle(self, rect):
        closest_x = max(rect.x, min(self.x, rect.x + rect.width))
        closest_y = max(rect.y, min(self.y, rect.y + rect.height))
        
        # Calculate the distance between the circle's center and this closest point
        distance_x = self.x - closest_x
        distance_y = self.y - closest_y
        distance_squared = distance_x ** 2 + distance_y ** 2
    
        # Check if the distance is less than or equal to the circle's radius squared
        return distance_squared <= self.radius ** 2

    def draw_food(self, win):
        win.blit(self.image, (self.x, self.y))

        
class Teleport():
    def __init__(self, food, player):
        self.width = 40
        self.height = 80 
        self.food = food
        self.player = player
        self.start_time = time.time()
        self.active = True
        self.generate_teleport_gate()
        self.color = "cyan"
        self.win = pygame.display.get_surface()

    def generate_teleport_gate(self):
        x1 = random.randint(self.player.width + 5, WIDTH - self.width - self.player.width - 5)
        y1 = random.randint(self.player.height + 5, HEIGHT - self.height - self.player.height- 5)
        self.gate1 = pygame.Rect(x1, y1, self.width, self.height)

        while self.food.collide_obstacle(self.gate1):
            x1 = random.randint(self.player.width + 5, WIDTH - self.width - self.player.width - 5)
            y1 = random.randint(self.player.height + 5, HEIGHT - self.height - self.player.height  - 5)
            self.gate1 = pygame.Rect(x1, y1, self.width, self.height)

        x2 = random.randint(self.player.width + 5, WIDTH - self.width - self.player.width - 5)
        y2 = random.randint(self.player.height + 5, HEIGHT - self.height - self.player.height - 5)        
        gate2 = pygame.Rect(x2, y2, self.width, self.height)
        gate2_scale = pygame.Rect(x2 - 62, y2 - 62, self.width + 62 * 2, self.height + 62 * 2)

        while pygame.Rect.colliderect(self.gate1, gate2_scale) or self.food.collide_obstacle(gate2):
            x2 = random.randint(self.player.width + 5, WIDTH - self.width - self.player.width - 5)
            y2 = random.randint(self.player.height + 5, HEIGHT - self.height - self.player.height - 5)
            gate2 = pygame.Rect(x2, y2, self.width, self.height)
            gate2_scale = pygame.Rect(x2 - 62, y2 - 62, self.width + 62 * 2, self.height + 62 * 2)
            print("fuck dat")
        self.gate2 = pygame.Rect(x2, y2, self.width, self.height)

    def move_player_logic(self, gate1, gate2):
        if pygame.Rect.colliderect(self.player.rect, gate1):
            if self.player.vel_x:
                self.player.y = gate2.top + (gate2.height - self.player.height) / 2
                
                if self.player.vel_x == 1:
                    self.player.x = gate2.right + 1
                elif self.player.vel_x == -1:
                    self.player.x = gate2.left - self.player.width - 1

            elif self.player.vel_y:
                self.player.x = gate2.left + (gate2.width - self.player.width) / 2

                if self.player.vel_y == 1:
                    self.player.y = gate2.bottom + 1            
                elif self.player.vel_y == -1:
                    self.player.y = gate2.top - self.player.height - 1
                    
    def move_player(self):
        self.move_player_logic(self.gate1, self.gate2)
        self.move_player_logic(self.gate2, self.gate1)

    def draw_teleport(self, win):
        if time.time() - self.start_time <= 5:
            pygame.draw.rect(win, self.color, self.gate1)
            pygame.draw.rect(win, "red", self.gate2)

            pygame.draw.rect(win, "red", self.gate1, 2)
            pygame.draw.rect(win, "green", self.gate2, 2)
        else:
            self.active = False

class Timer():
    def __init__(self, start_time):
        self.start_bullet_time = self.start_meteor_time = self.start_ufo_time = start_time 

    def releaseBullets(self, player, sprites, bullets):  
        if time.time() - self.start_bullet_time >= 3:
            bullet = Bullet(player.x + player.width / 2,
                            player.y + player.height / 2,
                            BULLETS_ORDER[player.bullet_direction],
                            player, [sprites, bullets]
                     )

            player.bullet_direction = (player.bullet_direction + 1) % 8
            self.start_bullet_time = time.time()

    def releaseMeteor(self, player, sprites, meteors):
        if time.time() - self.start_meteor_time >= 20:
            meteor = Meteor(player, [sprites, meteors])
            self.start_meteor_time = time.time()
            self.start_ufo_time = time.time()


    def releaseObjectsByTime(self, player, sprites, meteors, bullets):
        self.releaseBullets(player, sprites, bullets)   
        self.releaseMeteor(player, sprites, meteors)    