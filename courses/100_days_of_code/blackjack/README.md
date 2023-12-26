# Description
Blackjack game in the console.

Programming paradigm: OOP & Functional Programming.

Implementation of casino blackjack game (or 21/Twenty-One). The user will be able to set the the following configurations/rules:
1. Number of decks used by the Dealer;
2. Dealer hit at soft 17 instead of standing;
3. Enable surrender;
4. Enable hole card (Dealer's second card is face down);
5. Max number of hands (Limit the number of splits);
6. Allow split in aces;
7. Allow double after split;
8. Double in 9/10/11 only.

Fixed rules:
1. Player's cards are dealt face up (Dealer can see them);
2. The Dealer only makes his move after the Player ends all their hands;
3. Dealer must hit until a total of 17 or higher;
4. The Dealer pays 100% of the bets in the winning hands;
5. The Dealer returns 50% of the bets in hands that have been surrendered;
6. Can't double the bet in a blackjack hand.

# Planning
## Game steps
The game can be simplified in:
1. Set player funds;
2. Prepare deck;
3. Ask bet;
4. Set dealer and player hands;
5. While open hands exits, ask player decision;
6. After all hands are closed, the dealer makes their move;
7. Process the wagers in each hand (Process losses, winnings, and surrenders);
8. Ask for another round if the player still has money.

## Pseudocode
```
# See https://stackoverflow.com/q/51671699/16969525
Card = namedtuple('Card', ['rank', 'suit'])


class DrawPile()

    def __init__(self, num_decks):
        ...
    
    def draw(self, num_cards) -> list[Card]:
        ...

    def recompose(self):
        ...


class Hand():

    def __init__(self, ...):
        ...
    
    def split(self, ...) -> Hand:
        ...
    
    def add_card(self, card):
        ...

    def close(self):
        ...
    
    def surrender(self):
        ...
    
    def is_closed(self) -> bool:
        ...
    
    def is_busted(self) -> bool:
        ...
    
    def is_surrenrered(self) -> bool:
        ...


def play(start_money: int = 500,
         num_decks: int = 1,
         max_num_hands: int = 1,
         hit_soft_17: bool = False,
         double_in_splits: bool = False,
         split_in_aces: bool = False,
         restrict_double: bool = False,
         enable_surrender: bool = False,
         enable_hole_card: bool = False):
    bankroll = start_money
    pile = DrawPile(num_decks)
    while bankroll:
        message = "Let's start! Place your bet."
        while True:
            table_screen(bankroll=bankroll, message=message)
            bet = ask_bet('Initial bet: $')
            if bet is None:
                message = 'You must enter an interger number.'
            elif bet > bankroll:
                message = 'You do not have enough funds.'
            else:
                bankroll -= bet
                message = None
                break
        dealer_hand = Hand(cards=pile.draw(2), bet=None)
        player_hands = [Hand(cards=pile.draw(2), bet=bet)]
        num_split = max_num_hands - 1
        while has_open_hands(player_hands):
            decisions = [None] * len(player_hands)
            for i, hand in enumerate(player_hands):
                if hand.is_closed(): continue
                message = 'Make a decision for HAND %d.\n' \
                          'Hit, stand, double, split, or surrender?' %i
                while True:
                    table_screen(dealer_hand=dealer_hand,
                                 hole_card=enable_hole_card,
                                 player_hands=player_hands,
                                 decisions=decisions,
                                 bankroll=bankroll,
                                 message=message)
                    decision = ask_decision(hand_index=i)
                    if decision is None:
                        message = 'Not understood. ' \
                                  'Waiting decision for HAND %d.\n'
                                  'Hit, stand, double, split, or surrender?' %i
                        continue
                    elif decision == 'split':
                        if not num_split:
                            message = 'Cannot split HAND %d. ' \
                                      'Max number of hands reached.' %i
                            continue
                        if not split_in_aces and hand.ranks == ['A', 'A']:
                            message = 'Cannot split HAND %d. ' \
                                      'Split aces is not allowed.' %i
                            continue
                        if len(hand.cards) != 2 or len(set(hand.ranks)) != 1:
                            message = 'Cannot split HAND %d.' %i
                            continue
                    elif decision == 'double':
                        if len(player_hands) > 1 and not double_in_splits:
                            message = 'Cannot double HAND %d. ' \
                                      'Double after split is not allowed.' %i
                            continue
                        if restrict_double \
                                and hand.min_total() not in {9, 10, 11}:
                            message = 'Cannot double HAND %d. ' \
                                      'Double only allowed on 9, 10, or 11.' %i
                            continue
                        if hand.bet > bankroll:
                            message = 'Cannot double HAND %d. ' \
                                      'You do not have enough funds.' %i
                            continue
                    elif decision == 'surrender' and not enable_surrender:
                        message = 'Invalid decision for HAND %d. ' \
                                  'Surrender is not allowed.' %i
                        continue
                    message = None
                    decisions[i] = decision
                    break
            process_decisions(player_hands, decisions)
        dealer_play(dealer_hand)
        results = get_results(dealer_hand, player_hands)
        bankroll += sum(r[1] for r in results)
        pile.recompose()
        table_screen(dealer_hand=dealer_hand,
                     player_hands=player_hands,
                     bankroll=bankroll,
                     message='Round is over. Here the results.',
                     results=results)
        enter_to_continue()
    return end_of_game()

def main():
    configs = load_configs()
    while True:
        match menu():
            case 'play' | 'p':
                play(**configs)
            case 'exit' | 'e':
                terminate()
            case _:
                continue
```
