from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
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
SIDESSTR = ["LEFT", "RIGHT"]

# NUM_ASTEROIDS = 20
# HEIGHT_ASTEROID = 15
# WIDTH_ASTEROID = 15

# def generate_aseroids(num_ast):
#     list_asteroids = []
#     for i in range(num_ast):
#         x = random()
#         y = random()
#         ast = [x*SIZE[X],y*SIZE[Y]//3]
#         list_asteroids.append(ast)
#     return list_asteroids

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self):
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"
    
# class List_Asteroids():
#     def __init__(self, list_pos):
#         #mirar como debemos iniciar este
#         self.list_pos = list_pos

#     def get_pos(self):
#         return self.list_pos

#     def collide_ball(self, pos):
#         self.list_pos.remove(pos)

#     def __str__(self):
#         return f"B<{self.list_pos}>"

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ball = Ball()
        #OBS: la bola se inicializa sin velocidad, luego no se decide aqui -> se puede hacer aleatorio
        self.vidas = [3,3]
        self.loser = -1
        self.running = True
        # self.list_asteroids = List_Asteroids(generate_aseroids(NUM_ASTEROIDS)) #TODO revisar como inciar este atributo

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_ball(self):
        return self.ball
    
    def set_ball_pos(self, pos):
        self.ball.set_pos(pos)

    def get_vidas(self):
        return self.vidas

    def set_vidas(self, vidas):
        self.vidas = vidas

    def get_loser(self):
        return self.loser
    
    def set_loser(self, loser):
        self.loser = loser
    
    # def get_pos_asteroids(self):
    #     return self.list_asteroids
    
    # def set_pos_asteroids(self, asteroids):
    #     self.list_asteroids = asteroids


    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos(gameinfo['pos_ball'])
        self.set_loser(gameinfo['loser'])
        self.set_vidas(gameinfo['vidas'])
        # self.set_pos_asteroids(gameinfo['list_asteroids'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


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

# class AsteroidSprite(pygame.sprite.Sprite):
#     def __init__(self, list_asteroids, pos):
#         super().__init__()
#         self.list_asteroids = list_asteroids
#         self.pos = pos
#         self.image= pygame.image.load('asteroide.png')
#         pygame.draw.rect(self.image, WHITE, [0,0,WIDTH_ASTEROID, HEIGHT_ASTEROID],-1)
#         self.rect = self.image.get_rect(center=pos)
#         self.update()

    # def update(self):
    #     if self.pos in self.list_asteroids.get_pos():
    #         self.rect.centerx, self.rect.centery = self.pos
    #     else:
    #         self.rect.centerx, self.rect.centery = 0,0

    # def __str__(self):
    #     return f"S<{self.player}>"



class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        self.ball = BallSprite(self.game.get_ball())
        # self.l_ast = self.game.get_pos_asteroids().get_pos()
        # self.list_asteroids = [[AsteroidSprite(self.game.get_pos_asteroids(), pos)] for pos in self.l_ast]
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.all_sprites.add(self.ball)
        # for asteroid  in self.list_asteroids:
            # self.all_sprites.add(asteroid[0])

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('im1.png')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
            elif event.type == pygame.QUIT:
                events.append("quit")
        if pygame.sprite.collide_rect(self.ball, self.paddles[side]):
            events.append("collide_player")
        # for asteroid in self.list_asteroids:
            # if pygame.sprite.spritecollide(self.ball, asteroid, False):
            #     events.append("collide_asteroid")
                # events.append(f"destroy_asteroid {asteroid}")
                # self.all_sprites.remove(asteroid[0])
        return events


    def refresh(self,playing=True,loser=0):
        self.all_sprites.update()
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


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)