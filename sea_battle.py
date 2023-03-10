from random import randint, choice


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы стреляете мимо игрового поля"


class RepeatedShotException(BoardException):
    def __str__(self):
        return "Нет смысла сюда стрелять"


class NoFreeDotException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, anchor, direction='vert'):
        self.length = length
        self.anchor = anchor
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            x = self.anchor.x
            y = self.anchor.y

            if self.direction == 'vert':
                x += i

            elif self.direction == 'hor':
                y += i

            ship_dots.append(Dot(x, y))

        return ship_dots


class Board:
    def __init__(self, size=6):
        self.size = size
        self.field = [[" "] * self.size for _ in range(self.size)]
        self.ships = []
        self.hid = False
        self.count_ships = 0
        self.busy_dots = []

    def in_range(self, dot: Dot):
        return (0 <= dot.x < self.size) and (0 <= dot.y < self.size)

    def add_ship(self, ship):
        for dot in ship.dots:
            if not self.in_range(dot) or dot in self.busy_dots:
                raise NoFreeDotException

        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy_dots.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, show=False):
        around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dot in ship.dots:
            for x, y in around:
                buf = Dot(dot.x + x, dot.y + y)
                if self.in_range(buf) and buf not in self.busy_dots:
                    if show:
                        self.field[buf.x][buf.y] = "-"
                    self.busy_dots.append(buf)

    def __str__(self):
        res = ""
        res += "   1  2  3  4  5  6"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} [" + "][".join(row) + "]"

        if self.hid:
            res = res.replace("■", " ")
        return res

    def shot(self, dot):
        if not self.in_range(dot):
            raise BoardOutException

        if dot in self.busy_dots:
            raise RepeatedShotException

        self.busy_dots.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count_ships += 1
                    self.contour(ship, show=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль подбит")
                    return True

        self.field[dot.x][dot.y] = "-"
        print("Промах...")
        return False


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        while True:
            dot = Dot(randint(0, 5), randint(0, 5))
            if dot in self.enemy_board.busy_dots:
                continue
            else:
                print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
                return dot


class User(Player):
    def ask(self):
        while True:
            print("-" * 20)
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        user_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hid = True

        self.comp = AI(comp_board, user_board)
        self.user = User(user_board, comp_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        count = 0
        for length in lens:
            while True:
                count += 1
                if count > 2000:
                    return None
                ship = Ship(length, Dot(randint(0, self.size), randint(0, self.size)), choice(['vert', 'hor']))
                try:
                    board.add_ship(ship)
                    break
                except NoFreeDotException:
                    pass
        board.busy_dots = []
        return board

    def greet(self):
        print("-------------------")
        print("------МОРСКОЙ------")
        print("--------БОЙ--------")
        print("-------------------")
        print(" Формат ввода: 1 2 ")
        print(" 1 - номер строки  ")
        print(" 2 - номер столбца ")

    def show_boards(self):
        print("-" * 20)
        print("Доска пользователя:")
        print(self.user.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.comp.board)

    def loop(self):
        num = 0
        while True:
            if num % 2 == 0:
                self.show_boards()
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.comp.move()
            if repeat:
                num -= 1

            if self.comp.board.count_ships == 7:
                self.show_boards()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.board.count_ships == 7:
                self.show_boards()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
