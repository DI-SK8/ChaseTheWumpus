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

        start = None
        for r in range(ROW):
            for c in range(COL):
                if grid[r][c] == 0:
                    start = (r, c)
                    break
            if start : break
        if start:
            nb_of_case = FloodFile(grid, start[0], start[1])

            # Compter combien de cavernes existent au total
            total_of_case = 48

            # Si le Flood Fill a touché TOUTES les cavernes, la grille est valide
            if len(nb_of_case) == total_of_case:
                gridOk = True
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            print(grid[i][j], end=" ")
        print()

    return grid

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



