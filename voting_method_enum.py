from enum import Enum


class VotingMethod(str, Enum):
    single = 'Single Vote'
    multiple = 'Multiple Votes'
    ranked = 'Ranked Voting'
