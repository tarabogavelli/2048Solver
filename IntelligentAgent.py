#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 13:38:14 2022

@author: tarabogavelli
"""

from BaseAI import BaseAI
#import random
import sys
import math
import time

w1 = 0.25
w2 = 0.35
w3 = 0.2
w4 = 0.2
#d = 0
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
    def get_corner_score(self, grid):
        max_tile = grid.getMaxTile()

        tl = grid.getCellValue((0,0)) 
        tr = grid.getCellValue((0,3))
        bl = grid.getCellValue((3,0))
        br = grid.getCellValue((3,3))
        
        score = 0
        if max_tile >= 128:
            if tl == max_tile or tr == max_tile or br == max_tile or bl == max_tile:
                score += 5
        return score
    
    def get_adjacent_score(self, grid):
        copy = grid.clone()
        score = 0
        maxTile = copy.getMaxTile()
        maxPosition = None
        colCounter = -1
        rowCounter = -1
        for row in copy.map:
            colCounter += 1
            rowCounter = -1
            for item in row:
                rowCounter += 1
                if item == maxTile:
                    maxPosition = (rowCounter, colCounter)
        copy.setCellValue(maxPosition, 0)
        secondMax = copy.getMaxTile()
        secondMaxPos = None
        colCounter = -1
        rowCounter = -1
        for row in copy.map:
            colCounter += 1
            rowCounter = -1
            for item in row:
                rowCounter += 1
                if item == secondMax:
                    secondMaxPos = (rowCounter, colCounter)
        if (abs(secondMaxPos[0]-maxPosition[0]) == 1 and secondMaxPos[1] == maxPosition[1]) or (abs(secondMaxPos[1]-maxPosition[1])==1 and secondMaxPos[0] == maxPosition[0]):
            score = 3
        return score
            
        """
        (0,0) (1,0) (2,0) (3,0) 
        (0,1) (1,1) (2,1) (3,1) 
        (0,2) (1,2) (2,2) (3,2) 
        (0,3) (1,3) (2,3) (3,3) 
        """
        
        

    def evaluate(self, grid, w1, w2, w3, w4):

        monoton = self.get_monotonic_score(grid)
        free = self.get_free_score(grid)
        avg_tile = self.get_tiles_score(grid)
        moves = self.get_moves_score(grid)
        corner = self.get_corner_score(grid)
        adjacent = self.get_adjacent_score(grid)
        return w1*monoton + w2*free + w3*moves + w4*avg_tile +0.2*corner+0.2*adjacent
    
    def terminal(self, grid):
        cur_time = time.process_time()

        if cur_time-start > 0.185:
            #print("too much time", cur_time-start)
            return True
        if grid.canMove() == False:
            return True
        else:
            return False
    
    def minimize(self, grid, alpha, beta, value, depth):

        if depth > 3:
            return(grid, self.evaluate(grid, w1, w2, w3, w4))
        depth += 1
        if self.terminal(grid):
            return (None, self.evaluate(grid, w1, w2, w3, w4))

        
        options = grid.getAvailableCells()
        cur_min_val = sys.maxsize
        cur_min_grid = grid
        for option in options:
            copy = grid.clone()
            copy.insertTile(option,value)
            val = self.maximize(copy, alpha, beta, depth)[1]
            if val < cur_min_val:
                cur_min_grid = copy
                cur_min_val = val
            if cur_min_val <= alpha:
                break
            if cur_min_val < beta:
                beta = cur_min_val
        
        return (cur_min_grid, cur_min_val)
            
    def chance(self, grid, alpha, beta, depth):
        two = self.minimize(grid, alpha, beta, 2, depth)
        four = self.minimize(grid, alpha, beta, 4, depth)
        return two[1]*0.9+four[1]*0.1
        
        
    def maximize(self, grid, alpha, beta, depth):

        if depth > 3:
            return(grid, self.evaluate(grid, w1, w2, w3, w4 ))
        depth += 1
        if self.terminal(grid):
            return (None, self.evaluate(grid, w1, w2, w3, w4))
        cur_max = (None, -1*sys.maxsize)
        maxUtility = cur_max[1]
        
        moves = grid.getAvailableMoves()


        best_move = None
        for move in moves:
            child = move[1]
            utility = self.chance(child, alpha, beta, depth)
            
            if utility > maxUtility:
                cur_max = (child, utility)
                maxUtility = cur_max[1]
                best_move = move[0]
            if maxUtility >= beta:
                break
            if maxUtility > alpha:
                alpha = maxUtility
        return (cur_max, maxUtility, best_move)
    

    def getMove(self, grid):
        global start
        start = time.process_time()

        move = self.maximize(grid, -1 * sys.maxsize, sys.maxsize, 0)[2]
        stop = time.process_time()
        #print("TIME: ", stop-start)
        #if stop-start > 0.2:
            #print("FAILURE")
        return move
        
        
        
        """moveset = grid.getAvailableMoves()
        #print(moveset)
        return random.choice(moveset)[0] if moveset else None"""
    