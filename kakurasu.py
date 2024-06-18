import threading
import pygame
import random
from itertools import combinations

pygame.init()

AI_ENABLED = False
CELL_SIZE = 50
CELL_NUMBER = 6
RIGHT_SIDE_SCREEN_TAB = 200
SCREEN_WIDTH = ((CELL_SIZE * CELL_NUMBER) + RIGHT_SIDE_SCREEN_TAB)
SCREEN_HEIGHT = (CELL_SIZE * CELL_NUMBER)
SCREEN_WIDTH_WITHOUT_SIDE_TAB = SCREEN_WIDTH - RIGHT_SIDE_SCREEN_TAB

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kakurasu Puzzle Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)

# Game state data
game_state = {
    "cell_size": CELL_SIZE,
    "cell_number": CELL_NUMBER,
    "problem_cells": {},  # Problem state
    "player_cells": {},  # Player state
    "AI_cells": {},  # AI state
    "row_sums": [],
    "col_sums": []
}

# Gloval variables
AI_can_solve = False
AI_result = False
previous_states = []
TOTAL_CLUES = 0
CLUES_NUMBER = 0
REVEAL_ENABLED = False
AI_ENABLED = False
TEMP = []
show_popup = False
popup_button = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 160, 50)
run = True
popup_text = None
is_win = False
AI_SPEED = 10
PERCENTAGE = 0.0

# Display Game Screen
gameScreen = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

background_image = pygame.image.load('images/game_screen.png')
background_image = pygame.transform.scale(background_image, (gameScreen.width, gameScreen.height))
screen.blit(background_image, gameScreen.topleft)
pygame.display.update()
print(f"height: {SCREEN_HEIGHT} width: {SCREEN_WIDTH}")
pygame.time.delay(3000)
screen.fill(GOLD)
pygame.display.update()

# ------------------------------------------------------------------------------------------------
# AI Bot Functions

# Check Ai solution
def check_AI_solution():
    global AI_ENABLED  
    global AI_can_solve
    AI_can_solve = False
    
    for cell, value in game_state["problem_cells"].items():
        if AI_ENABLED:
            if value == 'B' and game_state["player_cells"].get(cell) != 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
            if value != 'B' and game_state["player_cells"].get(cell) == 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
        else:
            if value == 'B' and game_state["AI_cells"].get(cell) != 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
            if value != 'B' and game_state["AI_cells"].get(cell) == 'B':
                # print("Ai can not solve the game")
                AI_can_solve = False
                return False
    AI_ENABLED = False
    AI_can_solve = True
    # print("Ai can solve the game")
    return True

# Generate combinations of numbers from the limited numbers list
def find_combinations(target_sum):
    limited_numbers = range(1, CELL_NUMBER - 1)  # Limited numbers to be used
    possible_combinations = []
    for r in range(1, len(limited_numbers) + 1):
        for combination in combinations(limited_numbers, r):
            if sum(combination) == target_sum:
                possible_combinations.append(combination)
    return possible_combinations

# Remove combination that have X mark in cells
def remove_combination_with_x(combinations, index, axis):
    filtered_combinations = []
    for combination in combinations:
        if AI_ENABLED:
            if not any(game_state["player_cells"][(cell, index)] == 'X' if axis == "row" else game_state["player_cells"][(index, cell)] == 'X' for cell in combination):
                filtered_combinations.append(combination)
        else:
            if not any(game_state["AI_cells"][(cell, index)] == 'X' if axis == "row" else game_state["AI_cells"][(index, cell)] == 'X' for cell in combination):
                filtered_combinations.append(combination)
    return filtered_combinations

# Remove combination that don't have all black cells
def remove_combinations_without_all_black(combinations, black_cells, track):    
    black_combination = []
    if track == "row":
        for cell in black_cells:
            black_combination.append(cell[0])
    elif track == "column":
        for cell in black_cells:
            black_combination.append(cell[1])
            
    filtered_combinations = []
    
    if len(combinations) > 1:
        for combination in combinations:
            if all(cell in combination for cell in black_combination):  # Check if all black cells are present in combination
                filtered_combinations.append(combination)
    else:
        return combinations
    return filtered_combinations

