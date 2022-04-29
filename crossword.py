import pickle
from pprint import pprint as pp
import csv
import random
import math
import copy


# prints a formatted crossword grid, with un-entered letters indicated by dashes
def print_grid(grid):
    for s in grid:
        thing = {k: v for k, v in s.__dict__.items() if k != 'matches'}
        print(thing)


# saves data to a pickle file
def to_pkl(filename, d):
    with open(f'{filename}.pkl', 'wb') as f:
        pickle.dump(d, f)


# reads in data from a pickle file
def from_pkl(filename):
    with open(f'{filename}.pkl', 'rb') as f:
        d = pickle.load(f)
    return d


# creates a dictionary of words from a word list, where words are arranged by length
# outputs file words.pkl, which is a dictionary with lengths as keys, and words as values
def format_wordlist(filename):
    dictionary = {}
    with open(f'{filename}.txt', 'r+') as f:
        for word in f:
            word = word.rstrip()
            print(word)
            try:
                dictionary[len(word)].append(word)
            except KeyError:
                dictionary[len(word)] = [word]
        to_pkl("words", dictionary)
    return


# a class for each empty word slot in the crossword grid
# empty slots are referred to as "grid strings"
class GridString:

    # initialize class variables
    def __init__(self, start_x, start_y, direction, length):

        # starting coordinates of grid string
        self.start_x = start_x
        self.start_y = start_y

        # direction: either down or across
        self.direction = direction

        # length of grid string
        self.length = length

        # current word (or letters) in grid string slot
        # initialized to dashes
        self.word = '-' * self.length

        # words that could fit
        self.matches = from_pkl('words')[self.length]

        # a function to determine the amount of available words that can fit in the current slot
        # function adapted from http://gtoal.com/scrabble/meehan/cross.pdf
        self.freedom = self.most_constrained()

    # a function to check if a word could fit in a grid string slot
    # this function is very slow
    @staticmethod
    def check_match(candidate, word):
        for index, val in enumerate(candidate):
            if val != '-':
                if word[index] != val:
                    return False
        return True

    # calculates the number of words that match a grid string slot
    def most_constrained(self):
        self.matches = from_pkl('words')[self.length]
        if self.word == '-' * self.length:
            freedom = len(self.matches)
        else:
            new_matches = []
            for w in self.matches:
                # TODO: This is a MASSIVELY slow function.
                if self.check_match(self.word, w):
                    new_matches.append(w)
            self.matches = new_matches
            freedom = len(self.matches)
        return freedom

    # selects a random set of 10 words that match a particular grid string configuration
    # 10 is arbitrary and was recommended in http://gtoal.com/scrabble/meehan/cross.pdf
    def pick_matches(self):
        choice = min(10, len(self.matches))
        m = random.sample(self.matches, choice)
        return m


