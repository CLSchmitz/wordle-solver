import random as sysrand

from matplotlib.pyplot import get

'''
word_info schema:

{'positions': [{'correct': 'h', 'wrong': []},
  {'correct': '', 'wrong': ['o', 'p']},
  {'correct': '', 'wrong': ['o', 'p']},
  {'correct': '', 'wrong': ['o', 'p']},
  {'correct': 's', 'wrong': []}],
 'letters': ['u']}

Means position 1 contains an h,
positions 2-4 don't contain o or p,
position 5 contains an s,
one of the remaining letters is a u.
'''

file = open("sgb-words.txt", "r")

words = []
for line in file:
  stripped_line = line.strip()
  words.append(stripped_line)

file.close()

# Found using get_letter_frequencies and pick_best_word on entire word dataset.
# Greatly improves computation time to not compute this on each call
top_10_words =  ['earls',
                 'reals',
                 'tears',
                 'rates',
                 'stare',
                 'aster',
                 'tares',
                 'raise',
                 'arise',
                 'arose']

def make_word_info():
    '''
    Helper function that returns an empty word_info tuple
    '''

    d = [{'correct':'','wrong':[]},
    {'correct':'','wrong':[]},
    {'correct':'','wrong':[]},
    {'correct':'','wrong':[]},
    {'correct':'','wrong':[]}]
    word_info = {'positions':d, 'letters': []}

    return word_info

def get_letter_frequencies(words): #TODO remove letters that are already in word. Unless they're in there twice?
    '''
    Returns the relative frequency of each letter in the alphabet in a list of words.
    Each letter is only counted once per word.

    :param words: list of strings
    :return: dict of form {letter: relative frequency}
    '''
    
    
    al = 'abcdefghijklmnopqrstuvwxyz'
    all_words = ''.join([''.join(set(x)) for x in words])
    freqs = {x: all_words.count(x)/len(all_words) for x in al}
    
    return freqs

def pick_best_word(words, freqs, tiebreak = 'random_choice'):
    '''
    Given a list of words and relative letter frequencies, returns the best word to guess
    as measured by its frequency score (sum of its letters' frequencies).
    :param words: list of strings
    :param freqs: dict of form {letter: relative frequency}
    :param tiebreak: Defines behaviour if multiple words have same score. If 'random_choice', randomly 
                     returns one; if 'return_all', returns all as list
    :return: string or list of strings, highest-score word(s)
    '''
    
    scores = []
    
    for word in words:
        
        score = 0

        for letter in set(word):
            
            score += freqs[letter]
        
        scores.append(score)
    
    max_indexes = [i for i, x in enumerate(scores) if x == max(scores)]

    if len(max_indexes) > 1: 
            
            if tiebreak == 'random_choice':
                
                index = sysrand.choice(max_indexes)
                return words[index]
            
            elif tiebreak == 'return_all':
                
                return [words[x] for x in max_indexes]
    
    else: return words[max_indexes[0]]

def check_guess(guess, correct):
    '''
    Checks a guessed word against the answer and returns the result in wordle format
    :param guess: five-letter string
    :param correct: five-letter string
    :return: five-symbol string corresponding to guess, consisting of 
             'X' (correct letter, correct location),
             'O' (correct letter, wrong location),
             '_' (wrong letter).
    
    '''
    
    out = ['_','_','_','_','_']
    
    for i, letter in enumerate(guess):
        
        if correct[i] == letter: out[i] = 'X'
    
    for i, letter in enumerate(guess):
        
        if letter in correct and correct[i] is not letter:
            
            # Only need to put O if the correct position(s) is/are not X already
            # I'm sure this is ugly and misses edge cases
            letter_positions = [i for i, x in enumerate(correct) if x == letter]
            out_values_for_letter = [out[i] for i in letter_positions]
            num_letters_accounted_for = out_values_for_letter.count('X')
            if num_letters_accounted_for < len(letter_positions):
                out[i] = 'O'
    
    
    return ''.join(out)

def manual_check_guess(guess):
    '''
    Allows the user to manually check a guess using the schema above.
    Useful for solving the real wordle (without a frontend).
    :param guess: a five-letter string
    :return: the five-symbol status string input by the user
    '''
    print(guess)
    status = input()
    return status


def list_matching_words(word_info, words):
    '''
    Given a word_info variable (defined by schema at top of file),
    returns all words from list that qualify.
    :param word_info: dict(list of dicts, dict) as described above
    :param words: list of strings
    :return: list of strings, all words from list that match word_info
    '''
    
    matching_words = []
    
    for word in words:
        
        qualifies = True
        
        for i, pos in enumerate(word_info['positions']):
            
            if pos['correct'] != '' and word[i] != pos['correct']: qualifies = False
            
            for letter in pos['wrong']:
                
                if word[i] == letter: qualifies = False
        
        for letter in word_info['letters']:
            
            if letter not in word: qualifies = False
                
        if qualifies: matching_words.append(word)
    
    return matching_words