def solve_remaining_combination(rows_combination, cols_combination):
    global game_state
    global AI_ENABLED
    global AI_result
    global previous_states
    global AI_SPEED
    
    AI_result = False
    
    while not AI_result:
        # Remove row combinations with 'X' cells
        new_rows_combination = []
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            filtered_combinations = None
            if row_sum == 0 or len(combinations) == 1:
                new_rows_combination.append((row_sum, combinations))
            else:
                filtered_combinations = remove_combination_with_x(combinations, row_index + 1, "row")
            
            if filtered_combinations:
                new_rows_combination.append((row_sum, filtered_combinations))
        rows_combination[:] = new_rows_combination

        # Remove column combinations with 'X' cells
        new_cols_combination = []
        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            filtered_combinations = None
            if col_sum == 0 or len(combinations) == 1:
                new_cols_combination.append((col_sum, combinations))
            else:
                filtered_combinations = remove_combination_with_x(combinations, col_index + 1, "col")

            if filtered_combinations:
                new_cols_combination.append((col_sum, filtered_combinations))
        cols_combination[:] = new_cols_combination

        # Remove row combinations without all black cells
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            black_cells_row = None
            if AI_ENABLED:
                black_cells_row = [cell for cell in game_state["player_cells"] if game_state["player_cells"][cell] == 'B' and cell[1] == row_index + 1]
            else:
                black_cells_row = [cell for cell in game_state["AI_cells"] if game_state["AI_cells"][cell] == 'B' and cell[1] == row_index + 1]
            
            if black_cells_row:
                if filtered_combinations and row_sum != 0 and len:
                    filtered_combinations = remove_combinations_without_all_black(combinations, black_cells_row, "row")
                    rows_combination[row_index] = (row_sum, filtered_combinations)
                else:
                    rows_combination[row_index] = (row_sum, combinations)

        # Remove column combinations without all black cells
        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            black_cells_col = None
            if AI_ENABLED:
                black_cells_col = [cell for cell in game_state["player_cells"] if game_state["player_cells"][cell] == 'B' and cell[0] == col_index + 1]
            else:
                black_cells_col = [cell for cell in game_state["AI_cells"] if game_state["AI_cells"][cell] == 'B' and cell[0] == col_index + 1]

            if black_cells_col:
                if filtered_combinations and col_sum != 0:
                    filtered_combinations = remove_combinations_without_all_black(combinations, black_cells_col, "column")
                    cols_combination[col_index] = (col_sum, filtered_combinations)
                else:
                    cols_combination[col_index] = (col_sum, combinations)

        # Check if there's only one remaining combination in a row or column
        for row_index, (row_sum, combinations) in enumerate(rows_combination):
            
            if len(combinations) == 0:
                for col in range(1, CELL_NUMBER - 1):
                    if AI_ENABLED:
                        if game_state["player_cells"][(col, row_index + 1)] == '':
                            game_state["player_cells"][(col, row_index + 1)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col, row_index + 1)] == '':
                            game_state["AI_cells"][(col, row_index + 1)] = 'X'
            
            elif len(combinations) == 1:
                for cell in combinations[0]:
                    if AI_ENABLED:
                        if game_state["player_cells"][(cell, row_index + 1)] == '':
                            game_state["player_cells"][(cell, row_index + 1)] = 'B'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(cell, row_index + 1)] == '':
                            game_state["AI_cells"][(cell, row_index + 1)] = 'B'

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if AI_ENABLED:
                            if game_state["player_cells"][(col, row_index + 1)] == '':
                                game_state["player_cells"][(col, row_index + 1)] = 'X'
                                draw_screen(game_state)
                                pygame.display.update()
                                pygame.time.delay(AI_SPEED)
                        else:
                            if game_state["AI_cells"][(col, row_index + 1)] == '':
                                game_state["AI_cells"][(col, row_index + 1)] = 'X'

        for col_index, (col_sum, combinations) in enumerate(cols_combination):
            if len(combinations) == 0:
                for row in range(1, CELL_NUMBER - 1):
                    if AI_ENABLED:
                        if game_state["player_cells"][(col_index + 1, row)] == '':
                            game_state["player_cells"][(col_index + 1, row)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col_index + 1, row)] == '':
                            game_state["AI_cells"][(col_index + 1, row)] = 'X'
            
            elif len(combinations) == 1:
                for cell in combinations[0]:
                    if AI_ENABLED:
                        if game_state["player_cells"][(col_index + 1, cell)] == '':
                            game_state["player_cells"][(col_index + 1, cell)] = 'B'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
                    else:
                        if game_state["AI_cells"][(col_index + 1, cell)] == '':
                            game_state["AI_cells"][(col_index + 1, cell)] = 'B'
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if AI_ENABLED:
                            if game_state["player_cells"][(col_index + 1, row)] == '':
                                game_state["player_cells"][(col_index + 1, row)] = 'X'
                                draw_screen(game_state)
                                pygame.display.update()
                                pygame.time.delay(AI_SPEED)
                        else:
                            if game_state["AI_cells"][(col_index + 1, row)] == '':
                                game_state["AI_cells"][(col_index + 1, row)] = 'X'

        # pygame.display.update()
        check_AI_solution()
        previous_states.append(game_state["AI_cells"])
        result = check_last_previous_states(previous_states)

        # Check previous states if same
        if result:
            previous_states = []
            AI_ENABLED = False
            AI_result = True
    return rows_combination, cols_combination

