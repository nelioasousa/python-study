"""Hangman game for command line console/terminal.

Intended to be used as a script. Do not take command line arguments.
When running, user is presented with two options: play and bank of 
phrases. The first is to run the hangman game. The second is to the
user manage the words and phrases to be played with.

The user also can populate the `bank.json` file manually, outside the 
"bank of phrases" enviroment, but it isn't recommended since they can 
add invalid entries. The script won't run until all invalid phrases 
are removed from the file. When adding phrases manually, the 
difficulty is determined by the user.

Script uses pattern matching, available only with Python >= 3.10.
"""

import string
from enum import Enum
from typing import Literal, Union
from random import choice


def play(phrases_bank: dict[str, list[str]]) -> bool:
    """Run the hangman game in the terminal.
    
    ARGUMENTS:
    phrases_bank `dict[str, list[str]]` -- A dictionary where the keys 
    are strings representing the difficulty (easy, normal or hard) and 
    the values are lists of strings representing the words and phrases 
    available to the user play with.

    RETURN VALUE:
    `bool` -- A boolean value informing if the game runned normally.
    """
    try:
        if not phrases_bank: return False
        difficulty = ask_difficulty(phrases_bank)
        phrase = choice(phrases_bank[difficulty])
        phrase_letters = set(string.ascii_lowercase) & set(phrase)
        guessed_letters = set()
        num_lives = 6
        info = 'Good luck!'
        while True:
            clear_terminal()
            show_hangman(num_lives)
            show_phrase_board(phrase, guessed_letters)
            print('[!] %s' %info, end='\n\n')
            if not num_lives:
                input('Game over! ')
                return True
            if guessed_letters.issuperset(phrase_letters):
                input('You won! Congratulations! ')
                return True
            guess = check_phrase(input('Your guess: '))
            if not guess:
                info = 'Please, supply a valid guess. ' \
                       'Try to guess a letter or the whole phrase!\n' \
                       'Phrases contain only:\n' \
                       '  - letters (a-z)\n' \
                       '  - dots and commas (.,)\n' \
                       '  - hyphens and apostrophes (-\')\n' \
                       '  - exclamation and question marks (!?)'
            elif guess == phrase:
                guessed_letters.update(phrase_letters)
                info = 'You got it. Well done!'
            elif len(guess) == 1:
                if guess in string.ascii_lowercase:
                    guessed_letters.add(guess)
                    if guess in phrase_letters:
                        info = 'Good guess! There is letter "%s"!' %guess
                    else:
                        info = 'There isn\'t letter "%s"...' %guess 
                        num_lives -= 1
                else:
                    info = 'Only english alphabet letters allowed.'
            else:
                info = 'Wrong guess!'
                num_lives -= 1
    except KeyboardInterrupt:
        return True

def ask_difficulty(
        phrases_bank: dict[str, list[str]]
        ) -> Literal['easy', 'normal', 'hard']:
    """Ask the user to choose the game difficulty.
    
    ARGUMENTS:
    phrases_bank `dict[str, list[str]]` -- A dictionary where the keys 
    are strings representing the difficulty (easy, normal or hard) and 
    the values are lists of strings representing the words and phrases 
    available to the user play with.
    
    RETURN VALUE:
    `Literal['easy', 'normal', 'hard']` -- The game difficulty choosed 
    by the user.

    EXCEPTIONS RAISED:
    `KeyboardInterrupt` -- When the user chooses the EXIT option 
    instead of selecting a difficulty.
    """
    while True:
        clear_terminal()
        print('Choose the difficulty', end='\n\n')
        print('\n'.join(
            '[%s] %s' %(d[0], d) for d in sorted_phrases_bank(phrases_bank)
            ).upper())
        print('[X] EXIT', end='\n\n')
        match input('Select: ').lower():
            case ('easy' | 'e') if 'easy' in phrases_bank:
                return 'easy'
            case ('normal' | 'n') if 'normal' in phrases_bank:
                return 'normal'
            case ('hard' | 'h') if 'hard' in phrases_bank:
                return 'hard'
            case ('exit' | 'x'):
                raise KeyboardInterrupt('User interrupt')

