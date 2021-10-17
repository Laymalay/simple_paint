import pytest
from painter import (
    Canvas,
    CanvasCommand,
    LineCommand,
    Point,
    RectangleCommand,
    CommandParser,
    FillCommand,
    Invoker,
    main,
)
from exceptions import ExecutionError, InvalidCommandArgs


@pytest.fixture
def canvas():
    return Canvas(20, 4)


@pytest.fixture
def canvas_filled(canvas):
    return Canvas(canvas.width, canvas.height, background="o")


def draw_rectangle(canvas, start, end):
    canvas.grid[start.y][start.x : end.x + 1] = ["x"] * (end.x - start.x + 1)
    canvas.grid[end.y][start.x : end.x + 1] = ["x"] * (end.x - start.x + 1)

    for row in canvas.grid[start.y : end.y + 1]:
        row[start.x] = "x"
        row[end.x] = "x"


@pytest.fixture
def canvas_with_line(canvas):
    canvas.grid[2][4:7] = ["x"] * 3

    return canvas


@pytest.fixture
def canvas_with_rectangle(canvas):
    start = Point(15, 0)
    end = Point(19, 2)
    draw_rectangle(canvas, start, end)

    return canvas


@pytest.fixture
def canvas_with_rectangle_filled(canvas_filled):
    draw_rectangle(canvas_filled, Point(15, 0), Point(19, 2))
    canvas_filled.grid[1][16:19] = [" "] * 3

    return canvas_filled


@pytest.fixture
def commands():
    return [
        CanvasCommand(20, 4),
        RectangleCommand(15, 0, 19, 2),
        FillCommand(1, 1, "o"),
    ]


def test_canvas_creation():
    h = 10
    w = 10
    canvas = Canvas(w, h)
    assert canvas.width == 10
    assert canvas.height == 10
    assert canvas.background == " "
    assert canvas.brush == "x"
    assert canvas.grid == [
        [canvas.background for i in range(w)] for j in range(h)
    ]


class TestClassCanvasCommand:
    def test_canvas_command_creation(self):
        line = "C 10 5"
        assert CanvasCommand.check_command(line)

        parsed_command = CanvasCommand.parse(line)

        assert isinstance(parsed_command, CanvasCommand)
        assert parsed_command.width == 10
        assert parsed_command.height == 5

    def test_canvas_command_creation_invalid_name(self):
        line = "Can 10 5"
        assert not CanvasCommand.check_command(line)

    def test_canvas_command_creation_invalid_params(self):
        line = "C 10 -5"
        assert not CanvasCommand.check_command(line)


class TestClassLineCommand:
    def test_line_command_creation(self):
        line = "L 5 3 5 10"
        assert LineCommand.check_command(line)

        parsed_command = LineCommand.parse(line)

        assert isinstance(parsed_command, LineCommand)

    def test_line_command_creation_invalid_args_type(self):
        line = "L 5 3 t 10"

        assert not LineCommand.check_command(line)

    def test_line_command_creation_invalid_args(self):
        line = "L 5 3 5 2"

        assert LineCommand.check_command(line)
        with pytest.raises(InvalidCommandArgs):
            LineCommand.parse(line)

    def test_line_command_creation_invalid_name(self):
        line = "Li 5 3 t 10"

        assert not LineCommand.check_command(line)

    def test_line_command(self, canvas, canvas_with_line):
        line = "L 5 3 7 3"
        parsed_command = LineCommand.parse(line)
        parsed_command.execute(canvas)

        assert canvas.grid == canvas_with_line.grid

    def test_line_diagonal_command(self, canvas):
        line = "L 5 3 7 6"
        parsed_command = LineCommand.parse(line)
        with pytest.raises(ExecutionError):
            parsed_command.execute(canvas)


class TestClassRectangleCommand:
    def test_rectangle_command_creation(self):
        line = "R 16 1 20 3"

        assert RectangleCommand.check_command(line)
        parsed_command = RectangleCommand.parse(line)

        assert isinstance(parsed_command, RectangleCommand)

    def test_rectangle_command_creation_invalid_args(self):
        line = "R 16 3 20 1"

        assert RectangleCommand.check_command(line)
        with pytest.raises(InvalidCommandArgs):
            RectangleCommand.parse(line)

    def test_rectangle_command_creation_invalid_name(self):
        line = "GR 16 1 20 3"

        assert not RectangleCommand.check_command(line)


class TestClassFillCommand:
    def test_fill_command_creation(self):
        line = "B 16 3 o"

        assert FillCommand.check_command(line)
        parsed_command = FillCommand.parse(line)

        assert isinstance(parsed_command, FillCommand)

    def test_fill_command_creation_invalid_args(self):
        line = "B 16 r o"

        assert not FillCommand.check_command(line)

    def test_fill_command_creation_invalid_name(self):
        line = "F 6 1 20 3"

        assert not FillCommand.check_command(line)

    def test_fill_command(self, canvas, canvas_filled):
        line = "B 5 3 o"
        parsed_command = FillCommand.parse(line)
        parsed_command.execute(canvas)

        assert canvas.grid == canvas_filled.grid

    def test_fill_command_with_rectangle(
        self, canvas_with_rectangle, canvas_with_rectangle_filled
    ):
        line = "B 5 3 o"
        parsed_command = FillCommand.parse(line)
        parsed_command.execute(canvas_with_rectangle)

        assert canvas_with_rectangle.grid == canvas_with_rectangle_filled.grid


def test_command_parser():
    data = "C 10 10\nL 4 3 4 7\nR 6 1 10 5\nB 1 1 r\n L 4 3 4 7\nRe 6 1 10 5"
    commands = CommandParser.parse(data)

    assert len(commands) == 4
    assert isinstance(commands[0], CanvasCommand)
    assert isinstance(commands[1], LineCommand)
    assert isinstance(commands[2], RectangleCommand)
    assert isinstance(commands[3], FillCommand)


def test_invoker_execution(commands, canvas_with_rectangle_filled):
    invoker = Invoker()
    invoker.execute_all(commands)

    assert isinstance(invoker.canvas, Canvas)
    assert invoker.canvas.grid == canvas_with_rectangle_filled.grid
    assert len(invoker.history) == 3


def test_main(tmp_path):
    commands = "C 10 10\nL 4 3 4 7\nR 6 1 10 5\nB 1 1 o\n"
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.txt"
    input_file.write_text(commands, "utf8")

    assert len(list(tmp_path.iterdir())) == 1
    assert input_file.read_text("utf8") == commands

    main(input=input_file, output=output_file)

    assert len(list(tmp_path.iterdir())) == 2
