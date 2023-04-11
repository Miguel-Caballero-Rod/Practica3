"""
sala.py este será el lugar dionde se conectaran los jugadores
"""

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
from random import random

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["LEFT", "RIGHT"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 30

NUM_ASTEROIDS = 20
HEIGHT_ASTEROID = 15
WIDTH_ASTEROID = 15
PLAYER_HEIGHT = 10
PLAYER_WIDTH = 60

def generate_aseroids(num_ast,manager):
    # list_asteroids = manager.list()
    list_asteroids = []
    for i in range(num_ast):
        x = random()
        y = random()
        ast = [x*SIZE[X],y*SIZE[Y]//3]
        list_asteroids.append(ast)
    return list_asteroids

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
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

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

    def collide_asteroid(self):
        self.bounce(Y)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos, self.velocity}>"
    
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
    def __init__(self, manager):
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        i = random()
        if i<0.5:
            j = 1
        else:
            j=-1
        
        self.ball = manager.list( [ Ball([2*j,3]) ] )
        self.vidas = manager.list([3,3])
        self.loser = Value('i', -1)
        self.running = Value('i', 1) # 1 running
        self.list_asteroids = manager.list([List_Asteroids(generate_aseroids(NUM_ASTEROIDS,manager))])

        self.lock = Lock()

    def get_player(self, side):
        return self.players[side]

    def get_ball(self):
        return self.ball[0]

    def get_vidas(self):
        return self.vidas
    
    def get_pos_asteroids(self):
        return self.list_asteroids[0]

    def get_loser(self):
        return self.loser
    
    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()

    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()

    def ball_collide_player(self):
        self.lock.acquire()
        ball = self.ball[0]
        ball.collide_player()
        self.ball[0] = ball
        self.lock.release()

    def ball_collide_asteroid(self):
        self.lock.acquire()
        ball = self.ball[0]
        ball.collide_asteroid()
        self.ball[0] = ball
        self.lock.release()

    def destroy_asteroid(self, asteroid):
        self.list_asteroids[0].remove(asteroid)

    def get_info(self):
        info = {
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'pos_ball': self.ball[0].get_pos(),
            'vidas': list(self.vidas),
            'loser': self.get_loser()   ,
            'list_asteroids': list(self.list_asteroids[0].get_pos()),
            'is_running': self.running.value == 1
        }
        return info

    def move_ball(self): #movements in basic.py
        self.lock.acquire()
        ball = self.ball[0]
        ball.update()
        pos = ball.get_pos()
        if pos[X]<0 or pos[X]>SIZE[X]:
            ball.bounce(X)
        if pos[Y]>SIZE[Y]:
            ball.bounce(Y)
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
        self.ball[0]=ball
        self.lock.release()


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball[0]}:{self.running.value}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "left":
                    game.moveLeft(side)
                elif command == "right":
                    game.moveRight(side)
                elif command == "collide_player":
                    game.ball_collide_player()
                elif command == "collide_asteroid":
                    game.ball_collide_asteroid()
                elif "destroy_asteroid" in command:
                    asteroid=list(map(float,command[18:-1].split(',')))
                    game.ball_collide_asteroid(asteroid)
                    if game.list_asteroids[0] == []:
                        game.loser=2
                        game.stop()
                elif command == "quit":
                    game.stop()
            if side == 1:
                game.move_ball()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)