import time
import os
import curses
import random
import logging

logging.basicConfig(filename='./temp.log', level=logging.DEBUG, 
format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

clear = lambda : os.system('cls' if os.name == 'nt' else 'clear')

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def format_cell(cursor, current_coords, val):
    return f"[{val}]" if cursor[0] == current_coords[0] and cursor[1] == current_coords[1] else f" {val} "

def lists_equal(A, B):
    for _,obj in enumerate(A):
        if not obj in B:
            return False
    return True

## // CONFIG //

width = 20
height = 20
mines = 50

## // INIT //

start_time = time.time()
stop_time = -1
cursor = [0, 0]
state = "running" # dead or win

class Board:
    def __init__(self):
        self.board = [["■" for x in range(width)] for y in range(height)]
        
        self.mines = []
        
        for _ in range(mines):
            while True:
                coords = (random.randint(0, width-1), random.randint(0, height-1))
                if not coords in self.mines:
                    self.mines.append(coords)
                    break
        
        self.field = [[self.surrounding_mines((x, y)) for x in range(width)] for y in range(height)]
        
        self.opened = []
        
        self.flags = []
    
    def surrounding_mines(self, coords):
        if coords in self.mines:
            return "#"
        else:
            total = 0
            for y in range(coords[1]-1, coords[1]+2):
                for x in range(coords[0]-1, coords[0]+2):
                    if (x, y) in self.mines:
                        total += 1
            return total or " "
    
    def surrounding_flags(self, coords):
        flags = 0
        for y in range(coords[1]-1, coords[1]+2):
            for x in range(coords[0]-1, coords[0]+2):
                if (x, y) in self.flags:
                    flags += 1
        return flags
    
    def check_death(self, coords):
        if coords in self.mines:
            global state, stop_time
            stop_time = round(time.time()-start_time)
            state = "dead"
    
    def open_cell(self, coords): # lower level, opens a single cell
        self.check_death(coords)
        self.opened.append(coords)
    
    def open_surrounding(self, coords):
        for y in range(coords[1]-1, coords[1]+2):
            for x in range(coords[0]-1, coords[0]+2):
                if x >= 0 and x < width and y >= 0 and y < height and not (x, y) in self.opened:
                    if self.field[y][x] == " ":
                        self.invoke_open((x, y))
                    elif not (x, y) in self.flags:
                        self.open_cell((x, y))
        
    def invoke_open(self, coords): # check if other cells can be opened automatically
        fieldValue = self.field[coords[1]][coords[0]]
        if not coords in self.flags:
            if not coords in self.opened:
                self.open_cell(coords)
            if state == "running" and (fieldValue == " " or (type(fieldValue) == int and self.surrounding_flags(coords) == fieldValue)):
                self.open_surrounding(coords)
    
    def check_win(self):
        if len(self.flags) == mines and lists_equal(self.mines, self.flags):
            global state, stop_time
            stop_time = round(time.time()-start_time)
            state = "win"
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "".join(["".join([format_cell(cursor, (x, y), "⚑" if (x, y) in self.flags else (self.field[y][x] if (x, y) in self.opened or state == "dead" else cell)) for x, cell in enumerate(line)])+"\n" for y, line in enumerate(self.board)])+f"\n{f"{max(0, mines-len(board.flags))} mines • {round(time.time()-start_time) if state == "running" else stop_time}s{"" if state == "running" else " • yayyy you win!!!" if state == "win"  else " • lol you dead"}": ^{width*3}}"

board = Board()

mv_keys = {
    "KEY_LEFT": (-1, 0),
    "KEY_UP": (0, -1),
    "KEY_RIGHT": (1, 0),
    "KEY_DOWN": (0, 1),
}

## // RUNTIME //

def main(win):
    win.nodelay(True)
    key=""
    win.clear()
    win.addstr(str(board))
    while True:
        try:
            key = win.getkey()
            if key in mv_keys:
                direction = mv_keys[key]
                cursor[0] = clamp(cursor[0] + direction[0], 0, width-1)
                cursor[1] = clamp(cursor[1] + direction[1], 0, height-1)
            elif state == "running":
                if key == " ":
                    board.invoke_open(tuple(cursor))
                if key == "e":
                    coords = (cursor[0], cursor[1])
                    if coords in board.flags:
                        board.flags.remove(coords)
                    elif not coords in board.opened:
                        board.flags.append(coords)
                        board.check_win()

            if key == os.linesep:
                break
        except Exception as e:
            pass
        
        win.clear()
        win.addstr(str(board))

curses.wrapper(main)