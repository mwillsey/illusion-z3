import z3

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


def compute(flat: str, side: str):
    flat = convert(flat)
    side = convert(side)

    height = len(flat)
    assert len(side) == height

    width = len(flat[0])
    assert len(side[0]) == width

    high = [
        [z3.Bool(f'high-{y}-{x}') for x in range(width) ]
        for y in range(height)
    ]

    color = [
        [z3.Bool(f'color-{y}-{x}') for x in range(width) ]
        for y in range(height)
    ]

    opt = z3.Optimize()

    for y in range(height):
        for x in range(width):
            opt.add_soft(color[y][x] == flat[y][x])

            if y + 1 < height:
                obscured = z3.And(high[y+1][x], z3.Not(high[y][x]))
                side_color = z3.If(obscured, color[y+1][x], color[y][x])
            else:
                side_color = color[y][x]

            opt.add_soft(side_color == side[y][x])

    print(opt.check())
    m = opt.model()

    output = ''
    for y in range(height):
        for x in range(width):
            is_color = m[color[y][x]]
            is_high = m[high[y][x]]

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


FLAT = """
....................
OOOOOOOOOOOOOOOOOOOO
....................
OOOOOOOOOOOOOOOOOOOO
....................
OOOOOOOOOOOOOOOOOOOO
"""

SIDE = """
.......OOOOOO.......
.....OOOOOOOOOO.....
...OOOOOOOOOOOOOO...
...OOOOOOOOOOOOOO...
.....OOOOOOOOOO.....
.......OOOOOO.......
"""

compute(FLAT, SIDE)