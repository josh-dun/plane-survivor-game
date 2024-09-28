import pygame, random, time

UI_HEIGHT = 60
WIDTH, HEIGHT = 800,600 + UI_HEIGHT

VECTOR_DIRECTION = {"upleft":    [-1, -1],
                    "upright":   [ 1, -1],
                    "downleft":  [-1,  1],
                    "downright": [ 1,  1],
                    "up":        [ 0, -1], 
                    "down":      [ 0,  1], 
                    "left":      [-1,  0], 
                    "right":     [ 1,  0] 
            }


BULLETS_ORDER = ["upleft", "up", "upright",
                 "right", "downright", "down", 
                 "downleft", "left"]

oneVector_collide = {"left": "right", "right": "left", "up": "down", "down":"up"}
twoVector_collide = {"upleft": {"x": "upright", "y": "downleft"}, 
                                  "upright": {"x": "upleft", "y": "downright"},
                                  "downleft": {"x": "downright", "y": "upleft"},
                                  "downright": {"x": "downleft", "y": "upright"}}