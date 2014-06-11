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
# Created on Sun Jul 22 10:36:30 2012
"""
Musical Mines - Game package (modules and constants)
"""

# Some needed constants
MIN_TILE_SIZE = 2.8 # Pixels, just to avoid errors
PI = 3.14159265359

# This could have up to 35 default sizes. I think there's no need for more.
DEFAULT_GRID_SIZES = [(9, 9, 10), # (Rows, cols, number of mines)
                      (9, 9, 20),
                      (7, 15, 20),
                      (7, 15, 40),
                      (16, 16, 35),
                      (16, 16, 50),
                      (20, 20, 50),
                      (20, 20, 70),
                      (20, 40, 100),
                      (20, 40, 200),
                      (30, 60, 500)]

# Relative sizes and displacement for tile height and width equals to 1
DSIZE = {"FrameWidth": 0.1,
         "TileFrameWidth": .075,
         "TileBorderUpperLeft": .01,
         "TileBorderLowerRight": .01,
        }

# Colors (RGB)
DCOLOR = {"Background":    "#000060",
          "FrameUp":       "#666666",
          "FrameDown":     "#cccccc",
          "FrameUpWins":   "#33cc33",
          "FrameDownWins": "#80cc80",
          "FrameUpLoses":  "#ff3333",
          "FrameDownLoses":"#ff8080",
          "TileFrameUp":   "#e6e6e6",
          "TileFrameDown": "#808080",
          "TileUnclicked": "#cccccc",
          "TileBorder":    "#808080",
          "TileClicked":   "#b3b3b3",
          "TileSelected":  "#00ff00",
          "FlagPole":      "#000000",
          "FlagBase":      "#003300",
          "Flag":          "#ff0000",
          "Musical":       "#ffff00",
          "Mine":          "#000000",
          "MineLight":     "#ffffff",
          "Wrong":         "#803030c0", # Has alpha
         }

# Number colors
NCOLOR = {1: "#0000ff",
          2: "#008000",
          3: "#ff0000",
          4: "#000080",
          5: "#800000",
          6: "#008080",
          7: "#000000",
          8: "#808080",
         }
