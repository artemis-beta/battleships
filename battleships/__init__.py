import string

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging
logger = logging.getLogger('Battleships')
logging.basicConfig()
logger.setLevel('INFO')

class Board(object):
    def __init__(self, width, height):
        self.board    = [['O' for i in range(width)] for j in range(height)]
    def __repr__(self):
        out_str = '\t{}\n'.format(' '.join(string.ascii_uppercase[:10]))
        for i, row in enumerate(self.board):
            out_str += '{}\t{}\n'.format(i+1,' '.join(row))
        return out_str

    def place_ship(self,ship):
        x_0 = ship.coordinates[0][0]
        y_0 = ship.coordinates[0][1]
        x_i = ship.coordinates[1][0]
        y_i = ship.coordinates[1][1]
        try: 
             self.board[x_0][y_0]
             self.board[x_i][y_i]
             self.board[x_0][y_i]
             self.board[x_i][y_0]
        except:
            logger.debug("Unable to place ship '%s' here, are the coordinates within the game grid?", ship.name)
            return False
        try:
            assert ship.ship_array, ""
        except:
            logger.debug("No Ship Array exists for ship '%s'", ship.name)
            return False

        for i, row in enumerate(ship.ship_array):
            for j, column in enumerate(row):
                try:
                    self.board[x_0+i][y_0+j]
                    ship.ship_array[i][j]
                    assert self.board[x_0+i][y_0+j] not in [u'\u25C0' ,
                                                            u'\u2610' ,
                                                            u'\u25B6' ,
                                                            u'\u25B2' ,
                                                            u'\u25BC' ]
                except:
                    return False
                
        for k, row in enumerate(ship.ship_array):
            for m, column in enumerate(row):
                self.board[x_0+k][y_0+m] = ship.ship_array[k][m]            

        return True

class Ship(object):
    def __init__(self, length, name='ship'):
        self.length      = length
        self.coordinates = []
        self.orientation = None
        self.name = name
        self.health = self.length

    def _make_array(self):
       out_array = []
       try:
           assert self.orientation.lower(), ""
       except:
           logger.debug("Ship '%s' has no set orientation", self.name)

       if self.orientation.lower() in ['h', 'horizontal']:
           out_array.append([])
           out_array[0].append(u'\u25c0')
           for i in range(self.length-2):
               out_array[0].append(u'\u2610')
           out_array[0].append(u'\u25B6')
           return out_array

       elif self.orientation.lower() in ['v', 'vertical']:
           out_array.append([u'\u25B2'])
           for i in range(self.length-2):
               out_array.append([u'\u2610'])
           out_array.append([u'\u25BC'])
           return out_array

     
       else:
           return None

    def place(self, x, y, orient):
        if orient.lower() in ['h', 'horizontal']:
            self.coordinates = [(x,y), (x+self.length, y)]
            self.orientation = orient
        elif orient.lower() in ['v', 'vertical']:
            self.coordinates = [(x,y), (x, y+self.length)]
            self.orientation = orient
        else:
            logger.debug("Invalid argument given for 'orientation', options are (v/h).")
            return

        self.ship_array = self._make_array()

class Game(object):
    board_instance_ai = Board(10,10)
    board_instance_user = Board(10,10)
    def __init__(self):
        self.ships = { 'Carrier'    : {'ship' : Ship(5, 'Carrier') }    ,
                       'Battleship' : {'ship' : Ship(4, 'Battleship')}  ,
                       'Cruiser'    : {'ship' : Ship(3, 'Cruiser')}     ,
                       'Submarine'  : {'ship' : Ship(3, 'Submarine')}   ,
                       'Destroyer'  : {'ship' : Ship(2, 'Destroyer')}   }
        self.user_hits = []
    def _ai_ship_place(self):
        import random
        for ship in self.ships.keys():
            place_successful = False
            while not place_successful:
                x = random.randint(0,9)
                y = random.randint(0,9)
                direc = random.choice(['h','v'])
                self.ships[ship]['occupied'] = []
                if direc == 'h':
                    for i in range(x,x+self.ships[ship]['ship'].length):
                        self.ships[ship]['occupied'].append([i,y])
                else:
                    for j in range(y,y+self.ships[ship]['ship'].length):
                        self.ships[ship]['occupied'].append([x,j])
                self.ships[ship]['ship'].place(y,x,direc)
                place_successful = self.board_instance_ai.place_ship(self.ships[ship]['ship'])

    def _get_response(self, x, y):
        self.user_hits.append([y,x])
        if self.board_instance_ai.board[x][y] != 'O':
            for ship in [s for s in self.ships.keys() if len(self.ships[s]['occupied']) > 0]:
                if [y,x] in self.ships[ship]['occupied']:
                    self.ships[ship]['occupied'].remove([y,x])
                    if len(self.ships[ship]['occupied']) < 1:
                        print("HIT AND DESTROYED!")
                        break
                    else:
                        print("HIT!")
                        break
            self.board_instance_user.board[x][y] = u'\u272d'
        else:
            print("You missed!")
            self.board_instance_user.board[x][y] = 'X'
        print self.board_instance_user

    def start(self):
        print("Welcome to Battleships! Try Firing at your Computer Opponent's Armada.")
        turns = 20
        while turns > 0:
            y_valid = False
            x_valid = False
            while not y_valid:
                y = raw_input("COLUMN:")
                if y.upper() in ['Q', 'QUIT']:
                    return
                try:
                    y = string.ascii_uppercase[:10].index(y.upper())
                    y_valid = True
                except:
                   print("Invalid input, column must be a valid letter A-J!")
                   continue 
            while not x_valid:
                x = raw_input("ROW:")
                if x.upper() in ['Q', 'QUIT']:
                    return
                try:
                    assert int(x) < 11
                    x_valid = True
                except:
                    print("Invalid input, row must be an integer between 1-10")
                    continue
            self._get_response(int(x)-1,y)
            turns -= 1
        print self.board_instance_ai
        print("Game Over.")

if __name__ in "__main__":
   game  = Game()
   game._ai_ship_place()
   game.start()
