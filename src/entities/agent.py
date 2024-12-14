from ..utils import GameConfig, clamp
from .entity import Entity
import random
from ast import literal_eval
import numpy as np
import pandas as pd
import itertools
import os.path

class Agent(Entity):
    QTable = None
    NTable = None

    def __init__(self, config: GameConfig, player, pipes) -> None:
        self.hello = "hi"
        # print(np.__version__)
        # print(pd.__version__)
        self.xinterpolatelength = 30
        # If a previous qsa table is not present, initialize a new one
        if not os.path.isfile("qsa.csv"):
            print("Making a new Q table")
            self.initializeWeights()
        self.player, self.pipes = player, pipes
        
        #Read in csv into a pandas dataframe
        self.QTable = pd.read_csv("qsa.csv", index_col="SA")
        #Need to convert the string state action paris into tuples, and use them as the "keys"
        self.QTable.index = pd.Index([literal_eval(strSA) for strSA in self.QTable.index])
        # Get a series with the Q values
        self.QTable = self.QTable["Q"]
    
    def saveQ(self):
        # Convert into dataframe
        df = self.QTable.to_frame("Q")
        # Map state action pairs back into strings
        df.index = [str(tupSA) for tupSA in df.index]
        # Save as csv with same structure
        df.to_csv(path_or_buf="qsa.csv", header=["Q"], index_label=["SA"])

    def getInterpolatedState(self):
        #First find the current pipe (Flappy's x position is always x=53, so find the first pipe in front of flappy)
        if self.pipes.upper[0].x > 53:
            currpipe = self.pipes.upper[0]
        else:
            currpipe = self.pipes.upper[1]

        # Find Flappy'svelocity (can range from -9 to 10, interpolating into 5 states ranging from -2 to 2)   
        vel = self.player.vel_y
        if vel < -5:
            vel = -2
        elif vel < 0:
            vel = -1
        elif vel == 0:
            vel
        elif vel > 5:
            vel = 2
        else:
            vel = 1

        #Find whether flappy is above, between-upper, between-center, between-lower, or below pipe
        pos = self.findFlappyPos(currpipe)

        #pipex should be between 53 and 298, interpolating into buckets ranging from 50 to 300
        pipex = clamp(( currpipe.x // self.xinterpolatelength ) * self.xinterpolatelength, 50, 300)

        return (vel, pos, pipex)
    
    def getQ(self, gameStateAction):
        if gameStateAction in self.QTable.index:
            return self.QTable.loc[gameStateAction]
        return 0

    def setQ(self, gameStateAction, Qval):
        # set the value of the q table for the state action pair
        self.QTable.loc[gameStateAction] = Qval
    
    def getAction(self, gameState):
        # Epsilon greedy approach for exploration
        epsilon = 0.02
        if np.random.random() < epsilon:
            return np.random.choice([0,1])
        else:
            #If not taking random action, take the one with higher Q value
            nonJumpActionQVal = self.getQ((gameState, 0))
            JumpActionQVal = self.getQ((gameState, 1))
            return 1 if JumpActionQVal > nonJumpActionQVal else 0
            
        return 0

    def initializeWeights(self):
        pd.Series(data=None,index=None)

        # STATE RANGES
        # -9 to 10 player vely
        # interpolating into -2 to 2
        velRange = list(range(-2, 3))
        
        # States with playery and pipey have been scrapped due to producing too many states in favor of general positions
            # # -48 to 386.48 playery (Interpolating by length of 5)
            # playerYRange = list(range(-50, 390, 5))
            # # -184 to 0 pipeY (Interpolating by length of 5)
            # pipeYRange = list(range(-185, 0, 5))
            # 50 (53) to 298 pipeX (Interpolating by length of 5)

        # Flappy bird can be in position 0,1,2,3, or 4
        # This corresponds to below, between-lower, between-center, between-upper, and above next pipe respectively
        posRange = list(range(5))

        # the current pipex can range from 53 to 298, interpolation in buckets of self.xinterpolatelength
        pipeXRange = list(range(50, 301, self.xinterpolatelength))
        # FIND ALL STATE COMBINATIONS
        stateCombinations = list(itertools.product(velRange, posRange, pipeXRange))

        # ACTIONS (Flap or not Flap)
        actions = [0, 1]
        
        #Initialize Q(State, Action) to 0 for all states, actions
        QTable = pd.Series(0, index=[(tuple(combination), action) for combination in stateCombinations for action in actions])
        QTable.to_csv(path_or_buf="qsa.csv", header=["Q"], index_label=["SA"])


    def findFlappyPos(self, pipe):
        #Get flappy bird's true position by averaging top y and bottom y position
        flappyY = ((self.player.y) + (self.player.y + self.player.h)) / 2

        #Find whether flappy is above, between-upper, between-center, between-lower, or below pipe
        # The above positions correspond to 4, 3, 2, 1, and 0 respectively
        
        # Flappy bird is above the upper pipe height
        if flappyY < pipe.y + pipe.h:
            return 4
        # Flappy Bird is below the lower pipe height
        elif flappyY > pipe.y + pipe.h + 120:
            return 0
        # Othwerise in between pipes
        else:
            # In the upper third of gap
            if flappyY < pipe.y + pipe.h + 40:
                return 1
            # In the center third of gap
            elif flappyY < pipe.y + pipe.h + 80:
                return 2
            # In the lower third of gap
            else:
                return 3
            
        return -1