'''
GENERAR ASTEROIDES: niveles de dificultad??
COLISIONES PELOTA-ASTERIODES
VIDAS??
'''
import time
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
PLAYER_COLOR = [GREEN, GREEN]
PLAYER_HEIGHT = 10
PLAYER_WIDTH = 60

BALL_COLOR = RED
BALL_SIZE = 10
FPS = 60
DELTA = 30

SIDES = ["LEFT", "RIGHT"]

NUM_ASTEROIDS = 20
HEIGHT_ASTEROID = 15
WIDTH_ASTEROID = 15

# Función para generar posiciones aleatorias de los asteroides a través de la librería random
def generate_aseroids(num_ast):
    list_asteroids = []
    for i in range(num_ast):
        x = random()
        y = random()
        ast = [x*SIZE[X],y*SIZE[Y]//3]
        list_asteroids.append(ast)
    return list_asteroids

# Clase del jugador, análoga a la del juego del ping-pong
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

    # En vez de moverse de arriba a abajo se mueve hacia los lados, sin poder sobrepasar la mitad correspondiente de la pantalla
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
            
    # Si colisiona con un asteroide rebota en el eje Y        
    def collide_asteroid(self):
        self.bounce(Y)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"

# Clase que guarda la lista de posiciones de los asteroides que quedan en pantalla
class List_Asteroids():
    def __init__(self, list_pos):
        self.list_pos = list_pos

    def get_pos(self):
        return self.list_pos

    def collide_ball(self, pos):
        self.list_pos.remove(pos)

    def __str__(self):
        return f"B<{self.list_pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        i = random()
        if i<0.5:
            j = 1
        else:
            j=-1
        self.ball = Ball([2*j,3])
        self.vidas = [3,3]
        self.loser=-1
        self.running = True
        self.list_asteroids = List_Asteroids(generate_aseroids(NUM_ASTEROIDS))  # Inicializa aleatorio

    def get_player(self, side):
        return self.players[side]

    def get_ball(self):
        return self.ball
        
    def get_vidas(self):
        return self.vidas
    
    def get_pos_asteroids(self):
        return self.list_asteroids

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
            if pos[X]>SIZE[X]//2:
                if self.vidas[0]==1:
                    self.loser=1
                    self.stop()
                else:
                    self.vidas[0]-=1
            else:
                if self.vidas[1]==1:
                    self.loser=0
                    self.stop()
                else:
                    self.vidas[1]-=1
        elif pos[Y]<0:
            self.ball.bounce(Y)

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}:{self.list_asteroids}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image=pygame.image.load('plataforma.png')
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT],-1)
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
        self.image=pygame.image.load('ball.png')
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE],-1)
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos

class AsteroidSprite(pygame.sprite.Sprite):
    def __init__(self, list_asteroids, pos):
        super().__init__()
        self.list_asteroids = list_asteroids
        self.pos = pos
        self.image= pygame.image.load('asteroide.png')
        pygame.draw.rect(self.image, WHITE, [0,0,WIDTH_ASTEROID, HEIGHT_ASTEROID],-1)
        self.rect = self.image.get_rect(center=pos)
        self.update()

    def update(self):  # sólo dibujamos en pantalla los asteroides que siguen en la lista de asteroides no colisionados
        if self.pos in self.list_asteroids.get_pos():
            self.rect.centerx, self.rect.centery = self.pos
        else:
            self.rect.centerx, self.rect.centery = 0,0

    def __str__(self):
        return f"S<{self.player}>"


class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        self.ball = BallSprite(self.game.get_ball())
        self.l_ast = self.game.get_pos_asteroids().get_pos()
        #inicializamos como lista de listas para luego analizar las colisiones con la función spritecollide
        self.list_asteroids = [[AsteroidSprite(self.game.get_pos_asteroids(), pos)] for pos in self.l_ast]
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.all_sprites.add(self.ball)
        for asteroid  in self.list_asteroids:
            self.all_sprites.add(asteroid[0])

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('im1.png')
        running = True
        pygame.init()

    def analyze_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.stop()
                elif event.key == pygame.K_a:
                    self.game.moveLeft(LEFT_PLAYER)
                elif event.key == pygame.K_s:
                    self.game.moveRight(LEFT_PLAYER)
                elif event.key == pygame.K_k:
                    self.game.moveLeft(RIGHT_PLAYER)
                elif event.key == pygame.K_l:
                    self.game.moveRight(RIGHT_PLAYER)
        if pygame.sprite.spritecollide(self.ball, self.paddle_group, False):
            self.game.get_ball().collide_player()
        for asteroid in self.list_asteroids:
            if pygame.sprite.spritecollide(self.ball, asteroid, False):
                # Si colisiona con algún asteroide, ese se elimina de la lista de sprites y de la lista de asteroides restantes
                self.game.get_ball().collide_player()
                self.list_asteroids.remove(asteroid)
                self.all_sprites.remove(asteroid[0])
        if self.list_asteroids == []:
            self.game.loser=2
            self.game.stop()
        self.all_sprites.update()

    def refresh(self,playing=True,loser=0):
        if playing:
            self.screen.blit(self.background, (0, 0))
            vidas = self.game.get_vidas()
            font = pygame.font.Font(None, 74)
            text = font.render(f"{vidas[RIGHT_PLAYER]}", 1, GREEN)
            self.screen.blit(text, (250, 10))
            text = font.render(f"{vidas[LEFT_PLAYER]}", 1, GREEN)
            self.screen.blit(text, (SIZE[X]-250, 10))
            self.all_sprites.draw(self.screen)
            pygame.display.flip()
        else:
            self.screen.blit(self.background, (0, 0))
            # Cuando acaba la partida, deendiendo del resultado, mostramos la imagen de victoria o derrota orrespondiente con pygame.image.load
            if loser !=2:
                game_over=pygame.image.load('game_over.png')
                self.screen.blit(game_over,(173,10))           
                font = pygame.font.Font(None, 74)
                text = font.render(f"LOST {SIDES[loser]} PLAYER", 1, GREEN)
                self.screen.blit(text, (100, SIZE[Y]//2))
            else:
                game_over=pygame.image.load('trofeo.png')
                self.screen.blit(game_over,(220,10))
                font = pygame.font.Font(None,74)
                text = font.render("YOU WIN!",1, YELLOW)
                self.screen.blit(text, (235, 300))
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
        # Una vez termine
        if game.loser!=-1:
            display.refresh(game.running, game.loser)
            time.sleep(3)
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
