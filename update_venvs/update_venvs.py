import os
import sys

VENV_NAME = '.venv'
PY_EXECUTABLE = 'python'


def prompt_yes_no(default_choice: str, prompt_text: str = 'Please make your choice:', always_yes: bool = False) -> bool:
    """Prompt for user yes/no input.

    :param default_choice: should 'yes' or 'no', defaults to None
    :type default_choice: str, optional
    :param prompt_text: Text of the prompt (defaults to: Please make your choice)
    :type prompt_text: str, optional
    :param always_yes: Don't ask just 'YES', defaults to False
    :type always_yes: bool, optional
    :raises ValueError: default_Yes and default_No can't all be true at the same time
    :return: True if Yes, False if No
    :rtype: bool

    see https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    """
    valid_choices = {'yes': True, 'y': True, 'no': False, 'n': False}

    if default_choice is None:
        yesno_prompt = '[y/n]'
    elif default_choice == 'yes':
        yesno_prompt = '[Y/n]'
    elif default_choice == 'no':
        yesno_prompt = '[y/N]'
    else:
        raise ValueError("Func prompt_yes_no() error: default_choice should be 'yes' or 'no'")

    # if command line option --yes
    if always_yes:
        return valid_choices['yes']                 # ! ret

    while True:
        try:
            choice = input(prompt_text + ' ' + yesno_prompt)
        except EOFError:
            sys.exit()

        # if Enter is pressed, return default choice
        if default_choice is not None and choice == '':
            return valid_choices[default_choice]        # ! ret
        elif choice.lower() in valid_choices:
            return valid_choices[choice]                # ! ret
        else:
            print('Valid choices are:' + ' yes, no, y, n')


def search_and_update_venv(search_in_path: str):
    """Search venv folder and update (recursively)

    :param search_in_path: path to search a venv in
    :type search_in_path: str
    """
    if not search_in_path.endswith(VENV_NAME):
        dir_list = [f for f in os.listdir(search_in_path)]
        for f in dir_list:
            f_path = os.path.join(search_in_path, f)
            if (os.path.isdir(f_path) and f != '..'):
                search_and_update_venv(f_path)
    else:
        print(f'\n* venv found: {search_in_path}')
        if prompt_yes_no('no', 'Should I upgrade it?'):
            os.system(f'{PY_EXECUTABLE} -m venv --upgrade {search_in_path}')
            os.system(f'{PY_EXECUTABLE} -m venv --upgrade-deps {search_in_path}')


root_list = [f for f in os.listdir('.')]

for f in root_list:
    f_path = os.path.join('.', f)
    if (os.path.isdir(f_path) and f != '..'):
        search_and_update_venv(f_path)
