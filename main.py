import pygame, keyboard, maze_generator, random, math, time

pygame.init()
pygame.display.init()

SIZE_WIN = 700

surface = pygame.display.set_mode((SIZE_WIN, SIZE_WIN), pygame.DOUBLEBUF)
red = pygame.Surface((SIZE_WIN,SIZE_WIN))  # the size of your rect
red.set_alpha(255)                # alpha level
red.fill((255,50,50))  

green = pygame.Surface((SIZE_WIN,SIZE_WIN))  # the size of your rect
green.set_alpha(255)                # alpha level
green.fill((100, 255, 255))  

greenTimer = 120
speed_pu = pygame.Surface((SIZE_WIN,SIZE_WIN))  # the size of your rect
speed_pu.set_alpha(255)                # alpha level
speed_pu.fill((255, 255, 50))  

shield_pu = pygame.Surface((SIZE_WIN,SIZE_WIN))  # the size of your rect
shield_pu.set_alpha(255)                # alpha level
shield_pu.fill((50, 255, 255)) 

clock = pygame.time.Clock()

rounds = 1

starttime = time.perf_counter()


SIZE_CELL = 50
SIZE_PLAYER = 20
SIZE_PLAYER_IN_CELL = SIZE_PLAYER / SIZE_CELL

CELLS = SIZE_WIN // SIZE_CELL

maze_generator.RES = maze_generator.WIDTH, maze_generator.HEIGHT = SIZE_WIN, SIZE_WIN
maze_generator.TILE = SIZE_CELL
maze_generator.cols, maze_generator.rows = CELLS, CELLS

def oppisitenode(b,currentnode):
    global CELLS
    if b==0:
        oppisitenode=[currentnode[0]-1,currentnode[1]]
    elif b==1:
        oppisitenode=[currentnode[0],currentnode[1]+1]
    elif b==2:
        oppisitenode=[currentnode[0]+1,currentnode[1]]
    else:
        oppisitenode=[currentnode[0],currentnode[1]-1]
    return(oppisitenode)

def Dijkstrasearch(Walls, fromPos):
    global CELLS
    visited=[[0 for a in range(CELLS)] for b in range(CELLS)]
    visited[fromPos[1]][fromPos[0]]=1#starts bottom left with 1
    currentnodes=[[fromPos[0], fromPos[1]]]
    new=True
    while new==True:
        new=False
        for a in range(len(currentnodes)):#searches at all current nodes/squares
            currentnode=currentnodes[0]
            for b in range(4):#checks all 4 possible directions
                if not Walls[currentnode[1]][currentnode[0]].get_wall(b):#check for wall
                    nodeotherside=oppisitenode(b,currentnode)
                    if visited[nodeotherside[1]][nodeotherside[0]]==0:#check if hasnt been visited
                        visited[nodeotherside[1]][nodeotherside[0]]=visited[currentnode[1]][currentnode[0]]+1
                        currentnodes.append(nodeotherside)#adds the new node to the list of nodes curently at
                        new=True
            currentnodes.remove(currentnode)#removes the node previously at because it has been searched
    return(visited)

def Dijkstraroute(visited, Walls, fromPos, toPos):
    global CELLS
    distance=visited[toPos[1]][toPos[0]]
    routecoordinates=[[toPos[0],toPos[1]]]#sets finish to top right
    while routecoordinates[0][0]!=fromPos[0] or routecoordinates[0][1]!=fromPos[1]:
        nowCoords = routecoordinates[0]
        if not Walls[routecoordinates[0][1]][routecoordinates[0][0]].get_wall(0):#check for wall
            if nowCoords[0] >= 0 and visited[nowCoords[1]][nowCoords[0]-1]==distance-1:
                routecoordinates.insert(0,[nowCoords[0]-1,nowCoords[1]])
                distance=distance-1
        if not Walls[routecoordinates[0][1]][routecoordinates[0][0]].get_wall(1):#check for wall
            if nowCoords[1] < CELLS-1 and visited[nowCoords[1]+1][nowCoords[0]]==distance-1:
                routecoordinates.insert(0,[nowCoords[0],nowCoords[1]+1])
                distance=distance-1
        if not Walls[routecoordinates[0][1]][routecoordinates[0][0]].get_wall(2):#check for wall
            if nowCoords[0] < CELLS-1 and visited[nowCoords[1]][nowCoords[0]+1]==distance-1:
                routecoordinates.insert(0,[nowCoords[0]+1,nowCoords[1]])
                distance=distance-1
        if not Walls[routecoordinates[0][1]][routecoordinates[0][0]].get_wall(3):#check for wall
            if nowCoords[1] >= 0 and visited[nowCoords[1]-1][nowCoords[0]]==distance-1:
                routecoordinates.insert(0,[nowCoords[0],nowCoords[1]-1])
                distance=distance-1
    return(routecoordinates)

