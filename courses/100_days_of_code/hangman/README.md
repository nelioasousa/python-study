# Description
Hangman game.

Programming paradigm used: Functional Programming.

# Planning
## Input
User must populate the game with words. The words will be saved in a .txt file in the same directory as the script. The game menu will have two main options: "play" and "words". The "words" options will have a command interface to see, add and remove words from the .txt bank.

## Pseudocode
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
