import pygame as pg
import random
import time
import sys
from pygame.locals import *

FPS = 25   # Частота кадров в секунду
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 500   # Размеры игрового окна
BLOCK_SIZE = 20   # Размер базового элемента фигур-букв
CUP_HEIGHT, CUP_WIDTH = 20, 10   # Размеры игрового поля в блоках (высота, ширина)
SIDE_FREQ, DOWN_FREQ = 0.15, 0.1   # Время, которое затрачивается на перемещение фигуры в сторону или вниз
SIDE_MARGIN = int((WINDOW_WIDTH - CUP_WIDTH * BLOCK_SIZE) / 2)   # Отступ по бокам
TOP_MARGIN = WINDOW_HEIGHT - (CUP_HEIGHT * BLOCK_SIZE) - 5   # Отступ сверху

# Пути к шрифтам
FONT_PATH = 'Tetris/GNF.ttf'
FONT_PATH_MARIO = 'Tetris/mario.ttf'
FONT_PATH_CHAKRA = 'Tetris/ChakraPetch-Regular.otf'

# Цвета
COLORS = {
    'S': (128, 0, 128),   
    'Z': (65, 105, 225),     
    'J': (178, 34, 34),        
    'L': (255, 20, 147),      
    'I': (210, 105, 30),      
    'O': (189, 183, 107),     
    'T': (0, 128, 128)     
}

LIGHT_COLORS = {
    'S': (216, 128, 216),  
    'Z': (144, 176, 255),  
    'J': (255, 140, 140),  
    'L': (255, 153, 204),  
    'I': (255, 194, 153),  
    'O': (222, 222, 161),  
    'T': (128, 200, 200)   
}

GHOST_COLORS = {
    'S': (128, 0, 128, 13),    
    'Z': (65, 105, 225, 13),   
    'J': (178, 34, 34, 13),    
    'L': (255, 20, 147, 13),   
    'I': (210, 105, 30, 13),   
    'O': (189, 183, 107, 13),  
    'T': (0, 128, 128, 13)     
}

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRD_COLOR = WHITE   # Цвет границ
BG_COLOR = BLACK    # Цвет фона

FIG_W, FIG_H = 5, 5   # Размер шаблона 5 х 5
EMPTY = 'o'   # Обозначение пустой клетки

# Символом x отмечены занятые ячейки
FIGURES = {
    'S': [
        ['ooooo', 'ooooo', 'ooxxo', 'oxxoo', 'ooooo'],
        ['ooooo', 'ooxoo', 'ooxxo', 'oooxo', 'ooooo']
    ],
    'Z': [
        ['ooooo', 'ooooo', 'oxxoo', 'ooxxo', 'ooooo'],
        ['ooooo', 'ooxoo', 'oxxoo', 'oxooo', 'ooooo']
    ],
    'J': [
        ['ooooo', 'oxooo', 'oxxxo', 'ooooo', 'ooooo'],
        ['ooooo', 'ooxxo', 'ooxoo', 'ooxoo', 'ooooo'],
        ['ooooo', 'ooooo', 'oxxxo', 'oooxo', 'ooooo'],
        ['ooooo', 'ooxoo', 'ooxoo', 'oxxoo', 'ooooo']
    ],
    'L': [
        ['ooooo', 'oooxo', 'oxxxo', 'ooooo', 'ooooo'],
        ['ooooo', 'ooxoo', 'ooxoo', 'ooxxo', 'ooooo'],
        ['ooooo', 'ooooo', 'oxxxo', 'oxooo', 'ooooo'],
        ['ooooo', 'oxxoo', 'ooxoo', 'ooxoo', 'ooooo']
    ],
    'I': [
        ['ooxoo', 'ooxoo', 'ooxoo', 'ooxoo', 'ooooo'],
        ['ooooo', 'ooooo', 'xxxxo', 'ooooo', 'ooooo']
    ],
    'O': [
        ['ooooo', 'ooooo', 'oxxoo', 'oxxoo', 'ooooo']
    ],
    'T': [
        ['ooooo', 'ooxoo', 'oxxxo', 'ooooo', 'ooooo'],
        ['ooooo', 'ooxoo', 'ooxxo', 'ooxoo', 'ooooo'],
        ['ooooo', 'ooooo', 'oxxxo', 'ooxoo', 'ooooo'],
        ['ooooo', 'ooxoo', 'oxxoo', 'ooxoo', 'ooooo']
    ]
}

