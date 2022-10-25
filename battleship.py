class Point:
    ROW_LETTERS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')

    MAX_ROW = 10
    MAX_COL = 10

    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y

    def __str__(self) -> str:
        return "({}, {})".format(self.__x, self.__y)

    def board_row(self) -> str:
        return Point.ROW_LETTERS[self.__x]

    def board_col(self) -> int:
        return self.__y + 1

    def x(self) -> int:
        return self.__x

    def y(self) -> int:
        return self.__y

    def as_board_coordinate(self) -> (str, int):
        return [self.board_row(), self.board_col()]

    @staticmethod
    def from_board_coordinate(in_coord: (str, int)):
        if in_coord[1] < 0 or in_coord[1] > Point.MAX_COL:
            return Point(-1, -1)
        elif in_coord[0] not in Point.ROW_LETTERS:
            return Point(-1, -1)
        else:
            return Point(in_coord[1] - 1, Point.ROW_LETTERS.index(in_coord[0]))

class Ship:
    def __init__(self, obj: str, length: int, start: Point, direction: str):
        self.__obj = obj
        self.__length = length
        self.__start = start
        self.__dir = direction

    @staticmethod
    def make_by_name(name: str, start: Point, direction: str):
        if name == 'Carrier':
            return Ship('A', 5, start, direction)
        elif name == 'Battleship':
            return Ship('B', 4, start, direction)
        elif name == 'Cruiser':
            return Ship('C', 3, start, direction)
        elif name == 'Submarine':
            return Ship('S', 3, start, direction)
        elif name == "Destroyer":
            return Ship('D', 2, start, direction)

    def get_coords(self) ->  Point:
        return self.__start

    def get_marker(self) -> str:
        return self.__obj

    def get_dir(self) -> str:
        return self.__dir

    def get_length(self) -> int:
        return self.__length

class Space:
    def __init__(self):
        self.__obj = '-'

    def place(self, obj: str):
        self.__obj = obj

    def get_marker(self) -> str:
        return self.__obj

    def is_occupied(self) -> bool:
        return self.__obj not in ['-', 'X', 'o']

    def attacked_by_missile(self) -> bool:
        return self.__obj not in ['X', 'o']

    def __str__(self) -> str:
        return self.get_marker()


def parse_direction(direction: str):
     match direction[0]:
        case 'n':
            return Point(0, -1)
        case 'w':
            return Point(-1, 0)
        case 'e':
            return Point(1, 0)
        case 's':
            return Point(0, 1)

class Board:
    def __init__(self):
        self.__board = []
        
        for i in range(10):
            row = []
            for j in range(10):
                row.append(Space())
            self.__board.append(row)

    def place_ship(self, ship: Ship):
        start = ship.get_coords()
        direction = ship.get_dir()
        length = ship.get_length()

        spaces = self.get_spaces(start, direction, length)
        for space in spaces:
            space.place(ship.get_marker())

    def place_object(self, point: Point, obj: str):
        self.__board[point.y()][point.x()].place(obj)

    def detonate_missile(self, point: Point) -> bool:
        space = self.__board[point.y()][point.x()]
        hit = space.is_occupied()
        if hit:
            space.place('X')
        else:
            space.place('o')

        return hit

    @staticmethod
    def is_valid_position(position: Point):
        return 0 <= position.x() < 10 and 0 <= position.y() < 10

    def get_spaces_in_direction(self, start: Point, direction: Point, count):
        spaces = []
        for i in range(0, count):
            p = Point(start.x() + direction.x() * i, start.y() + direction.y() * i)
            if not Board.is_valid_position(p):
                break
            spaces.append(self.__board[p.y()][p.x()])

        return spaces

    def get_spaces(self, start: Point, direction: str, length: int):
        direction = parse_direction(direction)
        return self.get_spaces_in_direction(start, direction, length)

    def spaces_are_free(self, start: Point, direction: str, length: int) -> bool:
        out_spaces = self.get_spaces(start, direction, length)
        if len(out_spaces) < length: return False
        
        for space in out_spaces: 
            if space.is_occupied():
                return False

        return True

    def space_is_free(self, coord: Point) -> bool:
        return self.__board[coord.y()][coord.x()].is_occupied()

    def __str__(self) -> str:
        out_str = "  "
        for i in range(Point.MAX_COL):
            out_str += ' ' + str(i + 1)

        out_str += '\n'

        i = 0
        for row in self.__board:
            out_str += Point.ROW_LETTERS[i] + ' '
            for space in row:
                out_str += ' ' + space.get_marker()
            out_str += '\n'
            i += 1

        return out_str

class GameLogic:
    pass

