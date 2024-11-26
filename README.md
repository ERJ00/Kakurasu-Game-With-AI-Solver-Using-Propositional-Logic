# Kakurasu Game With AI Solver Using Propositional Logic

This is my project for our AI subject, showcasing the use of depth-first search and breadth-first search to solve a dynamic grid-based puzzle. A Python-based puzzle game built using Pygame, where players solve a grid by strategically placing black cells. The goal is to match the sums of rows and columns with the provided clues, ensuring each solution is logical and unique.

<img src="UI/image 1.png" height="500">

## Features
- **Dynamic Puzzle Generation**: Grids of varying sizes (adjustable by the user) are created with randomized black cell arrangements and predefined clues.
- **Interactive Gameplay**: Toggle cells between black (`B`), cross (`X`), or empty states to solve the puzzle.
- **AI Assistance**: Option to enable AI-generated solutions for hints or automatic solving.
- **Responsive Interface**: Intuitive grid visualization with labeled rows and columns for easier gameplay.
- **Multiple Controls**: Includes buttons for checking solutions, refreshing puzzles, resetting the game, and revealing solutions.
- **Adaptive Difficulty**: Adjusts clue density based on grid size to provide an engaging challenge.

## How It Works
1. **Grid Setup**: A square grid is generated, with cells labeled to aid navigation.
2. **Clues Calculation**: Row and column sums are calculated based on randomly placed black cells.
3. **Validation**: The game ensures that black cell placements and their combinations are logically solvable.
4. **Player Interaction**: Players modify cell states to match the grid's row and column sums.
5. **Win Condition**: Solve the puzzle by correctly placing all black cells.

## Technologies Used
- **Python**: Core language for logic and game mechanics.
- **Pygame**: Framework for graphics rendering and user interaction.

## Future Enhancements
- Enhanced AI for real-time assistance.
- Additional customization options for puzzles.
- Improved UI/UX design with animations and sound effects.

## Setup and Installation
1. Clone the repository: `git clone https://github.com/your-username/black-cell-puzzle.git`
2. Install dependencies: `pip install pygame`
3. Run the game: `python main.py`

Enjoy the challenge of solving the Black Cell Puzzle Game!