# Создает полупрозрачный верхний слой для паузы и конца игры
def show_overlay_screen():
    overlay = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pg.SRCALPHA)
    overlay.fill((15, 15, 15, 215))  # Полупрозрачный темный фон
    display_surf.blit(overlay, (0, 0))

def main():
    global fps_clock, display_surf, basic_font, big_font, control_font, font_for_hint

    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Загрузка шрифтов
    basic_font = pg.font.Font(FONT_PATH, 25)
    font_for_hint = pg.font.Font(FONT_PATH, 20)
    big_font = pg.font.Font(FONT_PATH_MARIO, 50)
    control_font = pg.font.Font(FONT_PATH_CHAKRA, 17)

    pg.display.set_caption('TETRIS')
    
    # Показ начального экрана и запуск игры
    showText('TETRIS')
    while True:
        runTetris()
        show_overlay_screen()
        showText('Игра закончена')

# Основной игровой цикл
def runTetris():
    # Инициализация игрового поля и параметров
    cup = emptycup()
    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    going_down = False 
    going_left = False
    going_right = False
    points = 0
    total_lines_cleared = 0
    level, fall_speed = calcSpeed(total_lines_cleared)
    fallingFig = getNewFig()
    nextFig = getNewFig()

    while True:
        # Обработка появления новой фигуры
        if fallingFig is None:
            fallingFig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()
            
            if not checkPos(cup, fallingFig):   # Проверка на завершение игры
                return

        quitGame()
        
        # Управление движением
        for event in pg.event.get(): 
            if event.type == KEYUP:
                if event.key == K_SPACE:   # Пауза
                    show_overlay_screen()
                    showText('Пауза')
                    last_fall = time.time()
                    last_move_down = time.time()
                    last_side_move = time.time()
                elif event.key == K_LEFT:
                    going_left = False
                elif event.key == K_RIGHT:
                    going_right = False
                elif event.key == K_DOWN:
                    going_down = False

            elif event.type == KEYDOWN:
                # Движение влево
                if event.key == K_LEFT and checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()

                # Движение вправо
                elif event.key == K_RIGHT and checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()

                # Вращение
                elif event.key == K_UP:
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(FIGURES[fallingFig['shape']])
                    if not checkPos(cup, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(FIGURES[fallingFig['shape']])

                # Ускоренное падение
                elif event.key == K_DOWN:
                    going_down = True
                    if checkPos(cup, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()

                # Мгновенное падение
                elif event.key == K_RETURN:
                    going_down = False
                    going_left = False
                    going_right = False
                    for i in range(1, CUP_HEIGHT):
                        if not checkPos(cup, fallingFig, adjY=i):
                            break
                    fallingFig['y'] += i - 1
        
        # Удержание клавиш
        # Автоматическое движение влево/вправо при зажатой клавише
        if (going_left or going_right) and time.time() - last_side_move > SIDE_FREQ:
            if going_left and checkPos(cup, fallingFig, adjX=-1):
                fallingFig['x'] -= 1
            elif going_right and checkPos(cup, fallingFig, adjX=1):
                fallingFig['x'] += 1
            last_side_move = time.time()

        # Автоматическое ускоренное падение вниз
        if going_down and time.time() - last_move_down > DOWN_FREQ and checkPos(cup, fallingFig, adjY=1):
            fallingFig['y'] += 1
            last_move_down = time.time()

        # Автоматическое падение фигуры
        if time.time() - last_fall > fall_speed:            
            if not checkPos(cup, fallingFig, adjY=1):
                addToCup(cup, fallingFig)
                add_points, lines_cleared = clearCompleted(cup)
                points += add_points
                total_lines_cleared += lines_cleared
                level, fall_speed = calcSpeed(total_lines_cleared)
                fallingFig = None
            else:
                fallingFig['y'] += 1
                last_fall = time.time()

        # Отрисовка игрового состояния
        display_surf.fill(BG_COLOR)
        drawTitle()
        gamecup(cup)
        drawInfo(points, level)
        drawnextFig(nextFig)
        if fallingFig is not None:
            drawGhost(cup, fallingFig)   # Отрисовка "призрака" фигуры
            drawFig(fallingFig)   # Отрисовка текущей фигуры
        pg.display.update()
        fps_clock.tick(FPS)

# Отрисовка "призрака" - места, куда упадет фигура
def drawGhost(cup, fig):
    ghost_fig = {
        'shape': fig['shape'], 
        'rotation': fig['rotation'],
        'x': fig['x'],
        'y': fig['y'],
        'color': fig['shape']
    }
    
    # Определение конечной позиции "призрака"
    while checkPos(cup, ghost_fig, adjY=1):
        ghost_fig['y'] += 1
    
    # Отрисовка полупрозрачного "призрака"
    figToDraw = FIGURES[ghost_fig['shape']][ghost_fig['rotation']]
    pixelx, pixely = convertCoords(ghost_fig['x'], ghost_fig['y'])
    
    for x in range(FIG_W):
        for y in range(FIG_H):
            if figToDraw[y][x] != EMPTY:
                ghost_rect = pg.Rect(pixelx + (x * BLOCK_SIZE) + 1, pixely + (y * BLOCK_SIZE) + 1, 
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1)
                ghost_surface = pg.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1), pg.SRCALPHA)
                ghost_surface.fill(GHOST_COLORS[ghost_fig['color']])
                display_surf.blit(ghost_surface, ghost_rect)
                pg.draw.rect(display_surf, GHOST_COLORS[ghost_fig['color']], ghost_rect, 1, 3)

