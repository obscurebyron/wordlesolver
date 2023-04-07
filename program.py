# Wordle solver
# -------------
#
# step 1: generate a list of five-letter words (5LW) from a list of popular English words:
#
#     cat popular.txt | grep -Eo '^\b[a-z]{5}\b$'|uniq > popular_five_letter_words.txt
#
# step 2: attack with either a) previous word or b) most-likely letters in the list of 5LW.
#
# algorithm:

from functools import reduce
from dataclasses import dataclass

# get the file's data
with open('valid-wordle-words.txt') as f:
    wordlist = f.read().splitlines()

# charCount = {}
# for word in wordlist:
#     for c in word:
#         charCount[c] = charCount.get(c, 0) + 1
#
# Result, sorted:


letterFrequency = {
 'q': 24, 'j': 47, 'z': 50, 'x': 53, 'v': 175, 'w': 258, 'f': 293,
 'b': 363, 'k': 364, 'g': 369, 'm': 439, 'y': 464, 'h': 492,
 'p': 506, 'u': 533, 'c': 583, 'd': 620, 'n': 723, 'i': 850, 'l': 872,
 't': 896, 'o': 1017, 'r': 1033, 'a': 1213, 's': 1553, 'e': 1650
 }

# So we might want to start with esaro, for example.
#
# Now we have a sense of what will net us the best return, our solver's algorithm is like this:
#
# * enter the guess
# * we'll find out which values are in their right place, in the word but not in right place, or not in the word:
#
#     Result(rightPlace={a:3, e:4}, notRightPlace={t:2}, notInWord=['r','q'])
#     Input('abcde', [2], [1,3])
#
# * with that information, we can narrow down the options.  Note that even in the very first case, there's only about 3000 words possible, so with the information in one round we can narrow it down tremendously.
# * "which words in the list have an 'a' at position 3, an 'e' at 4, and don't have a 't' at 2?: boom, here ya go:"
#
# for the following examples, this helper method will be used to see whether any of multiple chars are in a word

def containsAny(myString: str, chars: set[chr]):
    """ Check whether sequence str contains ANY of the items in set. """
    return True in [c in myString for c in chars]


def containsAll(myString: str, chars: set[chr]):
    """ Check whether sequence str contains ALL of the items in set. """
    return False not in [c in myString for c in chars]

def hasRightChars(myString: str, chrs: dict[chr,int]):
    """ Predicate for whether a given string has particular characters, at the given indexes"""
    for key in chrs:
        if myString[chrs[key]] != key:
            return False
    return True

def hasMisplacedChar(myString: str, chrs: dict[chr,int]):
    """ Predicate for whether a given string has particular characters, but not at the given indexes"""
    # we gotta check - it's in there, right?
    if not containsAll(myString, chrs):
        return False
    
    # but now, let's make sure it's not in the spot.  If it *is* in that spot, it's not the word under review
    for key in chrs:
        if myString[chrs[key]] == key:
            return False
    return True

def removeCharFromStringByIndexes(str, indexes: set[int]):
    result = set()
    for idx, c in enumerate(str):
        if idx not in indexes:
            result.add(c)
    return result

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}

# examples:
# ---------
#
#     # looking for a char at two spots
#     >>> list(filter(lambda w: w[2] == 'e' and w[4] == 'e', wordlist))
#     ['creme', 'crepe', 'geese', 'liege', 'niece', 'obese', 'piece', 'queue',
#     'reeve', 'scene', 'siege', 'suede', 'swede', 'theme', 'there', 'these', 'where']
#
#     # looking for a char at two spots and that doesn't have some particular chars
#     >>> list(filter(lambda w: w[2] == 'e' and w[4] == 'e' and not containsAny(w, {'c','d'}), wordlist))
#     ['geese', 'liege', 'obese', 'queue', 'reeve', 'siege', 'theme', 'there', 'these', 'where']
#
#     # char at two spots, doesn't have some chars, and has a known char *not* at a particular spot
#     >>> list(filter(lambda w: w[2] == 'e' and w[4] == 'e' and hasMisplacedChar(w, 'r',2) and not containsAny(w, {'c','d'}), wordlist))
#     ['reeve', 'there', 'where']
#
# input:
# ------

# analyze('abcde',[1,3],[2])
#
# analyze(str, rightIndexes, wrongLocationIndexes)


class WordleSolver:
    """A utility to help solve Wordle problems"""

    # State data
    # the first value is a dict of "right chars", that is, characters in their right spots.
    # the second value is characters to misplaced spots,
    # and the third is characters that don't exist in the word.
    # for example, ({'e':2,'e':4},{'r':2},{'c','d'})
    @dataclass
    class StateData:
        """state of the analyzer"""
        rightChars: dict[str, int]
        misplacedChars: dict[str, int]
        badChars: set
   
    state = StateData(dict(), dict(), set())

    def analyze(self, myString: str, rightIndexes: set[int], misplacedIndexes: set[int]):
        """str is the attempted word.  rightIndexes are what wordle told us are chars in the right place,
        misplacedIndexes are the chars that exist in the word but are in the wrong place"""

        # given myString=abcde and rightIndexes=[2,3], get {c:2,d:3}
        newRightChars = {myString[x] : x for x in rightIndexes}

        # given myString=abcde and misplacedIndexes=[4], get {e:4}
        newMisplaceChars = {myString[x] : x for x in misplacedIndexes}

        # given myString=abcde and misplacedIndexes=[4] and rightIndexes=[2,3], get ['a','b']
        newBadChars = removeCharFromStringByIndexes(myString, (rightIndexes | misplacedIndexes))
       
        self.state = self.StateData(
            newRightChars,
            newMisplaceChars, 
            (self.state.badChars | newBadChars) - (newRightChars.keys() | newMisplaceChars.keys()),
            )
        
        print('possible words: ' + str(self.new_possibilities()))
        print('suggested letters: ' + str(self.suggestions()))
        print('state: ' + str(self.state))
        print('recommended words: ' + str(self.maximum_unique_high_freq_letters()))

    def reset(self):
        self.state = self.StateData(dict(), dict(), set())

    def suggestions(self):
        surviving_chars = without_keys(letterFrequency, self.state.badChars)
        return sorted(surviving_chars, key=surviving_chars.get, reverse=True)
    
    def new_possibilities(self):
        return [x for x in wordlist if hasRightChars(x, self.state.rightChars) and hasMisplacedChar(x, self.state.misplacedChars) and not containsAny(x, self.state.badChars)]

    def maximum_unique_high_freq_letters(self):
        """return those words within the new_possibilities() set that have the most high-frequency letters"""
        results = dict()
        new_p = self.new_possibilities()
        no_dup_letters = [word for word in new_p if not any(word.count(x) > 1 for x in word)]
        for word in no_dup_letters:
            results[word] = reduce(lambda x,y: x + y, map(lambda x: letterFrequency[x], word))
        return sorted(results, key=results.get, reverse=True)

w = WordleSolver()

while(True):
    guess = input('enter your guess word: ')

    ri = input('right indexes, separated by space: ').split()
    riSet = set([int(i) for i in ri])

    mi = input('mismatched indexes, separated by space: ').split()
    miSet = set([int(i) for i in mi])

    w.analyze(guess, riSet, miSet)

