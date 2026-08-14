import random

ROW = 6
COL = 8

def GenerateGrid(level):
    """
    Generates a random grid (8x6) based on the level

    param :
        level (string) : level of the plate
    return :
        grid (list) : grid of the plate

    **niveau facile** => 1chauve souris
    en moyenne 32 caverne et 10 couloir (entre 8 et 14)
    **niveau moyen** => deux chauve souris
    24 cavernes et 18 couloir
    **niveau difficile** => deux chauve souris
    16 caverne et 26 couloir
    """

    if level == 'easy' :
        nb_hallway_target = random.randint(8, 14)
    elif level == 'medium' :
        nb_hallway_target = 18
    else :
        nb_hallway_target = 26

    gridOk = False

    while not gridOk :
        grid = [[0 for i in range(COL)] for j in range(ROW)]

        nb_hallway_put = 0
        while nb_hallway_put < nb_hallway_target :
            r = random.randint(0, ROW - 1)
            c = random.randint(0, COL - 1)
            if grid[r][c] == 0:
                grid[r][c] = random.randint(1, 2)
                nb_hallway_put += 1

        nb_of_case = FloodFile(grid, 0, 0)

        total_of_case = 48
        if len(nb_of_case) == total_of_case:
            gridOk = True

    neighbour = [(0, 1), (1, 0), (-1, 0), (0, -1)]

    GetPits(grid, neighbour)
    wumpus = GetStartCharacter(grid, 'wumpus')
    ApplyBlood(grid, wumpus[0], wumpus[1])

    for (dr, dc) in neighbour:
        GetWumpusHint(dr, dc, grid, wumpus[0], wumpus[1], 2)

    diag_neighbour = [(-1,-1),(1,1),(-1,1),(1,-1)]
    for (dr, dc) in diag_neighbour:
        diag_r = (wumpus[0] + dr) % ROW
        diag_c = (wumpus[1] + dc) % COL
        if grid[diag_r][diag_c] in (0, 4):
            ApplyBlood(grid, diag_r, diag_c)

    "affichage terminal"
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(grid[i][j], end=" ")
        print()
    return grid, wumpus

def GetPits(grid, neighbour):
    """
    will place the pits and the hints on the grid

    param :
        grid (list) : grid of the plate
    return :
        updated_grid (list) : grid of the plate with pits
    """
    is_pits_put = 0
    pits = set()
    while is_pits_put <2:
        r = random.randint(0, ROW - 1)
        c = random.randint(0, COL - 1)
        if grid[r][c] == 0:
            grid[r][c] = 3
            pits.add((r, c))
            is_pits_put+=1

    for (pr,pc) in pits:
        for (dr, dc) in neighbour:
            GetPitsHint(dr,dc,grid,pr,pc)
    return grid

def GetPitsHint(dr, dc, grid,pr,pc):
    """

    :param dr:
    :param dc:
    :param grid:
    :param pr:
    :param pc:
    :return:
    """
    r = (pr + dr) % ROW
    c = (pc + dc) % COL
    case = grid[r][c]

    if case in (3,4) :
        return
    if case == 0 :
        grid[r][c] = 4
        return

    next_dr, next_dc = None, None
    if case == 1:

        if (dr, dc) == (0, 1): next_dr, next_dc = (1, 0)
        elif (dr, dc) == (-1, 0): next_dr, next_dc = (0, -1)
        elif (dr, dc) == (0, -1): next_dr, next_dc = (-1, 0)
        elif (dr, dc) == (1, 0): next_dr, next_dc = (0, 1)

    elif case == 2:
        if (dr, dc) == (0, 1): next_dr, next_dc = (-1, 0)
        elif (dr, dc) == (1, 0): next_dr, next_dc = (0, -1)
        elif (dr, dc) == (0, -1): next_dr, next_dc = (1, 0)
        elif (dr, dc) == (-1, 0): next_dr, next_dc = (0, 1)

    if next_dr is None or next_dc is None:
        return

    GetPitsHint(next_dr, next_dc, grid, r, c)

def GetWumpusHint(dr, dc, grid, pr, pc, steps=2):
    """
    :param dr:
    :param dc:
    :param grid:
    :param pr:
    :param pc:
    :return:
    """
    if steps<=0:
        return


    r = (pr + dr) % ROW
    c = (pc + dc) % COL
    case = grid[r][c]

    if case == 3:
        return

    if case in (0, 4,6,7):
        ApplyBlood(grid, r, c)
        steps -= 1
        if steps <= 0:
            return

    next_dr, next_dc = None, None

    if case == 1:
        if (dr, dc) == (0, 1): next_dr, next_dc = (1, 0)
        elif (dr, dc) == (-1, 0): next_dr, next_dc = (0, -1)
        elif (dr, dc) == (0, -1): next_dr, next_dc = (-1, 0)
        elif (dr, dc) == (1, 0): next_dr, next_dc = (0, 1)

    elif case == 2:
        if (dr, dc) == (0, 1): next_dr, next_dc = (-1, 0)
        elif (dr, dc) == (1, 0): next_dr, next_dc = (0, -1)
        elif (dr, dc) == (0, -1): next_dr, next_dc = (1, 0)
        elif (dr, dc) == (-1, 0): next_dr, next_dc = (0, 1)

    elif case in (0, 4, 6, 7):
        next_dr, next_dc = dr, dc

    if next_dr is None or next_dc is None:
        return

    GetWumpusHint(next_dr, next_dc, grid, r, c, steps)

