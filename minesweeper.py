import time
import os
import curses
import random

clear = lambda : os.system('cls' if os.name == 'nt' else 'clear')

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def format_cell(cursor, current_coords, val):
    return f"[{val}]" if cursor[0] == current_coords[0] and cursor[1] == current_coords[1] else f" {val} "

## // CONFIG //

width = 20
height = 20
mines = 50

## // INIT //

start_time = time.time()
death_time = -1
cursor = [0, 0]
running = True

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
        
        self.field = [[self.surrounding((x, y)) for x in range(width)] for y in range(height)]
        
        self.opened = []
        
        self.flags = []
    
    def surrounding(self, coords):
        if coords in self.mines:
            return "#"
        else:
            total = 0
            for y in range(coords[1]-1, coords[1]+2):
                for x in range(coords[0]-1, coords[0]+2):
                    if (x, y) in self.mines:
                        total += 1
            return total or " "
        
    def open_cell(self, coords): # check if other cells can be opened automatically
        if not coords in self.opened and not coords in self.flags:
            if coords in self.mines:
                global running, death_time
                self.opened.append(coords)
                death_time = round(time.time()-start_time)
                running = False
            else:
                self.opened.append(coords)
                if self.field[coords[1]][coords[0]] == " ":
                    for y in range(coords[1]-1, coords[1]+2):
                        for x in range(coords[0]-1, coords[0]+2):
                            if x >= 0 and x < width and y >= 0 and y < height and not (x, y) in self.opened:
                                if self.field[y][x] == " ":
                                    self.open_cell((x, y))
                                else:
                                    self.opened.append((x, y))
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "".join(["".join([format_cell(cursor, (x, y), "⚑" if (x, y) in self.flags else (self.field[y][x] if (x, y) in self.opened or not running else cell)) for x, cell in enumerate(line)])+"\n" for y, line in enumerate(self.board)])+f"\n{f"{max(0, mines-len(board.flags))} mines • {round(time.time()-start_time) if running else death_time}s{"" if running else " • lol you dead"}": ^{width*3}}"

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
            elif running:
                if key == " ":
                    board.open_cell(tuple(cursor))
                if key == "e":
                    coords = (cursor[0], cursor[1])
                    if coords in board.flags:
                        board.flags.remove(coords)
                    elif not coords in board.opened:
                        board.flags.append(coords)

            if key == os.linesep:
                break
        except Exception as e:
            pass
        
        win.clear()
        win.addstr(str(board))

curses.wrapper(main)