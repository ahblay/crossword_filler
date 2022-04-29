import pickle
from pprint import pprint as pp
import csv
import random
import math
import copy


def print_grid(grid):
    for s in grid:
        thing = {k: v for k, v in s.__dict__.items() if k != 'matches'}
        print(thing)


def to_pkl(filename, d):
    with open(f'{filename}.pkl', 'wb') as f:
        pickle.dump(d, f)


def from_pkl(filename):
    with open(f'{filename}.pkl', 'rb') as f:
        d = pickle.load(f)
    return d


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


class GridString:
    def __init__(self, start_x, start_y, direction, length):
        self.start_x = start_x
        self.start_y = start_y
        self.direction = direction
        self.length = length
        self.word = '-' * self.length
        self.matches = from_pkl('words')[self.length]
        self.freedom = self.most_constrained()

    @staticmethod
    def check_match(candidate, word):
        for index, val in enumerate(candidate):
            if val != '-':
                if word[index] != val:
                    return False
        return True

    def most_constrained(self):
        self.matches = from_pkl('words')[self.length]
        #print(f"******** {self.word} ********")
        if self.word == '-' * self.length:
            freedom = len(self.matches)
        else:
            #print('comparing words...')
            new_matches = []
            for w in self.matches:
                # TODO: This is a MASSIVELY slow function.
                if self.check_match(self.word, w):
                    new_matches.append(w)
            self.matches = new_matches
            freedom = len(self.matches)
        #print(f'first 10 matches: {self.matches[:10]}')
        return freedom

    def pick_matches(self):
        choice = min(10, len(self.matches))
        m = random.sample(self.matches, choice)
        #m = self.matches[:10]
        return m


class Grid:
    def __init__(self, filename, size):
        self.grid = self.construct_grid(self.load_data(filename))
        self.size = size
        self.result = {}

    @staticmethod
    def load_data(filename):
        data = []
        with open(f'grid_shapes/{filename}.csv', newline='') as f:
            for item in csv.reader(f):
                t = (int(item[0]), int(item[1]), str(item[2]), int(item[3]))
                data.append(t)
        return data

    @staticmethod
    def construct_grid(data):
        grid = []
        for entry in data:
            (x, y, direction, length) = entry
            grid_string = GridString(x, y, direction, length)
            grid.append(grid_string)
        return grid

    def render_grid(self):
        to_print = []
        all_grid_strings = copy.deepcopy(self.grid)
        for k,v in self.result.items():
            c = copy.deepcopy(k)
            c.word = v
            all_grid_strings.append(c)
        all_grid_strings.sort(key=lambda x: (x.start_y, x.start_x), reverse=False)
        counter = 0
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
        print(''.join(to_print))

    def select_candidate(self):
        best = math.inf
        candidate = None
        for c in self.grid:
            if c.freedom < best:
                best = c.freedom
                candidate = c
        return candidate

    def remove(self, x, y, direction):
        for item in self.grid:
            if item.start_x == x and item.start_y == y and item.direction == direction:
                self.grid.remove(item)
        return

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

    def update(self, string, word):
        self.result[string] = word
        intersections = self.find_intersections(string)
        #print_grid(intersections)
        for index, item in enumerate(intersections):
            #print(f'string.start_y = {string.start_y}')
            #print(f'item.start_y = {item.start_y}')
            #print(f'string.start_x = {string.start_x}')
            #print(f'item.start_x = {item.start_x}')
            if string.direction == 'across':
                index_to_update = string.start_y - item.start_y
                new_word = list(item.word)
                new_word[index_to_update] = word[item.start_x - string.start_x]
            else:
                index_to_update = string.start_x - item.start_x
                new_word = list(item.word)
                new_word[index_to_update] = word[item.start_y - string.start_y]
            # TODO: something wrong here
            #print(f'index to update: {index_to_update}')
            #print(f"index: {index}")
            item.word = ''.join(new_word)
            item.freedom = item.most_constrained()
        self.remove(string.start_x, string.start_y, string.direction)
        return

    def arc_consistent(self):
        for word in self.grid:
            if word.freedom == 0:
                return False
        return True


def fill_grid(g):
    candidate = g.select_candidate()
    print_grid([candidate])
    #print_grid(g.grid)
    #print('+' * 100)
    #print(f"freedom: {candidate.freedom}")
    #print(f"x: {candidate.start_x}")
    #print(f"y: {candidate.start_y}")
    matches = candidate.pick_matches()
    print(matches)
    for match in matches:
        if not candidate:
            return
        print(match)
        # update grid_strings
        g.update(candidate, match)
        #print_grid(g.grid)
        g.render_grid()
        print('-' * 100)
        # if no strings have freedom == 0
        if g.arc_consistent():
            fill_grid(copy.deepcopy(g))
        print('not consistent')
    print("no success after 10 attempts...")
    return

#format_wordlist('usa2')
d = from_pkl('words')
g = Grid('11x11', 11)
#test = g.grid[0].check_match('--rex', 'pyrex')
#print(test)
fill_grid(g)
#pp(g.result)
