from enum import Enum
import random
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import bernoulli
from collections import defaultdict
from operator import itemgetter


class Role(Enum):
    Villager = 0
    Werewolf = 1
    Guard = 2
    Seer = 3


class Game(object):
    """
    We simulate the whole game progress in this class.
    """
    def __init__(self, num_players):
        """
        Construction method of Game class, assign roles to each player:
        Player 1, 2 and 3 are werewolves, player 4 is seer, player 5 is guard, and the rest of players are
        common villagers.
        :param num_players: number of players, we set this number before the game begins.
        """
        self.num_players = num_players
        self.player_role = {}

        for i in range(1, num_players + 1):
            if i <= 3:
                self.player_role[i] = Player(i, Role.Werewolf)
            elif i == 4:
                self.player_role[i] = Player(i, Role.Seer)
            elif i == 5:
                self.player_role[i] = Player(i, Role.Guard)
            else:
                self.player_role[i] = Player(i, Role.Villager)

    def play(self):
        """
        The function to start the game.
        :return: "v" if villagers have won and "w" if werewolves won.
        """
        villagersWon = False
        werewolvesWon = False

        isNight = True
        while not villagersWon and not werewolvesWon:
            if isNight:
                self.night()
            else:
                self.day()

            isNight = not isNight

            villagersWon = self.VillagersWon()
            werewolvesWon = self.WerewolvesWon()

        if villagersWon:
            print("The Villagers have won!\n", file=open("Activity Log.txt", 'a'))
            return 'v'

        else:
            print("The Werewolves have won!\n", file=open("Activity Log.txt", 'a'))
            return "w"

    def WerewolvesWon(self):
        """
        Victory condition for werewolves.
        :return: True, if there are no alive villagers left in game; False, otherwise.
        """
        return len(self.alive_nonwerewolves_id()) == 0

    def VillagersWon(self):
        """
        Victory condition for villagers.
        :return: True, if there are no alive werewolves left in game; False, otherwise.
        """
        return len(self.alive_werewolves_id()) == 0

    def alive_players(self):
        """
        Find alive players.
        :return: a list of alive players.
        """
        alive_players = []
        for player in list(self.player_role.values()):
            if player.is_alive:
                alive_players.append(player)
        return alive_players

    def alive_players_id(self):
        """
        Get alive players' IDs.
        :return: a list of alive players' IDs.
        """
        alive_players = self.alive_players()
        alive_players_id = []
        for player in alive_players:
            alive_players_id.append(player.player_id)
        return alive_players_id

    def alive_nonwerewolves_id(self):
        alive_players = self.alive_players()
        alive_nonwerewolves_id = []
        for player in alive_players:
            if player.role != Role.Werewolf:
                alive_nonwerewolves_id.append(player.player_id)
        return alive_nonwerewolves_id

    def alive_werewolves_id(self):
        alive_players = self.alive_players()
        alive_werewolves_id = []
        for player in alive_players:
            if player.role == Role.Werewolf:
                alive_werewolves_id.append(player.player_id)
        return alive_werewolves_id

    def alive_players_id_except(self, selfid):
        alive_players_id = self.alive_players_id()
        alive_players_except = []
        for pid in alive_players_id:
            if pid != selfid:
                alive_players_except.append(pid)
        return alive_players_except

    def alive_players_id_besides(self, id1, id2):
        alive_players_id = self.alive_players_id()
        alive_players_besides = []
        for pid in alive_players_id:
            if pid != id1 and pid != id2:
                alive_players_besides.append(pid)
        return alive_players_besides

    def who_is_sheriff(self):
        """
        Find out which player will be elected as sheriff.
        We assume in this program that only a villager and a werewolf will run for the sheriff title, when seer is
        alive, he will be the villager candidate; when seer is dead, we randomly choose another villager to take
        his place.
        :return: sheriff's ID.
        """
        alive_titles = []
        for player in self.alive_players():
            alive_titles.append(player.title)
        # If there is already a sheriff, return his ID:
        if 'sheriff' in alive_titles:
            for player in self.alive_players():
                if player.title == 'sheriff':
                    return player.player_id
        # If there is none, elect one:
        else:
            non_werewolves = {}
            werewolves = {}
            for player in self.alive_players():
                if player.role == Role.Werewolf:
                    werewolves[player.player_id] = player.credit
                else:
                    non_werewolves[player.player_id] = player.credit

            non_highest = defaultdict(list)
            wolf_highest = defaultdict(list)

            # Build two dictionaries reversing the keys and values of the original:
            # keys are different credits, values are lists of players who hold the same credit.
            for key, value in non_werewolves.items():
                non_highest[value].append(key)
            for key, value in werewolves.items():
                wolf_highest[value].append(key)

            # Get a list of players who hold the highest credit and value of their credits:
            non_credit = max(non_highest.items(), key=itemgetter(0))[0]
            non_highest_id = max(non_highest.items(), key=itemgetter(0))[1]
            wolf_credit = max(wolf_highest.items(), key=itemgetter(0))[0]
            wolf_highest_id = max(wolf_highest.items(), key=itemgetter(0))[1]

            # Since all villagers' credit are set as 0.5, and only the seer can improve his credit by checking others'
            # roles, the highest credit among villagers can only be possessed by the seer when he is alive, or any other
            # villagers when seer is dead.

            # Between the villager candidate's credit and the werewolf candidate's credit, we use the larger one
            # as the p-value of a Bernoulli distribution, the candidate with higher credit will be elected as
            # sheriff if the random variable is 1, the other candidate will be elected as sheriff if the random
            # variable is 0:
            sheriff_id = None
            if non_credit > wolf_credit:
                dec = bernoulli.rvs(non_credit)
                if dec == 1:
                    sheriff_id = random.choice(non_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    self.player_role[sheriff_id].credit += 0.1
                    return sheriff_id
                else:
                    sheriff_id = random.choice(wolf_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    self.player_role[sheriff_id].credit += 0.1
                    return sheriff_id
            elif wolf_credit < non_credit:
                dec = bernoulli.rvs(wolf_credit)
                if dec == 1:
                    sheriff_id = random.choice(wolf_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    self.player_role[sheriff_id].credit += 0.1
                    return sheriff_id
                else:
                    sheriff_id = random.choice(non_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    self.player_role[sheriff_id].credit += 0.1
                    return sheriff_id
            else:
                sheriff_id = random.choice(non_highest_id+wolf_highest_id)
                self.player_role[sheriff_id].title = 'sheriff'
                self.player_role[sheriff_id].credit += 0.1
                return sheriff_id

    def accused_by_seer(self):
        """
        This method is used to simulate the progress that seer choose a player to accuse based on his knowledge.
        :return: the accused player's ID.
        """
        seer = None
        accuse_id = None
        for player in self.alive_players():
            if player.role == Role.Seer:
                seer = player

        # If the seer finds a werewolf in night, he will accuse this werewolf next day:
        if seer.identity[-1].role == Role.Werewolf and seer.identity[-1].is_alive:
            accuse_id = seer.identity[-1].player_id
        else:
            # If the seer has only found a villager, he will randomly choose another player to accuse:
            if len(seer.identity) == 1:
                random_accuse_id = []
                for player in self.alive_players():
                    if player not in seer.identity and player.role != Role.Seer:
                        random_accuse_id.append(player.player_id)
                accuse_id = random.choice(random_accuse_id)

            # If the seer has found more than one players' roles, he will randomly choose a known werewolf to accuse if
            # he has found any, or randomly choose an unknown player to accuse if he has not found any werewolves.
            elif len(seer.identity) > 1:
                identity_wolf_id = []
                for player in seer.identity[0:-1]:
                    if player.is_alive and player.role == Role.Werewolf:
                        identity_wolf_id.append(player.player_id)
                if len(identity_wolf_id) >= 1:
                    accuse_id = random.choice(identity_wolf_id)
                else:
                    random_accuse_id = []
                    for player in self.alive_players():
                        if player not in seer.identity and player.role != Role.Seer:
                            random_accuse_id.append(player.player_id)
                    accuse_id = random.choice(random_accuse_id)

        return accuse_id

    def vote_only_one_accusation(self, sheriff_id, sheriff_credit, accused_id):
        """
        This method is to simulate the results of votes when there is only one accusation.
        Since we only take seer's and sheriff's accusations into consideration, this situation only happens when
        seer becomes sheriff, or seer is dead, and the accusation is made by sheriff.
        :param sheriff_id: ID of the player holding sheriff title.
        :param sheriff_credit: credit of the player holding sheriff title.
        :param accused_id: ID of the player being accused by sheriff.
        :return: ID of the player who get most votes and will be eliminated after.
        """
        # Set a dictionary to storage current alive players and the votes they get:
        votes = {}
        # Set the everyone's initial votes as 0:
        for pid in self.alive_players_id():
            votes[pid] = 0

        for player in self.alive_players():
            # Sheriff votes for the player he chose to accuse:
            if player.player_id == sheriff_id:
                votes[accused_id] += 1
            # The accused player will not vote himself, but randomly vote another player:
            elif player.player_id == accused_id:
                new_accuse_id = random.choice(self.alive_players_id_except(accused_id))
                votes[new_accuse_id] += 1
            # As for other players, their probabilities of voting as sheriff's accusation follow a Bernoulli
            # distribution, the p-value of this distribution is equal to sheriff's credit:
            else:
                voting = bernoulli.rvs(sheriff_credit)
                if voting == 1:
                    votes[accused_id] += 1
                # If they choose not to trust the sheriff, they will randomly select another player to vote:
                else:
                    new_accuse_id = random.choice(self.alive_players_id_besides(player.player_id, accused_id))
                    votes[new_accuse_id] += 1

        votes_highest = defaultdict(list)
        for key, value in votes.items():
            votes_highest[value].append(key)

        highest_id = max(votes_highest.items(), key=itemgetter(0))[1]
        # If there is a tie, we randomly choose one player from all players with the same highest votes to eliminate:
        return random.choice(highest_id)

    def vote_for_two_accusations(self, sheriff_id, sheriff_credit, sheriff_accused_id, seer_id, seer_credit, seer_accused_id):
        """
        This method is to simulate the results of votes when there are two accusations.
        Since we only take seer's and sheriff's accusations into consideration, this situation happens when the sheriff
        title is held by a werewolf, and seer is alive.
        :param sheriff_id: ID of the player holding sheriff title.
        :param sheriff_credit: credit of the player holding sheriff title.
        :param sheriff_accused_id: ID of the player being accused by sheriff.
        :param seer_id: seer's ID.
        :param seer_credit: seer's credit.
        :param seer_accused_id: ID of the player being accused by seer.
        :return: ID of the player who get most votes and will be eliminated after.
        """
        # Set a dictionary to storage current alive players and the votes they get:
        votes = {}
        # Set the everyone's initial votes as 0:
        for pid in self.alive_players_id():
            votes[pid] = 0
        for player in self.alive_players():
            # Sheriff votes for the player he chose to accuse:
            if player.player_id == sheriff_id:
                votes[sheriff_accused_id] += 1
            # Seer votes for the player he chose to accuse:
            elif player.player_id == seer_id:
                votes[seer_accused_id] += 1
            # The player or players accused by sheriff and seer will not vote for themselves, but randomly select
            # another player to vote.
            elif player.player_id == sheriff_accused_id or player.player_id == seer_accused_id:
                new_accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                votes[new_accuse_id] += 1
            # As for other players, they will first decide whether or not to trust the accusation made by player with
            # higher credit, the probabilities of being convinced follow a Bernoulli distribution, and the p-value
            # equals to the higher credit:
            else:
                if sheriff_credit > seer_credit:
                    dec1 = bernoulli.rvs(sheriff_credit)
                    if dec1 == 1:
                        votes[sheriff_accused_id] += 1
                    # If they are not convinced by the player with higher credit, they will decide if to trust the other
                    # accusation or not:
                    else:
                        dec2 = bernoulli.rvs(seer_credit)
                        if dec2 == 1:
                            votes[seer_accused_id] += 1
                        # If some of the players choose not to trust these two accusations, they will randomly choose
                        # another player to accuse:
                        else:
                            new_accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                            votes[new_accuse_id] += 1
                elif seer_credit > sheriff_credit:
                    dec1 = bernoulli.rvs(seer_credit)
                    if dec1 == 1:
                        votes[seer_accused_id] += 1
                    else:
                        dec2 = bernoulli.rvs(sheriff_credit)
                        if dec2 == 1:
                            votes[sheriff_accused_id] += 1
                        else:
                            new_accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                            votes[new_accuse_id] += 1
                # If sheriff and the seer have the same credit, we randomly choose one of them to be the player with
                # "higher" credit, then do the same thing as above:
                else:
                    accuse_ids = [sheriff_accused_id, seer_accused_id]
                    accuse_id = random.choice(accuse_ids)
                    if accuse_id == sheriff_accused_id:
                        if bernoulli.rvs(sheriff_credit) == 1:
                            accuse_id = sheriff_accused_id
                        else:
                            if bernoulli.rvs(seer_credit) == 1:
                                accuse_id = seer_accused_id
                            else:
                                accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                    else:
                        if bernoulli.rvs(seer_credit) == 1:
                            accuse_id = seer_accused_id
                        else:
                            if bernoulli.rvs(seer_credit) == 1:
                                accuse_id = sheriff_accused_id
                            else:
                                accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                    votes[accuse_id] += 1

        votes_highest = defaultdict(list)
        for key, value in votes.items():
            votes_highest[value].append(key)

        highest_id = max(votes_highest.items(), key=itemgetter(0))[1]
        # If there is a tie, we randomly choose one player from all players with the same highest votes to eliminate:
        return random.choice(highest_id)

    def night(self):
        """
        This method is used as a simulation of the nights in game.
        :return:
        """
        # First phrase: Guard chooses a player to protect.
        player_protected = None
        for player in self.alive_players():
            if player.role == Role.Guard:
                player_protected = player.Guard()

        # Second phrase: Werewolves choose a player to kill.
        player_killed_id = random.choice(self.alive_nonwerewolves_id())
        player_killed = self.player_role[player_killed_id]
        # If sheriff is not a werewolf, werewolves will choose to kill him:
        for player in self.alive_players():
            if player.title == 'sheriff' and player.role != Role.Werewolf:
                player_killed = player
                player_killed_id = player.player_id

        # Third phrase: Seer chooses a player to check his role.
        for player in self.alive_players():
            if player.role == Role.Seer:
                seer = player
                player_checked = self.player_role[player.Seer()]
                # If Seer is not sheriff, he will choose to check sheriff's role:
                for other in self.alive_players():
                    if other.title == 'sheriff' and other.role != Role.Seer:
                        player_checked = other
                seer.identity.append(player_checked)
                # Seer can have his credit increased by check others' roles:
                if player_checked.role == Role.Werewolf:
                    seer.credit += 0.1
                else:
                    seer.credit += 0.05
                # Seer's maximum credit is set as 0.8:
                if seer.credit >= 0.8:
                    seer.credit = 0.8

        if player_protected != player_killed_id:
            print('Player #{} ({}) was killed at night.'.format(player_killed_id, player_killed.role.name), file=open("Activity Log.txt", 'a'))
            for player in self.alive_players():
                if player.player_id == player_killed_id:
                    player.is_alive = False
        else:
            print('The Guard protected player #{} successfully.'.format(player_protected), file=open("Activity Log.txt", 'a'))

    def day(self):
        """
        This method is used as a simulation of the days in game.
        :return:
        """
        # First phrase: elect a sheriff if no one hold the title.
        sheriff_id = self.who_is_sheriff()
        sheriff_credit = self.player_role[sheriff_id].credit

        # Second phrase: debate and vote.
        # If seer is sheriff, only one person will be accused:
        if self.player_role[sheriff_id].role == Role.Seer:
            seer_accuse_id = self.accused_by_seer()
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, seer_accuse_id), file=open("Activity Log.txt", 'a'))

            # Get the vote result:
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, seer_accuse_id)
            print('Player #{} is eliminated in this round.'.format(eliminated_id), file=open("Activity Log.txt", 'a'))
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False

        # If a werewolf becomes sheriff, he will randomly choose a villager to accuse:
        elif self.player_role[sheriff_id].role == Role.Werewolf:
            werewolf_accuse_id = random.choice(self.alive_nonwerewolves_id())
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, werewolf_accuse_id), file=open("Activity Log.txt", 'a'))

            seer_id = None
            seer_credit = None
            for player in self.alive_players():
                if player.role == Role.Seer:
                    seer_id = player.player_id
                    seer_credit = player.credit

            # If seer is dead at that time, only the werewolf sheriff makes the accusation:
            if seer_id is None:
                eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, werewolf_accuse_id)
                print('Player #{} is eliminated in this round.'.format(eliminated_id), file=open("Activity Log.txt", 'a'))
                for player in self.alive_players():
                    if player.player_id == eliminated_id:
                        player.is_alive = False

            # If the seer is still alive, he will also make an accusation:
            else:
                seer_accuse_id = self.accused_by_seer()
                print('Player #{} says Player #{} is a Werewolf.'.format(seer_id, seer_accuse_id), file=open("Activity Log.txt", 'a'))
                eliminated_id = self.vote_for_two_accusations(sheriff_id, sheriff_credit, werewolf_accuse_id, seer_id, seer_credit, seer_accuse_id)
                print('Player #{} is eliminated in this round.'.format(eliminated_id), file=open("Activity Log.txt", 'a'))
                for player in self.alive_players():
                    if player.player_id == eliminated_id:
                        player.is_alive = False

        # When seer is dead, if a villager becomes sheriff, he will randomly choose another player to accuse:
        else:
            sheriff_accuse_id = random.choice(self.alive_players_id_except(sheriff_id))
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, sheriff_accuse_id), file=open("Activity Log.txt", 'a'))
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, sheriff_accuse_id)
            print('Player #{} is eliminated in this round.'.format(eliminated_id), file=open("Activity Log.txt", 'a'))
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False