def solveMaze(maze, fromPos, toPos):
    #fromPos = [0, 0]
    return Dijkstraroute(Dijkstrasearch(maze, fromPos), maze, fromPos, toPos)
    

def tupleToList(value:tuple[int, int]):
    return value[0], value[1]

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


ENEMYSPEED = 60

def timeToString(value):
    value = int(value)
    second = value % 60
    minute = (value - second) // 60
    hour = (value - minute * 60 - second) // 60
    resultGo = f"{hour}:"
    if minute < 10:
        resultGo += "0"
    resultGo += f"{minute}:"
    if second < 10:
        resultGo += "0"
    resultGo += f"{second}"
    return resultGo

def start():
    global ENEMYSPEED, SIZE_CELL, SIZE_PLAYER, SIZE_PLAYER_IN_CELL, CELLS, rounds, starttime, greenTimer, green, red, speed_pu, shield_pu

    LOCATIONS = [
        [0, 0],
        [CELLS-1, 0],
        [0, CELLS-1],
        [CELLS-1, CELLS-1]
    ]

    startLocation = random.choice(LOCATIONS)
    LOCATIONS.remove(startLocation)
    endLocation = random.choice(LOCATIONS)
    LOCATIONS.remove(endLocation)
    enemyLocation = random.choice(LOCATIONS)

    enemyTimer = ENEMYSPEED * 2
    shieldTimer = 0

    enemySpawnTimer = ENEMYSPEED * 15

    health = 100
    healthDrain = 0

    player: list[float, float] = [startLocation[0] + 0.5, startLocation[1] + 0.5]
    enemysNow: list[list[int, int]] = [[enemyLocation[0], enemyLocation[1]]]
    enemysNext: list[list[int, int]] = [enemysNow[0][:]]
    enemys: list[list[float, float]] = [enemysNow[0][:]]


    MAZE = maze_generator.generate_maze()
    MAZECONVERTED: list[list[maze_generator.Cell]] = [[None for x in range(CELLS)] for y in range(CELLS)]
    
    for cell in MAZE:
        MAZECONVERTED[cell.y][cell.x] = cell

    mazepath = solveMaze(MAZECONVERTED, startLocation, endLocation)
    
    powerUps = []
    powerUps_heal = []
    powerUps_speed = []
    powerUps_shield = []

    poc = 0

    speed = 1

    while poc < len(mazepath):
        poc += random.randint(15, 30)
        if poc < len(mazepath):
            powerUps.append(mazepath[poc])

    for i in range(random.randint(5, 15)):
        powerUps.append([random.randint(0, CELLS), random.randint(0, CELLS)])

    for pu in powerUps:
        rand = random.randint(0, 2)
        if rand == 0:
            powerUps_heal.append(pu)
        elif rand == 1:
            powerUps_speed.append(pu)
        else:
            powerUps_shield.append(pu)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        surface.fill((100, 100, 100))

        for x in range(CELLS):
            for y in range(CELLS):
                color = (50, 50, 50) if (x % 2 == y % 2) else (30, 30, 30)
                if x == startLocation[0] and y == startLocation[1]:
                    color = (125, 150, 150)
                if x == endLocation[0] and y == endLocation[1]:
                    color = (100, 255, 100)
                pygame.draw.rect(surface, color, (x * SIZE_CELL, y * SIZE_CELL, SIZE_CELL, SIZE_CELL))

        if keyboard.is_pressed("a") or keyboard.is_pressed("left"):
            player[0] -= 0.05 * speed
        if keyboard.is_pressed("d") or keyboard.is_pressed("right"):
            player[0] += 0.05 * speed
        if keyboard.is_pressed("w") or keyboard.is_pressed("up"):
            player[1] -= 0.05 * speed
        if keyboard.is_pressed("s") or keyboard.is_pressed("down"):
            player[1] += 0.05 * speed

        for cell in MAZE:
            playerX, playerY = int(player[0]), int(player[1])
            x, y = cell.x, cell.y
            cell.draw(surface)
            if cell.x == playerX and cell.y == playerY and not keyboard.is_pressed("g"):
                if cell.walls["top"]:
                    player[1] = max(cell.y + SIZE_PLAYER_IN_CELL / 2, player[1])
                if cell.walls["bottom"]:
                    player[1] = min(cell.y + 1 - SIZE_PLAYER_IN_CELL / 2, player[1])
                if cell.walls["left"]:
                    player[0] = max(cell.x + SIZE_PLAYER_IN_CELL / 2, player[0])
                if cell.walls["right"]:
                    player[0] = min(cell.x + 1 - SIZE_PLAYER_IN_CELL / 2, player[0])

                    
        playerInt = [int(player[0]), int(player[1])]

        if int(player[0]) == endLocation[0] and int(player[1]) == endLocation[1]:
            rounds += 1
            greenTimer = 120
            if ENEMYSPEED > 14:
                ENEMYSPEED -= 7
            return

        enemyTimer -= 1
        if enemyTimer % 30 == 0:
            for enemy in enemys:
                damage = False
                
                enemyInt = [int(enemy[0]), int(enemy[1])]
                enemyWalls = MAZECONVERTED[enemyInt[0]][enemyInt[1]].walls
                
                if playerInt[0] == enemyInt[0] and playerInt[1] == enemyInt[1]: damage = True
                if not enemyWalls["left"] and playerInt[0] == enemyInt[0]-1 and playerInt[1] == enemyInt[1]: damage = True
                if not enemyWalls["right"] and playerInt[0] == enemyInt[0]+1 and playerInt[1] == enemyInt[1]: damage = True
                if not enemyWalls["top"] and playerInt[0] == enemyInt[0] and playerInt[1] == enemyInt[1]-1: damage = True
                if not enemyWalls["bottom"] and playerInt[0] == enemyInt[0] and playerInt[1] == enemyInt[1]+1: damage = True
                    
                if damage:
                    if shieldTimer > 0:
                        shieldTimer = 0
                    else:
                        red.fill((255,50,50))
                        health -= 15
                        healthDrain = 30
                        if health <= 0:
                            return
        if enemyTimer <= 0:
            for i in range(len(enemys)):
                enemyTimer = ENEMYSPEED
                enemysNow[i] = enemysNext[i][:]
                enemys[i] = enemysNow[i][:]
                path = solveMaze(MAZECONVERTED, enemysNow[i], [int(player[0]), int(player[1])])
                if len(path) > 1:
                    enemysNext[i] = path[1]
        else:
            for i in range(len(enemys)):
                lerped = 1.0 - enemyTimer / float(ENEMYSPEED)
                enemys[i][0] = lerp(enemysNow[i][0], enemysNext[i][0], lerped)
                enemys[i][1] = lerp(enemysNow[i][1], enemysNext[i][1], lerped)

        enemySpawnTimer -= 1
        if enemySpawnTimer <= 0:
            enemySpawnTimer = ENEMYSPEED * 15
            spawn = [random.randint(0, CELLS-1), random.randint(0, CELLS-1)]
            enemysNext.append(spawn[:])
            enemysNow.append(spawn[:])
            enemys.append(spawn[:])

        if playerInt in powerUps_heal:
            red.fill((50, 255, 50))
            healthDrain = 30
            powerUps_heal.remove(playerInt)
            if health < 100:
                health += 15

        if playerInt in powerUps_speed:
            powerUps_speed.remove(playerInt)
            speed = 1.75

        if playerInt in powerUps_shield:
            powerUps_shield.remove(playerInt)
            shieldTimer = 150

        for enemy in enemys:
            pygame.draw.circle(surface, (255, 100, 100), (1 + (enemy[0] + 0.5) * SIZE_CELL, 1 + (enemy[1] + 0.5) * SIZE_CELL), SIZE_PLAYER / 2)
        
        for pu in powerUps_heal:
            pygame.draw.line(surface, (50, 255, 50), ((pu[0] + 0.5) * SIZE_CELL - 12, (pu[1] + 0.5) * SIZE_CELL), ((pu[0] + 0.5) * SIZE_CELL + 12, (pu[1] + 0.5) * SIZE_CELL), 6)
            pygame.draw.line(surface, (50, 255, 50), ((pu[0] + 0.5) * SIZE_CELL, (pu[1] + 0.5) * SIZE_CELL - 12), ((pu[0] + 0.5) * SIZE_CELL, (pu[1] + 0.5) * SIZE_CELL + 12), 6)
        
        for pu in powerUps_speed:
            pygame.draw.line(surface, (255, 255, 50), ((pu[0] + 0.5) * SIZE_CELL - 4, (pu[1] + 0.5) * SIZE_CELL), ((pu[0] + 0.5) * SIZE_CELL + 4, (pu[1] + 0.5) * SIZE_CELL), 6)
            pygame.draw.line(surface, (255, 255, 50), ((pu[0] + 0.5) * SIZE_CELL - 4, (pu[1] + 0.5) * SIZE_CELL - 12), ((pu[0] + 0.5) * SIZE_CELL - 4, (pu[1] + 0.5) * SIZE_CELL + 4), 6)
            pygame.draw.line(surface, (255, 255, 50), ((pu[0] + 0.5) * SIZE_CELL + 4, (pu[1] + 0.5) * SIZE_CELL + 12), ((pu[0] + 0.5) * SIZE_CELL + 4, (pu[1] + 0.5) * SIZE_CELL - 4), 6)
        
        for pu in powerUps_shield:
            points = [
                [-12, -6],
                [-8, -10],
                [8, -10],
                [12, -6],
                [0, 10]
            ]
            for i in range(len(points)):
                points[i] = [(pu[0] + 0.5) * SIZE_CELL + points[i][0], (pu[1] + 0.5) * SIZE_CELL + points[i][1]]
            pygame.draw.polygon(surface, (50, 255, 255), points)
            
        pygame.draw.circle(surface, (100, 255, 255), (1 + player[0] * SIZE_CELL, 1 + player[1] * SIZE_CELL), SIZE_PLAYER / 2)

        if healthDrain > 0:
            red.set_alpha(int(healthDrain * 180.0 / 30.0))
            surface.blit(red, (0, 0))
            healthDrain -= 1
        if greenTimer > 0:
            green.set_alpha(int(greenTimer * 180.0 / 120.0))
            surface.blit(green, (0, 0))
            greenTimer -= 1
            if greenTimer == 0:
                green.fill((100, 255, 100))
        if shieldTimer > 0:
            shield_pu.set_alpha(int(shieldTimer * 180.0 / 150.0))
            surface.blit(shield_pu, (0, 0))
            shieldTimer -= 1
        
        if speed > 1:
            speed -= 0.75/180
            speed_pu.set_alpha(int((speed - 1) * 180.0))
            surface.blit(speed_pu, (0, 0))


        healthBar = ""
        for i in range(20):
            healthBar += "#" if (health >= i * 5) else "-"

        pygame.display.set_caption(f"Лабиринт | Уровень {rounds} | Здоровье: [{healthBar}] | Время: {timeToString(time.perf_counter() - starttime)}")

        pygame.display.flip()

        clock.tick(60)

while True:
    start()