# Создает поверхность с текстом и возвращает ее
def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

# Корректно завершает игру
def stopGame():
    pg.quit()
    sys.exit()

# Проверяет нажатия клавиш для продолжения
def checkKeys():
    quitGame()
    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None

# Отображает текст на экране
def showText(text):
    if text == 'TETRIS':
        special_font = pg.font.Font(FONT_PATH_MARIO, 80)
        text_color = (176, 196, 222)
        outline_color = (148, 0, 211)
        outline_size = 4
    else:
        special_font = pg.font.Font(FONT_PATH, 60)
        if text == 'Игра закончена':
            text_color = (230, 230, 250)
            outline_color = (75, 0, 130)
            outline_size = 3
        elif text == 'Пауза':
            text_color = (230, 230, 250)
            outline_color = (75, 0, 130)
            outline_size = 3
        else:
            text_color = TITLE_COLOR
            outline_color = (0, 0, 0)
            outline_size = 2

    # Создание текстовой поверхности
    titleSurf = special_font.render(text, True, text_color)
    titleRect = titleSurf.get_rect()
    titleRect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2))

    # Отрисовка обводки текста
    for dx in [-outline_size, 0, outline_size]:
        for dy in [-outline_size, 0, outline_size]:
            if dx != 0 or dy != 0:
                outline_surf = special_font.render(text, True, outline_color)
                outline_rect = outline_surf.get_rect()
                outline_rect.center = (titleRect.centerx + dx, titleRect.centery + dy)
                display_surf.blit(outline_surf, outline_rect)

    # Отрисовка основного текста
    display_surf.blit(titleSurf, titleRect)

    # Добавление подсказки для продолжения (кроме экрана конца игры)
    if text != 'Игра закончена':
        pressKeySurf, pressKeyRect = txtObjects(
            'Нажмите любую клавишу для продолжения', font_for_hint, (245, 245, 245))
        pressKeyRect.center = (int(WINDOW_WIDTH / 2), int(WINDOW_HEIGHT / 2) + 100)
        display_surf.blit(pressKeySurf, pressKeyRect)

    # Ожидание нажатия клавиши
    while checkKeys() is None:
        pg.display.update()
        fps_clock.tick()

# Обрабатывает выход из игры
def quitGame():
    for event in pg.event.get(QUIT):
        stopGame() 
    for event in pg.event.get(KEYUP): 
        if event.key == K_ESCAPE:
            stopGame() 
        pg.event.post(event) 

