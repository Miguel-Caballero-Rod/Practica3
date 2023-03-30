'''
GENERAR ASTEROIDES: niveles de dificultad??
COLISIONES PELOTA-ASTERIODES
VIDAS??

'''



import pygame
import sys, os
import socket
import pickle
from random import random

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 10
PLAYER_WIDTH = 60

BALL_COLOR = WHITE
BALL_SIZE = 10
FPS = 60
DELTA = 30

SIDES = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
            self.pos = [SIZE[X]//4, SIZE[Y]-10]
        else:
            self.pos = [3*SIZE[X]//4, SIZE[Y]-10]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveRight(self):
        self.pos[X] += DELTA
        if self.side == LEFT_PLAYER:
            if self.pos[X] > SIZE[X]//2-PLAYER_WIDTH//2:
                self.pos[X] = SIZE[X]//2-PLAYER_WIDTH//2
        else:
            if self.pos[X] > SIZE[X]-PLAYER_WIDTH//2:
                self.pos[X] = SIZE[X]-PLAYER_WIDTH//2

    def moveLeft(self):
        self.pos[X] -= DELTA
        if self.side == RIGHT_PLAYER:
            if self.pos[X] < SIZE[X]//2+PLAYER_WIDTH//2:
                self.pos[X] = SIZE[X]//2+PLAYER_WIDTH//2
        else:
            if self.pos[X] < 0+PLAYER_WIDTH//2:
                self.pos[X] = 0+PLAYER_WIDTH//2

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self, velocity):
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]
        self.velocity = velocity

    def get_pos(self):
        return self.pos

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self):
        self.bounce(Y)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        i = random()
        if i<0.5:
            j = 1
        else:
            j=-1
        self.ball = Ball([2*j,3])
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def get_ball(self):
        return self.ball

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def moveLeft(self, player):
        self.players[player].moveLeft()

    def moveRight(self, player):
        self.players[player].moveRight()

    def movements(self):
        self.ball.update()
        pos = self.ball.get_pos()
        if pos[X]<0 or pos[X]>SIZE[X]:
            self.ball.bounce(X)
        if pos[Y]>SIZE[Y]:
            self.ball.bounce(Y)
            # MENSAJE DE GAME OVER!!!!
            self.stop()
        elif pos[Y]<0:
            self.ball.bounce(Y)


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)#drawing the paddle
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos



class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]

        self.ball = BallSprite(self.game.get_ball())
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.all_sprites.add(self.ball)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        running = True
        pygame.init()

    def analyze_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.stop()
                elif event.key == pygame.K_s:
                    self.game.moveLeft(LEFT_PLAYER)
                elif event.key == pygame.K_x:
                    self.game.moveRight(LEFT_PLAYER)
                elif event.key == pygame.K_k:
                    self.game.moveLeft(RIGHT_PLAYER)
                elif event.key == pygame.K_m:
                    self.game.moveRight(RIGHT_PLAYER)
        if pygame.sprite.spritecollide(self.ball, self.paddle_group, False):
            self.game.get_ball().collide_player()
        self.all_sprites.update()



    def refresh(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

class Network:
    def __init__(self): ##this will connect to the server initially
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1' #server ip #<---
        self.port = 5555   #server port #<---
        self.addr = (self.server, self.port)
        self.p = self.connect()
    def getP(self):
        return self.p
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)



def main():
    try:
        game = Game()
        display = Display(game)

        while game.is_running():
            game.movements()
            display.analyze_events()
            display.refresh()
            display.tick()
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