class Player(object):
    """
    We use this class to simulate the players in game.
    """
    def __init__(self, player_id, role, title=None, credit=0.5):
        self.player_id = player_id
        self.role = role
        self.is_alive = True
        self.credit = credit
        self.title = title

        # A list of identities that seer has checked:
        if self.role == Role.Seer:
            self.identity = []
        # Set the werewolves' credit as 0.6:
        elif self.role == Role.Werewolf:
            self.credit = 0.6

    def Seer(self):
        """
        Seer select a player to check his role.
        :return: ID of the player checked by seer.
        """
        seer = None
        unknown = []
        for player in aGame.alive_players():
            if player.role == Role.Seer:
                seer = player

        for other in aGame.alive_players():
            if other.role != Role.Seer and other not in seer.identity:
                unknown.append(other.player_id)

        if len(unknown) > 0:
            return random.choice(unknown)
        else:
            return seer.player_id

    def Guard(self):
        """
        Guard choose a player to protect.
        The probability of guard choosing to protect sheriff is equal to sheriff's credit, we use a Bernoulli
        distribution to simulate this progress. If the random variable turns out to be 0, guard will randomly choose
        another player to protect.
        :return: ID of the player protected by guard.
        """
        civilian = []  # To storage alive players' IDs, except sheriff's.
        for player in aGame.alive_players():
            if player.title != 'sheriff':
                civilian.append(player.player_id)

        protected = random.choice(aGame.alive_players_id())
        for player in aGame.alive_players():
            if player.title == "sheriff":
                sheriff = player
                decision = bernoulli.rvs(sheriff.credit)
                if decision == 1:
                    protected = sheriff.player_id
                else:
                    protected = random.choice(civilian)
        return protected


