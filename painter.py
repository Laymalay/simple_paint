#!/usr/bin/python3
from abc import ABCMeta, abstractmethod, abstractclassmethod
import argparse
from collections import namedtuple
import re
from exceptions import ExecutionError, InvalidCommandArgs

Point = namedtuple("Point", "x y")


class Canvas:
    """
    Provides area to draw in
    """

    def __init__(
        self,
        width: int = 10,
        height: int = 10,
        background: str = " ",
        brush: str = "x",
    ) -> None:
        self.width = width
        self.height = height

        self.background = background
        self.grid = [
            [self.background for i in range(self.width)]
            for j in range(self.height)
        ]
        self.brush = brush

    def display(self) -> None:
        line = "-" * (self.width + 2) + "\n"
        inner = []
        for i in self.grid:
            inner.append("|" + "".join(i) + "|" + "\n")
        return "".join([line] + inner + [line])


class Command(metaclass=ABCMeta):
    """
    Abstract class for commands
    """

    @abstractmethod
    def execute(self, canvas: Canvas = None) -> None:
        pass

    @abstractclassmethod
    def check_command(cls, line: str) -> bool:
        pass

    @abstractclassmethod
    def parse(cls, line: str):
        pass


class CanvasCommand(Command):
    """
    Creates canvas
    """

    template = re.compile(r"^C (?P<w>\d+) (?P<h>\d+)$")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def execute(self) -> Canvas:
        return Canvas(self.width, self.height)

    @classmethod
    def check_command(cls, line):
        return cls.template.match(line)

    @classmethod
    def parse(cls, line):
        m = cls.template.match(line)
        w = int(m.group("w"))
        h = int(m.group("h"))
        return cls(w, h)


class LineCommand(Command):
    """
    Draw horizontal or vertical lines on canvas
    """

    template = re.compile(
        r"^L (?P<x1>\d+) (?P<y1>\d+) (?P<x2>\d+) (?P<y2>\d+)$"
    )

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.start = Point(x1, y1)
        self.end = Point(x2, y2)

    def execute(self, canvas: Canvas = None) -> None:
        LineCommand.draw_line(canvas, self.start, self.end)

    @staticmethod
    def draw_line(canvas: Canvas, start: Point, end: Point) -> None:
        if start.x == end.x:
            for row in canvas.grid[start.y : end.y + 1]:
                row[start.x] = canvas.brush
        elif start.y == end.y:
            canvas.grid[start.y][start.x : end.x + 1] = [canvas.brush] * (
                end.x - start.x + 1
            )
        else:
            raise ExecutionError("Can't draw diagonal lines yet")

    @classmethod
    def check_command(cls, line: str) -> bool:
        return cls.template.match(line)

    @classmethod
    def parse(cls, line):
        m = cls.template.match(line)
        coords = [int(c) - 1 for c in m.groups()]
        if coords[2] < coords[0] or coords[3] < coords[1]:
            raise InvalidCommandArgs(
                "Invalid LineCommand args: x2 y2 should be >= x1 y1."
            )
        return cls(*coords)


class RectangleCommand(Command):
    """
    Draw rectangle on canvas
    """

    template = re.compile(
        r"^R (?P<x1>\d+) (?P<y1>\d+) (?P<x2>\d+) (?P<y2>\d+)$"
    )

    def __init__(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.start = Point(x1, y1)
        self.end = Point(x2, y2)

    def execute(self, canvas: Canvas = None) -> None:
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        lines = (
            (Point(x1, y1), Point(x1, y2)),
            (Point(x1, y1), Point(x2, y1)),
            (Point(x1, y2), Point(x2, y2)),
            (Point(x2, y1), Point(x2, y2)),
        )
        for line in lines:
            LineCommand.draw_line(canvas, *line)

    @classmethod
    def check_command(cls, line: str) -> bool:
        return cls.template.match(line)

    @classmethod
    def parse(cls, line):
        m = cls.template.match(line)
        coords = [int(c) - 1 for c in m.groups()]
        if coords[2] < coords[0] or coords[3] < coords[1]:
            raise InvalidCommandArgs(
                "Invalid RectangleCommand args: x2 y2 should be >= x1 y1."
            )
        return cls(*coords)


class FillCommand(Command):
    """
    Bucket fill of selected area
    """

    template = re.compile(r"^B (?P<x>\d+) (?P<y>\d+) (?P<color>\w+)$")

    def __init__(self, x: int, y: int, c: str) -> None:
        self.point = Point(x, y)
        self.color = c

    def execute(self, canvas: Canvas = None) -> None:
        cells = set([self.point])
        # check is point empty
        while cells:
            current = cells.pop()
            canvas.grid[current.y][current.x] = self.color
            neighbours = (
                Point(current.x + 1, current.y),
                Point(current.x, current.y + 1),
                Point(current.x - 1, current.y),
                Point(current.x, current.y - 1),
            )
            for neighbour in neighbours:
                if (
                    0 <= neighbour.y < canvas.height
                    and 0 <= neighbour.x < canvas.width
                    and canvas.grid[neighbour.y][neighbour.x]
                    == canvas.background
                ):
                    cells.add(neighbour)

    @classmethod
    def check_command(cls, line):
        return cls.template.match(line)

    @classmethod
    def parse(cls, line):
        m = cls.template.match(line)
        x = int(m.group("x")) - 1
        y = int(m.group("y")) - 1
        return cls(x, y, m.group("color"))


class CommandParser:
    """
    Parse strings to commands
    """

    available_commands = [
        CanvasCommand,
        LineCommand,
        RectangleCommand,
        FillCommand,
    ]

    @classmethod
    def parse(cls, data: str) -> list:
        """
        Parse raw data to commands objects
        """
        result = []

        for line in data.splitlines():
            for cmd in cls.available_commands:
                if cmd.check_command(line):
                    parsed_command = cmd.parse(line)
                    result.append(parsed_command)
        return result


class Invoker:
    """
    Commands executor
    """

    def __init__(self, commands: list = None) -> None:
        self.history: list[list[str]] = []
        self.canvas = None
        self.commands = commands

    def execute_all(self, commands: list = None) -> None:
        for command in commands:
            if isinstance(command, CanvasCommand):
                self.canvas = command.execute()
            elif self.canvas is None:
                print("Cannot draw without canvas")
                continue
            else:
                command.execute(canvas=self.canvas)

            print(self.canvas.display())
            self.history.append(self.canvas.display())




def main(input: str, output: str) -> None:
    with open(input, "r") as in_file:
        data = in_file.read()

    commands = CommandParser.parse(data)
    invoker = Invoker()
    invoker.execute_all(commands)

    with open(output, "w") as out_file:
        for state in invoker.history:
            out_file.write(state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        help="path to input file",
        type=str,
        default="input.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="path to output file",
        type=str,
        default="output.txt",
    )
    args = parser.parse_args()
    main(args.input, args.output)
