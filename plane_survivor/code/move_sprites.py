from settings import * 
from support import METEOR_IMAGES, EATER_IMAGES, BULLET_IMAGES, load_images_directly, load_player_images 

def object_screen_collide(obj):
    if obj.x <= 0:
        obj.vel_x = -obj.vel_x
        obj.x = 0
        return "horizontal"

    elif obj.x + obj.width >= WIDTH:
        obj.vel_x = -obj.vel_x
        obj.x = WIDTH - obj.width
        return "horizontal"

    if obj.y <= UI_HEIGHT:
        obj.vel_y = -obj.vel_y 
        obj.y = UI_HEIGHT
        return "vertical"
        
    elif obj.y + obj.height >= HEIGHT:
        obj.vel_y = -obj.vel_y 
        obj.y = HEIGHT - obj.height
        return "vertical"

class gameObject():
    def get_data(self, width, height, x, y, vel_x, vel_y):
        self.width = width
        self.height = height 
        self.x, self.y = x, y
        self.vel_x, self.vel_y = vel_x, vel_y 


class Plane(pygame.sprite.Sprite, gameObject):
    def __init__(self, width, height, groups):
        super().__init__(groups)
        self.speed = 400
        self.get_data(width, height, 100, 100, 0, 0)
        self.bullet_direction = 0
        self.direction = "up"
        self.lives = 3

        self.images = load_player_images("plane", self.width, self.height)
        self.image = self.images["up"]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.reset_screen_collide_pos()

    def reset_screen_collide_pos(self):
        self.min_up = UI_HEIGHT
        self.min_left = 0
        self.max_down = HEIGHT - self.height
        self.max_right = WIDTH - self.width

    def collide_bullets(self, bullets):
        collided_bullets = pygame.sprite.spritecollide(self, bullets, False, pygame.sprite.collide_mask)
        for bullet in collided_bullets:
            if bullet.active:   
                bullet.kill()
                self.lives -= 1

    def draw_plane(self, win):
        win.blit(self.image, (self.x, self.y))

    def screen_collide(self):
        if self.y < self.min_up:
            self.y = self.min_up
        elif self.y > self.max_down:
            self.y = self.max_down 
        if self.x < self.min_left:
            self.x = self.min_left
        elif self.x > self.max_right:
            self.x = self.max_right

    def move(self, keys, dt):
        if keys[pygame.K_UP] and self.y >= self.min_up:
            self.vel_y = -1
            self.direction = "up"

        if keys[pygame.K_DOWN] and self.y <= self.max_down:
            self.vel_y = 1
            self.direction = "down"

        if keys[pygame.K_RIGHT] and self.x <= self.max_right:
            self.vel_x = 1
            self.direction = "right"

        if keys[pygame.K_LEFT] and self.x >= self.min_left:
            self.vel_x = -1
            self.direction = "left"

        self.image = self.images[self.direction]
        self.x += self.speed * self.vel_x * dt 
        self.y += self.speed * self.vel_y * dt
        self.screen_collide()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.mask = pygame.mask.from_surface(self.image)

class Bullet(pygame.sprite.Sprite, gameObject):
    def __init__(self, x, y, direction, player, groups):
        super().__init__(groups)
        self.get_data(20, 20, x, y,*VECTOR_DIRECTION[direction])
        self.active = False
        self.player = player
        self.image = BULLET_IMAGES["inactive"]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def screen_colide(self):
        if object_screen_collide(self):
            self.active = True
            self.image = BULLET_IMAGES["active"]
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            self.mask = pygame.mask.from_surface(self.image)

    def move(self, bullets):
        self.screen_colide()

        self.x += self.vel_x 
        self.y += self.vel_y 
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.player.collide_bullets(bullets)


    def draw_bullet(self, win):
        win.blit(self.image, (self.x, self.y))

