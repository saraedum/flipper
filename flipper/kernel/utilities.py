
''' A module of useful, generic functions; including input and output formatting. '''

from string import ascii_lowercase, digits, ascii_letters, punctuation
import itertools

import flipper

VISIBLE_CHARACTERS = digits + ascii_letters + punctuation

def string_generator(n, skip=None):
    ''' Return a list of n usable names, none of which are in skip. '''
    
    assert isinstance(n, flipper.IntegerType)
    assert skip is None or isinstance(skip, (list, tuple, dict, set))
    
    skip = set() if skip is None else set(skip)
    if n < 1: return []
    
    alphabet = ascii_lowercase
    results = []
    for letters in (c for i in itertools.count(start=1) for c in itertools.product(alphabet, repeat=i)):
        word = ''.join(letters)
        if word not in skip:
            results.append(word)
        if len(results) >= n:
            break
    
    return results

def name_objects(objects, skip=None):
    ''' Return a list of pairs (name, object). '''
    
    assert isinstance(objects, (list, tuple))
    
    return zip(string_generator(len(objects), skip), objects)

###############################################################################

def product(iterable, start=1, left=True):
    ''' Return the product of start (default 1) and an iterable of numbers. '''
    assert False
    
    value = None
    for item in iterable:
        if value is None:
            value = item
        elif left:
            value = item * value
        else:
            value = value * item
    if value is None: value = start
    
    return value

def encode_binary(sequence):
    ''' Return the given sequence of 0's and 1's as a string in base 64. '''
    
    step = 6  # 2**step <= len(VISABLE_CHARACTERS)
    return ''.join(VISIBLE_CHARACTERS[int(''.join(str(x) for x in sequence[i:i+step]), base=2)] for i in range(0, len(sequence), step))

