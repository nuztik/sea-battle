from random import randint
import time

# записываем исключения для дальнейшего отлова их
class BoardException(Exception): #родительский класс
    pass
class BoardOutException(BoardException):  # выстрел за доску
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"
class BoardUsedException(BoardException):  # выстрел в туже точку
    def __str__(self):
        return "Вы уже стреляли в эту клетку"
class BoardWrongShipException(BoardException):  #для размещения кораблей на доске
    pass

#создаем класс точка для проверки и вывода в консоль
class Dot:
    def __init__(self, x, y): #создаем параметры точек
        self.x = x
        self.y = y

    def __eq__(self, other):  #сравнение двух объектов
        return self.x == other.x and self.y == other.y

    def __repr__(self):    #вывод точки в консоль, при создании
        return f"Dot({self.x}, {self.y})"

#создаем класс корабль
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):    #создаем свойство в пространстве (метод размещения) корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):   #создаем метод, который показывает попали или нет
        return shot in self.dots

#создаем класс игрового поля
class Board:
    def __init__(self, hid=False, size=6):  #свойства поля
        self.size = size  #размер
        self.hid = hid  #видимость
        self.count = 0  #кол-во пораженных кораблей
        self.field = [["O"] * size for _ in range(size)] #сетка хранение информации о клетках
        self.busy = []  #занятые точки
        self.ships = []  #список кораблей доски
    def __str__(self): #выводим наше поле
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res  #выводится уже, если не требуется этого скрыть, истенно
    def out(self, d): #находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
    def contour(self, ship, verb=False): #создание метода, который будет обводить корабль
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)
    def add_ship(self, ship): #создаем метод размещения корабля
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)
    def shot(self, d): # создаем метод, который стреляет
        if self.out(d): #проверяем исключения
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d) #добавляем в список занятых точек
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    def begin(self): #обнуляем для того, чтобы хранить в этой переменной информацию, куда стрелял игрок
        self.busy = []
    def defect(self): # подсчет кораблей
        return self.count == len(self.ships)

#создаем класс Игрока
class Player: #родительский класс
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    def ask(self): #расшифровка, что будет в этом методе - пропишется у потомков
        raise NotImplementedError()
    def move(self): #создается бесконечный цикл с задачами
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

#создаем класс-потомок игрока компьютера
class AI(Player):
    def ask(self): #произвольный выстрел в диапозоне
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

#создаем класс-потомок игрока пользователя
class User(Player):
    def ask(self): # запрос координат от пользователя для выстрела и проверки уместности
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

#главный класс
class Game:
    def __init__(self, size=6): # конструктор игры, задаем размер поля, поля игрока и компьютера
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
    def try_board(self): #создание доски, расстановка кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    def random_board(self): #цикл дает возможность на 100% создать доску с кораблями
        board = None
        while board is None:
            board = self.try_board()
        return board
    def loop(self): #цикл самой игры
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
                time.sleep(0.5) # замедляет, видимость игры с пользователем
            if repeat:  #если попали в корабль
                num -= 1
            if self.ai.board.defect():
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.defect():
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
    def start(self): #генерация игры
        self.greet()
        self.loop()

g = Game()
g.start()