def sorted_phrases_bank(
        phrases_bank: dict[str, list[str]]
        ) -> dict[str, list[str]]:
    """Builds a new `phrases_bank` sorted by key (difficulty)."""
    def key_sorter(key_value_pair):
        match key_value_pair[0]:
            case 'easy': return 0
            case 'normal': return 1
            case 'hard': return 2
    return {k: v \
            for k, v \
            in sorted(phrases_bank.items(), key=key_sorter)}

def clear_terminal():
    """Clear the terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_hangman(num_lives: Literal[0, 1, 2, 3, 4, 5, 6]):
    """Show the gallows and the hanging man according to life count."""
    hangmans = (
""" +---+
 |   |
 O   |
/|\\  |
/ \\  |
_____| Lives: 0/6""",
""" +---+
 |   |
 O   |
/|\\  |
/    |
_____| Lives: 1/6""",
""" +---+
 |   |
 O   |
/|\\  |
     |
_____| Lives: 2/6""",
""" +---+
 |   |
 O   |
/|   |
     |
_____| Lives: 3/6""",
""" +---+
 |   |
 O   |
 |   |
     |
_____| Lives: 4/6""",
""" +---+
 |   |
 O   |
     |
     |
_____| Lives: 5/6""",
""" +---+
 |   |
     |
     |
     |