if __name__ == "__main__":
    results = pd.DataFrame()
    num_players = []
    freq_villagers = []
    freq_werewolves = []
    rate_villagers = []
    rate_werewolves = []

    for num in range(11, 17):
        num_players.append(num)
        villagers_won = 0
        werewolves_won = 0

        for i in range(1000):
            aGame = Game(num)
            if aGame.play() == 'v':
                villagers_won += 1
            else:
                werewolves_won += 1

        freq_villagers.append(villagers_won)
        freq_werewolves.append(werewolves_won)

        villagers_rate = villagers_won / (villagers_won + werewolves_won)
        werewolves_rate = werewolves_won / (villagers_won + werewolves_won)

        rate_villagers.append(villagers_rate)
        rate_werewolves.append(werewolves_rate)

    results['Num of Players'] = num_players
    results['Villagers Winning Freq'] = freq_villagers
    results['Villagers Winning Rate'] = rate_villagers
    results['Werewolves Winning Freq'] = freq_werewolves
    results['Werewolves Winning Rate'] = rate_werewolves

    results.to_csv('Simulation Results.csv', index=False)

    results.plot.line(x='Num of Players', y='Villagers Winning Rate')
    results.plot.line(x='Num of Players', y='Werewolves Winning Rate')
    plt.show()
