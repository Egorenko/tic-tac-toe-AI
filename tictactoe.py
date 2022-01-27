import random


class Table(list):  # игровое поле изначально пустое
    def __init__(self, score: int = None,
                 initial_view: str = None,
                 parent=None,
                 children: list = None,
                 moves: str = None):
        super().__init__()
        if initial_view:  # строка вида [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
            self.table = [[initial_view[i] for i in range(3, 14, 5)],
                          [initial_view[i] for i in range(20, 31, 5)],
                          [initial_view[i] for i in range(37, 48, 5)]]
        else:
            self.table = [[' ' for _ in range(3)] for _ in range(3)]
        self.parent = parent
        self.children = []
        if children:
            self.children = children
        self.score = score
        self.is_over = False
        self.char = 'X'
        self.result = False
        self.moves = ''
        if moves:
            self.moves = moves

    def child(self, child):
        self.children.append(child)

    def plus_move(self, move: str):
        self.moves += move

    def minus_move(self):
        self.moves = self.moves[0:-2]

    def __str__(self) -> str:
        value = '---------\n'
        for i in range(3):
            value += '| ' + ' '.join(c for c in self.table[i]) + ' |\n'
        value += '---------'
        return value

    def __repr__(self) -> str:
        return str(self.table)

    def game_over(self):  # проверка на конец игры
        for i in range(3):  # победа по горизонтали
            if self.table[i][0] != ' ' and self.table[i] == [self.table[i][0] for _ in range(3)]:
                return self.table[i][0]
        for i in range(3):  # победа по вертикали
            if (self.table[0][i] != ' '
                    and self.table[0][i] == self.table[1][i]
                    and self.table[1][i] == self.table[2][i]):
                return self.table[0][i]
        if self.table[0][0] != ' ' and all(self.table[0][0] == self.table[i][i] for i in range(1, 3)):
            return self.table[0][0]  # победа по главной диагонали
        if self.table[0][2] != ' ' and all(self.table[0][2] == self.table[i][2 - i] for i in range(1, 3)):
            return self.table[0][2]  # победа по побочной диагонали
        not_empty = True
        for line in self.table:
            if ' ' in line:
                not_empty = False
        if not_empty:
            return 'Draw'  # ничья
        return False

    @staticmethod
    def tree(root=None, ai_char='X'):
        if root is None:
            parent = Table()
        else:
            parent = root
        if not parent.children:
            for i in range(3):
                for j in range(3):
                    if parent.table[i][j] == ' ':
                        if (''.join(c for c in map(''.join, parent.table)).count('X') <=
                                ''.join(c for c in map(''.join, parent.table)).count('O')):
                            parent.char = 'X'
                        else:
                            parent.char = 'O'
                        parent.table[i][j] = parent.char
                        parent.plus_move(f'{i}{j}')
                        parent.child(Table(initial_view=repr(parent), parent=parent, moves=parent.moves))
                        parent.minus_move()
                        parent.table[i][j] = ' '
            for child in parent.children:
                if not child.game_over():
                    child.tree(root=child, ai_char=ai_char)
                else:
                    child.is_over = True
                    child.result = child.game_over()
                    if child.result == 'Draw':
                        child.score = 0
                    else:
                        if child.result != ai_char:
                            child.score = -1
                        else:
                            child.score = 1
        return parent

    def children_score(self, ai_char='X', root=None, is_one=True):
        if is_one:
            tree = self.tree(root=root, ai_char=ai_char)
            is_one = False
        else:
            tree = root
        if tree.score is None:
            for child in tree.children:  # переберимаем потомков
                if child.score is not None:
                    continue
                else:
                    res = child.game_over()  # проверяем на конец игры
                    if res == 'Draw':
                        child.score = 0
                    elif res == ai_char:
                        child.score = 1
                    else:
                        if res is not False:
                            child.score = -1
                        else:
                            child.children_score(root=child, is_one=is_one, ai_char=ai_char)  # вызываем оценку
                            # потомков для этого потомка
        if all(map(lambda baby: baby.score is not None, tree.children)):
            if ai_char == tree.char:
                tree.score = max(child.score for child in tree.children)
            else:
                tree.score = min(child.score for child in tree.children)
        return self

    def minimax(self, ai_char='X', root=None):
        if root.score is None:
            tree = self.children_score(root=root, ai_char=ai_char)
        else:
            tree = root
        for child in tree.children:
            if child.score == tree.score:
                line = int(child.moves[-2])
                col = int(child.moves[-1])
                self.table[line][col] = ai_char
                print(self)
                return child

    def valid_coordinates(self, char):
        coordinates = input('Enter the coordinates: ')
        if not (coordinates.split()[0].isdigit() and coordinates.split()[1].isdigit()):
            print('You should enter numbers!')
        else:
            if not (1 <= int(coordinates.split()[0]) <= 3 and 1 <= int(coordinates.split()[1]) <= 3):
                print('Coordinates should be from 1 to 3!')
            else:
                if not (self.table[int(coordinates.split()[0]) - 1][int(coordinates.split()[1]) - 1] == ' '):
                    print('This cell is occupied! Choose another one!')
                else:
                    self.table[int(coordinates.split()[0]) - 1][int(coordinates.split()[1]) - 1] = char
                    print(self)
                    return self.table
        self.valid_coordinates(char)

    def randomize_coordinates(self, char, name):
        line = random.randint(0, 2)
        col = random.randint(0, 2)
        if self.table[line][col] == ' ':
            print(f'Making move level "{name}"')
            self.table[line][col] = char
            print(self)
            return self
        else:
            self.randomize_coordinates(char, name)

    def winner_or_scum_coordinates(self, char, name):
        un_char = 'X' if char == 'O' else 'O'
        for num, line in enumerate(self.table):  # по горизонтали
            if (line == [char, char, ' ']
                    or line == [char, ' ', char]
                    or line == [' ', char, char]):
                self.table[num][line.index(' ')] = char
                print(f'Making move level "{name}"')
                print(self)
                return True
            elif (line == [un_char, un_char, ' ']
                  or line == [un_char, ' ', un_char]
                  or line == [' ', un_char, un_char]):
                self.table[num][line.index(' ')] = char
                print(f'Making move level "{name}"')
                print(self)
                return True
        for i in range(3):  # по вертикали
            if ((self.table[0][i] == char or self.table[0][i] == un_char)
                    and self.table[1][i] == self.table[0][i]
                    and self.table[2][i] == ' '):
                self.table[2][i] = char
                print(f'Making move level "{name}"')
                print(self)
                return True
            elif ((self.table[1][i] == char or self.table[0][i] == un_char)
                  and self.table[2][i] == self.table[1][i]
                  and self.table[0][i] == ' '):
                self.table[0][i] = char
                print(f'Making move level "{name}"')
                print(self)
                return True
            elif ((self.table[0][i] == char or self.table[0][i] == un_char)
                  and self.table[2][i] == self.table[0][i]
                  and self.table[1][i] == ' '):
                self.table[1][i] = char
                print(f'Making move level "{name}"')
                print(self)
                return True
        if ((self.table[0][0] == char or self.table[0][0] == un_char)
                and self.table[0][0] == self.table[1][1]
                and self.table[2][2] == ' '):
            self.table[2][2] = char
            print(f'Making move level "{name}"')
            print(self)
            return True
        if ((self.table[0][2] == char or self.table[0][2] == un_char)
                and self.table[0][2] == self.table[1][1]
                and self.table[2][0] == ' '):
            self.table[2][0] = char
            print(f'Making move level "{name}"')
            print(self)
            return True