# Вычисляет текущий уровень и скорость падения
def calcSpeed(total_lines_cleared):
    level = int(total_lines_cleared / 10) + 1
    fall_speed = max(0.05, 0.27 - (level * 0.02))
    return level, fall_speed

# Создает новую случайную фигуру
def getNewFig():
    shape = random.choice(list(FIGURES.keys()))
    return {
        'shape': shape,
        'rotation': random.randint(0, len(FIGURES[shape]) - 1),
        'x': int(CUP_WIDTH / 2) - int(FIG_W / 2),
        'y': -2, 
        'color': shape
    }

# Добавляет фигуру в стакан после падения
def addToCup(cup, fig):
    for x in range(FIG_W):
        for y in range(FIG_H):
            if FIGURES[fig['shape']][fig['rotation']][y][x] != EMPTY:
                cup[x + fig['x']][y + fig['y']] = fig['shape']

# Создает пустой стакан
def emptycup():
    return [[EMPTY] * CUP_HEIGHT for _ in range(CUP_WIDTH)]

# Проверяет, находится ли позиция в пределах стакана
def incup(x, y):
    return 0 <= x < CUP_WIDTH and y < CUP_HEIGHT

# Проверяет, находится ли фигура в границах стакана, не сталкиваясь с другими фигурами
def checkPos(cup, fig, adjX=0, adjY=0):
    for x in range(FIG_W):
        for y in range(FIG_H):
            abovecup = y + fig['y'] + adjY < 0
            if abovecup or FIGURES[fig['shape']][fig['rotation']][y][x] == EMPTY:
                continue
            if not incup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != EMPTY:
                return False
    return True

# Проверяем наличие полностью заполненных рядов
def isCompleted(cup, y):
    return all(cup[x][y] != EMPTY for x in range(CUP_WIDTH))

