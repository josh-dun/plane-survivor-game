import pygame 

pygame.init()
def load_images_directly(name, width, height):
    image = pygame.image.load(f"../images/{name}.png")
    scaled_image = pygame.transform.scale(image, (width, height))
    
    return scaled_image

# import player image 
def load_player_images(name, width, height):
    images = {}
    image = load_images_directly(name, width, height)
    angle = 0
    for direction in ["up", "left", "down", "right"]:
        images[direction] = pygame.transform.rotate(image, angle) 
        angle += 90 

    return images

def load_food_images(width, height):
    images = {}

    for food_type in ["normal", "teleport", "shield", "eater", "heart"]:
        scaled_image = load_images_directly(food_type + "_food", width, height)
        images[food_type] = scaled_image

    return images 

def load_bullets_images(radius):
    images = {}
    active_image = load_images_directly("active_bullet", radius * 2, radius * 2)
    inactive_image = load_images_directly("inactive_bullet", radius * 2, radius * 2)

    images["active"] = active_image
    images["inactive"] = inactive_image
    return images

def load_eater_images():
    all_images = load_images_directly("motion", 600, 800)
    images = {}
    directions = ["right", "upright", "up", "upleft", "left", "downleft", "down", "downright"]

    for row, direction in enumerate(directions):
        motion = []
        for col in range(6):
            surface = pygame.Surface((100, 100))
            area = pygame.Rect((col * 100, row * 100), (100, 100))
            surface.blit(all_images, (0, 0), area)
            surface.set_colorkey("black")
            motion.append(surface)

        images[direction] = motion
    return images

def load_meteor_image():    
    image = load_images_directly("meteor", 400, 400)
    images = {}

    for row in range(4):
        images[row] = []
        for col in range(4):
            # surface = pygame.Surface((100, 100))
            # surface.set_colorkey("black")
            area = pygame.Rect((col * 100, row * 100), (100, 100))
            # surface.blit(image, (0, 0), area)
            surface = image.subsurface(area).copy()
            images[row].append(surface)

    return images

screen = pygame.display.get_surface()
METEOR_IMAGES = load_meteor_image()
EATER_IMAGES = load_eater_images()
BULLET_IMAGES = load_bullets_images(10)
# <a href="https://www.flaticon.com/free-icons/spaceship" title="spaceship icons">Spaceship icons created by Freepik - Flaticon</a>