# Check previous state to see if it not changed
def check_last_previous_states(lst):
    if len(lst) < 6:
        return False
    
    # Extract the last 5 elements
    last_five = lst[-6:]
    
    # Check if all elements in last_five are the same
    return all(element == last_five[0] for element in last_five)

def ai_bot():
    global AI_ENABLED
    global AI_SPEED
    
    rows_combination = []
    cols_combination = []

    # Generate all unique combinations for each row and column
    for row_sum in game_state["row_sums"]:
        rows_combination.append((row_sum, find_combinations(row_sum)))

    for col_sum in game_state["col_sums"]:
        cols_combination.append((col_sum, find_combinations(col_sum)))
    
    # Check if only one combination is possible
    for row_index, (row_sum, combinations) in enumerate(rows_combination):
        
        # Mark all other cells in the row as 'X' if no combination have
        if len(combinations) == 0:
            for col in range(1, CELL_NUMBER - 1):
                if AI_ENABLED:
                    if game_state["player_cells"][(col, row_index + 1)] == '':
                        game_state["player_cells"][(col, row_index + 1)] = 'X'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
                else:
                    if game_state["AI_cells"][(col, row_index + 1)] == '':
                        game_state["AI_cells"][(col, row_index + 1)] = 'X'
        
        elif len(combinations) == 1:
            if AI_ENABLED:
                for cell in combinations[0]:
                    if game_state["player_cells"][(cell, row_index + 1)] == '':
                        game_state["player_cells"][(cell, row_index + 1)] = 'B'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if game_state["player_cells"][(col, row_index + 1)] == '':
                            game_state["player_cells"][(col, row_index + 1)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
            else:
                for cell in combinations[0]:
                    if game_state["AI_cells"][(cell, row_index + 1)] == '':
                        game_state["AI_cells"][(cell, row_index + 1)] = 'B'

                # Mark all other cells in the row as 'X'
                for col in range(1, CELL_NUMBER - 1):
                    if col not in combinations[0]:
                        if game_state["AI_cells"][(col, row_index + 1)] == '':
                            game_state["AI_cells"][(col, row_index + 1)] = 'X'

    for col_index, (col_sum, combinations) in enumerate(cols_combination):
        # Mark all other cells in the column as 'X' if no combination have
        if len(combinations) == 0:
            if AI_ENABLED:
                for row in range(1, CELL_NUMBER - 1):
                    if game_state["player_cells"][(col_index + 1, row)] == '':
                        game_state["player_cells"][(col_index + 1, row)] = 'X'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
            else:
                for row in range(1, CELL_NUMBER - 1):
                    if game_state["AI_cells"][(col_index + 1, row)] == '':
                        game_state["AI_cells"][(col_index + 1, row)] = 'X'
        
        elif len(combinations) == 1:
            if AI_ENABLED:
                for cell in combinations[0]:
                    if game_state["player_cells"][(col_index + 1, cell)] == '':
                        game_state["player_cells"][(col_index + 1, cell)] = 'B'
                        draw_screen(game_state)
                        pygame.display.update()
                        pygame.time.delay(AI_SPEED)
                    
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if game_state["player_cells"][(col_index + 1, row)] == '':
                            game_state["player_cells"][(col_index + 1, row)] = 'X'
                            draw_screen(game_state)
                            pygame.display.update()
                            pygame.time.delay(AI_SPEED)
            else:
                for cell in combinations[0]:
                    if game_state["AI_cells"][(col_index + 1, cell)] == '':
                        game_state["AI_cells"][(col_index + 1, cell)] = 'B'
                    
                # Mark all other cells in the column as 'X'
                for row in range(1, CELL_NUMBER - 1):
                    if row not in combinations[0]:
                        if game_state["AI_cells"][(col_index + 1, row)] == '':
                            game_state["AI_cells"][(col_index + 1, row)] = 'X'

    solve_remaining_combination(rows_combination, cols_combination)

# ------------------------------------------------------------------------------------------------

# Class for input size
class TextInput:
    def __init__(self, position, width, height):
        self.position = position
        self.width = width
        self.height = height
        self.text = ""

    def handle_event(self, event):
        global CELL_NUMBER
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 2:
                self.text += event.unicode
                if int(self.text) > 10:
                    self.text = '10'
                CELL_NUMBER = int(self.text) + 2
        if len(self.text) == 0 or int(self.text) < 4 or self.text == "":
            CELL_NUMBER = 6

    def render(self, surface):
        input_image = pygame.image.load("images/input.png")
        input_image = pygame.transform.scale(input_image, (self.width, self.height))
        surface.blit(input_image, self.position)

        font = pygame.font.Font(None, 35)
        text_surface = font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.position[0] + 70, self.position[1] + 5))

