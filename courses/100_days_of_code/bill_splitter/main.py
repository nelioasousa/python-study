"""Split bill tool."""

from enum import Enum
from typing import Any, Callable
from collections import defaultdict
from random import randrange



class Command(Enum):
    HELP = 0
    CONTINUE = 1
    RESTART = 2
    TERMINATE = 3



def asker(handler: Callable[[str], Any]) -> Callable[[str], Command | Any]:
    def ask(request_message: str) -> Command | Any:
        response = input(request_message)
        command = get_command(response)
        return handler(response) if command is None else command
    return ask

def get_command(response: str) -> Command | None:
    match response.strip().lower():
        case 'help' | '?':
            return Command.HELP
        case '' | 'continue':
            return Command.CONTINUE
        case 'r' | 'restart':
            return Command.RESTART
        case 't' | 'terminate':
            return Command.TERMINATE
        case _:
            return None

@asker
def ask_bill_value(response: str) -> float | str:
    try:
        bill_value = round(float(response), 2)
    except ValueError:
        return 'Not understood: "%s"' %response
    if bill_value <= 0:
        return 'Bill must be greater than $0.0'
    return bill_value

@asker
def ask_values(response: str) -> list[float] | str:
    str_values = response.split(',')
    values, fails = [], []
    for str_value in str_values:
        try:
            values.append(float(str_value))
        except ValueError:
            fails.append(str_value)
    if fails:
        fail_str = ', '.join('"%s"' %f for f in fails)
        return 'Not understood: %s' %fail_str
    return values

@asker
def ask_names(response: str) -> list[str] | str:
    names = [process_name(name) for name in response.split(',')]
    fails = []
    for name in names:
        try:
            _ = float(name)  # Don't allow numbers as names
            fails.append(name)
        except ValueError:
            continue
    if fails:
        return 'Invalid name(s): %s' %(', '.join('"%s"' %f for f in fails))
    return names

def process_name(name: str):
    from re import sub
    # Replace multiple whitespaces with a single space character
    # Also capitalize the name portions
    name = ' '.join([p.capitalize() for p in name.split()])
    # Fix hyphenated names
    # "Soul - Ju" becomes "Soul-Ju"
    name = sub(' ?- ?', '-', name)
    # Capitalize the first character after "-"
    # "Soul-ju Hiuy" becomes "Soul-Ju Hiuy"
    name = '-'.join([upper_first_char(i) for i in name.split('-')])
    return name

def upper_first_char(string: str):
    return ''.join((string[0].upper(), string[1:]))



def split_bill(data: dict) -> dict[str, list]:
    group = data['names']
    bill_value = data['bill']
    payments = data['paid']
    targets = data['target']
    paid_value = sum(payments)
    balances = [(paid_value - targets[i]) \
                for i, paid_value in enumerate(payments)]
    bill_debt = bill_value - paid_value
    creditors = [('DEBT', bill_debt)] if bill_debt > 0 else []
    creditors += [(group[i], balance) \
                  for i, balance in enumerate(balances) if balance > 0]
    debtors = [('CHANGE', abs(bill_debt))] if bill_debt < 0 else []
    debtors += [(group[i], abs(balance)) \
                for i, balance in enumerate(balances) if balance < 0]
    key_func = lambda x: x[1]
    creditors.sort(key=key_func)
    debtors.sort(key=key_func)
    debt_list = defaultdict(list)
    for debtor, debt in debtors:
        while True:
            try:
                creditor, credit = creditors[0]
            except IndexError:
                break
            if debt > credit:
                debt -= credit
                debt_list[debtor].append((creditor, credit))
                creditors = creditors[1:]
            else:
                credit -= debt
                debt_list[debtor].append((creditor, debt))
                if credit >= 0.01:
                    creditors[0] = (creditor, credit)
                else:
                    creditors = creditors[1:]
                break
    assert not creditors, 'All creditors must be fully paid.'
    return debt_list



def clear_terminal():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def att_screen(data: dict, info: str = ''):
    clear_terminal()
    print('BILL SPLITTER TOOL')
    print('by github.com/nelioasousa', end='\n\n')
    bill_value = data['bill']
    names = data['names']
    payments = data['paid']
    proportions = data['weights']
    paid_value = sum(payments)
    if bill_value is not None:
        # bill_pad = len(str(bill_value))  # For %.2f money formatting
        print('Bill value     : $%.2f' %bill_value)
        print('Already paid   : $%.2f' %paid_value)
        print('Remaining debt : $%.2f' %(bill_value - paid_value), end='\n\n')
    if names:
        payments = ['$%.2f' %p for p in payments]
        payments.extend([''] * (len(names) - len(payments)))
        payments = ['Paid'] + payments
        if 'target' in data:
            targets = data['target']
            proportions = ['~%5.1f%% ($%.2f)' \
                           %(100 * p, targets[i]) \
                           for i, p in enumerate(proportions)]
        else:
            proportions = ['%s' %w for w in proportions]
            proportions.extend([''] * (len(names) - len(proportions)))
        proportions = ['Proportion'] + proportions
        names = ['Name'] + names
        name_pad = max(len(n) for n in names)
        paid_pad = max(len(p) for p in payments)
        prop_pad = max(len(p) for p in proportions)
        for name, paid, prop in zip(names, payments, proportions):
            print(f'| %-{name_pad}s | %-{paid_pad}s | %-{prop_pad}s |' \
                  %(name, paid, prop))
        print('')
    if info:
        print('[MESSAGE]', info, end='\n\n')

