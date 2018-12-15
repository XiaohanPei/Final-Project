## Title: "The Werewolves of Miller's Hollow" Game Simulation

## Team Member(s): Xiaohan Pei, Ran Li, Jingxian Na

## Monte Carlo Simulation Scenario & Purpose:
In a basic *Werewolf* game, there are two opposing groups and they aim to kill each other: the Werewolves and the Villagers. 

The game is divided into two parts: **nights**, during which werewolves take action to kill a villager and some special villagers to perform their special action; **days**, when all players open their eyes, debate and vote a player they think is werewolf, and remove him or her out of this game. 

The intriguing part of the game lies in that all players know nothing but their own roles in the beginning(except for werewolves, they recognize each other in the first night), which makes it possible for werewolf players to pretend themselves to be villagers and lead other players to vote real villagers out of game. As the game progresses, players get more and more information from deaths in nights and debates in days, to help them guess others' roles and make a plausible speech in debates to convince other players.

In this program, we use Monte Carlo simulation to simulate players' votes in each day and night of a game, and analyze the game result data. Here are the assumptions used in this simulation:
1. _With more information, a player is more likely to convince others, i.e., his credit becomes higher._
2. _Though Villagers also get their chances to make speeches in debates, only the Seer and the Sheriff’s accusations are possible to convince others, that is, we only consider their accusations, and let others vote._

Extra variables are included for the simulation:
* **Credit:** an attribute of every player, denoting the chance that this player successfully convinces others. 
  * Villagers: 0.5
  * Werewolves: 0.6
  * Seer: <= 0.8 | +0.05 (discovers a Villager) / +0.1 (discovers a Werewolf)
* **Sheriff:** we take the player with this title as the one that is thinked trustworthy by others. As a result.
  * Credit: +0.1

## Simulation's variables of uncertainty:
### Night Simulation
* **Who is protected by the Guard**
  * Sheriff: whether or not protect him first --> **Bernoulli distribution** with a p-value of Sheriff’s credit
  * NO Sheriff/Not protect Sheriff: choose from the others --> **Random Choice**
* **Who is killed by Werewolves**
  * Werewolf Sheriff: choose from alive non-werewolves --> **Random Choice**
  * Non-werewolf Sheriff: kill him first
* **Who is checked by Seer**
  * Not Sheriff: check him first
  * Sheriff: choose from other unknown players --> **Randomly Choice**
  
### Day Simulation
* **Who is the Sheriff**
  * Candidates from each side (Werewolves / Non-werewolves): The ones with the highest credit
  * Equal credits: choose from all the candidates --> **Random Choice**
  * Unequal credits: whether or not the side with the highest credit become the Sheriff --> **Bernoulli distribution** with a p-value of the highest credit
* **Who will be accused**
  * Seer: choose from alive knowns/unknowns --> **Random Choice**
  * Werewolves: choose from alive non-werewolves --> **Randomly Choice**
  * Villagers/Guard: choose from alive players --> **Randomly Choice**
* **Who will be eliminated**
  * Vote for the accused player --> **Bernoulli distribution** with a p-value of accuser’s credit
  * Not vote: choose from the other alive players(excluding himself) --> **Randomly Choice**

## Hypothesis or hypotheses before running the simulation:
1. The number of players is postively correlated with the Villagers' winning rate, while keeping the number of Werewolves & Seer & Guard constant.
2. Changes in the Werewolves' winning conditions would cause an insignificant impact on their winning rate. 

## Analytical Summary of your findings:
* Along with the simulations, we made several changes & found out:
  1. Whoever becomes the Sheriff will get a 0.1 increase in his credit, causing a roughly 10% increase in Werewolves' winning rate. (Once Werewolves becomes the Sheriff, it's easier for them to make more plausible accusations)
  2. During the vote part, players cannot vote for themselves. It would slightly alter both sides' winning rates but not a significant change.
* Based on the simulation outcomes, it does support our hypotheses:
  1. The more players involved in the game, the higher the Villagers' winning rate. (Basically, there are more Villagers while only three Werewolves in the game, causing it a little harder for the Werewolves to kill most of non-werewolves).  
  2. Three conditions are considered (1. num of non-werewolves <= num of werewolves; 2. num of non-werewolves < num of werewolves; 3. num of non-werewolves = 0), and the highest Werewolves' winning rates under these three conditions is all around 80%. Thus, we decided to use the original winning condition (num of non-werewolves = 0) in our program. 

## Instructions on how to use the program:
* Download the Simulation.py and run it in Python 3.6. (The program has been fully-structued without requiring the users to enter any information).
* The outputs are expected to include three parts:
  * A text file including all the activity log from the simulations
  * A csv file consisting of the stats (winning frequencies & rates) with the number of players from 11 to 16
  * Two line charts showing the winning rate of Werewolves and Villagers
* There is a sample of the outputs in the sample_results file.
  
## All Sources Used:
https://en.wikipedia.org/wiki/The_Werewolves_of_Millers_Hollow

http://blog.sina.com.cn/s/blog_70930a3f0101hr5x.html

https://github.com/aszecsei/Werewolf
