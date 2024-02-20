from enum import Enum
import pygame
import os
import random

pygame.init()
pygame.display.set_caption('Pirate Dinosaur')

FIRST_START = True
RUN = True
MAIN_RUN = True
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 620
FPS = 60
FLOOR_Y = 500
FLOOR_Y_OFFSET = 15
SKY_Y = 150
BIRD_Y = 250
GAME_SPEED = 12

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
RESET_IMG = [pygame.image.load(os.path.join("./Assets/Other", "Reset.png"))]
RUNNING_IMG = [pygame.image.load(os.path.join("./Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("./Assets/Dino", "DinoRun2.png"))]

JUMPING_IMG = [pygame.image.load(os.path.join("./Assets/Dino", "DinoJump.png"))]

DUCKING_IMG = [pygame.image.load(os.path.join("./Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("./Assets/Dino", "DinoDuck2.png"))]


SMALL_CACTUS = [pygame.image.load(os.path.join("./Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("./Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("./Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("./Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("./Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("./Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("./Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("./Assets/Bird", "Bird2.png"))]

CLOUD = [pygame.image.load(os.path.join("./Assets/Other", "Cloud.png"))]
BG = [pygame.image.load(os.path.join("./Assets/Other", "Track.png"))]
class BEHAVIOR:
    RUNNING = 1
    DUCKING = 2
    JUMPING = 3

class ScoreRender:
    scoreText = "Points: {}"
    def __init__(self):
        self.score = 0
    def Update(self):
        self.score += 1

    def Draw(self):
        text = pygame.font.Font(size=24).render(self.scoreText.format(self.score), False, (0,0,0))
        textRect = text.get_rect()
        textRect.center = (1200,50)
        SCREEN.blit(text, textRect)

class Obstacle:
    def __init__(self, image, type, x):
        self.image = image
        self.type = type
        self.rect = self.image[type].get_rect()
        self.rect.x = x
    
    def NeedRomove(self) -> bool:
        self.rect.x -= GAME_SPEED
        if self.rect.x < -self.rect.width:
            return True
        return False

    def Draw(self):
        SCREEN.blit(self.image[self.type], self.rect)



class SmallCactus(Obstacle):
    def __init__(self, type, x):
        super().__init__(SMALL_CACTUS, type, x)
        self.rect.y = FLOOR_Y - SMALL_CACTUS[type].get_height() + FLOOR_Y_OFFSET
    

class LargeCactus(Obstacle):
    def __init__(self, type, x):
        super().__init__(LARGE_CACTUS, type, x)
        self.rect.y = FLOOR_Y - LARGE_CACTUS[type].get_height() + FLOOR_Y_OFFSET


class Bird(Obstacle):
    def __init__(self, x):
        super().__init__(BIRD, 0, x)
        self.rect.y = BIRD_Y
        self.step_index = 0
    
    def Draw(self):
        if self.step_index >= 10:
            self.step_index = 0
        SCREEN.blit(BIRD[self.step_index//5], self.rect)
        self.step_index += 1

class ObstacleManager:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.obstacles = set()

    def update(self):
        savefiles = set()
        for obstacle in self.obstacles:
            if(not obstacle.NeedRomove()):
                savefiles.add(obstacle)

        self.obstacles = savefiles

        if self.x <= SCREEN_WIDTH + 200:
            self.GenRandomObstacle()
            self.x += random.randint(300, 2100)
        
        self.x -= GAME_SPEED
    
    def GenRandomObstacle(self):
        category = random.randint(0, 2)
        if category == 0:
            self.obstacles.add(SmallCactus(random.randint(0, 2), self.x))
        elif category == 1:
            self.obstacles.add(LargeCactus(random.randint(0, 2), self.x))
        else:
            self.obstacles.add(Bird(self.x))
    def CollisionDetect(self, player):
        for obstacle in self.obstacles:
            if player.colliderect(obstacle.rect):
                #pygame.draw.rect(SCREEN, (255,0,0), player, 2)
                #pygame.draw.rect(SCREEN, (255,0,0), obstacle.rect, 2)
                global MAIN_RUN
                MAIN_RUN = False
                menu()

    def Draw(self):
        for obstacle in self.obstacles:
            obstacle.Draw()



class BackGround:
    def __init__(self) -> None:
        self.x = 0
        self.y = FLOOR_Y
        self.image = BG[0]
        self.width = self.image.get_width()

    def update(self):
        self.x -= GAME_SPEED
        if self.x < -self.width:
            self.x = 0
    
    def Draw(self):
        SCREEN.blit(self.image, (self.x, self.y))
        SCREEN.blit(self.image, (self.x + self.width, self.y))

class Cloud:
    def __init__(self) -> None:
        self.x = SCREEN_WIDTH + random.randint(200, 700)
        self.y = SKY_Y
        self.image = CLOUD[0]
        self.width = self.image.get_width()
    
    def update(self):
        self.x -= GAME_SPEED
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(1000, 3000)
            self.y = random.randint(100,200)
        
    def Draw(self):
        SCREEN.blit(self.image, (self.x, self.y))




class Dinosour:
    GRAVITY_FPS = 8.5 * 0.0001 * (100 / FPS)
    MAX_VELOCITY = GRAVITY_FPS * (FPS / 4)
    def __init__(self):
        self.duck_img = DUCKING_IMG
        self.run_img = RUNNING_IMG
        self.jump_img = JUMPING_IMG
        self.x, self.y = 100, FLOOR_Y - RUNNING_IMG[0].get_height() + FLOOR_Y_OFFSET
        self.y_duck = self.y + 34
        self.jump_velocity = self.MAX_VELOCITY
        self.dino_bahavior = BEHAVIOR.RUNNING

        self.step_index = 0
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()

    def Rect(self):
        return self.dino_rect
    
    def update(self, userInput):
        if self.dino_bahavior == BEHAVIOR.DUCKING:
            self.duck()
        elif self.dino_bahavior == BEHAVIOR.RUNNING:
            self.run()
        elif self.dino_bahavior == BEHAVIOR.JUMPING:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0
        
        if userInput[pygame.K_UP] and (self.dino_bahavior == BEHAVIOR.RUNNING):
            self.dino_bahavior = BEHAVIOR.JUMPING
        
        elif userInput[pygame.K_DOWN] and (self.dino_bahavior == BEHAVIOR.RUNNING):
            self.dino_bahavior = BEHAVIOR.DUCKING
        
        elif self.dino_bahavior != BEHAVIOR.JUMPING and not userInput[pygame.K_DOWN]:
            self.dino_bahavior = BEHAVIOR.RUNNING

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.x
        self.dino_rect.y = self.y_duck
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.x
        self.dino_rect.y = self.y
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img[0]

        self.dino_rect.y -= self.jump_velocity * 1600
        self.jump_velocity -= self.GRAVITY_FPS

        if self.jump_velocity < -self.MAX_VELOCITY:
            self.dino_bahavior = BEHAVIOR.RUNNING
            self.jump_velocity = self.MAX_VELOCITY
            self.dino_rect.y = self.y
        

    def Draw(self):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

def main():
    global RUN, MAIN_RUN
    clock = pygame.time.Clock()
    player = Dinosour()
    cloud = Cloud()
    floor = BackGround()
    obstablemanager = ObstacleManager()
    scorerender = ScoreRender()

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
    
        SCREEN.fill((255,255,255))
        userInput = pygame.key.get_pressed()

        player.Draw()
        player.update(userInput)

        obstablemanager.Draw()
        obstablemanager.update()

        cloud.Draw()
        cloud.update()

        floor.Draw()
        floor.update()

        scorerender.Draw()
        scorerender.Update()

        clock.tick(FPS)
        pygame.display.update()

        obstablemanager.CollisionDetect(player.Rect())
        if not MAIN_RUN:
            break

def menu():
    global FIRST_START
    clock = pygame.time.Clock()
    if FIRST_START:
        SCREEN.fill((255,255,255))
        FIRST_START = False

    global RUN, MAIN_RUN
    while RUN:
        SCREEN.blit(RESET_IMG[0], ((SCREEN_WIDTH - RESET_IMG[0].get_width()) / 2 , SCREEN_HEIGHT * 0.8))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            if event.type == pygame.KEYDOWN:
                MAIN_RUN = True
                main()
        clock.tick(FPS)
        pygame.display.update()



menu()