def check_last_previous_rows_states(lst):
    if len(lst) < 5:
        return False
    
    # Extract the last 5 elements
    last_five = lst[-5:]
    
    # Check if all elements in last_five are the same
    return all(element == last_five[0] for element in last_five)

# Initialize all cells to empty state
def initialize_game_state(state):
    global AI_result
    global AI_can_solve
    global TOTAL_CLUES
    global CELL_NUMBER
    global PERCENTAGE
    
    state["problem_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    state["player_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    state["AI_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    
    # Generate problem cells, Difficulty Level: Very hard
    # for j in range(1, state["cell_number"] - 1):
    #     num_black_cells = random.randint(1, state["cell_number"] - 2)
    
    #     selected_cells = random.sample(range(1, state["cell_number"] - 1), num_black_cells)
    
    #     for i in selected_cells:
    #         state["problem_cells"][(i, j)] = 'B'
    # # Calculate sums
    # state["row_sums"] = [sum(i for (i, j), v in state["problem_cells"].items() if v == 'B' and j == y) for y in range(1, state["cell_number"] - 1)]
    # state["col_sums"] = [sum(j for (i, j), v in state["problem_cells"].items() if v == 'B' and i == x) for x in range(1, state["cell_number"] - 1)]


    # Generate random problem cells that can solve the AI
    generate_problem_cells(state)
    print('-'*30)
    num = 0
    previous_row_state = []
    while not AI_can_solve:
        num += 1
        if AI_result:
            AI_result = False
        print(f'Generating attempt {num}')
        while TOTAL_CLUES != round((state['cell_number'] - 2) * PERCENTAGE) or check_last_previous_rows_states(previous_row_state):
            generate_problem_cells(state)
            AI_result = False
        previous_row_state.append(state['row_sums'])
        ai_bot()
        state["AI_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
        TOTAL_CLUES = 0
    previous_row_state = []

# Generate problem cells
def generate_problem_cells(state):
    global TOTAL_CLUES
    global CLUES_NUMBER
    global PERCENTAGE
    
    if CELL_NUMBER <= 7:
        PERCENTAGE = 0.3
    elif CELL_NUMBER == 10:
        PERCENTAGE = 0.45
    elif CELL_NUMBER == 11:
        PERCENTAGE = 0.459
    elif CELL_NUMBER > 11:
        PERCENTAGE = 0.6

    TOTAL_CLUES = round(((state["cell_number"] - 2) * PERCENTAGE))
    remaining_cells_without_black_cells = (state["cell_number"] - 2)
    selected_cells = None
    num_black_cells = 0
    CLUES_NUMBER = 0
    current_total_clues = TOTAL_CLUES
    check_clues = 0
    
    state["problem_cells"] = {(i, j): '' for i in range(1, state["cell_number"] - 1) for j in range(1, state["cell_number"] - 1)}
    
    print("="*30)
    print(f"Total Clues: {current_total_clues}")
    print(f"Number of clues: {CLUES_NUMBER}")
    
    values = [0, 1, state["cell_number"] - 2]
    
    for j in range(1, state["cell_number"] - 1):
        # Rand choose if the row is to have a single black cell
        rand = random.randint(1, 2)

        if rand == 2 and current_total_clues > 0: # row will have a single black
            current_total_clues -= 1
            num_black_cells = random.choice(values)
            CLUES_NUMBER += 1
        else:
            num_black_cells = random.randint(1, state["cell_number"] - 2)
            while num_black_cells == 1 or num_black_cells == 0 or num_black_cells == state["cell_number"] - 2:
                num_black_cells = random.randint(1, state["cell_number"] - 2)
        
        remaining_cells_without_black_cells -= 1
        
        if current_total_clues == remaining_cells_without_black_cells and current_total_clues !=0:
        
            current_total_clues -= 1
            # remaining_cells_without_black_cells -= 1
            num_black_cells = random.choice(values)
            CLUES_NUMBER += 1
        
        if num_black_cells == 1 or num_black_cells == 0 or num_black_cells == state["cell_number"] - 2:
            check_clues += 1 

        selected_cells = random.sample(range(1, state["cell_number"] - 1), num_black_cells)
        
        # Make sure the single black cell have single digit combination
        if num_black_cells == 1:
            while check_total_combinations(sum(selected_cells)) > 1:
                selected_cells = random.sample(range(1, state["cell_number"] - 1), num_black_cells)
            print(f"Combinations: {selected_cells}, {check_total_combinations(sum(selected_cells))}, {current_total_clues}, {remaining_cells_without_black_cells}")

        print(f'selected cells: {selected_cells}')
        print("-"*30)
        for i in selected_cells:
            state["problem_cells"][(i, j)] = 'B'
    print(f"Total Clues: {current_total_clues}")
    print(f"Number of clues: {CLUES_NUMBER}")
    print(f"current clues: {check_clues}")
    
    # Calculate sums
    state["row_sums"] = [sum(i for (i, j), v in state["problem_cells"].items() if v == 'B' and j == y) for y in range(1, state["cell_number"] - 1)]
    state["col_sums"] = [sum(j for (i, j), v in state["problem_cells"].items() if v == 'B' and i == x) for x in range(1, state["cell_number"] - 1)]

    print(f'row sum: {state["row_sums"]}')
    print(f'col sum: {state["col_sums"]}')

# Check sum if have a single combination
def check_total_combinations(target_sum):
    possible_combinations = []
    limited_numbers = range(1, CELL_NUMBER -1)
    for r in range(1, len(limited_numbers) + 1):
        for combination in combinations(limited_numbers, r):
            if sum(combination) == target_sum:
                possible_combinations.append(combination)

    return len(possible_combinations)

# Initialize the game state and buttons 
initialize_game_state(game_state)

check_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 10, 160, 30)
refresh_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 60, 160, 30)
reset_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 110, 160, 30)
text_input = TextInput((SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 160), 160, 30)
AI_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 210, 160, 30)
reveal_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 260, 160, 30)

