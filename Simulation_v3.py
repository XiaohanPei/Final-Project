from enum import Enum
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
            print("The Villagers have won!")

        else:
            print("The Werewolves have won!")

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
                    accuse_id = random.choice(sheriff_accused_id, seer_accused_id)
                    votes[accuse_id] += 1

        votes_highest = defaultdict(list)
        for key, value in votes.items():
            votes_highest[value].append(key)

        highest_id = max(votes_highest.items(), key=itemgetter(0))[1]
        return random.choice(highest_id)

    def night(self):
        # choose somebody to protect.
        player_saved = None
        for player in self.alive_players():
            if player.role == Role.Guard:
                player_saved = player.Guard()

        # choose someone to kill.
        player_killed = random.choice(self.alive_nonwerewolves_id())
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
                seer.identity.append(player_checked)
                while seer.credit <= 0.8:
                    if player_checked.role == Role.Werewolf:
                        seer.credit += 0.1
                    else:
                        seer.credit += 0.05

        if player_saved != player_killed:
            for player in list(self.player_role.values()):
                if player.player_id == player_killed:
                    player.is_alive = False
                    print('Player #{} ({}) was killed at night.'.format(player.player_id, player.role.name))
        else:
            print('The Guard managed to protect the other player at night.')

    def day(self):
        # select a sheriff if there is no sheriff
        sheriff_id = self.who_is_sheriff()
        sheriff_credit = self.player_role[sheriff_id].credit

        # when the sheriff is the seer, only one person will be accused
        if self.player_role[sheriff_id].role == Role.Seer:
            seer_accuse_id = self.accused_by_seer()
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id,seer_accuse_id) )

            # vote
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, seer_accuse_id)
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False
                    print('Player #{} is eliminated in this round.'.format(eliminated_id))

        # when the sheriff is a werewolf, who will be accused by the sheriff
        elif self.player_role[sheriff_id].role == Role.Werewolf:
            werewolf_accuse_id = random.choice(self.alive_nonwerewolves_id())
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, werewolf_accuse_id))

            seer_id = 999
            seer_credit = -1
            for player in self.alive_players():
                if player.role == Role.Seer:
                    seer_id = player.player_id
                    seer_credit = player.credit

            if seer_id == 999:
                eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, werewolf_accuse_id)
                for player in list(self.player_role.values()):
                    if player.player_id == eliminated_id:
                        player.is_alive = False
                        print('Player #{} is eliminated in this round.'.format(eliminated_id))
            else:
                seer_accuse_id = self.accused_by_seer()
                eliminated_id = self.vote_for_two_accusations(sheriff_id, sheriff_credit, werewolf_accuse_id, seer_id, seer_credit, seer_accuse_id)
                for player in list(self.player_role.values()):
                    if player.player_id == eliminated_id:
                        player.is_alive = False
                        print('Player #{} is eliminated in this round.'.format(eliminated_id))

        # when the sheriff is neither a werewolf nor seer, who will be accused by the sheriff
        else:
            sheriff_accuse_id = random.choice(self.alive_players_id_except(sheriff_id))
            print('Player #{} says Player #{} is a Werewolf.'.format(sheriff_id, sheriff_accuse_id))
            eliminated_id = self.vote_only_one_accusation(sheriff_id, sheriff_credit, sheriff_accuse_id)
            for player in list(self.player_role.values()):
                if player.player_id == eliminated_id:
                    player.is_alive = False
                    print('Player #{} is eliminated in this round.'.format(eliminated_id))

class Player(object):
    def __init__(self, player_id, role, num_players, title=None, credit=0.5, vote = 0):
        self.player_id = player_id
        self.role = role
        self.is_alive = True
        self.credit = credit
        self.title = title
        self.vote = vote

        if self.role == Role.Seer:
            # a list of identities that seer has checked
            self.identity = []

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
            return 999

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
                    protected = sheriff
                else:
                    protected = random.choice(civilian)

        return protected

if __name__ == "__main__":
    aGame = Game(11)
    aGame.play()

