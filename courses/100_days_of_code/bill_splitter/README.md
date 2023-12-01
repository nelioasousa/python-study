# Description
Split a bill between a group of people, telling each one how much they owe to the others.

Programming paradigm used: Functional Programming.

# Planning

## Input:
- Bill value (float)
- People to split the bill among (list[str])
- How much each person paid (list[float])
- Split proportions (list[float])

## Output:
- NxN matrix, where N is the number of people to split the bill among

## Pseudocode
```
def main():
    data <- dict('bill': None, 'names': [], 'paid': [], 'split': [])
    att_screen(data)
    while data['bill'] is None:
        response = ask_bill_value()
        match response:
            case command.Restart:
                return main()
            case command.Terminate:
                return terminate()
            case float():
                data['bill'] = response
                att_screen(data)
            case _:
                att_screen(data, warning=response)
    while True:
        response = ask_names()
        match response:
            case command.Restart:
                return main()
            case command.Terminate:
                return terminate()
            case command.Continue:
                if len(data['names']) > 1:
                    att_screen(data)
                    break
                else:
                    att_screen(data, 
                               warning='At least 2 names must be supplied')
            case list():
                data['names'].extend(response)
            case _:
                att_screen(data, warning=response)
    while len(data['paid']) < len(data['names']):
        response = ask_paid_values()
        match response:
            case command.Restart:
                return main()
            case command.Terminate:
                return terminate()
            case command.Continue:
                att_screen(data, 
                           warning='Supply paid values for the entire group')
            case list():
                if len(response) + len(data['paid']) > len(data['names']):
                    att_screen(data,
                               warning='Paid values exceed group size')
                else:
                    data['paid'].extend(response)
                    att_screen(data)
            case _:
                att_screen(data, warning=response)
    while len(data['split']) < len(data['names']):
        response = ask_split_proportions()
        match response:
            case command.Restart:
                return main()
            case command.Terminate:
                return terminate()
            case command.Continue:
                att_screen(data, 
                           warning='Supply proportions for the entire group')
            case list():
                if len(response) + len(data['split']) > len(data['names']):
                    att_screen(data,
                               warning='Split proportions exceed group size')
                else:
                    data['split'].extend(response)
                    att_screen(data)
            case _:
                att_screen(data, warning=response)
    split_matrix = split_bill(data)
    show_result(data['names'], split_matrix)
    return restart_or_terminate()()
```
