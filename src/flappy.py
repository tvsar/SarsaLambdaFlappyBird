import asyncio
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

import os.path
import numpy as np

from .entities import (
    Agent,
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window

class Flappy:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
        )

    async def start(self):
        while True:
            self.background = Background(self.config)
            self.floor = Floor(self.config)
            self.player = Player(self.config)
            self.welcome_message = WelcomeMessage(self.config)
            self.game_over_message = GameOver(self.config)
            self.pipes = Pipes(self.config)
            self.score = Score(self.config)
            self.agent = Agent(self.config, self.player, self.pipes)
            #Commenting out the splash screen and game over screen results in it playing the game endlessly
            #await self.splash()
            await self.play()
            #await self.game_over()

    async def splash(self):
        """Shows welcome splash screen animation of flappy bird"""

        self.player.set_mode(PlayerMode.SHM)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        #Start of the game, initialize Q (If doesn't exist) and N
        if not os.path.isfile("qsa.csv"):
            print("Making a new Q table")
            self.agent.initializeWeights()       
        # N table initially empty (No states visited yet in run)
        self.agent.NTable = {}
        
        #Start of the game, initialize time, state, and initial action
        time = 0
        s0 = self.agent.getInterpolatedState()
        a0 = 0
        s1 = None
        a1 = -1

        # Learning rate
        alpha = 0.1
        # Discount rate
        gamma = 0.9
        # lambda
        lambdaVal = 0.5

        # loop (game running)
        while True:
            # Current action, flap if action is 1
            if a0 == 1:
                self.player.flap()

            #Observe Reward at t and new State at s t+1
            # Small reward if alive, dying negative reward
            reward = 1
            if self.player.collided(self.pipes, self.floor):
                reward = -100
            else:
                if self.pipes.upper[0].x > 53:
                    currpipe = self.pipes.upper[0]
                else:
                    currpipe = self.pipes.upper[1]
                position = self.agent.findFlappyPos(currpipe)
                if position == 1 or position == 3:
                    reward +=1
                elif position == 2:
                    reward +=2
                for i, pipe in enumerate(self.pipes.upper):
                    if self.player.crossed(pipe):
                        reward += 10

            #Find next state s t+1
            s1 = self.agent.getInterpolatedState()
                        
            #Choose action a t+1 based on some exploration strategy (Using epsilon greedy)
            a1 = self.agent.getAction(s1)

            #N(st, at) = N(st, at) + 1
            self.agent.NTable[(s0, a0)] = self.agent.NTable.get((s0, a0), 0) + 1
            # print(s0, a0)

            #delta = rt + gamma*Q(s t+1, a t+1) - Q(st, at)
            delta = reward + gamma * self.agent.getQ((s1, a1)) - self.agent.getQ((s0, a0))

            #for s in S (Only need to iterate through the visited in this playthrough, held in N table)
            for sa, N in self.agent.NTable.items():
                #for a in A (The N table's current value also has the relevant action)
                
                QSA = self.agent.getQ(sa)
                    #Q(s,a) = Q(s,a) + alpha * delta * N(s, a)
                self.agent.setQ(sa, QSA + alpha * delta * N)
                    #N(s,a) = gamma * lambda * N(s,a)
                self.agent.NTable[sa] = gamma * lambdaVal * N

            #Step time
            time += 1

            #Set the old state and action to the "new"
            s0 = s1
            a0 = a1

            ### BUILTIN CODE####
            if self.player.collided(self.pipes, self.floor):
                self.agent.saveQ()
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    self.player.flap()

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            ### BUILTIN CODE####

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH)
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)