Wordle solver
-------------

To use:

    python3 -i program.py

    >>> w.analyze('share',set(),{0})
    >>> w.analyze('toils',{1,4},{3})
    >> etc..

    enter your guess word: share
    right indexes, separated by space: 1 4
    mismatched indexes, separated by space: 3


    possible words: ['bolds', 'bolks', 'bolos', 'bolus', 'colds', 'dolos', 'folds', 'folks', 'golds', 'golfs', 'golps', 'kolos', 'lobos', 'lobus', 'locks', 'locos', 'locus', 'logos', 'lolos', 'longs', 'loofs', 'looks', 'looms', 'loons', 'loops', 'louns', 'loups', 'lowns', 'lowps', 'molds', 'molos', 'molys', 'nolos', 'polks', 'polos', 'polys', 'solds', 'solos', 'solus', 'volks', 'wolds', 'wolfs', 'xolos', 'yolks', 'yolps']
    suggested letters: ['s', 'o', 'l', 'n', 'd', 'c', 'u', 'p', 'y', 'm', 'g', 'k', 'b', 'f', 'w', 'v', 'x', 'z', 'j', 'q']
    state: WordleSolver.StateData(rightChars={'o': 1, 's': 4}, misplacedChars={'l': 3}, badChars={'r', 'e', 't', 'i', 'a', 'h'})
    recommended words: ['louns', 'colds', 'locus', 'longs', 'molds', 'loups', 'golds', 'bolds', 'lowns', 'polys', 'yolps', 'locks', 'folds', 'molys', 'bolus', 'lobus', 'wolds', 'golps', 'polks', 'yolks', 'lowps', 'bolks', 'golfs', 'folks', 'wolfs', 'volks']