def reset_game_state():
    # Reset the game state
    global game_state
    global check_button_rect
    global refresh_button_rect
    global reset_button_rect
    global text_input
    global AI_button_rect
    global reveal_button_rect
    global SCREEN_HEIGHT
    global SCREEN_WIDTH
    global SCREEN_WIDTH_WITHOUT_SIDE_TAB
    global screen
    global AI_ENABLED
    global REVEAL_ENABLED
    global is_win
    global AI_result
    global AI_can_solve
    global TOTAL_CLUES
    global CLUES_NUMBER
    global previous_states
    global TEMP
    global show_popup
    global popup_text
    
    TOTAL_CLUES = 0
    CLUES_NUMBER = 0
    AI_can_solve = False
    AI_result = False
    is_win = False
    AI_ENABLED = False
    REVEAL_ENABLED = False
    previous_states = []
    TEMP = []
    show_popup = False
    popup_text = None
    
    SCREEN_WIDTH = ((CELL_SIZE * CELL_NUMBER) + RIGHT_SIDE_SCREEN_TAB)
    SCREEN_HEIGHT = (CELL_SIZE * CELL_NUMBER)
    SCREEN_WIDTH_WITHOUT_SIDE_TAB = SCREEN_WIDTH - RIGHT_SIDE_SCREEN_TAB
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    game_state = {
        "cell_size": CELL_SIZE,
        "cell_number": CELL_NUMBER,
        "problem_cells": {},  # Problem state
        "player_cells": {},  # Player state
        "AI_cells": {},  # AI state
        "row_sums": [],
        "col_sums": []
    }
    initialize_game_state(game_state)
    draw_screen(game_state)
    check_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 10, 160, 30)
    refresh_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 60, 160, 30)
    reset_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 110, 160, 30)
    text_input = TextInput((SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 160), 160, 30)
    AI_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 210, 160, 30)
    reveal_button_rect = pygame.Rect(SCREEN_WIDTH_WITHOUT_SIDE_TAB + 20, 260, 160, 30)
    # pygame.display.update()

