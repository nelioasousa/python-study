Self-documented script. Check [main.py](./main.py) for more details.

# Description
Split a bill between a group of people, telling each one how much they owe to the others.

Programming paradigm used: Functional Programming.

# Input
- Bill value (`float`)
- People to split the bill among (`list[str]`)
- How much each person paid (`list[float]`)
- Split proportions (`list[float]`)

# Output
A dictionary of debts (`dict[str, list[tuple[str, float]]]`), where keys are the names of the debtors (`str`) and values are the corresponding debts (`list[tuple[str, float]]`), each debt (`tuple[str, float]`) consists of the creditor name (`str`) and the value the debtor owes to the creditor (`float`).

Initially, the output was thought to be a matrix, where rows represent debtors and columns represent creditors.

# Planning pseudocode
The "pseudocode" below does not represent the exact structure of the script. It was used as the basis of the source code but was changed as the project progressed to address difficulties and unforeseen problems, like the change in the output of the split described above.

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

# Notes
1. The use of [Structural Pattern Matching](https://peps.python.org/pep-0636/) (SPM) allows for cleaner code but handcuffs the Python version compatible with the script, as Pattern Matching is only available from version 3.10 onward. The design decision between SPM and if/elif/else isn't clear yet, but [PEPs 634 and 635](/PEPs/README.md) may clarify it;
2. I especially liked the implementation of the `asker()` decorator;
3. I need to take more care with the limitations of floating-point numbers;
4. The `main()` function is a bit large. A little more modularity might be a better fit.
