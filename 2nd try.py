from enum import Enum
import numpy as np
import random
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
                self.player_role[i] = Player(i, Role.Werewolf, self.num_players)
            if i == 4:
                self.player_role[i] = Player(i, Role.Seer, self.num_players)
            if i == 5:
                self.player_role[i] = Player(i, Role.Guard, self.num_players)
            if i >= 6 and i <= num_players:
                self.player_role[i] = Player(i, Role.Villager, self.num_players)

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

    #select a sheriff if there is no sheriff
    def who_is_sheriff(self):
        alive_titles = []
        for player in self.alive_players(self):
            alive_titles.append(player.title)
        if 'sheriff' in alive_titles:
            for player in self.alive_players(self):
                if player.title == 'sheriff':
                    return player.player_id
        else:
            non_werewolves = {}
            werewolves = {}
            for player in self.alive_players(self):
                if player.role == Role.Werewolf:
                    werewolves[player.player_id] = player.credit
                else:
                    non_werewolves[player.player_id] = player.credit

            non_highest = defaultdict(list)
            wolf_highest = defaultdict(list)

            for key, value in non_werewolves.items():
                non_highest[value].append(key)
            for key,value in werewolves.items():
                wolf_highest[value].append(key)

            non_credit = max(non_highest.items(), key = itemgetter(0)[0])
            non_highest_id = max(non_highest.items(), key = itemgetter(0)[1])
            wolf_credit = max(wolf_highest.items(), key = itemgetter(0)[0])
            wolf_highest_id = max(wolf_highest.items(), key = itemgetter(0)[1])

            if non_credit > wolf_credit:
                dec = bernoulli.rvs(1, non_credit)
                if dec == 1:
                    return random.choice(non_highest_id)
                else:
                    return random.choice(wolf_highest_id)
            elif wolf_credit < non_credit:
                dec = bernoulli.rvs(1, wolf_credit)
                if dec == 1:
                    return random.choice(wolf_highest_id)
                else:
                    return random.choice(non_highest_id)
            else:
                return random.choice(non_highest_id+wolf_highest_id)

    # who will be accused by seer
    def accused_by_seer(self):
        for player in self.alive_players():
            if player.role == Role.Seer and player.is_alive:
                seer = player

        if seer.identity[-1].role == Role.Werewolf:
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
                for player in seer.identity[0, -1]:
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



    def night(self):
        # choose somebody to protect.
        player_saved = Player.Guard()

        # choose someone to kill.
        player_killed = random.choice(self.alive_players_id())
        # if the sheriff is not a werewolf, werewolves will kill the guard.
        for player in list(self.player_role.values()):
            if player.title == 'sheriff' and player.role != Role.Werewolf:
                player_killed = player

        # Check someone's identity
        for player in list(self.player_role.values()):
            if player.role == Role.Seer and player.is_alive:
                seer = player
                player_checked = self.player_role[player.Seer()]
                # if Seer is not the Sheriff, Seer must be very curious about the Sheriff's identity and check it.
                for other in list(self.player_role.values()):
                    if other.title == 'sheriff' and other.role != Role.Seer:
                        player_checked = other
                seer.identity[player_checked.player_id] = player_checked.role
                if player_checked.role == Role.Werewolf:
                    seer.credit += 0.1
                else:
                    seer.credit += 0.05

        if player_saved.player_id != player_killed.player_id:
            for player in list(self.player_role.values()):
                if player.player_id == player_killed.player_id:
                    player.is_alive = False
                    print('Player #{} ({}) was killed at night.'.format(player.player_id, player.role.name))

    def day(self):
        # select a sheriff if there is no sheriff
        sheriff_id = self.who_is_sheriff()

        # when the sheriff is the seer, only one person will be accused
        if self.player_role[sheriff_id].role == Role.Seer:
            seer_accuse_id = self.accused_by_seer()
            print('player #{} says player #{} is a werewolf.'.format(sheriff_id), seer_accuse_id)

        # when the sheriff is a werewolf, who will be accused by the sheriff

        # when the sheriff is neither a werewolf nor seer, who will be accused by the sheriff


class Player(object):
    def __init__(self, player_id, role, num_players, title=None, credit=0.5):
        self.player_id = player_id
        self.role = role
        self.is_alive = True
        self.credit = credit
        self.title = title

        if self.role == Role.Seer:
            # a list of identities that seer has checked
            self.identity = []

    def Seer(self):
        unknown = []
        for player in Game.alive_players():
            if player.role == Role.Seer:
                seer = player

        for other in Game.alive_players():
            if other.role != Role.Seer and other not in seer.identity:
                unknown.append(other.player_id)

        if len(unknown) > 0:
            return random.choice(unknown)
        else:
            return 999

    def Guard(self):
        civilian = []
        for player in Game.alive_players():
            if player.title != 'sheriff':
                civilian.append(player.player_id)

        protected = random.choice(Game.alive_players_id())
        for player in Game.alive_players():
            if player.title == "sheriff":
                sheriff = player
                decision = bernoulli.rvs(1, sheriff.credit)
                if decision == 1:
                    protected = sheriff
                else:
                    protected = random.choice(civilian)

        return protected


