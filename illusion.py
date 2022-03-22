from turtle import circle
import z3

from enum import Enum

class Offset(Enum):
    Up = (-1, 0)
    Down = (1, 0)
    Left = (0, -1)
    Right = (0, 1)

def convert(s: str):
    grid = []
    for line in s.strip().splitlines():
        row = []
        for ch in line.strip():
            if ch == '.':
                row.append(False)
            elif ch == 'O': 
                row.append(True)
            else:
                raise ValueError("Unrecognized char", ch)
        grid.append(row)
    return grid


class Illusion:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.opt = z3.Optimize()
        self.offsets = []

        self.high = [
            [z3.Bool(f'high-{y}-{x}') for x in range(width) ]
            for y in range(height)
        ]

        self.color = [
            [z3.Bool(f'color-{y}-{x}') for x in range(width) ]
            for y in range(height)
        ]

    def constrain(self, offset, values, weight = 1):
        if offset not in self.offsets:
            self.offsets.append(offset)

        assert offset is None or isinstance(offset, Offset)
        for y in range(self.height):
            for x in range(self.width):
                color = self.get_color(y, x, offset)
                self.opt.add_soft(color == values[y][x], weight=weight)

    def get_color(self, y, x, offset):
        if offset is None:
            return self.color[y][x]

        yy = y + offset.value[0]
        xx = x + offset.value[1]
        if 0 <= yy < self.height and 0 <= xx < self.width:
            obscured = z3.And(self.high[yy][xx], z3.Not(self.high[y][x]))
            return z3.If(obscured, self.color[yy][xx], self.color[y][x])
        else:
            return self.color[y][x]

    def render_offset(self, model, offset):
        output = ''
        for y in range(self.height):
            for x in range(self.width):
                color = self.get_color(y, x, offset)
                color = model.eval(color)
                output += 'O' if color else '.'
            output += '\n'

        return output

    def solve(self):
        print(self.opt.check())
        m = self.opt.model()
        for obj in self.opt.objectives():
            print(m.eval(obj))

        output = ''
        for y in range(self.height):
            for x in range(self.width):
                is_color = m[self.color[y][x]]
                is_high = m[self.high[y][x]]

                if is_color:
                    if is_high:
                        output += 'O'
                    else:
                        output += 'o'
                else:
                    if is_high:
                        output += '*'
                    else:
                        output += '.'
            output += '\n'

        print(output)

        for offset in self.offsets:
            print(offset)
            print(self.render_offset(m, offset))



STRIPES = """
OOOOOOOOOOOOOOOOOOOO
....................
OOOOOOOOOOOOOOOOOOOO
....................
OOOOOOOOOOOOOOOOOOOO
....................
"""

CIRCLE = """
.......OOOOOO.......
.....OOOOOOOOOO.....
...OOOOOOOOOOOOOO...
...OOOOOOOOOOOOOO...
.....OOOOOOOOOO.....
.......OOOOOO.......
"""

DOT = """
....................
....................
........OOOO........
........OOOO........
....................
....................
"""

STAR = """
.........OO.........
........OOOO........
...OOOOOOOOOOOOOO...
......OOOOOOOO......
.....OO......OO.....
....................
"""


illusion = Illusion(6, 20)
illusion.constrain(Offset.Up, convert(DOT))
illusion.constrain(Offset.Down, convert(STAR))
illusion.solve()

# illusion = Illusion(6, 20)
# illusion.constrain(Offset.Up, convert(CIRCLE))
# illusion.constrain(Offset.Down, convert(STAR))
# illusion.solve()