# Function for cell click event
def toggle_cell_state(state, cell):
    if state["player_cells"][cell] == '':
        state["player_cells"][cell] = 'B'
    elif state["player_cells"][cell] == 'B':
        state["player_cells"][cell] = 'X'
    else:
        state["player_cells"][cell] = ''

def draw_screen(state):
    screen.fill(GOLD)
    for i in range(1, state["cell_number"]):
        for j in range(1, state["cell_number"]):
            cell_state = state["player_cells"].get((i, j), None)  
            if cell_state is not None:
                if cell_state == 'B':
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
                    pygame.draw.rect(screen, BLACK, ((i * state["cell_size"] + 5), (j * state["cell_size"] + 5), state["cell_size"] - 10, state["cell_size"] - 10))
                elif cell_state == 'X':
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
                    font = pygame.font.Font(None, 36)
                    text = font.render('X', True, RED)
                    screen.blit(text, (i * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, j * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))
                else:
                    pygame.draw.rect(screen, WHITE, (i * state["cell_size"], j * state["cell_size"], state["cell_size"], state["cell_size"]))
    
    draw_gridline(state)
    draw_check_button()
    draw_refresh_button()
    draw_reset_button()
    draw_ai_button()
    draw_text()
    draw_reveal_button()
    text_input.render(screen)

