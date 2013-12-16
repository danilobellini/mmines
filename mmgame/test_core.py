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
# Created on Sun Dec 15 16:20:48 2013
"""
Musical Mines - Game core module testing
"""

from .core import GameGrid

def test_1x1_0():
    gg = GameGrid()
    gg.new_game(1, 1, 0)
    assert not gg[0, 0].has_mine
    assert not gg.started
    assert not gg.finished
    gg[0, 0].explore()
    assert gg.started
    assert gg.finished
    assert gg[0, 0].explored
    assert not gg[0, 0].has_mine
    assert gg.victory()

def test_1x2_0():
    gg = GameGrid()
    gg.new_game(1, 2, 0)
    assert not gg[0, 0].has_mine
    assert not gg[0, 1].has_mine
    assert not gg.started
    assert not gg.finished
    gg[0, 1].explore()
    assert gg.started
    assert gg.finished
    assert gg[0, 0].explored
    assert gg[0, 1].explored
    assert gg.victory()

def test_1x2_1():
    gg = GameGrid()
    gg.new_game(1, 2, 1)
    assert not gg.started
    assert not gg.finished
    col = 1 if gg[0, 0].has_mine else 0
    gg[0, col].explore()
    assert gg.started
    assert gg.finished
    assert gg[0, col].explored
    assert not gg[0, 1 - col].explored
    assert gg.victory()

def test_3x1_1():
    gg = GameGrid()
    gg.new_game(3, 1, 1)
    assert not gg.started
    assert not gg.finished
    gg[1, 0].explore()
    assert gg.started
    assert not gg.finished
    assert not gg[0, 0].explored
    assert gg[1, 0].explored
    assert not gg[2, 0].explored
    assert gg[0, 0].has_mine or gg[2, 0].has_mine
    assert not (gg[0, 0].has_mine and gg[2, 0].has_mine)
    if gg[0, 0].has_mine:
        gg[2, 0].explore()
    else:
        gg[0, 0].explore()
    assert gg.finished
    assert gg.victory()
    assert gg.started

def test_3x1_1_loses():
    gg = GameGrid()
    gg.new_game(3, 1, 1)
    assert not gg.started
    assert not gg.finished
    gg[1, 0].explore()
    assert gg.started
    assert not gg.finished
    assert not gg[0, 0].explored
    assert gg[1, 0].explored
    assert not gg[2, 0].explored
    assert gg[0, 0].has_mine or gg[2, 0].has_mine
    assert not (gg[0, 0].has_mine and gg[2, 0].has_mine)
    if gg[0, 0].has_mine:
        gg[0, 0].explore()
    else:
        gg[2, 0].explore()
    assert gg.finished
    assert not gg.victory()
    assert gg.started

def test_2x2_1_loses_in_2nd_explore():
    gg = GameGrid()
    gg.new_game(2, 2, 1)
    assert not gg.started
    assert not gg.finished
    gg[1, 1].explore()
    assert gg.started
    assert not gg.finished
    mined = [cell for cell in gg if cell.has_mine]
    assert len(mined) == 1
    mined[0].explore()
    assert gg.finished
    assert not gg.victory()
    explored = mined + [gg[1, 1]]
    for cell in gg:
        assert cell.explored == (cell in explored)
    assert gg.started

def test_2x2_1_loses_in_3rd_explore():
    gg = GameGrid()
    gg.new_game(2, 2, 1)
    assert not gg.started
    assert not gg.finished
    gg[0, 1].explore()
    assert gg.started
    assert not gg.finished
    notmined = [cell for cell in gg if not cell.has_mine]
    assert len(notmined) == 3
    notmined.remove(gg[0, 1])
    assert len(notmined) == 2
    notmined[0].explore()
    assert gg.started
    assert not gg.finished
    mined = [cell for cell in gg if cell.has_mine]
    assert len(mined) == 1
    mined[0].explore()
    assert gg.finished
    assert not gg.victory()
    explored = mined + [gg[0, 1], notmined[0]]
    for cell in gg:
        assert cell.explored == (cell in explored)
    assert gg.started

def test_2x2_1_wins():
    gg = GameGrid()
    gg.new_game(2, 2, 1)
    assert len([cell for cell in gg if cell.has_mine]) == 0
    gg[0, 0].explore()
    notmined = [cell for cell in gg if not cell.has_mine]
    assert len(notmined) == 3
    for cell in notmined:
        assert not gg.finished
        assert gg.victory() is None
        cell.explore()
    assert gg.finished
    assert gg.victory()

def test_1000x1000_1_stress():
    gg = GameGrid()
    gg.new_game(1000, 1000, 1)
    assert len([cell for cell in gg if cell.has_mine]) == 0
    gg[573, 227].explore()
    for cell in gg:
        assert cell.explored is not cell.has_mine
    assert gg.finished
    assert gg.victory()
