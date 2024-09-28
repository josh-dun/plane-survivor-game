import pygame
from move_sprites import *
from stand_sprites import Food, Teleport, Timer
from support import load_images_directly

pygame.init()
pygame.font.init()

POINT_FONT = pygame.font.SysFont("comicsans", 35)

class Game():
	def __init__(self):
		self.win = pygame.display.set_mode((WIDTH, HEIGHT))
		self.reset_game()

	def reset_game(self):
		# groups
		self.all_sprites = pygame.sprite.Group()
		self.bullets_sprites = pygame.sprite.Group()
		self.eater_sprites = pygame.sprite.Group()
		self.meteor_sprites = pygame.sprite.Group()

		self.plane = Plane(60, 60, self.all_sprites)
		self.food = Food(self.plane, self.all_sprites)
		self.timer = Timer(time.time())
		self.points = 0
		self.teleport = self.shield = None
		self.ufo = None
		self.game_over_surface = load_images_directly("game_over", WIDTH, HEIGHT)

	def draw_window(self, dt):
		self.win.fill("lightgray")
		self.draw_points()

		pygame.draw.line(self.win, "black", (0, UI_HEIGHT), (WIDTH, UI_HEIGHT), 5)
		self.food.draw_food(self.win)
		if self.shield:
			self.shield.draw_shield(self.win)

		self.plane.draw_plane(self.win)

		for bullet in self.bullets_sprites:
			bullet.move(self.bullets_sprites)
			bullet.draw_bullet(self.win)

		if self.teleport:
			self.teleport.draw_teleport(self.win)

		for eater in self.eater_sprites:
			eater.draw_eater(self.win)
			eater.move(self.bullets_sprites)
			
		for meteor in self.meteor_sprites:
			meteor.draw_meteor(self.win)
			if meteor.live_time:
				meteor.move(dt, self.bullets_sprites, self.eater_sprites)
	
		if self.ufo:
			self.ufo.draw_ufo(self.win)
			if self.ufo.collide_player():
				self.ufo = None

		if self.plane.lives <= 0:
			self.game_over()
		
	def draw_points(self):
		# points
		point = POINT_FONT.render(f"{self.points}", True, "red")
		point_text = POINT_FONT.render(f"Points: ", True, "red")
		self.win.blit(point_text, (0, 0))
		self.win.blit(point, (120, 0))

		#lives 
		live_points = POINT_FONT.render(f"{self.plane.lives}", True, "red")
		live_text = POINT_FONT.render("Lives: ", True, "red")
		live_text_rect = live_text.get_rect(topleft = (130 + point.get_width() + 20, 0))
		self.win.blit(live_text, (live_text_rect.left, 0))
		self.win.blit(live_points, (live_text_rect.right, 0))

		#special food bar
		life_points_rect = live_points.get_rect(topleft = (live_text_rect.topright))
		pygame.draw.rect(self.win, "black", (life_points_rect.right + 20, 10, 400, UI_HEIGHT / 1.5))
		if self.points % 10:
			pygame.draw.rect(self.win, "red", (life_points_rect.right + 20, 10, 
				(self.points % 10) * 40, UI_HEIGHT / 1.5))


	def destroy_bullets(self):
		if len(self.bullets) <= 4:
			self.bullets.clear()
		else:
			for i in range(4):
				self.bullets.pop(0)

	def collide_special_food(self, food_type):
		if food_type  == "destroy":
			self.destroy_bullets()
		elif food_type == "heart":
			self.plane.lives += 2
		elif food_type == "teleport":
			self.teleport = Teleport(self.food, self.plane)
		elif food_type == "shield":
			self.shield = Shield(self.plane, self.all_sprites)
			self.shield.set_min_max_player_pos()
		elif food_type == "eater":
			directions = ["upleft", "upright", "downright", "downleft"]
			for i in range(4):
				Eater(self.plane.rect.centerx, self.plane.rect.centery, directions[i],
				    (self.eater_sprites, self.all_sprites))

	def handle_eat_food(self, dt):
		food_type = 'normal'
		self.points += 1

		if self.points % 10 == 0:
			food_type = random.choice(["eater", "shield", "teleport", "heart"])

		current_food_type = self.food.food_type
		self.food = Food(self.plane, self.all_sprites)
		self.collide_special_food(current_food_type)
		
		self.food.food_type = food_type
		self.food.image = self.food.images[food_type]

	def game_over(self): 
		self.win.blit(self.game_over_surface, (0, 0))
		pygame.display.update()
		pygame.time.delay(2000)
		self.reset_game()

	def main(self):
		run = True 	
		clock = pygame.time.Clock()
		last_time = time.time()

		while run:
			dt = time.time() - last_time
			last_time = time.time()
			clock.tick(60)

			keys = pygame.key.get_pressed()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False 

			self.plane.move(keys, dt)
			
			if self.shield:
				self.shield.move()
				self.shield.collide_objects(self.bullets_sprites, self.meteor_sprites, self.ufo)
				if self.shield.time_death():
					self.shield = None 

			self.draw_window(dt)

			if self.food.collide_player():
				self.handle_eat_food(dt)


			if self.teleport and self.teleport.active:
				self.teleport.move_player()

			self.plane.vel_x = self.plane.vel_y = 0

			# release UFO
			if time.time() - self.timer.start_ufo_time >= 20:
				self.ufo = UFO(self.plane, self.all_sprites)



			self.timer.releaseObjectsByTime(self.plane, self.all_sprites, self.meteor_sprites, self.bullets_sprites)


			pygame.display.update()
		pygame.quit()
		quit()

game = Game()
game.main()