# Анимация мигания заполненных линий перед удалением
def flashLines(cup, lines, flashes=4, delay=0.1):
    for i in range(flashes):
        color_on = (i % 2 == 0)   # Чередование цветов
        for y in lines:
            for x in range(CUP_WIDTH):
                pixelx, pixely = convertCoords(x, y)
                if color_on:
                    color = COLORS[cup[x][y]]
                    pg.draw.rect(display_surf, color, (pixelx + 1, pixely + 1, BLOCK_SIZE - 1, BLOCK_SIZE - 1), 0, 3)
                    pg.draw.rect(display_surf, LIGHT_COLORS[cup[x][y]], (pixelx + 1, pixely + 1, BLOCK_SIZE - 4, BLOCK_SIZE - 4), 0, 3)
                    pg.draw.circle(display_surf, color, (pixelx + BLOCK_SIZE // 2, pixely + BLOCK_SIZE // 2), 5)
                else:
                    pg.draw.rect(display_surf, BG_COLOR, (pixelx, pixely, BLOCK_SIZE, BLOCK_SIZE))
        pg.display.update()
        time.sleep(delay)

# Очищает заполненные линии и возвращает очки
def clearCompleted(cup):
    removed_lines = []
    y = CUP_HEIGHT - 1
    # Поиск заполненных линий снизу вверх
    while y >= 0:
        if isCompleted(cup, y):
            removed_lines.append(y)
        y -= 1

    # Анимация мигания, если есть линии для удаления
    if removed_lines:
        flashLines(cup, removed_lines)

    # Удаление линий и сдвиг верхних рядов вниз
    for y in sorted(removed_lines):
        for pull_down_y in range(y, 0, -1):
            for x in range(CUP_WIDTH):
                cup[x][pull_down_y] = cup[x][pull_down_y - 1]
        for x in range(CUP_WIDTH):
            cup[x][0] = EMPTY

    # Начисление очков в зависимости от количества удаленных линий
    points = {1: 100, 2: 300, 3: 700, 4: 1500}.get(len(removed_lines), 0)
    return points, len(removed_lines)

# Преобразует координаты блоков в пиксельные координаты
def convertCoords(block_x, block_y):
    return (SIDE_MARGIN + (block_x * BLOCK_SIZE)), (TOP_MARGIN + (block_y * BLOCK_SIZE))

# Отрисовка квадратных блоков, из которых состоят фигуры
def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    if color == EMPTY:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf, COLORS[color], (pixelx + 1, pixely + 1, BLOCK_SIZE - 1, BLOCK_SIZE - 1), 0, 3)
    pg.draw.rect(display_surf, LIGHT_COLORS[color], (pixelx + 1, pixely + 1, BLOCK_SIZE - 4, BLOCK_SIZE - 4), 0, 3)
    pg.draw.circle(display_surf, COLORS[color], (pixelx + BLOCK_SIZE / 2, pixely + BLOCK_SIZE / 2), 5)
    
# Отрисовывает стакан с границами
def gamecup(cup):
    # Границы игрового поля-стакана
    pg.draw.rect(display_surf, BRD_COLOR, 
                (SIDE_MARGIN - 4, TOP_MARGIN - 4, 
                 (CUP_WIDTH * BLOCK_SIZE) + 8, (CUP_HEIGHT * BLOCK_SIZE) + 8), 5)
    # Фон игрового поля
    pg.draw.rect(display_surf, BG_COLOR, 
                (SIDE_MARGIN, TOP_MARGIN, 
                 BLOCK_SIZE * CUP_WIDTH, BLOCK_SIZE * CUP_HEIGHT))
    # Отрисовка всех блоков в стакане
    for x in range(CUP_WIDTH):
        for y in range(CUP_HEIGHT):
            drawBlock(x, y, cup[x][y])

# Отрисовывает заголовок игры с обводкой
def drawTitle():
    title_surf = big_font.render('TETRIS', True, WHITE)
    title_rect = title_surf.get_rect()
    title_rect.midtop = (WINDOW_WIDTH // 2, 20)
    
    # Отрисовка обводки
    for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
        outline_surf = big_font.render('TETRIS', True, BLACK)
        display_surf.blit(outline_surf, (title_rect.x + dx, title_rect.y + dy))
    
    display_surf.blit(title_surf, title_rect)

# Отрисовывает информацию
def drawInfo(points, level):
    left_margin = 30
    info_start_y = 180
    
    score_text = f'БАЛЛЫ: {points}'
    score_surf = basic_font.render(score_text, True, WHITE)
    display_surf.blit(score_surf, (left_margin, info_start_y))
    
    level_text = f'УРОВЕНЬ: {level}'
    level_surf = basic_font.render(level_text, True, WHITE)
    display_surf.blit(level_surf, (left_margin, info_start_y + 40))
    
    pause_text = 'ПАУЗА: ПРОБЕЛ'
    pause_surf = control_font.render(pause_text, True, (245, 245, 245))
    display_surf.blit(pause_surf, (left_margin, WINDOW_HEIGHT - 100))
    
    exit_text = 'ВЫХОД: ESC'
    exit_surf = control_font.render(exit_text, True, (245, 245, 245))
    display_surf.blit(exit_surf, (left_margin, WINDOW_HEIGHT - 70))

# Отрисовывает текущую фигуру
def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = FIGURES[fig['shape']][fig['rotation']]
    if pixelx is None and pixely is None:    
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    # Отрисовка элементов фигур
    for x in range(FIG_W):
        for y in range(FIG_H):
            if figToDraw[y][x] != EMPTY:
                drawBlock(None, None, fig['color'], pixelx + (x * BLOCK_SIZE), pixely + (y * BLOCK_SIZE))

# Отрисовывает следующую фигуру на боковой панели
def drawnextFig(fig):
    right_margin = 20
    start_y = 180
    
    next_text = 'СЛЕДУЮЩАЯ:'
    next_surf = basic_font.render(next_text, True, WHITE)
    next_rect = next_surf.get_rect()
    next_rect.topright = (WINDOW_WIDTH - right_margin, start_y)
    display_surf.blit(next_surf, next_rect)

    # Отрисовка фигуры
    drawFig(fig, pixelx=WINDOW_WIDTH - right_margin - 120, pixely=start_y + 40)

if __name__ == '__main__':
    main()

