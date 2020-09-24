import requests, sys

base_url = 'https://api.trello.com/1/{}'

"""
    Enter Key and ID of your Trello account.
    Then create or choose the board on the Trello and copy the board ID.  
"""

board_id = 'Write the board id here'
auth_params = {
    'key': 'Write your Trello key here',
    'token': 'Write your Trello id here'
}

"""
    commands in console:
      PATH > python TrelloClient.py   // Show all the lists and all the tasks in those lists
      PATH > python TrelloClient.py create_list "name-of-list"    // Create new list
      PATH > python TrelloClient.py create_task "name-of-task" "name-of-list"    // Create a new task in a list that you have choose
      PATH > python TrelloClient.py move "name-of-task" "name-of-list"     // Move your task in a list that you have choose 
"""


def read():
    """
    Get all columns and column data from the board 'board_id'.
    """

    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params = auth_params).json()
    for column in column_data:
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(f'"{column["name"]}" list. Number of tasks - {len(task_data)}')
        tasks_counter = 0
        if not task_data:
            print(f'\tTasks is absent')
            continue
        for task in task_data:
            tasks_counter += 1
            print(f'\t{tasks_counter}. {task["name"]}')

def create_list(name):
    """
    Creating a new column in a board with a name = name.
    """
    name = name_handler(name)

    board = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
    our_board_id = board['id']
    requests.post(base_url.format('lists'), data={'name': name, 'idBoard': our_board_id, **auth_params})

def create_task(name, column_name):
    """
    Creating a new task with a name = name in to a column = column_name.
    """
    name = name_handler(name, component='task')

    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    column_list = []

    for column in column_data:
        if column['name'] == column_name:
            column_list.append({
                'name': column['name'],
                'id': column['id']
            })

    if len(column_list) == 1:
        requests.post(base_url.format('cards'), data={'name': name, 'idList': column_list[0]['id'], **auth_params})
    else:
        counter = 0
        print('All lists with the same name:')
        for column in column_list:
            counter += 1
            print(f'{counter} - List: "{column["name"]}" with ID: "{column["id"]}"')
        answer_number = int(input('Choose number of list, where do you want add the new task:\n'))
        while answer_number not in range(1, len(column_list) + 1):
            answer_number = int(input('The list with this number is not exist, choose a correct number:\n'))
        requests.post(base_url.format('cards'), data={'name': name, 'idList': column_list[answer_number - 1]['id'], **auth_params})

def name_handler(name, component = 'list'):
    """
     Check: is a task or list with same name is in a board? If yeas - offer choose do you want to create a task or list with this
     name, or to make new name.
     param: default = 'list', or can be 'task'. Choose what a name you want to find.
    """
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    lists = []
    tasks = []

    for column in column_data:
        if column['name'] == name:
            lists.append({
                'name': column['name'],
                'id': column['id']
            })

        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()

        for task in task_data:
            if task['name'] == name:
                tasks.append({
                    'name': task['name'],
                    'id': task['id'],
                    'list': column['name']
                })

    if (component == 'list') and len(lists) >= 1:
        print('Lists with the same name already is:')
        counter = 0
        for list in lists:
            counter += 1
            print(f'\t{counter} - Name: "{list["name"]}". ID: "{list["id"]}"')
        answer_number = int(input('Enter number:\n1 - If you want create list with the same name.\n2 - If you want enter enother name.\n'))
        while answer_number not in range(1, 3):
            answer_number = int(input('Incorrect number:\nTry again.\n'))
        if answer_number == 1:
            return name
        elif answer_number == 2:
            name = input('Enter new name:\n')
            return name
    elif (component == 'task') and len(tasks) >= 1:
        print('Tasks with the same name already is:')
        counter = 0
        for task in tasks:
            counter += 1
            print(f'\t{counter} - Name: "{task["name"]}". List: "{task["list"]}". ID: "{task["id"]}".')
        answer_number = int(input('Enter number:\n1 - If you want create task with the same name.\n2 - If you want enter enother name.\n'))
        while answer_number not in range(1, 3):
            answer_number = int(input('Incorrect number:\nTry again.\n'))
        if answer_number == 1:
            return name
        elif answer_number == 2:
            name = input('Enter new name:\n')
            return name

    return name

def move(name, column_name):
    """
    Move a task with a name = name in to a column = column_name.
    """
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    tasks_list = []

    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                tasks_list.append({
                    'id': task['id'],
                    'name': task['name'],
                    'list_name': column['name']
                })

    if len(tasks_list) > 1:
        task_id = choose_task(tasks_list)
    else:
        task_id = tasks_list[0]['id']

    column_list = []

    for column in column_data:
        if column['name'] == column_name:
            column_list.append({
                'name': column['name'],
                'id': column['id']
            })

    if len(column_list) > 1:
        print('The lists with the same name:')
        counter = 0
        for column in column_list:
            counter += 1
            print(f'{counter} - Name: "{column["name"]}". ID: "{column["id"]}".')
        answer_number = int(input('Choose number of list, where do you want move the task:\n'))
        while answer_number not in range(1, len(column_list) + 1):
            answer_number = int(input('Number of list is incorrect. Try again:\n'))
        requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_list[answer_number - 1]['id'], **auth_params})
    elif len(column_list) == 1:
        requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column_list[0]['id'], **auth_params})
    else:
        print('List with those name is not exist')

def choose_task(dict):
    """
    Show in console all the tasks names from the dictionary and offers to choose one of it . Then return id of this task.
    """
    counter = 0
    for task in dict:
        counter += 1
        print(f'{counter} - Task "{task["name"]}"\n    from the "{task["list_name"]}" list\n    with "id" - {task["id"]}')
    number_of_task = int(input('Choose the number of tusk, that you want to move:\n '))
    return dict[number_of_task - 1]['id']

if __name__ == '__main__':
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create_list':
        create_list(sys.argv[2])
    elif sys.argv[1] == 'create_task':
        create_task(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])

