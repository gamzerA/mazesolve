# -*- coding: utf-8 -*-
import pygame
import time
import random
import heapq
import copy

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
LIGHT_GRAY = (230, 230, 230)

CELL_SIZE = 30
FPS = 15
TOP_MARGIN = 60  # reduced margin

def generate_valid_maze(filename, size=10, wall_prob=0.3):
    while True:
        maze = [['0' for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if i == 0 or j == 0 or i == size - 1 or j == size - 1:
                    maze[i][j] = '1'
                elif random.random() < wall_prob:
                    maze[i][j] = '1'
        sx, sy = random.randint(1, size - 2), random.randint(1, size - 2)
        ex, ey = random.randint(1, size - 2), random.randint(1, size - 2)
        if (sx, sy) == (ex, ey):
            continue
        maze[sx][sy] = 'e'
        maze[ex][ey] = 'x'
        if is_valid(maze, (sx, sy)) and is_valid(maze, (ex, ey)):
            with open(filename, 'w') as f:
                f.write(str(size) + '\n')
                for row in maze:
                    f.write(''.join(row) + '\n')
            return

def is_valid(maze, pos):
    x, y = pos
    n = len(maze)
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x+dx, y+dy
        if 0<=nx<n and 0<=ny<n and maze[nx][ny]=='0':
            return True
    return False

def read_maze(filename):
    with open(filename) as f:
        size = int(f.readline())
        maze = [list(f.readline().strip()) for _ in range(size)]
    return maze

def find_points(maze):
    start = end = None
    for i, row in enumerate(maze):
        for j, val in enumerate(row):
            if val == 'e': start = (i,j)
            if val == 'x': end = (i,j)
    return start, end

def draw(surface, maze, path, current, visited, offset, title):
    font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 26)
    label_font = pygame.font.Font(None, 18)

    for i, row in enumerate(maze):
        for j, val in enumerate(row):
            x = offset + j*CELL_SIZE
            y = i*CELL_SIZE + TOP_MARGIN
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if val == '1': color = BLACK
            elif val == 'e': color = GREEN
            elif val == 'x': color = RED
            else: color = GRAY
            pygame.draw.rect(surface, color, rect)
            if val == 'e':
                surface.blit(label_font.render("start", True, BLACK), (x + 2, y + 2))
            elif val == 'x':
                surface.blit(label_font.render("exit", True, BLACK), (x + 2, y + 2))

    for idx, (x, y) in enumerate(visited):
        pygame.draw.rect(surface, LIGHT_GRAY, (offset + y*CELL_SIZE+4, x*CELL_SIZE+TOP_MARGIN+4, CELL_SIZE-8, CELL_SIZE-8))
        num = font.render(str(idx+1), True, (0, 0, 0))
        surface.blit(num, (offset + y*CELL_SIZE+6, x*CELL_SIZE+TOP_MARGIN+6))

    for idx, (x, y) in enumerate(path):
        pygame.draw.rect(surface, BLUE, (offset + y*CELL_SIZE+8, x*CELL_SIZE+TOP_MARGIN+8, CELL_SIZE-16, CELL_SIZE-16))

    if current:
        cx, cy = current
        pygame.draw.rect(surface, YELLOW, (offset + cy*CELL_SIZE+8, cx*CELL_SIZE+TOP_MARGIN+8, CELL_SIZE-16, CELL_SIZE-16))

    surface.blit(title_font.render(title, True, (0, 0, 0)), (offset + 10, 10))

def run_algorithm(maze, algorithm, offset, surface, clock):
    start, end = find_points(maze)
    visited = set()
    visited_order = []
    time_start = time.time()
    if algorithm == 'DFS':
        frontier = [(start, [start])]
    elif algorithm == 'BFS':
        frontier = [(start, [start])]
    elif algorithm == 'PQ':
        frontier = [(0, start, [start])]

    while frontier:
        if algorithm == 'DFS':
            (x, y), path = frontier.pop()
        elif algorithm == 'BFS':
            (x, y), path = frontier.pop(0)
        elif algorithm == 'PQ':
            _, (x, y), path = heapq.heappop(frontier)
        if (x,y) in visited:
            continue
        visited.add((x,y))
        visited_order.append((x,y))
        draw(surface, maze, path, (x,y), visited_order, offset, algorithm)
        pygame.display.update()
        clock.tick(FPS)
        if (x,y) == end:
            t = time.time() - time_start
            return {'name': algorithm, 'path': path, 'visited': visited_order, 'time': t}
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<len(maze) and 0<=ny<len(maze[0]) and maze[nx][ny] != '1' and (nx,ny) not in visited:
                new_path = path + [(nx,ny)]
                if algorithm == 'DFS' or algorithm == 'BFS':
                    frontier.append(((nx,ny), new_path))
                elif algorithm == 'PQ':
                    hx = abs(end[0]-nx) + abs(end[1]-ny)
                    heapq.heappush(frontier, (len(new_path)+hx, (nx,ny), new_path))
    return None

def main():
    pygame.init()
    width = CELL_SIZE * 15 * 3
    height = CELL_SIZE * 15 + TOP_MARGIN + 100
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze Algorithm Comparison")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 28)
    restart_button = pygame.Rect(width//2 - 60, height - 40, 120, 30)

    while True:
        generate_valid_maze("maze.txt", 15)
        base = read_maze("maze.txt")
        dfs_m = copy.deepcopy(base)
        bfs_m = copy.deepcopy(base)
        pq_m = copy.deepcopy(base)

        screen.fill(WHITE)
        dfs_result = run_algorithm(dfs_m, 'DFS', 0, screen, clock)
        bfs_result = run_algorithm(bfs_m, 'BFS', width//3, screen, clock)
        pq_result  = run_algorithm(pq_m,  'PQ',  2*width//3, screen, clock)

        if not dfs_result or not bfs_result or not pq_result:
            continue

        results = [dfs_result, bfs_result, pq_result]
        results.sort(key=lambda r: (len(r['visited']), r['time']))

        for i, res in enumerate(results):
            txt = f"{i+1}. {res['name']} - Time: {res['time']:.2f}s, Visited: {len(res['visited'])}, Path: {len(res['path'])}"
            screen.blit(font.render(txt, True, (0,0,0)), (10, height - 100 + i*20))

        pygame.draw.rect(screen, (200, 200, 200), restart_button)
        screen.blit(font.render("Restart", True, (0,0,0)), (restart_button.x + 20, restart_button.y + 5))

        pygame.display.update()
        print("--- Results ---")
        for res in results:
            print(f"{res['name']} | Time: {res['time']:.2f}s | Visited: {len(res['visited'])} | Path Length: {len(res['path'])}")
            print(f"{res['name']} Visited Coordinates:")
            for coord in res['visited']:
                print(coord, end=' ')
            print('\n')

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(event.pos):
                    waiting = False
                    break

if __name__ == '__main__':
    main()
