# Wordle solver
# -------------
#
# step 1: get the wordle word list
#
# step 2: attack with most-likely letters in the list.
#
# algorithm:

from functools import reduce
from dataclasses import dataclass

# get the file's data
with open('wordlist.txt') as f:
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

# So we might want to start with "later", since it has the most frequent letters.
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
# * use a new word with letters we haven't already used, that are highly frequent, so we can cut down letters faster.
#
# for the following examples, this helper method will be used to see whether any of multiple chars are in a word

def containsAny(myString: str, chars: set[chr]):
    """ Check whether sequence str contains ANY of the items in set. """
    return True in [c in myString for c in chars]


def containsAll(myString: str, chars: set[chr]):
    """ Check whether sequence str contains ALL of the items in set. """
    return False not in [c in myString for c in chars]

def hasRightChars(myString: str, chrs: dict[int,chr]):
    """ Predicate for whether a given string has particular characters, at the given indexes"""
    for key in chrs:
        if myString[key] != chrs[key]:
            return False
    return True

def hasMisplacedChar(myString: str, chrs: set[(int,chr)]):
    """ Predicate for whether a given string has particular characters, but not at the given indexes"""
    # we gotta check - it's in there, right?
    if not containsAll(myString, [x for _,x in chrs]):
        return False
    
    # but now, let's make sure it's not in the spot.  If it *is* in that spot, it's not the word under review
    for x,y in chrs:
        if myString[x] == y:
            return False
    return True

def removeCharFromStringByIndexes(str, indexes: set[int]):
    result = set()
    for idx, c in enumerate(str):
        if idx not in indexes:
            result.add(c)
    return result

def without_keys(d, keys):
    """return a dict d with certain keys (keys) removed"""
    return {x: d[x] for x in d if x not in keys}


