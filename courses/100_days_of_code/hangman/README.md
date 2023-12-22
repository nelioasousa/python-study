Self-documented script. Check [main.py](./main.py) for more details.

# Description
Hangman game.

Users must populate the game with valid words/phrases. Phrases are considered valid if they consist of pure ASCII characters, don't contain numbers, and include only the `!?',.-` punctuations. The phrases are saved in the [bank.json](./bank.json) file (which must be in the same directory as the script). The game menu have two main options: "play" and "bank of phrases". The "bank of phrases" option includes a command interface to show, hide, add, and remove phrases from the JSON bank.

Programming paradigm used: Functional Programming.

# Planning pseudocode
The "pseudocode" below does not represent the exact structure of the script. It was used as the basis of the source code but was changed as the project progressed to address difficulties and unforeseen problems.

```
def exit_to_menu(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            return None
    return wrapper

@exit_to_menu
def play(word_bank):
    if not word_bank: return False
    difficulty = ask_difficulty(word_bank)
    num_lives = get_num_lives(difficulty)
    word = get_random_word(word_bank, difficulty)
    word_letters = set(word)
    guessed_letters = set()
    last_guess = None
    while True:
        if not num_lives:
            game_over()
            return True
        if guessed_letters.issuperset(word_letters):
            congratulations(word)
            return True
        show_hangman(num_lives, difficulty)
        show_word_board(word, gessed_letters)
        show_hit_message(last_guess, word_letters)
        guess = ask_guess(gessed_letters)
        if guess == word:
            congratulations(word)
            return True
        if guess not in word_letters:
            num_lives -= 1
        if len(guess) == 1:
            guessed_letters.add(guess)
        last_guess = guess

@exit_to_menu
def words(word_bank):
    show_words, info = False, None
    while True:
        words_screen(word_bank, show_words, info)
        command, args = ask_words_command()
        match command:
            case WordsCommand.SHOW_WORDS:
                show_words, info = True, None
            case WordsCommand.HIDE_WORDS:
                show_words, info = False, None
            case WordsCommand.ADD_WORDS:
                info = add_words(word_bank, **args)
            case WordsCommand.REMOVE_WORDS:
                info = remove_words(word_bank, **args)
            case WordsCommand.SAVE_WORDS:
                save_words(word_bank)
                info = 'Words saved in memory.'
            case WordsCommand.MENU:
                save_words(word_bank)
                return
            case WordsCommand.UNKNOW:
                info = 'Unknow command.'
            case WordsCommand.ERROR:
                info = 'Invalid arguments.'

def menu(info = None):
    while True:
        menu_screen(info)
        match input('Select: ').strip().lower():
            case 'play' | 'p':
                return Menu.PLAY
            case 'word' | 'words' | 'w':
                return Menu.WORDS
            case 'exit' | 'e':
                return Menu.EXIT
            case _:
                info = 'Invalid option.'

def main():
    word_bank = load_words()
    info = None
    while True:
        match menu(info):
            case Menu.PLAY:
                success = play(word_bank)
                if success:
                    info = None
                else:
                    info = 'Could not start the game. ' \
                           'Please, register words first.'
            case Menu.WORDS:
                words(word_bank)
                info = None
            case Menu.EXIT:
                return terminate()
```

# Notes
1. Initially the idea was to increase/decrease the number of lives according to the chosen difficulty, but the gallow and hanging man drawings from the `show_hangman()` function were getting sloppy. A fixed six lives were chosen to align with the number of body parts in the basic drawing (head, arms, torso, and legs);
2. Once again, the [Structural Pattern Matching](https://peps.python.org/pep-0636/) was used, limiting the versions of Python compatible with the script;
3. The `main()` function is cleaner compared to the one in the [bill splitter project](../bill_splitter/main.py);
4. I especially like the `KeyboardInterrupt` exception handling.
