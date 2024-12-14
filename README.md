# CSCI 4511 Flappy Bird Sarsa Lambda Project 
### Tharun Saravanan

For this project I utilized the Sarsa-Lambda reinforcement learning algorithm to play the game "Flappy Bird". I used the flappy bird game made at the following link as a base for this project: https://github.com/sourabhv/FlapPyBird 

To run the game with the agent loaded, navigate to the central directory and run ``main.py`` 

My code is found within src/flappy.py, and src/entities/agent.py. Within flappy.py I added the Sarsa-Lambda algorithm to the main loop of the existing game. agent.py contains various helper methods including initializing the Q(s,a) table as a CSV, loading the CSV Q(s,a) table as a pandas Series object, and getting interpolations of Flappy Bird's state.

## Software and Hardware requirements:
I utilized pandas version 2.0.3 and numpy version 1.24.4. Both of these packages are included within the pyproject.toml file, along with other dependencies preexisting for this game. I wasn't sure on how to include the remaining imports, so I just included the remaining imports in a list as the requirements.txt file.

## Data Sources:
This project was based on the Flappy Bird game found at the following repository: https://github.com/sourabhv/FlapPyBird 

## Motivation:
I chose "Flappy Bird" as a project for this class as it involved sequential decision making (deciding to flap or not flap at each state action pair), and as such I thought it could be a good fit for a project in this class. I also have fond memories of the original game back when it was released in 2013.

## Accomplishment:

I was successfully able to apply the Sarsa-Lambda algorithm to play the game "Flappy Bird" by updating a Q(s,a) table.

My code starts by initializing an instance of an ```Agent``` (defined in  ```agent.py```), which contains helper functions to help with the Sarsa Lambda algorithm within ```Flappy.py``` when the game first starts a run. The Agent takes in the Flappy Bird ```player``` object and the Pipes ```pipes``` object, and then reads in the existing Q(s,a) table (held as qsa.csv) into a ```Pandas Series``` object. If no table is present, an empty one is made. 

From there it then continues from the ```play()``` method, where the game is run as a loop. From here, a new N(s,a) eligibility trace table is initialized as a dictionary (Dictionary chosen as the majority of states are unikely to be visited in any run of the game).

From this point, an initial state and action are defined. The agent is called for the initial state as it has access to the player and pipe objects. My state space consisted of Flappy Bird's velocity, Flappy Bird's position relative to the closest pipe gap on the y axis, and Flappy Bird's position relative to the closest pipe on the x axis. My action space consisted of simply flapping at a state, or choosing to not flap at a state.

Worth noting about the state however is that all of the values in the state are interpolations. 
- Within the game, Flappy Bird has a velocity ranging from -9 to 10.
- Velocities were mapped from those values to the range -2 to 2.
- Flappy Bird's position was described as above, between-upper, between-center, between-lower, or below relative to the pipe gap.
- The position relative to the closest x axis was defined as buckets defined by the agent's self.xinterpolatelength (set to 30).
- I chose to do this because my program was taking too long to converge when passing in exact values for all of these fields, as there were simply too many states when I passed in the exact values, and it was not approaching convergence.
- I initially tried having just 3 y positions (above, between, and below), but found better results with the added nuance.

Sarsa lamda constants are also defined here:
- Learning rate - alpha = 0.1
- Discount rate - gamma = 0.9
- lambda - lambdaVal = 0.5

From here the program enters the main loop portion of the game. 

First, if the player's action is a flap for the current time step, Flappy Bird will flap

From here, the reward and a new state is observed
- Flappy Bird gets 1 point of reward for being alive at a time step
- Dying results in a reward of -100
- For being in the between-upper or between-lower pipe gap, Flappy Bird gets an additional 1 point of reward
- For being in the between-center pipe gap, Flappy Bird gets an additional 2 points of reward
- For crossing a pipe (increasing the score), Flappy Bird gets an additional 10 points of reward

Then the Eligibility Trace for the state action pair is increased by 1, and the delta is calculated as reward + gamma * Q(s t+1, a t+1) - q(st, at)

Each state action pair in the N dictionary is then looped through. Q for each state action is set to the existing Q(s,a) + alpha * delta * N(s,a), and N for each state action is set to gamma * lambda * N(s,a).

Finally, the old state and action are set to the new state and action, and the program continues to loop until Flappy Bird collides, upon which point the new Q(s,a) table overwrites the old one stored in ```qsa.csv```

## Measures of Success/Failure:

While I was able to successfully apply the algorithm to play "Flappy Bird", I wish that I was able to use more fine grained measurements rather than interpolations for the state. The maximum score I observed Flappy Bird get in a run was 22. This is technically a successful result, I was hoping to train Flappy Bird to fly "endlessly" without colliding. 

Part of the reason I think this failed is because there was a significant data loss by interpolating my measurements, however it was simply taking too long for the table to converge (In total around 7.2 million state action pairs, did not converge with over 8 hours in runs). For further research, I would potentially want to try another approach such as linear approximation, as I believe it could potentially allow for Flappy Bird to learn to fly endlessly.