# a class representing the overall crossword grid
class Grid:

    # initializes class variables
    def __init__(self, filename, size):

        # loads in grid configuration from .csv file
        # constructs GridString objects for all grid strings in grid
        self.grid = self.construct_grid(self.load_data(filename))

        # width and height of grid
        self.size = size

        # resulting completed grid
        self.result = {}

    # loads in .csv file
    # data contains tuples (x, y, direction, length)
    @staticmethod
    def load_data(filename):
        data = []
        with open(f'grid_shapes/{filename}.csv', newline='') as f:
            for item in csv.reader(f):
                t = (int(item[0]), int(item[1]), str(item[2]), int(item[3]))
                data.append(t)
        return data

    # instantiates GridString objects from .csv data and stores them in class variable self.grid
    @staticmethod
    def construct_grid(data):
        grid = []
        for entry in data:
            (x, y, direction, length) = entry
            grid_string = GridString(x, y, direction, length)
            grid.append(grid_string)
        return grid

    # formats all grid string data into human-readable crossword grid and prints it
    def render_grid(self):
        to_print = []

        # deep copies the nested list of grid string data in self.grid
        all_grid_strings = copy.deepcopy(self.grid)

        # for all grid strings and words in result.items(), deep copy grid string, append word to grid string, and
        # append grid string to all_grid_strings
        for k,v in self.result.items():
            c = copy.deepcopy(k)
            c.word = v
            all_grid_strings.append(c)

        # sort list of grid strings by starting y coordinate, then starting x coordinate
        all_grid_strings.sort(key=lambda x: (x.start_y, x.start_x), reverse=False)
        counter = 0

        # a complicated procedure for formatting grid strings from self.result into a human-readable, printable
        # block of text representing the current state of the crossword grid
        for item in all_grid_strings:
            if item.direction == 'across':
                while counter % self.size < item.start_x or (counter / self.size) < item.start_y:
                    to_print.append(' ')
                    counter += 1
                    if (counter % self.size) == 0:
                        to_print.append('\n')
                to_print.append(item.word)
                counter += item.length
                if (counter % self.size) == 0:
                    to_print.append('\n')

        # print the crossword grid
        print(''.join(to_print))

    # function to pick the grid string to next fill with a word
    def select_candidate(self):
        best = math.inf
        candidate = None
        for c in self.grid:
            if c.freedom < best:
                best = c.freedom
                candidate = c
        return candidate

    # remove a grid string from self.grid given its x and y coordinates and direction
    def remove(self, x, y, direction):
        for item in self.grid:
            if item.start_x == x and item.start_y == y and item.direction == direction:
                self.grid.remove(item)
        return

    # takes a grid string and returns the list of grid strings that intersect it
    def find_intersections(self, string):
        intersections = []
        if string.direction == 'across':
            for cell in range(string.start_x, string.start_x + string.length):
                for word in self.grid:
                    if word.direction == 'down' \
                            and word.start_x == cell \
                            and string.start_y in range(word.start_y, word.start_y + word.length):
                        intersections.append(word)
                        break
        if string.direction == 'down':
            for cell in range(string.start_y, string.start_y + string.length):
                for word in self.grid:
                    if word.direction == 'across' \
                            and word.start_y == cell \
                            and string.start_x in range(word.start_x, word.start_x + word.length):
                        intersections.append(word)
                        break
        return intersections

    # takes a grid string and a word and updates that grid string and all its intersecting grid strings with that word
    def update(self, string, word):
        self.result[string] = word

        # gets intersecting grid strings
        intersections = self.find_intersections(string)

        # for all intersections, update the intersecting squares
        for index, item in enumerate(intersections):
            if string.direction == 'across':
                index_to_update = string.start_y - item.start_y
                new_word = list(item.word)
                new_word[index_to_update] = word[item.start_x - string.start_x]
            else:
                index_to_update = string.start_x - item.start_x
                new_word = list(item.word)
                new_word[index_to_update] = word[item.start_y - string.start_y]

            # updates word in intersecting grid string
            item.word = ''.join(new_word)

            # updates freedom in intersecting grid string
            item.freedom = item.most_constrained()

        # since grid string has been added to result, remove it from grid
        self.remove(string.start_x, string.start_y, string.direction)
        return

    # checks to make sure that each word in the grid is in fact a word, or is comprised of letters in a word
    def arc_consistent(self):
        for word in self.grid:
            if word.freedom == 0:
                return False
        return True


# the backtracking algorithm responsible for filling in the crossword grid
# g is a Grid object
def fill_grid(g):

    # pick the grid string to initially attempt to fill and print it
    candidate = g.select_candidate()
    print_grid([candidate])

    # find 10 words that could fit in the grid string slot and print them
    matches = candidate.pick_matches()
    print(matches)

    # iterate through all matches
    for match in matches:

        # if candidate is already filled, step out
        if not candidate:
            return
        print(match)

        # update grid string with candidate word
        g.update(candidate, match)

        # print the resulting crossword grid
        g.render_grid()
        print('-' * 100)

        # if no strings have freedom == 0
        if g.arc_consistent():

            # step in and fill grid with remaining unfilled grid string slots
            fill_grid(copy.deepcopy(g))

        # if no words fit
        print('not consistent')

    # if none of the 10 candidates work, step out (backtrack) and try again
    print("no success after 10 attempts...")
    return

#format_wordlist('usa2')

# load in words and grid
d = from_pkl('words')
g = Grid('11x11', 11)

# run backtracking algorithm
fill_grid(g)