# Draw grid lines and sums
def draw_gridline(state):
    for x in range(0, SCREEN_WIDTH_WITHOUT_SIDE_TAB, state["cell_size"]):
        if x > 0:
            pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, state["cell_size"]):
        if y > 0:
            pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH_WITHOUT_SIDE_TAB, y))

    # Draw border line
    pygame.draw.rect(screen, WHITE, (state["cell_size"], state["cell_size"], (SCREEN_WIDTH_WITHOUT_SIDE_TAB - (state["cell_size"] * 2)), (SCREEN_HEIGHT - (state["cell_size"] * 2))), width=5)

    # Draw row sums
    for j, sum_row in enumerate(state["row_sums"]):
        font = pygame.font.Font(None, 24)
        text = font.render(str(sum_row), True, BLACK)
        screen.blit(text, ((state["cell_number"] - 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, (j + 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw column sums
    for i, sum_col in enumerate(state["col_sums"]):
        font = pygame.font.Font(None, 24)
        text = font.render(str(sum_col), True, BLACK)
        screen.blit(text, ((i + 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, (state["cell_number"] - 1) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw row numbering on the left side outside of the grid
    for j in range(state["cell_number"]):
        if j > 0 and j < (state["cell_number"] - 1):
            font = pygame.font.Font(None, 36)
            text = font.render(str(j), True, BLACK)
            screen.blit(text, (5, (j) * state["cell_size"] + state["cell_size"] // 2 - text.get_height() // 2))

    # Draw column numbering above the grid outside of the grid
    for i in range(state["cell_number"]):
        if i > 0 and i < (state["cell_number"] - 1):
            font = pygame.font.Font(None, 36)
            text = font.render(str(i), True, BLACK)
            screen.blit(text, ((i) * state["cell_size"] + state["cell_size"] // 2 - text.get_width() // 2, 5))

def draw_text():
    global CLUES_NUMBER
    font = pygame.font.Font('freesansbold.ttf', 15)
    # total clue text
    # total_clue_text = font.render(f'{CLUES_NUMBER}', True, BLACK)
    # clue_textRect = total_clue_text.get_rect()
    # clue_textRect.center = (10, 10)
    # screen.blit(total_clue_text, clue_textRect)

    # label for size input
    size_label = font.render(f'Input Size: ', True, BLACK)
    screen.blit(size_label, (reset_button_rect.x, reset_button_rect.y + 35))
    
    size_label = font.render(f'( Size: {CELL_NUMBER - 2}x{CELL_NUMBER - 2} )', True, BLACK)
    screen.blit(size_label, (reset_button_rect.x, reset_button_rect.y + 85))

# Draw Check button
def draw_check_button():
    # Load and scale the button image
    check_button_image = pygame.image.load("images/check.png")
    check_button_image = pygame.transform.scale(check_button_image, (check_button_rect.width, check_button_rect.height))
    # Draw the button image
    screen.blit(check_button_image, check_button_rect.topleft)

# Draw Refresh button
def draw_refresh_button():
    # Load and scale the button image
    newGame_button_image = pygame.image.load("images/new_game.png")
    newGame_button_image = pygame.transform.scale(newGame_button_image, (refresh_button_rect.width, refresh_button_rect.height))
    # Draw the button image
    screen.blit(newGame_button_image, refresh_button_rect.topleft)

# Draw Reset button
def draw_reset_button():
    # Load and scale the button image
    reset_button_image = pygame.image.load("images/reset.png")
    reset_button_image = pygame.transform.scale(reset_button_image, (reset_button_rect.width, reset_button_rect.height))
    # Draw the button image
    screen.blit(reset_button_image, reset_button_rect.topleft)

# Draw reveal button
def draw_reveal_button():
    # Load and scale the button image
    revealOn_button_image = pygame.image.load("images/revealOn.png")
    revealOff_button_image = pygame.image.load("images/revealOff.png")
    revealOn_button_image = pygame.transform.scale(revealOn_button_image, (reveal_button_rect.width, reveal_button_rect.height))
    revealOff_button_image = pygame.transform.scale(revealOff_button_image, (reveal_button_rect.width, reveal_button_rect.height))

    if REVEAL_ENABLED:
        screen.blit(revealOn_button_image, reveal_button_rect.topleft)
    else:
        screen.blit(revealOff_button_image, reveal_button_rect.topleft)

# Draw AI button
def draw_ai_button():
    # Load and scale the button image
    aiBotOn_button_image = pygame.image.load("images/aiBotOn.png")
    aiBotOff_button_image = pygame.image.load("images/aiBotOff.png")
    aiBotOn_button_image = pygame.transform.scale(aiBotOn_button_image, (AI_button_rect.width, AI_button_rect.height))
    aiBotOff_button_image = pygame.transform.scale(aiBotOff_button_image, (AI_button_rect.width, AI_button_rect.height))

    if AI_ENABLED:
        screen.blit(aiBotOn_button_image, AI_button_rect.topleft)
    else:
        screen.blit(aiBotOff_button_image, AI_button_rect.topleft)

def handle_click(state, pos):
    if not REVEAL_ENABLED:
        x, y = pos
        if x < state["cell_size"] or y < state["cell_size"] or x >= SCREEN_WIDTH_WITHOUT_SIDE_TAB - state["cell_size"] or y >= SCREEN_HEIGHT - state["cell_size"]:
            return
        i = x // state["cell_size"]
        j = y // state["cell_size"]
        if (i, j) in state["player_cells"]:
            toggle_cell_state(state, (i, j))

def handle_refresh_click():
    reset_game_state()

def handle_reset_click():
    global AI_ENABLED
    global REVEAL_ENABLED
    AI_ENABLED = False
    REVEAL_ENABLED = False
    print(game_state["player_cells"])
    for key in game_state["player_cells"]:
        game_state["player_cells"][key] = ''

def handle_ai_button_click():
    if AI_ENABLED:
        draw_ai_button()
        # pygame.display.update()
        ai_bot()
    else:
        draw_ai_button()
        # pygame.display.update()

def handle_reveal_button_click():
    global TEMP
    if REVEAL_ENABLED:
        TEMP = game_state["player_cells"]
        game_state["player_cells"] = game_state["problem_cells"]
    else:
        game_state["player_cells"] = TEMP
    # draw_screen()
    # pygame.display.update()

def check_solution():
    global AI_ENABLED  
    for cell, value in game_state["problem_cells"].items():
        if value == 'B' and game_state["player_cells"].get(cell) != 'B':
            return False
        if value != 'B' and game_state["player_cells"].get(cell) == 'B':
            return False
    AI_ENABLED = False
    return True

def show_popup_display(message):
    global show_popup
    global run
    color = None
    if show_popup:
        # Background
        background_rect = pygame.Rect(0, 0, 400, 200)
        background_image = pygame.image.load('images/popupBG.png')
        background_image = pygame.transform.scale(background_image, (background_rect.width, background_rect.height))
        background_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        screen.blit(background_image, background_rect.topleft)

        # Text display
        popup_text1_image = pygame.image.load('images/popup_text1.png')
        popup_text2_image = pygame.image.load('images/popup_text2.png')
        popup_text3_image = pygame.image.load('images/popup_text3.png')
        
        popup_text1_image = pygame.transform.scale(popup_text1_image, (background_rect.width, background_rect.height))
        popup_text2_image = pygame.transform.scale(popup_text2_image, (background_rect.width, background_rect.height))
        popup_text3_image = pygame.transform.scale(popup_text3_image, (background_rect.width, background_rect.height))

        if message == 'text1':
            screen.blit(popup_text1_image, background_rect.topleft)
        elif message == 'text2':
            screen.blit(popup_text2_image, background_rect.topleft)
        elif message == 'text3':
            screen.blit(popup_text3_image, background_rect.topleft)

        # Button
        popup_button_width = 160
        popup_button_height = 50
        popup_button_x = (SCREEN_WIDTH - popup_button_width) // 2
        popup_button_y = ((SCREEN_HEIGHT - popup_button_height) // 2) + 60
        popup_button_rect = pygame.Rect(popup_button_x, popup_button_y, popup_button_width, popup_button_height)

        popup_button1_image = pygame.image.load('images/popup_button1.png')
        popup_button2_image = pygame.image.load('images/popup_button2.png')

        popup_button1_image = pygame.transform.scale(popup_button1_image, (popup_button_rect.width, popup_button_rect.height))
        popup_button2_image = pygame.transform.scale(popup_button2_image, (popup_button_rect.width, popup_button_rect.height))

        if is_win:
            screen.blit(popup_button1_image, popup_button_rect.topleft)
        else:
            screen.blit(popup_button2_image, popup_button_rect.topleft)

        # pygame.display.update()

        # Handle click event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if popup_button_rect.collidepoint(event.pos):
                        if is_win:
                            reset_game_state()
                            show_popup = False
                        else:
                            show_popup = False

def threaded_handle_refresh_click():
    refresh_thread = threading.Thread(target=handle_refresh_click())
    refresh_thread.start()
    # refresh_thread.join()

# Initialize the check button before the event loop
draw_screen(game_state)
pygame.display.update()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if check_button_rect and check_button_rect.collidepoint(event.pos):
                # print('Problem State: ', game_state["problem_cells"])
                # print('Player State: ', game_state["player_cells"])
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                elif check_solution():
                    print("You Win!")
                    show_popup = True
                    is_win = True
                    popup_text = "text1"
                else:
                    show_popup = True
                    print("Incorrect, keep trying!")
                    popup_text = "text2"
            else:
                handle_click(game_state, event.pos)
                
            # Handle click on the refresh button
            if refresh_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    threaded_handle_refresh_click()
            
            # Handle click on the reset button
            if reset_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    handle_reset_click()
            
            # Handle click on the AI button
            if AI_button_rect.collidepoint(event.pos):
                if REVEAL_ENABLED:
                    show_popup = True
                    popup_text = "text3"
                else:
                    AI_ENABLED = not AI_ENABLED
                    game_state["player_cells"] = {(i, j): '' for i in range(1, game_state["cell_number"] - 1) for j in range(1, game_state["cell_number"] - 1)}
            
            # Handle click on the Reveal button
            if reveal_button_rect.collidepoint(event.pos):
                REVEAL_ENABLED = not REVEAL_ENABLED
                handle_reveal_button_click()

        elif event.type == pygame.KEYDOWN:
            # Handle keyboard events for text input
            text_input.handle_event(event)

    # Draw the screen only once per iteration
    draw_screen(game_state)

    if AI_ENABLED:
        handle_ai_button_click()

    if show_popup:
        show_popup_display(popup_text)
    pygame.display.update()

pygame.quit()
