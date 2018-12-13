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
    def __init__(self, num_players):
        self.num_players = num_players
        self.player_role = {}

        for i in range(1, num_players + 1):
            if i <= 3:
                self.player_role[i] = Player(i, Role.Werewolf)
            if i == 4:
                self.player_role[i] = Player(i, Role.Seer)
            if i == 5:
                self.player_role[i] = Player(i, Role.Guard)
            if i >= 6 and i <= num_players:
                self.player_role[i] = Player(i, Role.Villager)

    def play(self):
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
            print("The Villagers have won!\n", file = open("Activity Log.txt", 'a'))
            return 'v'

        else:
            print("The Werewolves have won!\n", file = open("Activity Log.txt", 'a'))
            return "w"

    def WerewolvesWon(self):
        return len(self.alive_nonwerewolves_id()) <= len(self.alive_werewolves_id())

    def VillagersWon(self):
        return len(self.alive_werewolves_id()) == 0

    def alive_players(self):
        alive_players = []
        for player in list(self.player_role.values()):
            if player.is_alive:
                alive_players.append(player)
        return alive_players

    def alive_players_id(self):
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

    def alive_players_id_except(self,selfid):
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

    #select a sheriff if there is no sheriff
    def who_is_sheriff(self):
        alive_titles = []
        for player in self.alive_players():
            alive_titles.append(player.title)
        if 'sheriff' in alive_titles:
            for player in self.alive_players():
                if player.title == 'sheriff':
                    return player.player_id
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

            for key, value in non_werewolves.items():
                non_highest[value].append(key)
            for key, value in werewolves.items():
                wolf_highest[value].append(key)

            non_credit = max(non_highest.items(), key = itemgetter(0))[0]
            non_highest_id = max(non_highest.items(), key = itemgetter(0))[1]
            wolf_credit = max(wolf_highest.items(), key = itemgetter(0))[0]
            wolf_highest_id = max(wolf_highest.items(), key = itemgetter(0))[1]

            sheriff_id = None
            if non_credit > wolf_credit:
                dec = bernoulli.rvs(non_credit)
                if dec == 1:
                    sheriff_id = random.choice(non_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    return sheriff_id
                else:
                    sheriff_id = random.choice(wolf_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    return sheriff_id
            elif wolf_credit < non_credit:
                dec = bernoulli.rvs(wolf_credit)
                if dec == 1:
                    sheriff_id = random.choice(wolf_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    return sheriff_id
                else:
                    sheriff_id = random.choice(non_highest_id)
                    self.player_role[sheriff_id].title = 'sheriff'
                    return sheriff_id
            else:
                sheriff_id = random.choice(non_highest_id+wolf_highest_id)
                self.player_role[sheriff_id].title = 'sheriff'
                return sheriff_id

    # who will be accused by seer
    def accused_by_seer(self):
        seer = None
        accuse_id = None
        for player in self.alive_players():
            if player.role == Role.Seer:
                seer = player

        if seer.identity[-1].role == Role.Werewolf and seer.identity[-1].is_alive:
            accuse_id = seer.identity[-1].player_id
        else:
            if len(seer.identity) == 1:
                random_accuse_id = []
                for player in self.alive_players():
                    if player not in seer.identity and player.role != Role.Seer:
                        random_accuse_id.append(player.player_id)
                accuse_id = random.choice(random_accuse_id)

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
        votes = {}
        for pid in self.alive_players_id():
            votes[pid] = 0

        for player in self.alive_players():
            if player.player_id == sheriff_id:
                votes[accused_id] += 1
            else:
                voting = bernoulli.rvs(sheriff_credit)
                if voting == 1:
                    votes[accused_id] += 1
                else:
                    new_accuse_id = random.choice(self.alive_players_id_except(accused_id))
                    votes[new_accuse_id] += 1

        votes_highest = defaultdict(list)
        for key, value in votes.items():
            votes_highest[value].append(key)

        highest_id = max(votes_highest.items(), key=itemgetter(0))[1]
        return random.choice(highest_id)

    def vote_for_two_accusations(self,sheriff_id, sheriff_credit, sheriff_accused_id, seer_id, seer_credit, seer_accused_id):
        votes = {}
        for pid in self.alive_players_id():
            votes[pid] = 0
        for player in self.alive_players():
            if player.player_id == sheriff_id:
                votes[sheriff_accused_id] += 1
            elif player.player_id == seer_id:
                votes[seer_accused_id] += 1
            else:
                if sheriff_credit > seer_credit:
                    dec1 = bernoulli.rvs(sheriff_credit)
                    if dec1 == 1:
                        votes[sheriff_accused_id] += 1
                    else:
                        dec2 = bernoulli.rvs(seer_credit)
                        if dec2 == 1:
                            votes[seer_accused_id] += 1
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
                            if bernoulli.rvs(seer_credit)  == 1:
                                accuse_id = sheriff_accused_id
                            else:
                                accuse_id = random.choice(self.alive_players_id_besides(sheriff_accused_id, seer_accused_id))
                    votes[accuse_id] += 1

        votes_highest = defaultdict(list)
        for key, value in votes.items():
            votes_highest[value].append(key)

        highest_id = max(votes_highest.items(), key=itemgetter(0))[1]
        return random.choice(highest_id)

    def night(self):
        # choose somebody to protect.
        player_protected = None
        for player in self.alive_players():
            if player.role == Role.Guard:
                player_protected = player.Guard()

        # choose someone to kill.
        player_killed_id = random.choice(self.alive_nonwerewolves_id())
        player_killed = self.player_role[player_killed_id]
        # if the sheriff is not a werewolf, werewolves will kill the guard.
        for player in self.alive_players():
            if player.title == 'sheriff' and player.role != Role.Werewolf:
                player_killed = player
                player_killed_id = player.player_id

        # Check someone's identity
        for player in self.alive_players():
            if player.role == Role.Seer:
                seer = player
                player_checked = self.player_role[player.Seer()]
                # if Seer is not the Sheriff, Seer must be very curious about the Sheriff's identity and check it.
                for other in self.alive_players():
                    if other.title == 'sheriff' and other.role != Role.Seer:
                        player_checked = other
                seer.identity.append(player_checked)
                if player_checked.role == Role.Werewolf:
                    seer.credit += 0.1
                else:
                    seer.credit += 0.05
                if seer.credit >= 0.8:
                    seer.credit = 0.8

        if player_protected != player_killed_id:
            print('Player #{} ({}) was killed at night.'.format(player_killed_id, player_killed.role.name), file = open("Activity Log.txt", 'a'))
            for player in self.alive_players():
                if player.player_id == player_killed_id:
                    player.is_alive = False
        else:
            print('The Guard protected player #{} successfully.'.format(player_protected), file = open("Activity Log.txt", 'a'))

    def day(self):
        # select a sheriff if there is no sheriff
        sheriff_id = self.who_is_sheriff()
        sheriff_credit = self.player_role[sheriff_id].credit

        # when the sheriff is the seer, only one person will be accused
        if self.player_role[sheriff_id].role == Role.Seer:
            seer_accuse_id = self.accused_by_seer()
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id,seer_accuse_id), file = open("Activity Log.txt", 'a'))
            # vote
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, seer_accuse_id)
            print('Player #{} is eliminated in this round.'.format(eliminated_id), file = open("Activity Log.txt", 'a'))
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False

        # when the sheriff is a werewolf, who will be accused by the sheriff
        elif self.player_role[sheriff_id].role == Role.Werewolf:
            werewolf_accuse_id = random.choice(self.alive_nonwerewolves_id())
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, werewolf_accuse_id), file = open("Activity Log.txt", 'a'))

            seer_id = None
            seer_credit = None
            for player in self.alive_players():
                if player.role == Role.Seer:
                    seer_id = player.player_id
                    seer_credit = player.credit
            # when seer is dead, there's only one accusation from the sheriff
            if seer_id == None:
                eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, werewolf_accuse_id)
                print('Player #{} is eliminated in this round.'.format(eliminated_id), file = open("Activity Log.txt", 'a'))
                for player in self.alive_players():
                    if player.player_id == eliminated_id:
                        player.is_alive = False
            # when the seer is alive, there're two accusations from the sheriff and the seer
            else:
                seer_accuse_id = self.accused_by_seer()
                print('Player #{} says Player #{} is a Werewolf.'.format(seer_id,seer_accuse_id), file = open("Activity Log.txt", 'a'))
                eliminated_id = self.vote_for_two_accusations(sheriff_id, sheriff_credit, werewolf_accuse_id, seer_id, seer_credit, seer_accuse_id)
                print('Player #{} is eliminated in this round.'.format(eliminated_id), file = open("Activity Log.txt", 'a'))
                for player in self.alive_players():
                    if player.player_id == eliminated_id:
                        player.is_alive = False

        # when the sheriff is neither a werewolf nor seer, who will be accused by the sheriff
        else:
            sheriff_accuse_id = random.choice(self.alive_players_id_except(sheriff_id))
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, sheriff_accuse_id), file = open("Activity Log.txt", 'a'))
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, sheriff_accuse_id)
            print('Player #{} is eliminated in this round.'.format(eliminated_id), file = open("Activity Log.txt", 'a'))
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False

class Player(object):
    def __init__(self, player_id, role, title=None, credit=0.5):
        self.player_id = player_id
        self.role = role
        self.is_alive = True
        self.credit = credit
        self.title = title

        if self.role == Role.Seer:
            # a list of identities that seer has checked
            self.identity = []
        # werewolves' default credit is 0.6
        elif self.role == Role.Werewolf:
            self.credit = 0.6

    def Seer(self):
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
        civilian = []
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

    results.to_csv('Simulation Results.csv', index = False)

    results.plot.line(x = 'Num of Players', y = 'Villagers Winning Rate')
    results.plot.line(x = 'Num of Players', y = 'Werewolves Winning Rate')
    plt.show()
