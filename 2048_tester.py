#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 11:53:16 2022

@author: tarabogavelli
"""

from BaseAI import BaseAI
import random
import sys
import math
import time
from Grid       import Grid
from ComputerAI import ComputerAI
from Displayer  import Displayer
import heapq

"""w1 = 0
w2 = 0
w3 = 0
w4 = 0"""

d = 0
start = 0
class IntelligentAgent(BaseAI):
    
    def get_monotonic_score(self, grid):
        cols = []
        for x in range(4):
           col = [row[x] for row in grid.map]
           cols.append(col)
        row_dec_score, row_inc_score, col_dec_score, col_inc_score = 0,0,0,0
        for row in grid.map:
            if all(row[i] <= row[i+1] for i in range(len(row) - 1)):
                row_inc_score += 1
            elif all(row[i] >= row[i+1] for i in range(len(row) - 1)):
                row_dec_score += 1
        for col in cols:
            if all(col[i] <= col[i+1] for i in range(len(col) - 1)):
                col_inc_score += 1
            elif all(col[i] >= col[i+1] for i in range(len(col) - 1)):
                col_dec_score += 1
        return max(col_dec_score, col_inc_score) + max(row_dec_score, row_inc_score)
    
    def get_free_score(self, grid):
        return len(grid.getAvailableCells())
    
    def get_moves_score(self, grid):
        return len(grid.getAvailableMoves())
    
    def get_tiles_score(self, grid):
        total = 0
        for row in grid.map:
            for item in row:
                total += item
        avg = total/16
        return math.log2(avg)
            

    def evaluate(self, grid, w1, w2, w3, w4):

        monoton = self.get_monotonic_score(grid)
        free = self.get_free_score(grid)
        avg_tile = self.get_tiles_score(grid)
        moves = self.get_moves_score(grid)
        return w1*monoton + w2*free + w3*moves + w4*avg_tile
    
    def terminal(self, grid):
        cur_time = time.process_time()
        print(cur_time, start, cur_time-start)
        if cur_time-start > 0.18:
            print("too much time")
            return True
        if grid.canMove() == False:
            return True
        else:
            return False
    
    def minimize(self, grid, alpha, beta, value, depth, w1, w2, w3, w4):
        if self.terminal(grid):
            return (None, self.evaluate(grid, w1, w2, w3, w4))
        if depth > 5:
            return(grid, self.evaluate(grid, w1, w2, w3, w4))
        global d
        d += 1
        options = grid.getAvailableCells()
        cur_min_val = sys.maxsize
        cur_min_grid = grid
        for option in options:
            copy = grid.clone()
            copy.insertTile(option,value)
            val = self.maximize(grid, alpha, beta, d, w1, w2, w3, w4)[1]
            if val < cur_min_val:
                cur_min_grid = copy
                cur_min_val = val
            if cur_min_val <= alpha:
                break
            if cur_min_val < beta:
                beta = cur_min_val
        
        return (cur_min_grid, cur_min_val)
            
    def chance(self, grid, alpha, beta, depth, w1, w2, w3, w4):
        two = self.minimize(grid, alpha, beta, 2, depth, w1, w2, w3, w4)
        four = self.minimize(grid, alpha, beta, 4, depth, w1, w2, w3, w4)
        return two[1]*0.9+four[1]*0.1
        
        
    def maximize(self, grid, alpha, beta, depth, w1, w2, w3, w4):
        if depth > 5:
            return(grid, self.evaluate(grid, w1, w2, w3, w4 ))
        if self.terminal(grid):
            return (None, self.evaluate(grid, w1, w2, w3, w4))
        cur_max = (None, -1*sys.maxsize)
        maxUtility = cur_max[1]
        
        moves = grid.getAvailableMoves()
        global d
        d += 1

        best_move = None
        for move in moves:
            child = move[1]
            utility = self.chance(child, alpha, beta, d, w1, w2, w3, w4)
            
            if utility > maxUtility:
                cur_max = (child, utility)
                maxUtility = cur_max[1]
                best_move = move[0]
            if maxUtility >= beta:
                break
            if maxUtility > alpha:
                alpha = maxUtility
        return (cur_max, maxUtility, best_move)
    

    def getMove(self, grid, w1, w2, w3, w4):
        global start
        start = time.process_time()

        move = self.maximize(grid, -1 * sys.maxsize, sys.maxsize, 0, w1, w2, w3, w4)[2]
        stop = time.process_time()
        if stop-start > 0.2:
            print("FAILURE")
        return move
    
    """def terminal(self, grid):
        if grid.canMove() == False:
            return True
        else:
            return False
    
    def minimize(self, grid, alpha, beta, value, w1, w2, w3, w4):
        options = grid.getAvailableCells()
        cur_min_val = sys.maxsize
        cur_min_grid = grid
        for option in options:
            copy = grid.clone()
            copy.insertTile(option,value)
            val = self.evaluate(copy, w1, w2, w3, w4)
            if val < cur_min_val:
                cur_min_grid = copy
                cur_min_val = val
            if cur_min_val <= alpha:
                break
            if cur_min_val < beta:
                beta = cur_min_val
        
        return (cur_min_grid, cur_min_val)
            
    def chance(self, grid, alpha, beta, w1, w2, w3, w4):
        two = self.minimize(grid, alpha, beta, 2, w1, w2, w3, w4)
        four = self.minimize(grid, alpha, beta, 4, w1, w2 ,w3, w4)
        return two[1]*0.9+four[1]*0.1
        
        
    def maximize(self, grid, alpha, beta, w1, w2, w3, w4):
        if self.terminal(grid):
            return (None, self.evaluate(grid, w1, w2, w3, w4))
        cur_max = (None, -1*sys.maxsize)
        maxUtility = cur_max[1]
        
        moves = grid.getAvailableMoves()

        best_move = None
        for move in moves:
            child = move[1]
            utility = self.chance(child, alpha, beta, w1, w2, w3, w4)
            
            if utility > maxUtility:
                cur_max = (child, utility)
                maxUtility = cur_max[1]
                best_move = move[0]
            if maxUtility >= beta:
                break
            if maxUtility > alpha:
                alpha = maxUtility
        return (cur_max, maxUtility, best_move)
    

    def getMove(self, grid, w1, w2, w3, w4):

        start = time.process_time()

        move = self.maximize(grid, -1 * sys.maxsize, sys.maxsize, w1, w2, w3, w4)[2]
        stop = time.process_time()
        if stop-start > 0.2:
            print("FAILURE")
        return move"""
defaultInitialTiles = 2
defaultProbability  = 0.9

actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT",
    None: "NONE" # For error logging
}

(PLAYER_TURN, COMPUTER_TURN) = (0, 1)

# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05
maxTime   = timeLimit + allowance

class GameManager:
    def __init__(self, size=4, intelligentAgent=None, computerAI=None, displayer=None):
        self.grid = Grid(size)
        self.possibleNewTiles = [2, 4]
        self.probability = defaultProbability
        self.initTiles   = defaultInitialTiles
        self.over        = False

        # Initialize the AI players
        self.computerAI = computerAI or ComputerAI()
        self.intelligentAgent   = intelligentAgent   or IntelligentAgent()
        self.displayer  = displayer  or Displayer()

    def updateAlarm(self) -> None:
        """ Checks if move exceeded the time limit and updates the alarm """
        if time.process_time() - self.prevTime > maxTime:
            self.over = True
        
        self.prevTime = time.process_time()

    def getNewTileValue(self) -> int:
        """ Returns 2 with probability 0.95 and 4 with 0.05 """
        return self.possibleNewTiles[random.random() > self.probability]

    def insertRandomTiles(self, numTiles:int):
        """ Insert numTiles number of random tiles. For initialization """
        for i in range(numTiles):
            tileValue = self.getNewTileValue()
            cells     = self.grid.getAvailableCells()
            cell      = random.choice(cells) if cells else None
            self.grid.setCellValue(cell, tileValue)

    def start(self, w1, w2, w3, w4) -> int:
        """ Main method that handles running the game of 2048 """

        # Initialize the game
        self.insertRandomTiles(self.initTiles)
        #self.displayer.display(self.grid)
        turn          = PLAYER_TURN # Player AI Goes First
        self.prevTime = time.process_time()

        while self.grid.canMove() and not self.over:
            # Copy to Ensure AI Cannot Change the Real Grid to Cheat
            gridCopy = self.grid.clone()

            move = None

            if turn == PLAYER_TURN:
                #print("Player's Turn: ", end="")
                move = self.intelligentAgent.getMove(gridCopy, w1, w2, w3, w4)
                
                #print(actionDic[move])

                # If move is valid, attempt to move the grid
                if move != None and 0 <= move < 4:
                    if self.grid.canMove([move]):
                        self.grid.move(move)

                    else:
                        #print("Invalid intelligentAgent Move - Cannot move")
                        self.over = True
                else:
                    #print("Invalid intelligentAgent Move - Invalid input")
                    self.over = True
            else:
                #print("Computer's turn: ")
                move = self.computerAI.getMove(gridCopy)

                # Validate Move
                if move and self.grid.canInsert(move):
                    self.grid.setCellValue(move, self.getNewTileValue())
                else:
                    #print("Invalid Computer AI Move")
                    self.over = True

            # Comment out during heuristing optimizations to increase runtimes.
            # Printing slows down computation time.
            #self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm()
            turn = 1 - turn

        return self.grid.getMaxTile()
def main():
    print("here")
    intelligentAgent = IntelligentAgent()
    computerAI  = ComputerAI()
    displayer   = Displayer()
    #gameManager = GameManager(4, intelligentAgent, computerAI, displayer)
    maxes = []
    max_average = 0
    weights = {'w1': None,
               'w2': None,
               'w3': None,
               'w4': None}
    w1 = w2 = w3= w4 = 0
    counter = 0
    # add cutoff at certain point, like if max of the things you've seen on the ith iteration is not 1024 give up?
    for x1 in range(0,11):
        
        for x2 in range(0,11-x1):
            
            for x3 in range(0,11-x1-x2):
                counter += 1
                x4 = 10-x1-x2-x3
                
                w1 = x1/10
                w2 = x2/10
                w3 = x3/10
                w4 = x4/10
                print(counter, ": ", w1,w2,w3,w4)
                maxes.clear()
                for i in range(10):
                    gameManager = GameManager(4, intelligentAgent, computerAI, displayer)
                    maxTile     = gameManager.start(w1, w2, w3, w4)
                    print("MAXTILE: ", maxTile)
                    maxes.append(maxTile)
                if sum(maxes)/len(maxes) > max_average:
                    max_average = sum(maxes)/len(maxes)
                    weights.clear()
                    weights['w1'] = w1
                    weights['w2'] = w2
                    weights['w3'] = w3
                    weights['w4'] = w4
                    print(max_average)
                    print(weights)
    print(weights)
    print(max_average)
                
    #print("counter: ", counter)
    
    
    """
    for i in range(10):
        w1 += 0.1
        # if w1 < 1: w1+=0.1
        # w2 = 0
        # break if sum of weights
        for j in range(10):
            w2 += 0.1
            #if w2 < 1-w1: w2 += 0.1
            #w3 = 0
            # break if sum of weights
            for k in range(10):
                w3 += 0.1
                #w4 = 0
                # break if sum of weights
                for l in range(10):
                    w4 += 0.1
                    #w4 = 1-w2-w3-w1
                    # break if sum of weights >= 1
                    maxes.clear()
                    # actually do the game
                    for i in range(10):
                        gameManager = GameManager(4, intelligentAgent, computerAI, displayer)
                        maxTile     = gameManager.start(w1, w2, w3, w4)
                        print("MAXTILE: ", maxTile)
                        maxes.append(maxTile)
                    if sum(maxes)/len(maxes) > max_average:
                        max_average = sum(maxes)/len(maxes)
                        weights.clear()
                        weights['w1'] = w1
                        weights['w2'] = w2
                        weights['w3'] = w3
                        weights['w4'] = w4
                        print(max_average)
                        print(weights)
                        
    print(weights)
    print(max_average)"""
                    
    f"""or i in range(10):
        gameManager = GameManager(4, intelligentAgent, computerAI, displayer)
        maxTile     = gameManager.start(w1, w2, w3, w4)
        print("MAXTILE: ", maxTile)
        maxes.append(maxTile)
    print(heapq.nlargest(5, maxes))
    return sum(maxes)/len(maxes)"""
if __name__ == '__main__':
    main()

