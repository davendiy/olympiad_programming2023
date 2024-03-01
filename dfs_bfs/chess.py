
EMPTY_SPACE = -1


def create_board(fill=EMPTY_SPACE): 
    """Create 8x8 board and fill it with `fill` value."""
    return [
        [fill for _ in range(8)]
        for _ in range(8)
    ]


def usr2coord(position: str): 
    """Transform position c2 to (2, 1)."""

    alphabet = 'abcdefgh'
    x, y = position
    assert x in alphabet, y in '12345678'
    return alphabet.index(x), int(y) - 1


def coord2usr(position: tuple): 
    """Transform position (2, 1) to c2."""
    alphabet = 'abcdefgh'
    x, y = position
    return f'{alphabet[x]}{y + 1}'


def _moves_wrapper(x, y, board=None) -> bool:
    if board is None: 
        return 0 <= x < 8 and 0 <= y < 8
    else:
        return 0 <= x < 8 and 0 <= y < 8 \
                and board[x][y] == EMPTY_SPACE


def _next_moves(start_pos, deltas): 

    x, y = start_pos 
    for delta_x, delta_y in deltas: 
        next_x, next_y = x + delta_x, y + delta_y
        if _moves_wrapper(next_x, next_y): 
            yield next_x, next_y


def knight_moves(start_pos: tuple): 
    """Return every possible cells where knight can move."""

    return _next_moves(start_pos, 
                       deltas=[
        [1, 2], [1, -2], [-1, 2], [-1, -2], 
        [2, 1], [2, -1], [-2, 1], [-2, -1]]
    )


def king_moves(start_pos: tuple): 
    """Return every possible cells where king can move."""
    return _next_moves(
        start_pos, 
        deltas=((i, j) for i in [-1, 0, 1] for j in [-1, 0, 1] 
                if i != 0 or j != 0)
    )


def rook_moves(start_pos, board=None): 
    """Return every possible cells where rook can move if there is no other 
    figure on the way."""
    x, y = start_pos   

    for mul_x, mul_y in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
        for delta in range(1, 8): 
            next_x = x + mul_x * delta
            next_y = y + mul_y * delta
            if _moves_wrapper(next_x, next_y, board=board):
                yield next_x, next_y
            else: 
                break


def bishop_moves(start_pos, board=None): 
    """Return every possible cells where bishop can move if there is no other 
    figure on the way."""
    x, y = start_pos   

    for mul_x, mul_y in [[1, -1], [-1, 1], [1, 1], [-1, -1]]:
        for delta in range(1, 8): 
            next_x = x + mul_x * delta
            next_y = y + mul_y * delta
            if _moves_wrapper(next_x, next_y, board=board):
                yield next_x, next_y
            else: 
                break


def queen_moves(start_pos, board=None): 
    """Return every possible cells where queen can move if there is no other 
    figure on the way."""

    for pos in rook_moves(start_pos, board): 
        yield pos 
    for pos in bishop_moves(start_pos, board): 
        yield pos 
