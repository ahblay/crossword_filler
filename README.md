# Crossword Filler with Backtracking

This project implements an algorithm for filling out an empty crossword grid from a list of words using backtracking. The implementation is adapted from the paper "Constructing Crossword Grids: Use of Heuristics vs Constraints" by Gary Meehan and Peter Gray, published in 1997. The paper can be found at http://gtoal.com/scrabble/meehan/cross.pdf.

## Features

The algorithm takes as input a CSV file containing data representing empty slots in a crossword grid, which we shall refer to as "grid strings." A Grid object is instantiated with a list of these grid strings and an empty results dictionary to be filled with the words that shall ultimately populate the grid. The algorithm selects the grid string that accommodates the fewest number of possible words (initially, this is likely to be the longest grid string) and selects 10 of those words at random. It then iterates through this selection, attempting to fill in each word in the grid. Once a word is entered into the grid, the corresponding grid string is deleted from the grid and added to the results. The algorithm then recursively steps into the function with the updated grid.

If at any point, the addition of a new word creates a string in the grid that cannot accommodate an English word, this new word is removed, and the next candidate is attempted. If all candidates fail, the algorithm steps back out to the previous word and updates that word to the next available. This process continues until the grid is filled.

As a note, this algorithm could continue until all possible word combinations have been exhausted. In its current implementation, it acts more as a depth-first search than an enumeration algorithm. However, this is entirely a consequence of the enormous search space. It currently takes my computer roughly five minutes to fill out one 11 × 11 grid.

## Usage

To use this algorithm, follow these steps:

1. Clone the repository from GitHub.
2. Run the crossword.py file with the path to your input CSV file as an argument.

For example, if your input CSV file is located in the same directory as `crossword.py`, you can run the following command:

`python crossword.py input.csv`

## Conclusion

This project implements an algorithm for filling out a crossword grid using backtracking. It is adapted from the paper by Meehan and Gray and can fill out grids of various sizes. The implementation is quite slow due to the large search space, but it works effectively.