def print_result(result):
    if result == 'X':
        print('X wins!')
    elif result == 'O':
        print('O wins!')
    else:
        print('Draw')


# функция для вызова - ее еще нет
command = input('Input command: ')
while not command == 'exit':
    if command.split(' ')[0] == 'start':
        if len(command.split(' ')) != 3:
            print('Bad parameters!')
            command = input('Input command: ')
        elif not (command.split(' ')[1] == 'user'
                  or command.split(' ')[1] == 'easy'
                  or command.split(' ')[1] == 'medium'
                  or command.split(' ')[1] == 'hard'):
            print('Bad parameters!')
            command = input('Input command: ')
        elif not (command.split(' ')[2] == 'user'
                  or command.split(' ')[2] == 'easy'
                  or command.split(' ')[2] == 'medium'
                  or command.split(' ')[2] == 'hard'):
            print('Bad parameters!')
            command = input('Input command: ')
        else:
            table_game = Table()
            print(table_game)
            if command.split()[1] == 'user':
                if command.split()[2] == 'easy':
                    result = False
                    while result is False:
                        table_game.valid_coordinates('X')
                        if not table_game.game_over():
                            table_game.randomize_coordinates('O', 'easy')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'user':
                    result = False
                    while result is False:
                        if not table_game.game_over():
                            table_game.valid_coordinates('X')
                            if not table_game.game_over():
                                table_game.valid_coordinates('O')
                            else:
                                result = table_game.game_over()
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'medium':
                    result = False
                    while result is False:
                        table_game.valid_coordinates('X')
                        if not table_game.game_over():
                            if not table_game.winner_or_scum_coordinates('O', 'medium'):
                                table_game.randomize_coordinates('O', 'medium')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                else:
                    result = False
                    game_tree = table_game
                    while result is False:
                        table_game.valid_coordinates('X')
                        for chi in game_tree.children:
                            if chi.table == table_game.table:
                                game_tree = chi
                                break
                        if not table_game.game_over():
                            game_tree = table_game.minimax(ai_char='O', root=game_tree)
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
            elif command.split()[1] == 'easy':
                if command.split()[2] == 'easy':
                    result = False
                    while result is False:
                        table_game.randomize_coordinates('X', 'easy')
                        if not table_game.game_over():
                            table_game.randomize_coordinates('O', 'easy')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'user':
                    result = False
                    while result is False:
                        table_game.randomize_coordinates('X', 'easy')
                        if not table_game.game_over():
                            table_game.valid_coordinates('O')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'medium':
                    result = False
                    while result is False:
                        table_game.randomize_coordinates('X', 'easy')
                        if not table_game.game_over():
                            if not table_game.winner_or_scum_coordinates('O', 'medium'):
                                table_game.randomize_coordinates('O', 'medium')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                else:
                    result = False
                    while result is False:
                        table_game.randomize_coordinates('X', 'easy')
                        if not table_game.game_over():
                            table_game.minimax('O', root=table_game)
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
            elif command.split()[1] == 'medium':
                if command.split()[2] == 'easy':
                    result = False
                    while result is False:
                        if not table_game.winner_or_scum_coordinates('X', 'medium'):
                            table_game.randomize_coordinates('X', 'medium')
                        if not table_game.game_over():
                            table_game.randomize_coordinates('O', 'easy')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'medium':
                    result = False
                    while result is False:
                        if not table_game.winner_or_scum_coordinates('X', 'medium'):
                            table_game.randomize_coordinates('X', 'medium')
                        if not table_game.game_over():
                            if not table_game.winner_or_scum_coordinates('O', 'medium'):
                                table_game.randomize_coordinates('O', 'medium')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'user':
                    result = False
                    while result is False:
                        if not table_game.winner_or_scum_coordinates('X', 'medium'):
                            table_game.randomize_coordinates('X', 'medium')
                        if not table_game.game_over():
                            table_game.valid_coordinates('O')
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                else:
                    result = False
                    game_tree = table_game
                    while result is False:
                        if not table_game.winner_or_scum_coordinates('X', 'medium'):
                            table_game.randomize_coordinates('X', 'medium')
                        for chi in game_tree.children:
                            if chi.table == table_game.table:
                                game_tree = chi
                                break
                        if not table_game.game_over():
                            game_tree = table_game.minimax('O', root=game_tree)
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
            else:
                if command.split()[2] == 'easy':
                    result = False
                    game_tree = table_game
                    while result is False:
                        game_tree = table_game.minimax('X', root=game_tree)
                        if not table_game.game_over():
                            table_game.randomize_coordinates('O', 'easy')
                            for chi in game_tree.children:
                                if chi.table == table_game.table:
                                    game_tree = chi
                                    break
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'medium':
                    result = False
                    game_tree = table_game
                    while result is False:
                        game_tree = table_game.minimax('X', root=game_tree)
                        if not table_game.game_over():
                            if not table_game.winner_or_scum_coordinates('O', 'medium'):
                                table_game.randomize_coordinates('O', 'medium')
                            for chi in game_tree.children:
                                if chi.table == table_game.table:
                                    game_tree = chi
                                    break
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                elif command.split()[2] == 'user':
                    result = False
                    game_tree = table_game
                    while result is False:
                        game_tree = table_game.minimax('X', root=game_tree)
                        if not table_game.game_over():
                            table_game.valid_coordinates('O')
                            for chi in game_tree.children:
                                if chi.table == table_game.table:
                                    game_tree = chi
                                    break
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
                else:
                    result = False
                    game_tree = table_game.randomize_coordinates('X', 'hard')
                    while result is False:
                        game_tree = table_game.minimax('O', root=game_tree)
                        if not table_game.game_over():
                            table_game.minimax('X', root=game_tree)
                            for chi in game_tree.children:
                                if chi.table == table_game.table:
                                    game_tree = chi
                                    break
                        else:
                            result = table_game.game_over()
                    else:
                        print_result(result)
                        command = input('Input command: ')