_____| Lives: 6/6"""
    )
    print(hangmans[num_lives], end='\n\n')

def show_phrase_board(phrase: str, guessed_letters: set[str]):
    """Reveals the `phrase` according to the `guessed_letters`."""
    board = []
    for char in phrase:
        if char in guessed_letters or char in " !?,'.-":
            board.append(char)
        else:
            board.append('_')
    print(''.join(board), end='\n\n')

def check_phrase(phrase: str) -> Union[Literal[False], str]:
    """Check `phrase` validity based on some criteria.
    
    `phrase` is considered valid if it is constituted of pure ASCII 
    characters, don't contain numbers, and contain only "!?,'.-" 
    punctuations. Valid entries are returned after being put in lower 
    case and have consecutive whitespaces removed. `False` is returned 
    when a invalid `phrase` is encontered. 

    ARGUMENTS:
    phrase `str` -- String to be checked.

    RETURN VALUE:
    `Union[Literal[False], str]` -- `False` if `phrase` is invalid or 
    `str` otherwise.
    """
    # Only ASCII characters
    if not phrase.isascii(): return False
    # Lower case and space char instead of whitespaces
    phrase = ' '.join(phrase.lower().split())
    # Catch empty strings (just whitespaces)
    if not phrase: return False
    word_chars = frozenset(phrase)  # frozenset is more efficient
    puncts = frozenset(string.punctuation).intersection(word_chars)
    # Only "!?,'.-" punctuations are allowed
    if not puncts <= {'!', '?', '-', ',', '.', "'"}: return False
    # Numbers are not allowed in the phrase
    if frozenset(string.digits).intersection(word_chars): return False
    return phrase



def bank(phrases_bank: dict[str, list[str]]):
    """Bank of phrases handler."""
    try:
        show_phrases, info = False, None
        while True:
            phrases_display(phrases_bank, show_phrases)
            command, arg = ask_command(info)
            match command:
                case BankCommand.SHOW_PHRASES:
                    show_phrases, info = True, None
                case BankCommand.HIDE_PHRASES:
                    show_phrases, info = False, None
                case BankCommand.ADD_PHRASE:
                    result = add_phrase(phrases_bank, arg)
                    if result:
                        info = 'Phrase added: "%s"' %result
                    else:
                        info = 'Invalid phrase for "add" command: "%s"\n' \
                               'Phrases must contain only:\n' \
                               '  - letters (a-z)\n' \
                               '  - dots and commas (.,)\n' \
                               '  - hyphens and apostrophes (-\')\n' \
                               '  - exclamation and question marks (!?)' %arg
                case BankCommand.RMV_PHRASE:
                    result = rmv_phrase(phrases_bank, arg)
                    if result:
                        info = 'Phrase removed: "%s"' %result
                    else:
                        info = 'Phrase not found: "%s"' %arg
                case BankCommand.MENU:
                    save_phrases(phrases_bank)
                    return
                case BankCommand.ERROR:
                    info = arg
    except KeyboardInterrupt:
        save_phrases(phrases_bank)
        return

class BankCommand(Enum):
    """Enumerate commands available inside the bank of phrases."""
    SHOW_PHRASES = 0
    HIDE_PHRASES = 1
    ADD_PHRASE = 2
    RMV_PHRASE = 3
    MENU = 4
    ERROR = 5

def phrases_display(phrases_bank: dict[str, list[str]], show_phrases: bool):
    """Handle the phrases display inside the bank of phrases."""
    clear_terminal()
    print('REGISTERED WORDS/PHRASES', end='\n\n')
    if not phrases_bank:
        print('None registered yet!', end='\n\n')
    elif show_phrases:
        phrases_bank = sorted_phrases_bank(phrases_bank)
        for difficulty, phrases in phrases_bank.items():
            print('%s:' %difficulty.upper())
            print('\n'.join('    - %s' %p for p in phrases))
        print('')
    else:
        count = sum(len(phrases) for phrases in phrases_bank.values())
        print('Hidding %d word(s)/phrase(s)!' %count, end='\n\n')

def ask_command(
        info: Union[str, None] = None
        ) -> tuple[BankCommand, Union[str, None]]:
    """Handle the command screen inside the bank of phrases."""
    print('AVAILABLE COMMANDS:')
    print('  show')
    print('  hide')
    print('  add <word/phrase>')
    print('  rmv <word/phrase>')
    print('  menu', end='\n\n')
    if info is not None:
        print('[!] %s' %info, end='\n\n')
    command, *argument = input('>>> ').split(maxsplit=1)
    match (command.lower(), *argument):
        case [('show' | 'hide' | 'menu') as command, _]:
            return BankCommand.ERROR, '"%s" command doesn\'t ' \
                                      'accept arguments' %command
        case ['show']:
            return BankCommand.SHOW_PHRASES, None
        case ['hide']:
            return BankCommand.HIDE_PHRASES, None
        case ['menu']:
            return BankCommand.MENU, None
        case [('add' | 'rmv') as command]:
            return BankCommand.ERROR, '"%s" command must be followed ' \
                                      'by a word or phrase' %command
        case ['add', phrase]:
            return BankCommand.ADD_PHRASE, phrase
        case ['rmv', phrase]:
            return BankCommand.RMV_PHRASE, phrase
        case _:
            return BankCommand.ERROR, 'Unknow command'

def add_phrase(
        phrases_bank: dict[str, list[str]], phrase: str
        ) -> Union[Literal[False], str]:
    """Handle the "add" command in the bank of phrases.
    
    ARGUMENTS:
    phrases_bank `dict[str, list[str]]` -- A dictionary where the keys 
    are strings representing the difficulty (easy, normal or hard) and 
    the values are lists of strings representing the words and phrases 
    available to the user play with.

    phrase `str` -- String to be added to `phrases_bank`.

    RETURN VALUE:
    `Union[Literal[False], str]` -- Returns `False` if `phrase` can't 
    be added to `phrases_bank` or a `str` representing the processed 
    `phrase` added to `phrases_bank` otherwise.
    """
    phrase = check_phrase(phrase)
    if not phrase: return False
    if len(phrase) < 2: return False
    if phrase_exists(phrases_bank, phrase): return phrase
    num_letters = len(set(string.ascii_lowercase) & set(phrase))
    difficulty = 'easy' if num_letters < 5 \
        else 'normal' if num_letters < 8 \
        else 'hard'
    phrases_bank.setdefault(difficulty, []).append(phrase)
    return phrase

def phrase_exists(phrases_bank: dict[str, list[str]], phrase: str):
    """Checks if `phrase` exists inside `phrases_bank`."""
    for phrases in phrases_bank.values():
        if phrase in phrases:
            return True
    return False

def rmv_phrase(
        phrases_bank: dict[str, list[str]], phrase: str
        ) -> Union[str, Literal[False]]:
    """Handle the "rmv" command in the bank of phrases.
    
    ARGUMENTS:
    phrases_bank `dict[str, list[str]]` -- A dictionary where the keys 
    are strings representing the difficulty (easy, normal or hard) and 
    the values are lists of strings representing the words and phrases 
    available to the user play with.

    phrase `str` -- String to be removed from `phrases_bank`.

    RETURN VALUE:
    `Union[Literal[False], str]` -- Returns `False` if `phrase` wasn't 
    found inside `phrases_bank` or a `str` representing the removed 
    phrase.
    """
    phrase = check_phrase(phrase)
    if not phrase: return False
    for difficulty, phrases in phrases_bank.items():
        try:
            phrases.remove(phrase)
            if not phrases:
                del phrases_bank[difficulty]
            return phrase
        except ValueError:
            continue
    return False

def save_phrases(phrases_bank: dict[str, list[str]]):
    """Save `phrases_bank` in memory as a JSON file."""
    from json import dump
    with open('./bank.json', mode='w') as json_bank:
        dump(sorted_phrases_bank(phrases_bank), json_bank, ensure_ascii=True)



def menu(info: Union[str, None] = None):
    """Handle the menu."""
    while True:
        menu_screen(info)
        match input('Select: ').strip().lower():
            case 'play' | 'p':
                return MenuCommand.PLAY
            case 'bank' | 'b':
                return MenuCommand.BANK
            case 'exit' | 'x':
                return MenuCommand.EXIT
            case _:
                info = 'Invalid option.'

class MenuCommand(Enum):
    """Enumerate commands available to the user inside the menu."""
    PLAY = 0
    BANK = 1
    EXIT = 2

def menu_screen(info: Union[str, None] = None):
    """Display the menu screen."""
    clear_terminal()
    print('(x_x) HANGMAN GAME (x_x)', end='\n\n')
    print('[P] PLAY\n[B] BANK OF PHRASES\n[X] EXIT', end='\n\n')
    if info is not None: print('[!] %s' %info, end='\n\n')

def main():
    phrases_bank = load_phrases_bank()
    info = None
    while True:
        match menu(info):
            case MenuCommand.PLAY:
                success = play(phrases_bank)
                if success:
                    info = None
                else:
                    info = "Couldn't start the game. " \
                           "Please, register phrases first."
            case MenuCommand.BANK:
                bank(phrases_bank)
                info = None
            case MenuCommand.EXIT:
                return terminate()

def load_phrases_bank() -> dict[str, list[str]]:
    """Load the bank.json file while checking its validity."""
    from json import load
    def not_allowed(str_to_decode: str):
        raise ValueError('Invalid value: %s' %str_to_decode)
    with open('./bank.json', mode='br') as json_bank:
        phrases_bank = load(json_bank,
                            parse_int=not_allowed,
                            parse_float=not_allowed,
                            parse_constant=not_allowed)
    assert isinstance(phrases_bank, dict), \
        "Decoded file isn't a JSON object (dict)"
    assert {'easy', 'normal', 'hard'} >= frozenset(phrases_bank), \
        'Only "easy", "normal", and "hard" difficulties are allowed'
    for difficulty, phrases in phrases_bank.items():
        assert isinstance(phrases, list), \
            f"Couldn't understand {difficulty=} phrases"
        for phrase in phrases:
            assert check_phrase(phrase), \
                f'Invalid phrase found in {difficulty=}: "%s"' %phrase
    return {k: v for k, v in phrases_bank.items() if v}  # skip empty lists

def terminate():
    """Script exit screen."""
    clear_terminal()
    print('Tranks for playing! Goodbye!')
    print('More in github.com/nelioasousa/python-study')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        terminate()