def show_split_result(split_result: dict[str, list]):
    if 'CHANGE' in split_result:
        for name, value in split_result['CHANGE']:
            print('- %s gets a change of $%.2f' %(name, value))
        del split_result['CHANGE']
    for debtor, debts in split_result.items():
        for creditor, value in debts:
            if creditor == 'DEBT':
                print('- %s must pay $%.2f to close the bill' \
                        %(debtor, value))
            else:
                print('- %s owns $%.2f to %s' %(debtor, value, creditor))
    print('')



def restart_or_terminate():
    response = input('[R]estart? ').strip().lower()
    if response in {'y', 'yes', 'r', 'restart'}:
        return main
    else:
        return terminate

def terminate():
    clear_terminal()
    print('Tranks for using the tool! Goodbye!')
    print('More in github.com/nelioasousa/python-study')



def main():
    data = {'bill': None, 'names': [], 'paid': [], 'weights': []}
    att_screen(data)
    while True:
        response = ask_bill_value('Bill value: $')
        match response:
            case Command.HELP:
                help_message = 'Enter a number using dot ' \
                               'as the decimal separtor. ' \
                               'E.g.: 784.15'
                att_screen(data, info=help_message)
            case Command.CONTINUE:
                att_screen(data, info='Supply the bill value to continue')
            case Command.RESTART:
                return main()
            case Command.TERMINATE:
                return terminate()
            case float():
                data['bill'] = response
                att_screen(data)
                break
            case _:
                att_screen(data, info=response)
    while True:
        response = ask_names('Debtor(s): ')
        match response:
            case Command.HELP:
                help_message = 'Inform the name of the debtors. ' \
                               'Enter "continue" when finished. ' \
                               'E.g.: Cornélio, Julio, Wang-Hu'
                att_screen(data, info=help_message)
            case Command.CONTINUE:
                if len(data['names']) > 1:
                    att_screen(data)
                    break
                else:
                    att_screen(data, 
                               info='At least 2 debtors must be supplied')
            case Command.RESTART:
                return main()
            case Command.TERMINATE:
                return terminate()
            case list():
                data['names'].extend(response)
                att_screen(data)
            case _:
                att_screen(data, info=response)
    while len(data['paid']) < len(data['names']):
        response = ask_values('Paid values: $')
        match response:
            case Command.HELP:
                help_message = 'Enter the value paid by each debtor. ' \
                               'E.g.: 42.75, 102.10'
                att_screen(data, info=help_message)
            case Command.RESTART:
                return main()
            case Command.TERMINATE:
                return terminate()
            case Command.CONTINUE:
                att_screen(data, 
                           info='Enter paid values for all debtors')
            case list():
                if len(response) + len(data['paid']) > len(data['names']):
                    att_screen(data, 
                               info=('Paid values exceeded'
                                     ' the number of debtors'))
                else:
                    data['paid'].extend([round(p, 2) for p in response])
                    if sum(data['paid']) >= data['bill']:
                        extend_size = len(data['names']) - len(data['paid'])
                        data['paid'] += [0.0] * extend_size
                        att_screen(data)
                        break
                    att_screen(data)
            case _:
                att_screen(data, info=response)
    while len(data['weights']) < len(data['names']):
        response = ask_values('Split weight(s): ')
        match response:
            case Command.HELP:
                help_message = 'Enter values to base the bill split. ' \
                               'Values are treated as weights.' \
                               '\nE.g.: 0.25, 0.5, 0.25 (one pays double)' \
                               '\nE.g.: 1, 1, 1         (split equally)' \
                               '\nE.g.: 0.5, 0.5, 0.5   (also equally)'
                att_screen(data, info=help_message)
            case Command.RESTART:
                return main()
            case Command.TERMINATE:
                return terminate()
            case Command.CONTINUE:
                att_screen(data, 
                           info='Supply split weights for all debtors')
            case list():
                if len(response) + len(data['weights']) > len(data['names']):
                    att_screen(data,
                               info=('Split weights exceeded'
                                     ' the number of debtors'))
                else:
                    data['weights'].extend(response)
                    att_screen(data)
            case _:
                att_screen(data, info=response)
    weights_sum = sum(data['weights'])
    data['weights'] = [w / weights_sum for w in data['weights']]
    data['target'] = [round(data['bill'] * p, 2) \
                      for p in data['weights']]
    # To evade the inaccuracy bring by round()
    # One unlucky one will take on the difference
    unlucky = randrange(0, len(data['names']))
    data['target'][unlucky] = 0.0
    data['target'][unlucky] = data['bill'] - sum(data['target'])
    att_screen(data)
    split_result = split_bill(data)
    show_split_result(split_result)
    return restart_or_terminate()()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        terminate()