def ApplyBlood(grid, r, c):
    """

    :param grid:
    :param r:
    :param c:
    :return:
    """
    if grid[r][c] == 0 :
        grid[r][c] = 6
        return
    if grid[r][c] == 4 :
        grid[r][c] = 7
        return

def GetStartCharacter(grid, character) :
    """
    will found the start of the player and the wumpus

    param :
        grid (list) : grid of the plate
    return :
        start (tuple of int) : coordinates of the start of the player
    """
    if character == 'player':
        last_cave = [
            (r, c) for r in range(ROW) for c in range(COL)
            if grid[r][c] == 0
        ]
        return random.choice(last_cave)

    else :
        start = None
        while start is None:
            r = random.randint(0, ROW - 1)
            c = random.randint(0, COL - 1)
            if grid[r][c] == 0 or grid[r][c] == 3 or grid[r][c] == 4 :
                start = (r, c)
    return start

def GetBat(level, grid, pos_creature) :
    """

    :param level:
    :param grid:
    :return:
    """
    if level == 'easy' : target_count = 1
    else : target_count = 2
    valid_cells = [
        (r, c) for r in range(ROW) for c in range(COL)
        if grid[r][c] in (0, 1, 2, 4, 6, 7) and (r, c) not in pos_creature.values()
    ]
    chosen_cel =random.sample(valid_cells, min(target_count, len(valid_cells)))
    return  [[(r, c), 0] for r, c in chosen_cel]

def FloodFile(grid, r_start, c_start):
    """
    will try to go in all the cave

    param :
        grid (list) : grid of the plate
        r_start (int) : starting row
        c_start (int) : starting column

    return :
        nb_of_case (int) : number of caves we can acces
    """
    view = set()

    def propagation(r, c):
        """

        param :
            r (int) : starting row
            c (int) : starting column

        """
        r = r % ROW
        c = c % COL

        if (r, c) in view:
            return
        if (grid[r][c] == 2) and (grid[r][(c+1)%COL]==1 and grid[(r+1)%ROW][c]==1 and grid[(r+1)%ROW][(c+1)%COL]==2):
            return

        view.add((r, c))


        propagation(r + 1, c)
        propagation(r - 1, c)
        propagation(r, c + 1)
        propagation(r, c - 1)

    propagation(r_start, c_start)
    return view

def DepPlayer(grid, value, pos_creature) :
    player = pos_creature['player']
    r, c = player[0], player[1]

    match value:
        case 'up':
            new_coord = ((r - 1) % ROW, c)
        case 'down':
            new_coord = ((r + 1) % ROW, c)
        case 'left':
            new_coord = (r, (c - 1) % COL)
        case 'right':
            new_coord = (r, (c + 1) % COL)

    current_tile = grid[r][c]
    came_from = pos_creature.get('came_from')


    if current_tile == 1:
        if came_from in ('right', 'up'):
            if value not in ('left', 'down'):
                return pos_creature
        else:
            if value not in ('right', 'up'):
                return pos_creature

    elif current_tile == 2:
        if came_from in ('right', 'down'):
            if value not in ('left', 'up'):
                return pos_creature
        else:
            if value not in ('right', 'down'):
                return pos_creature


    player = new_coord


    if grid[player[0]][player[1]] in (1, 2):
        pos_creature['came_from'] = value

    pos_creature['player'] = player
    return pos_creature

def IsHeDead(grid, pos_creature) :

    player = pos_creature['player']
    wumpus = pos_creature.get('wumpus')
    pits = set()

    if player == wumpus:
        return 1

    for r in range(ROW):
        for c in range(COL):
            if grid[r][c] == 3:
                pits.add((r, c))
    if player in pits :
        return 2

    return 0


def UseBat(grid, pos_creature):
    bats = pos_creature.get('bats')
    player = pos_creature.get('player')

    bat = next((b for b in bats if b[0] == player), None)

    if bat:
        indice = bats.index(bat)
        if bat[1] == 0:
            bat[1] += 1
        else :
            other_bat = [b[0] for b in bats]
            valid_cells = [
                (r, c) for r in range(ROW) for c in range(COL)
                if grid[r][c] in (0, 1, 2, 4, 6, 7)
                   and (r, c) not in other_bat
                   and (r,c) != pos_creature['wumpus']
            ]
            chosen_cel = random.sample(valid_cells, min(2, len(valid_cells)))
            bat[0] = chosen_cel[0]
            bat[1] = 0
            player = chosen_cel[1]

    pos_creature['bats'] = bats
    pos_creature['player'] = player
    return pos_creature

