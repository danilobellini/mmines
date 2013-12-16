# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Danilo de Jesus da Silva Bellini
#                         danilo [dot] bellini [at] gmail [dot] com
#
# Musical Mines is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Created on Sun Jul 22 07:07:16 2012
"""
Musical Mines - Game core module
"""

import random
from itertools import product, repeat

random.seed()

# Deltas (dx, dy) coords for neighbor position
DIFF_POS = set(product(*repeat([-1, 0, 1], 2))).difference([(0, 0)])

class GameCell(object):

    def __init__(self, grid, row, col):
        # Cell fixed information
        self.grid = grid
        self.row = row
        self.col = col

        # Cell status information
        self.explored = False # a.k.a. "clicked"
        self.has_mine = False
        self.has_flag = False
        self._typed_number = None

    # Small interface needed afterwards for keyboard inputs
    @property
    def typed_number(self):
        return self._typed_number

    @typed_number.setter
    def typed_number(self, value):
        if self.explored and not self.grid.finished: # Avoid changes after end
            self._typed_number = value

    def neighbor_generator(self):
        neigh_pos = ((r + self.row, c + self.col) for r, c in DIFF_POS)
        return (self.grid[r, c] for r, c in neigh_pos
                                if (r >= 0) and
                                   (c >= 0) and
                                   (r < self.grid.rows) and
                                   (c < self.grid.cols)
               )

    def num_mined_neighbors(self):
        """ Number that would appear graphically in a given cell """
        return sum(1 for cell in self.neighbor_generator() if cell.has_mine)

    def explore(self):
        """ Explore (process a click) in this cell """

        # Place the mines, if it's the first call (click)
        if not self.grid.started:
            self.grid.put_mines(self)

        # Process with the exploration (click)
        if not (self.grid.finished or self.explored or self.has_flag):
            self.explored = True
            self.grid.add_one() # Exploration counting
            if self.has_mine:
                self.grid.finished = True
            else: # Zero mines: auto-click neighbors!
                cells_to_get_neighbors = {self}
                while cells_to_get_neighbors:
                    cell = cells_to_get_neighbors.pop()
                    if cell.num_mined_neighbors() == 0:
                        for neighbor in cell.neighbor_generator():
                            if not neighbor.explored:
                                neighbor.explored = True
                                self.grid.add_one()
                                cells_to_get_neighbors.add(neighbor)

    def toggle_flag(self):
        if self.grid.started and not (self.grid.finished or self.explored):
            self.has_flag = not self.has_flag


class GameGrid(object):
    """ Game board (a grid of row x col cells) abstraction """

    def victory(self):
        if not self.finished:
            return None # Victory is still undefined
        return all(cell.explored != cell.has_mine for cell in self)

    def new_game(self, rows, cols, nmines):
        # Grid fixed information (for this game)
        self.rows = rows
        self.cols = cols
        self.nmines = max(0, min(rows * cols - 1, nmines))

        # Creates the cell grid
        self._cells = [[GameCell(self, row, col) for col in range(cols)]
                                                 for row in range(rows)]

        # Grid status information
        self.finished = False
        self.started = False # Mines weren't placed yet
        self.explored = 0

    def add_one(self):
        """
        Count one more exploration, to help finding when it finishes.
        Should be called by the cells when exploring somewhere.
        """
        self.explored += 1
        if self.explored + self.nmines == self.rows * self.cols:
            self.finished = True

    def __iter__(self):
        """ Iterates all cells in the grid """
        return (self._cells[row][col] for row in range(self.rows)
                                      for col in range(self.cols))

    def __getitem__(self, coords):
        """ Gets the item at the coords = (row, col) in the board """
        row, col = coords
        assert not isinstance(row, slice)
        return self._cells[row][col]

    def put_mines(self, cell):
        """
        Starts the game, and ensures the given cell isn't a mine.
        This method is used to ensure there's no mine in the 1st click.
        """
        cells = list(self) # List of all cells
        random.shuffle(cells)
        for c in cells[:self.nmines]:
            c.has_mine = True

        # The given cell shouldn't be a mine. Takes next in shuffle, if needed
        if cell.has_mine:
            cell.has_mine = False
            cells[self.nmines].has_mine = True
        self.started = True