def update_info_from_guess(status, guess, word_info):
    '''
    Given a word_info variable, a guess that conforms to that variable
    (any guess, doesn't have to be the optimal one), and the status returned by wordle
    for that guess, updates the word_info variable.
    :param status: string using X, O, _ schema described in check_guess
    :param guess: string, the guess that generated the status
    :param word_info: tuple, the word_info before the guess was made
    :return: tuple, updated word_info
    '''

    for i, result in enumerate(status):
        
        guessed_letter = guess[i]
        
        if result == '_':
            
            for pos in word_info['positions']:
                
                if pos['correct'] == '' and guessed_letter not in pos['wrong']: pos['wrong'].append(guessed_letter)
        
        if result == 'X':
        
            word_info['positions'][i]['correct'] = guessed_letter
            word_info['positions'][i]['wrong'] = [] # Just an optimization
            
            #TODO remove from letters if in there? Double letters?
        
        if result == 'O':
            
            if guessed_letter not in word_info['letters']: word_info['letters'].append(guessed_letter)
            word_info['positions'][i]['wrong'].append(guessed_letter)
    
    return word_info
        

def solve(correct = None, method = 'standard', count_tries = False, verbose = True):

    if method == 'standard':
        return solve_standard(correct,count_tries,verbose)
    elif method == 'two_guess':
        return solve_two_guess(correct,count_tries,verbose)

def solve_standard(correct = None, count_tries = False, verbose = True):
    '''
    The big boy function. Optionally takes in a correct word and solves it automatically,
    else suggests guesses and solves using user feedback.
    :param correct: string, optional, a correct word to solve for. If None, user can supply correct word or guess feedback.
    :param count_tries: bool, optional, if True, function returns number of guesses taken until correct word
    :param verbose: verbose
    :return: None if count_tries is false, else int: number of tries taken
    '''

    word_info = make_word_info()
    
    # Initiate all the other stuff
    status = '_____'
    tries = 0
    choices = words
    
    while status != 'XXXXX':
            
        if tries > 0:
            
            choices = list_matching_words(word_info, choices) # Get updated list of choices

            # TODO see if making the second guess use completely different letters improves performance

            if len(choices) == 0:
                print('No matching word found!')
                break

            freqs = get_letter_frequencies(choices) # Get letter frequencies in list of choices
            guess = pick_best_word(choices, freqs) # Pick best word according to letter frequencies
            

        else: # On first iteration just pick a good starting word
            
            guess = sysrand.choice(top_10_words)
        
        if correct is not None:

            status = check_guess(guess, correct) # Check guess against correct word
            if verbose: print(guess + ' ' + status)

        else: 

            status = manual_check_guess(guess) # Ask for user feedback
        
        word_info = update_info_from_guess(status, guess, word_info) # Update word_info
        
        tries += 1
    
    if count_tries: return tries

def solve_two_guess(correct = None, count_tries = False, verbose = True):
    '''
    The big boy function. Optionally takes in a correct word and solves it automatically,
    else suggests guesses and solves using user feedback.
    :param correct: string, optional, a correct word to solve for. If None, user can supply correct word or guess feedback.
    :param count_tries: bool, optional, if True, function returns number of guesses taken until correct word
    :param verbose: verbose
    :return: None if count_tries is false, else int: number of tries taken
    '''

    # Initiate word_info
    word_info = make_word_info()
    
    # Initiate all the other stuff
    status = '_____'
    tries = 0
    choices = words
    
    while status != 'XXXXX':

        if tries == 1 and status.count('X') < 3: # Make another guess with a word covering high-prob new letters,
                                                 # unless first guess was great (3 correct letters)

            temp_word_info = make_word_info()
            for pos in temp_word_info['positions']:
                for letter in guess: 
                    pos['wrong'].append(letter)

            temp_choices = list_matching_words(temp_word_info, choices)
        
            freqs = get_letter_frequencies(temp_choices)
            guess = pick_best_word(temp_choices, freqs)


        elif tries > 1:
            
            choices = list_matching_words(word_info, choices) # Get updated list of choices

            # TODO see if making the second guess use completely different letters improves performance

            if len(choices) == 0:
                print('No matching word found!')
                break

            freqs = get_letter_frequencies(choices) # Get letter frequencies in list of choices
            guess = pick_best_word(choices, freqs) # Pick best word according to letter frequencies

        else: # On first iteration just pick a good starting word
            
            guess = sysrand.choice(top_10_words)
        
        if correct is not None:

            status = check_guess(guess, correct) # Check guess against correct word
            if verbose: print(guess + ' ' + status)

        else: 

            status = manual_check_guess(guess) # Ask for user feedback
        
        word_info = update_info_from_guess(status, guess, word_info) # Update word_info
       
        tries += 1
    
    if count_tries: return tries

def solve_benchmark():

    from tqdm import tqdm

    s = []
    print('Standard') # 4.271 tries on average
    for x in tqdm(words):
        s.append(solve(x , count_tries= True, verbose = False))
    
    t = []
    print('Two Guess') # 4.343 tries on average
    for x in tqdm(words):
        t.append(solve(x , method = 'two_guess', count_tries= True, verbose = False))

    return s, t    

if __name__ == "__main__":
        
    solve()