class Player:
    def __init__(self):
        self.self_board = Board()
        self.other_board = Board()

    def setup(self):
        pass

    def print_state(self):
        out_str = ""

        own = str(self.self_board).split('\n')
        other = str(self.other_board).split('\n')

        for i in range(len(own) - 1):
            if i == 0:
                out_str += own[i] + '   ' + other[i] + '\n'
            else:
                out_str += own[i] + '  | ' + other[i] + '\n'

        print(out_str)

    def run_turn(self, game_logic: GameLogic):
        pass

    def receive_missile(self, coord: Point) -> bool:
        return self.self_board.detonate_missile(coord)

class Human(Player):
    def __init__(self, name):
        super().__init__()
        self.__name = name

    @staticmethod
    def query_coordinates(query, validate: bool = True) -> (Point, bool):
        result = input(query + ': ')
        result = result.split(' ')

        # I'm not wild about this approach, but it'll be fine for now.
        # basically if the validation fails, it'll return an error code within the point.
        # -1 is an invalid letter
        # -2 is an invalid column number
        # -3 is an invalid number of arguments (also provides the number of arguments given)
        if validate:
            if len(result) != 2: 
                return Point(len(result), -3), False

            result[1] = int(result[1])

            if result[0] not in Point.ROW_LETTERS:
                return Point(0, -1), False
            elif Point.MAX_COL < int(result[1]) < 0:
                return Point(0, -2), False

        return Point.from_board_coordinate(result), True

    @staticmethod
    def query_direction(query) -> (str, bool):
        result = input(query + ': ')
        result = result.strip()

        directions = ['n', 's', 'e', 'w']
        return result, result in directions

    @staticmethod
    def __show_error_messages(out) -> bool:
        if not out[1]:
            if out[0].y() == -1:
                print("Invalid row! Only rows from {} to {}.".format(Point.ROW_LETTERS[0],
                                                                     Point.ROW_LETTERS[Point.MAX_ROW - 1]))
            elif out[0].y() == -2:
                print("Invalid column! Only columns from {} to {}".format(0, Point.MAX_COL))
            elif out[0].y() == -3:
                print("Invalid argument count! Expected {}, got {}".format(2, out[0].x()))

    def setup(self):
        ships_to_place = [['Carrier', "AAAAA"], ['Battleship', 'BBBB'], ['Cruiser', 'CCC'], ['Submarine', 'SSS'], ['Destroyer', 'DD']]

        for ship in ships_to_place:
            valid_spot_found = False
            while not valid_spot_found:

                self.print_only_my_board()
                out = self.query_coordinates("{}    Place your {}".format(ship[1], ship[0]))

                Human.__show_error_messages(out)

                out_direction = self.query_direction("Which way will your {} face? ".format(ship[0]))

                if out_direction[1]:
                    new_ship = Ship.make_by_name(ship[0], out[0], out_direction[0])
                    if out[1] and self.self_board.spaces_are_free(new_ship.get_coords(), new_ship.get_dir(), new_ship.get_length()):
                        self.self_board.place_ship(new_ship)
                        valid_spot_found = True
                    else:
                        print("Cannot place a ship here!")

        self.print_only_my_board()
        print("Now lets begin battle!")
        
    def run_turn(self, game_logic: GameLogic):
        self.print_state()
        out = self.query_coordinates("Attempt to fire a missile")

        if not out[1]:
            Human.__show_error_messages(out)
        else:
            hit = game_logic.fire_missile(game_logic.get_opponent(self), out[0])
            if hit:
                self.other_board.place_object(out[0], 'X')
                print("Hit!")
            else:
                self.other_board.place_object(out[0], 'o')
                print("Miss!")

    def print_only_my_board(self):
        print(self.self_board)

class Robot(Player):
    MAX_DIFFICULTY = 4

    def __init__(self, difficulty: int):
        super().__init__()

        self.__difficulty = min(difficulty, Robot.MAX_DIFFICULTY)

    def setup(self):
        test_carrier = Ship.make_by_name("Destroyer", Point(0, 0), 's')
        self.self_board.place_ship(test_carrier)

    def run_turn(self, game_logic: GameLogic):
        pass


class GameLogic:
    def __init__(self):
        self.__human = Human("Patrick")
        self.__robot = Robot(1)

        self.__game_over = False

    def setup_players(self):
        self.__human.setup()
        self.__robot.setup()

    def run_game(self):
        while not self.__game_over:
            self.__human.run_turn(self)
            self.__robot.run_turn(self)

    def get_opponent(self, instigator) -> Player:
        if instigator == self.__human:
            return self.__robot
        elif instigator == self.__robot:
            return self.__human

    @staticmethod
    def fire_missile(target: Player, coord: Point) -> bool:
        return target.receive_missile(coord)


def main():
    logic = GameLogic()
    logic.setup_players()
    logic.run_game()


main()