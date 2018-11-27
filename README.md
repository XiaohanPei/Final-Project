# Title: 
**"The Werewolves of Miller's Hollow" Game Simulation**
## Team Member(s):
Xiaohan Pei, Ran Li, Jingxian Na

# Monte Carlo Simulation Scenario & Purpose:
In a basic *Werewolf* game, there are two opposing groups: the werewolves and the villagers, and the aim of game for each group is to kill all their opponents. The game is divided into two parts: nights, during which werewolves take action to kill a villiager and some special villiagers to perform their special action; days, when all players open their eyes, debate and vote a player they think is werewolf, and remove him or her out of this game. The intriguing part of the game lies in that all players know nothing but their own roles in the beginning(except for werewolves, they recognize each other in the first night), which makes it possible for werewolf players to pretend themselves to be villagers and lead other players to vote real villagers out of game. As the game progresses, players get more and more information from deaths in nights and debates in days, to help them guess others' roles and make a plausible speech in debates to convince other players.

In this program, we use Monte Carlo simulation to simulate players' votes in each day and night of a game, and analyze the game result data. We first let all players vote randomly and get the results, then we give each player a vote preference based on their roles and the popular tactics of this game, and compare the new reults data with the old one, to see if those tactics really help players win this game.

## Simulation's variables of uncertainty
The variables of uncertainty in this program are each player's vote in days and each werewolf's vote in nights(to decide which villager to kill). For the first part of the program, we let all players vote randomly: anyone but themselves in days and any players including themselves in nights. In the second part, we assign different vote preference to each players baesd on popular tactics.

We think these uncertain variables can represent real players' actions in game to some extent, for people in real games make decisions based on others' characteristics(if they know each other), actions, speeches, facial expressions and body languages, all of which can be simulated by random variables.

## Hypothesis or hypotheses before running the simulation:

## Analytical Summary of your findings: (e.g. Did you adjust the scenario based on previous simulation outcomes?  What are the management decisions one could make from your simulation's output, etc.)

## Instructions on how to use the program:

## All Sources Used:
https://en.wikipedia.org/wiki/The_Werewolves_of_Millers_Hollow

http://blog.sina.com.cn/s/blog_70930a3f0101hr5x.html