class Shield(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.width = self.height = 100
        self.player = player  
        self.image = load_images_directly("shield_food", self.width, self.height)
        self.rect = self.image.get_rect(center=player.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = time.time()

    def move(self):
        self.rect.center = self.player.rect.center 
        self.mask = pygame.mask.from_surface(self.image)
 
    def collide_objects(self, bullets_sprites, meteors_sprites, ufo):
        collided_bullets = pygame.sprite.spritecollide(self, bullets_sprites, True, pygame.sprite.collide_mask)
        collided_meteors = pygame.sprite.spritecollide(self, meteors_sprites, True, pygame.sprite.collide_mask)
        # collide ufo
        if ufo:
            if pygame.sprite.collide_mask(self, ufo):
                ufo.kill()


    def set_min_max_player_pos(self):
        self.player.min_up = (self.height - self.player.height) / 2 + 5 + UI_HEIGHT
        self.player.max_down = HEIGHT - (self.height - self.player.height) / 2 - self.player.height - 5
        self.player.min_left = (self.width - self.player.width) / 2 + 5
        self.player.max_right = WIDTH - self.player.min_left - self.player.width - 5

    def time_death(self):
        if time.time() - self.start_time > 5:
            self.player.reset_screen_collide_pos()
            return True 

    def draw_shield(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Eater(pygame.sprite.Sprite, gameObject):
    def __init__(self, x, y, direction, groups):
        super().__init__(groups)
        self.direction = direction

        # images
        self.images = EATER_IMAGES[direction]
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(x, y))

        # frames
        self.get_data(100, 100, *self.rect.topleft, *VECTOR_DIRECTION[direction])
        self.animation_frame = 0 
        self.animation_count = time.time()

        # live time 
        self.live_time = time.time()

    def animation_eater(self):
        if time.time() - self.animation_count >= 0.1:
            self.animation_frame = (self.animation_frame + 1) % 6
            self.image = self.images[self.animation_frame]
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            self.animation_count = time.time()
            
    def change_collided_frame(self, collide_side):
        if self.direction in oneVector_collide:
            self.direction = oneVector_collide[self.direction]
            
        elif self.direction in twoVector_collide:
            if collide_side == "horizontal":
                self.direction = twoVector_collide[self.direction]["x"]
            elif collide_side == "vertical":
                self.direction = twoVector_collide[self.direction]["y"]    

        self.images = EATER_IMAGES[self.direction]
        self.image = self.images[0]
        self.animation_count = time.time()
        self.animation_frame = 0 


    def screen_collide(self):
        collided_side = object_screen_collide(self)
        if collided_side:
            self.change_collided_frame(collided_side)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, bullets):
        self.x += self.vel_x 
        self.y += self.vel_y
        self.screen_collide()
        self.collide_bullets(bullets)        

    def collide_bullets(self, bullets):
        collided_bullets = pygame.sprite.spritecollide(self, bullets, True, pygame.sprite.collide_mask)

    def draw_eater(self, win):
        self.animation_eater()   
        win.blit(self.image, (self.x, self.y))
        if time.time() - self.live_time >= 5:
            self.kill()

class Meteor(pygame.sprite.Sprite): 
    def __init__(self, player, groups):
        super().__init__(groups) 
        self.width = self.height = 100
        self.x = random.randint(self.width, WIDTH - self.width) 
        self.y = random.randint(self.height, HEIGHT - self.height)

        self.speed = 100
        self.player = player
        meteor_image = random.choice([0, 1, 3])

        self.images = METEOR_IMAGES[meteor_image]
        surf = pygame.mask.from_surface(self.images[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
        
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = time.time()
        self.animation_frame = 0

        self.appear_time = time.time()
        self.live_time = 0 

    def draw_meteor(self, win):
        if self.live_time:
            self.update_frame()
        else:
            self.activeMeteor()

        win.blit(self.image, self.rect.topleft)


    def move(self, dt, bullets, eaters):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        try: 
            self.direction = (player_pos - enemy_pos).normalize()
        except:
            self.direction = pygame.Vector2(0, 0)
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

        self.collide_objects(bullets, eaters)

    def collide_objects(self, bullets, eaters):
        # eater
        if pygame.sprite.spritecollide(self, eaters, True, pygame.sprite.collide_mask):
            self.kill()

        # bullets
        pygame.sprite.spritecollide(self, bullets, True, pygame.sprite.collide_mask)
        
        # player
        if pygame.sprite.collide_mask(self, self.player):
            if self.live_time:
                self.kill()
                self.player.lives -= 1

    def activeMeteor(self):
        if time.time() - self.appear_time >= 2:
            self.image = self.images[0]
            self.animation_frame = 0 
            self.animation_count = time.time()
            self.live_time = time.time()

    def update_frame(self):
        if self.live_time and time.time() - self.animation_count >= 0.1:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.image = self.images[self.animation_frame]
            self.animation_count = time.time()


UFO_VEL_X = [i * j / 10 for i in range(5, 10, 2) for j in [1, -1]]
UFO_VEL_Y = UFO_VEL_X

class UFO(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.vel_x = random.choice(UFO_VEL_X)
        self.vel_y = random.choice(UFO_VEL_Y)
        self.width = self.height = 100
        self.player = player
        pos = self.generate_pos()

        self.image = load_images_directly("ufo", self.width,self.height)
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def generate_pos(self):
        if self.vel_x > 0:
            x = -self.width
        else:
            x = WIDTH
        if self.vel_y > 0:
            y = random.randint(UI_HEIGHT, HEIGHT / 2)
        elif self.vel_y < 0:
            y = random.randint(HEIGHT / 2, HEIGHT - self.height)

        return (x, y)

    def draw_ufo(self, win):
        self.move()
        win.blit(self.image, self.rect.topleft)

    def move(self):
        self.rect.x += self.vel_x 
        self.rect.y += self.vel_y

    def collide_player(self):
        if pygame.sprite.collide_mask(self, self.player):
            self.player.lives -= 1
            self.kill()
            return True