class WordleSolver:
    """A utility to help solve Wordle problems"""

    # State data
    # the first value is a dict of "right chars", that is, characters in their right spots.
    # the second value is characters to misplaced spots,
    # and the third is characters that don't exist in the word.
    # for example, ({2:'e',4:'e'},{2:'r'},{'c','d'})
    @dataclass
    class StateData:
        """state of the analyzer"""
        rightChars: dict[int, chr]
        misplacedChars: set[(int, chr)]
        badChars: set
   
    state = StateData(dict(), set(), set())

    def analyze(self, myString: str, rightIndexes: set[int], misplacedIndexes: set[int]):
        """str is the attempted word.  rightIndexes are what wordle told us are chars in the right place,
        misplacedIndexes are the chars that exist in the word but are in the wrong place"""

        # given myString=abcde and rightIndexes=[2,3], get {2:c,3:d}
        newRightChars = {x : myString[x] for x in rightIndexes}

        # given myString=abcde and misplacedIndexes=[4], get {4:e}
        newMisplaceChars = {(x , myString[x]) for x in misplacedIndexes}

        # given myString=abcde and misplacedIndexes=[4] and rightIndexes=[2,3], get ['a','b']
        newBadChars = removeCharFromStringByIndexes(myString, (rightIndexes | misplacedIndexes))

        self.state = self.StateData(
            self.state.rightChars | newRightChars,
            self.state.misplacedChars | newMisplaceChars, 
            (self.state.badChars | newBadChars) - (set(newRightChars.values()) | {x for _,x in newMisplaceChars})
            )
        
        new_possibilities = self.new_possibilities()
        suggestions = self.suggestions()
        max_unique_high_freq_letters = self.maximum_unique_high_freq_letters()
        max_unique_high_freq_letters_fresh = self.maximum_unique_high_freq_letters_fresh()
        max_vowels_unique_high_freq_letters_fresh = self.maximum_vowels_unique_high_freq_letters_fresh()

        print('possible words: ' + str(new_possibilities[0:10]) + ' ('+ str(len(new_possibilities)) +' total)')
        print('suggested letters: ' + str(suggestions))
        print('state: ' + str(self.state))
        print('recommended words (no duplicate letters): ' + str(max_unique_high_freq_letters[0:10]) + ' ('+ str(len(max_unique_high_freq_letters)) +' total)')
        print('recommended fresh words (untested letters): ' + str(max_unique_high_freq_letters_fresh[0:10])+ ' ('+ str(len(max_unique_high_freq_letters_fresh)) +' total)')
        print('recommended vowel-fresh words (vowels added in): ' + str(max_vowels_unique_high_freq_letters_fresh[0:10])+ ' ('+ str(len(max_vowels_unique_high_freq_letters_fresh)) +' total)')
        if len(self.maximum_vowels_unique_high_freq_letters_fresh()) < 3:
            last_ditch_fresh_possibilities = self.last_ditch_fresh_possibilities()
            print('last-ditch fresh words: ' + str(last_ditch_fresh_possibilities[0:20]) + ' ('+ str(len(last_ditch_fresh_possibilities)) +' total)')

    def reset(self):
        self.state = self.StateData(dict(), dict(), set())

    def suggestions(self):
        """calculates letters to try based on whether they exist in the possible words / not already used, etc."""
        surviving_chars = without_keys(letterFrequency, self.state.badChars | set(self.state.rightChars.values()) | {y for x,y in self.state.misplacedChars})
        result = set(sorted(surviving_chars, key=surviving_chars.get, reverse=True))
        intersectionWithPossibleWords = result.intersection(set(''.join(self.new_possibilities())))
        return intersectionWithPossibleWords
    
    def new_possibilities(self):
        """calculates a list of the words that are actually possible now, based on used/right/misplaced characters"""
        return [x for x in wordlist if hasRightChars(x, self.state.rightChars) and hasMisplacedChar(x, self.state.misplacedChars) and not containsAny(x, self.state.badChars)]

    def new_fresh_letter_possibilities(self):
        """calculates words with letters you haven't used, to knock out letters faster"""
        return [x for x in wordlist if not containsAny(x, self.state.badChars | set(self.state.rightChars.values()) | {y for x,y in self.state.misplacedChars} )]

    def last_ditch_fresh_possibilities(self):
        """This is like new fresh letter possibilities, except we give it back vowels (we can't make many words without vowels)"""
        words = [x for x in wordlist if not containsAny(x, (self.state.badChars | set(self.state.rightChars.values()) | {y for x,y in self.state.misplacedChars}) - {'a','e','i','o','u','y'} )]
        scored_words = {w : len(self.suggestions().intersection(set(w))) for w in words}
        return sorted(scored_words, key=scored_words.get, reverse=True)

    def maximum_unique_high_freq_letters(self):
        """words that are possible that have the most high-frequency letters"""
        results = dict()
        new_p = self.new_possibilities()
        
        no_dup_letters = [word for word in new_p if not any(word.count(x) > 1 for x in word)]

        for word in no_dup_letters:
            results[word] = reduce(lambda x,y: x + y, map(lambda x: letterFrequency[x], word))
        return sorted(results, key=results.get, reverse=True)
    

    def maximum_unique_high_freq_letters_fresh(self):
        """words that are possible that have the most high-frequency letters, with all unused letters (to knock out letter faster)"""
        results = dict()
        fresh_p = self.new_fresh_letter_possibilities()
        
        no_dup_letters = [word for word in fresh_p if not any(word.count(x) > 1 for x in word)]

        for word in no_dup_letters:
            results[word] = reduce(lambda x,y: x + y, map(lambda x: letterFrequency[x], word))
        return sorted(results, key=results.get, reverse=True)
    

    def maximum_vowels_unique_high_freq_letters_fresh(self):
        """return those words within the new_possibilities() set that have the most high-frequency letters, with frequency-weighting adjusted to favor vowels (to knock out vowels faster)"""
        results = dict()
        fresh_p = self.new_fresh_letter_possibilities()
        
        no_dup_letters = [word for word in fresh_p if not any(word.count(x) > 1 for x in word)]

        for word in no_dup_letters:
            results[word] = reduce(lambda x,y: x + y, map(lambda x: letterFrequency[x] * (1, 100)[x in ['a','e','i','o','u','y']], word))
        return sorted(results, key=results.get, reverse=True)
    
w = WordleSolver()

print("""
Help:
====

Enter the guess you used in Wordle (https://www.nytimes.com/games/wordle/index.html).
Each word's indexes are zero-based (i.e. the first index is 0, the last is 4).
"right indexes" means those letters that Wordle tells you are in the right spot.
"mismatched indexes" means letters that Wordle tells you are not in the right spot.
"possible words" are a list of words that are still possibilities, given everything we know.
"suggested letters" are what remain to try out, filtered by what exist in the possible words.
"state" shows what the program knows about the state of this puzzle (e.g. rightChars, etc).
Recommended words are what you might try, sorted to include the most frequently-used letters.
"recommended fresh words" are similar, but include more unused letters (to knock out possibilities faster).
"recommended vowel fresh words" is similar, but with more vowels.
"last-ditch fresh words" are like recommended fresh words, except we give it back vowels (we can't make many words without vowels).
""")

while(True):
    guess = input('\nenter your guess word: ')

    ri = input('right indexes, separated by space: ').split()
    riSet = set([int(i) for i in ri])

    mi = input('mismatched indexes, separated by space: ').split()
    miSet = set([int(i) for i in mi])

    w.analyze(guess, riSet, miSet)

