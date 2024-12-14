## CSCI 4511 Flappy Bird Sarsa Lambda Project 
# Tharun Saravanan

For this project I tried to utilize the Sarsa-Lambda reinforcement learning algorithm to play the game "Flappy Bird". I utilized the flappy bird game made at the following link for this project: https://github.com/sourabhv/FlapPyBird 

To run the game, navigate to the main directory and run ``main.py`` 

My code is found within src/flappy.py, and src/entities/agent.py. Within flappy.py I added the Sarsa-Lambda algorithm to the main loop of the existing game. agent.py contains various helper methods including initializing the Q(s,a) table as a CSV, loading the CSV Q(s,a) table as a pandas Series object, and getting interpolations of Flappy Bird's state.

Software and Hardware requirements:
I utilized pandas version 2.0.3 and numpy version 1.24.4. Both of these packages are included within the pyproject.toml file, along with other dependencies preexisting for this game. I wasn't sure on how to include the remaining imports, so I just included the remaining imports in a list as the requirements.txt file.

Data Sources:
This project was based on the Flappy Bird game found at the following repository: https://github.com/sourabhv/FlapPyBird 

Motivation:
I chose "Flappy Bird" as a project for this class as it involved sequential decision making (deciding to flap or not flap at each state action pair), and as such I thought it could be a good fit for a project in this class. I also have fond memories of the original game back when it was released in 2013.

Accomplishment:

Measures of Success/Failure:
