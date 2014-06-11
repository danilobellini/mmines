#!/usr/bin/env python
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
# Created on Sat Jul 14 03:41:45 2012
"""
Musical Mines - A minesweeper game to help learning musical skills.
"""

from _mmines.core import GameGrid
from _mmines import (MIN_TILE_SIZE, PI, DEFAULT_GRID_SIZES, DSIZE, DCOLOR,
                    NCOLOR)
import wx
import audiolazy as lz
import random

__version__ = "0.1"
__author__ = "Danilo de Jesus da Silva Bellini"

rate = 44100
s, Hz = lz.sHz(rate)
ms = 1e-3 * s

SYNTH_ADSR_PARAMS = dict(a=40*ms, d=20*ms, s=.7, r=50*ms)
SYNTH_DURATION = .4 * s
SYNTH_ENVELOPE = list(lz.adsr(SYNTH_DURATION, **SYNTH_ADSR_PARAMS) * .55)
SYNTH_PAUSE_AT_END = lz.zeroes(.25 * s).take(lz.inf)
synth_table = lz.sin_table.harmonize(dict(enumerate(
                  [.1, .15, .08, .05, .04, .03, .02]
              )))

class GameScreenArea(wx.Panel):

    def __init__(self, parent, rows, cols, nmines, *args, **kwargs):
        super(GameScreenArea, self).__init__(parent, *args, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM) # Avoids flicker

        # Event handlers binding
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_up)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self._show_numbers = False

        self.game = GameGrid()
        self.new_game(rows, cols, nmines)

    @property
    def show_numbers(self):
        return self._show_numbers

    @show_numbers.setter
    def show_numbers(self, value):
        self._show_numbers = value
        self.Refresh()

    def new_game(self, rows, cols, nmines):
        self.coords = None # Grid coords from (0, 0) to (rows - 1, cols - 1)
        self.rcoords = None # The same, for right click
        self.clicked_btn = None # Mouse button used in last click
        self.game.new_game(rows, cols, nmines)
        self.Refresh()

    def pos2coords(self, x, y):
        """
        From a given (x, y) pixel coordinates, returns the (row, col) in the
        game grid board, starting from (0,0). If the given coordinates brings
        us outside the grid, this method returns None.
        """
        row = (y - self.ytop - 1) // self.tile_size
        col = (x - self.xleft - 1) // self.tile_size
        return (row, col) if (row >= 0) and \
                             (col >= 0) and \
                             (row < self.game.rows) and \
                             (col < self.game.cols) else None

    def state(self, cell):
        """
        Returns the actual state of the cell, which could be seen as the kind
        of image that should be drawn. Possible values are:

        - Mine
        - MineRevealed
        - Flag
        - WrongFlag
        - Empty
        - Clicked (a.k.a. musical note)
        - Unclicked
        - Number
        - NumberRevealed
        - WrongNumber

        """
        if cell.explored:
            if cell.has_mine:
                return "Mine"
            if cell.typed_number:
                if self.show_numbers:
                    return "NumberRevealed"
                if cell.grid.finished:
                    if cell.num_mined_neighbors() != cell.typed_number:
                        return "WrongNumber"
                return "Number"
            if cell.num_mined_neighbors() == 0:
                return "Empty"
            if cell.grid.finished or self.show_numbers:
                return "NumberRevealed"
            return "Clicked"

        if cell.has_flag:
            if cell.grid.finished and not cell.has_mine:
                return "WrongFlag"
            return "Flag"

        if cell.grid.finished and cell.has_mine:
            return "MineRevealed"

        return "Unclicked"


    def play_interval(self, interval):
        # Finds 2 note frequencies in Hz with the given configuration
        if self.is_up is None:
            direction = random.choice([-1, 1])
        else:
            direction = 1 if self.is_up else -1
        note1 = lz.MIDI_A4 + random.randint(-15, 5) # Semitones (MIDI pitch)
        note2 = note1 + interval * direction
        freq1 = lz.midi2freq(note1) * Hz
        freq2 = lz.midi2freq(note2) * Hz

        # Creates the audio generators for each note
        audio1 = SYNTH_ENVELOPE * synth_table(freq1)
        audio2 = SYNTH_ENVELOPE * synth_table(freq2)

        # Play it in another thread
        audio = lz.chain(audio1, audio2, SYNTH_PAUSE_AT_END)
        player.play(audio, rate=rate)

    def on_mouse_down(self, evt):
        self.clicked_btn = evt.GetButton()

        if self.clicked_btn == wx.MOUSE_BTN_LEFT:
            self.coords = self.pos2coords(*evt.Position)
            self.rcoords = None
        else:
            self.rcoords = self.pos2coords(*evt.Position)

        # See if it should play the interval
        if self.coords and (self.clicked_btn == wx.MOUSE_BTN_LEFT):
            cell = self.game[self.coords]
            if self.state(cell) in ("Clicked", "Number", "NumberRevealed",
                                    "WrongNumber"):
                self.play_interval(cell.num_mined_neighbors())

        # Focus should be kept with the window
        evt.Skip()
        self.Refresh() # Redraw everything

    def on_mouse_move(self, evt):
        if evt.ButtonIsDown(wx.MOUSE_BTN_LEFT):
            self.coords = self.pos2coords(*evt.Position)
            self.Refresh() # Redraw everything
        elif evt.ButtonIsDown(wx.MOUSE_BTN_RIGHT):
            if self.rcoords != self.pos2coords(*evt.Position):
                self.rcoords = None

    def explore_selected_cell(self):
        """ Simple cell explore (click) action """
        cell = self.game[self.coords]
        old_state = self.state(cell)
        cell.explore()
        if old_state == "Unclicked" and \
           self.state(cell) in ("Clicked", "Number", "NumberRevealed",
                                "WrongNumber"):
            self.play_interval(cell.num_mined_neighbors())
        self.Refresh() # Redraw everything

    def on_mouse_up(self, evt):
        # Useful clicks are press-release pairs for the same cell
        if self.clicked_btn == evt.GetButton():
            clicked_coords = self.pos2coords(*evt.GetPosition())
            if self.clicked_btn == wx.MOUSE_BTN_LEFT:
                if self.coords and self.coords == clicked_coords:
                    self.explore_selected_cell()
            elif self.clicked_btn == wx.MOUSE_BTN_RIGHT:
                if self.rcoords and self.rcoords == clicked_coords:
                    self.game[self.rcoords].toggle_flag()
                    self.Refresh() # Redraw everything

    def on_key_down(self, evt):
        if evt.HasModifiers():
            return

        key = evt.GetKeyCode()
        tnumber = None

        # Typing a number
        if wx.WXK_NUMPAD1 <= key <= wx.WXK_NUMPAD8:
            tnumber = key - wx.WXK_NUMPAD0
        elif ord("1") <= key <= ord("8"):
            tnumber = key - ord("0")

        if not tnumber is None:
            if self.coords and not self.show_numbers:
                cell = self.game[self.coords]
                if self.state(cell) in ("Clicked", "Number", "NumberRevealed",
                                        "WrongNumber"):
                    cell.typed_number = tnumber
                    self.Refresh() # Redraw everything

        # Arrow keys
        elif key in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN):
            if self.coords:
                self.coords = list(self.coords)
                if key == wx.WXK_LEFT:
                    self.coords[1] = max(self.coords[1] - 1, 0)
                elif key == wx.WXK_RIGHT:
                    self.coords[1] = min(self.coords[1] + 1, self.game.cols - 1)
                elif key == wx.WXK_UP:
                    self.coords[0] = max(self.coords[0] - 1, 0)
                else: # Down
                    self.coords[0] = min(self.coords[0] + 1, self.game.rows - 1)
                self.coords = tuple(self.coords)
            else:
                self.coords = (0, 0)
            self.Refresh() # Redraw everything

        # "Click" (play or explore)
        elif key in (wx.WXK_SPACE, wx.WXK_RETURN):
            if self.coords:
                cell = self.game[self.coords]
                if self.state(cell) in ("Clicked", "Number", "NumberRevealed",
                                        "WrongNumber"):
                    self.play_interval(cell.num_mined_neighbors())
                else:
                    self.explore_selected_cell()

        # Flag
        elif key == ord("F"):
            if self.coords:
                self.game[self.coords].toggle_flag()
                self.Refresh() # Redraw everything

        # Delete number/flag
        elif key in (wx.WXK_DELETE, wx.WXK_BACK):
            if self.coords:
                cell = self.game[self.coords]
                if cell.has_flag:
                    self.game[self.coords].toggle_flag()
                else:
                    cell.typed_number = None
                self.Refresh() # Redraw everything

    def on_size(self, evt):
        self.Refresh() # This calls OnPaint for the entire widget rectangle

    def on_paint(self, evt):
        # Creates the context (it clips to refresh only the needed rectangle)
        dc = wx.AutoBufferedPaintDCFactory(self) # Avoid wx.PaintDC flicker
        dc.SetBackground(wx.Brush(DCOLOR["Background"]))
        dc.Clear() # TODO: Redraw only changed area
        gc = wx.GraphicsContext.Create(dc)

        # Configures and draws the screen contents
        self.config_graphics_context(gc) # Displacement/scale config
        self.draw_frame(gc) # Border
        for cell in self.game: # Draw each tile (size is unitary)
            self.draw_tile(gc, cell)

    def config_graphics_context(self, gc):
        """
        Configure displacement and scale for the given wx.GraphicsContext, so
        that (0,0) is the starting grid coords, and "1" is the tile
        width/length, centralizing the game board.
        """

        # Finds the max tile size ...
        width, height = self.GetSize()
        fw = DSIZE["FrameWidth"]
        self.tile_size = max(
            MIN_TILE_SIZE,
            lz.rint(min(
                width  / (self.game.cols + 2 * fw),
                height / (self.game.rows + 2 * fw)
            ))
        )

        # ... and the game displacement
        self.gamewidth = self.tile_size * self.game.cols
        self.gameheight = self.tile_size * self.game.rows
        self.xleft = (width - self.gamewidth) / 2 # Corner to draw tiles
        self.ytop = (height - self.gameheight) / 2

        # Adjust axis for unitary tile size starting from (0,0)
        gc.Translate(self.xleft, self.ytop)
        gc.Scale(self.tile_size, self.tile_size)

    def draw_generic_frame(self, gc, hwidth, vwidth, ul_color, br_color):
        """
        Draws a frame from (0,0) to (1,1) with the given horizontal and
        vertical width, upper-left color and lower-right color into the
        wx.GraphicsContext "gc" input.
        This method changes the brush color.
        """

        # Creates a full path for the upper-left region of the frame
        frame_path = gc.CreatePath()
        frame_path.MoveToPoint(0., 0.)
        frame_path.AddLineToPoint(0., 1.)
        frame_path.AddLineToPoint(hwidth, 1. - vwidth)
        frame_path.AddLineToPoint(hwidth, vwidth)
        frame_path.AddLineToPoint(1. - hwidth, vwidth)
        frame_path.AddLineToPoint(1., 0.)

        # Fills the frame (only border): upper-left side ...
        gc.SetBrush(wx.Brush(ul_color))
        gc.FillPath(frame_path)

        # ... and lower-right side
        gc.SetBrush(wx.Brush(br_color))
        gc.PushState()
        gc.Translate(1., 1.)
        gc.Rotate(PI)
        gc.FillPath(frame_path)
        gc.PopState()

    def draw_frame(self, gc):
        """
        Draws a frame in a scaled wx.GraphicsContext input, assuming it's placed
        in point (0,0) and that the frame lies outside the contents grid (i.e.,
        the frame starts in point (-fw,-fw) where fw is the frame width).
        This method changes the brush color.
        """

        if self.game.finished:
            if self.game.victory():
                colors = (DCOLOR["FrameUpWins"], DCOLOR["FrameDownWins"])
            else:
                colors = (DCOLOR["FrameUpLoses"], DCOLOR["FrameDownLoses"])
        else:
            colors = (DCOLOR["FrameUp"], DCOLOR["FrameDown"])

        gc.PushState()
        fw = DSIZE["FrameWidth"]
        gc.Translate(-fw, -fw)
        #gc.Scale(self.game.cols+2*fw, self.game.rows+2*fw)
        #self.draw_generic_frame(gc, fw/(self.game.cols+2*fw),
        #                            fw/(self.game.rows+2*fw),
        #                            *colors)

        # Creates a full path for the upper-left region of the frame
        frame_path = gc.CreatePath()
        frame_path.MoveToPoint(0., 0.)
        frame_path.AddLineToPoint(0., self.game.rows + 2 * fw)
        frame_path.AddLineToPoint(fw, self.game.rows + fw)
        frame_path.AddLineToPoint(fw, fw)
        frame_path.AddLineToPoint(self.game.cols + fw, fw)
        frame_path.AddLineToPoint(self.game.cols + 2 * fw, 0.)

        # Fills the frame (only border): upper-left side ...
        gc.SetBrush(wx.Brush(colors[0]))
        gc.FillPath(frame_path)

        # ... and lower-right side
        gc.SetBrush(wx.Brush(colors[1]))
        gc.PushState()
        gc.Translate(self.game.cols+2*fw, self.game.rows+2*fw)
        gc.Rotate(PI)
        gc.FillPath(frame_path)
        gc.PopState()

        gc.PopState()

    def draw_tile(self, gc, cell):
        """
        Draws the cell. The wx.GraphicsContext input "gc" should be configured
        by self.config_graphics_context previously.
        This method changes the brush color.
        """

        # Initialization
        img = self.state(cell)

        gc.PushState()
        gc.Translate(cell.col, cell.row) # From (0, 0) drawing up to (1, 1)

        #
        # Draws the cell background and border/frame
        #
        if img in ("Flag", "Unclicked", "WrongFlag",
                   "MineRevealed"): # Unclicked states
            gc.SetBrush(wx.Brush(DCOLOR["TileUnclicked"]))
            gc.DrawRectangle(0, 0, 1, 1)
            tfw = DSIZE["TileFrameWidth"]
            if self.coords == (cell.row, cell.col):
                self.draw_generic_frame(gc, tfw, tfw,
                                            DCOLOR["TileFrameDown"],
                                            DCOLOR["TileFrameUp"])
            else:
                self.draw_generic_frame(gc, tfw, tfw,
                                            DCOLOR["TileFrameUp"],
                                            DCOLOR["TileFrameDown"])
        else: # Clicked background
            gc.SetBrush(wx.Brush(DCOLOR["TileBorder"]))
            gc.DrawRectangle(0, 0, 1, 1)
            gc.SetBrush(wx.Brush(DCOLOR[
                "TileSelected" if self.coords == (cell.row, cell.col)
                               else "TileClicked"
            ]))
            tbul = DSIZE["TileBorderUpperLeft"]
            tblr = DSIZE["TileBorderLowerRight"]
            gc.DrawRectangle(tbul, tbul, 1 - tblr - tbul, 1 - tblr - tbul)

        #
        # Draws the cell foreground
        #
        if img in ("Flag", "WrongFlag"): # Flag
            # Pole
            gc.SetBrush(wx.Brush(DCOLOR["FlagPole"]))
            gc.DrawRoundedRectangle(.545, .205, .05, .6, .025)

            # Ground/base
            gc.SetBrush(wx.Brush(DCOLOR["FlagBase"]))
            base_path = gc.CreatePath()
            base_path.MoveToPoint(.1, .83)
            base_path.AddLineToPoint(.1, .9)
            base_path.AddLineToPoint(.9, .9)
            base_path.AddLineToPoint(.9, .83)
            base_path.AddLineToPoint(.65, .75)
            base_path.AddLineToPoint(.35, .75)
            gc.FillPath(base_path)

            # Flag
            gc.SetBrush(wx.Brush(DCOLOR["Flag"]))
            flag_path = gc.CreatePath()
            flag_path.MoveToPoint(.575, .5)
            flag_path.AddLineToPoint(.575, .2)
            flag_path.AddLineToPoint(.2, .35)
            gc.FillPath(flag_path)

        if img in ("Mine", "MineRevealed"): # Mine
            gc.SetBrush(wx.Brush(DCOLOR["Mine"]))
            gc.DrawRoundedRectangle(.1, .45, .8, .1, .05)
            gc.DrawRoundedRectangle(.45, .1, .1, .8, .05)
            gc.DrawEllipse(.17, .17, .66, .66)
            gc.SetBrush(wx.Brush(DCOLOR["MineLight"]))
            gc.DrawEllipse(.3, .3, .12, .12)

        if img in ("Clicked", "NumberRevealed"): # Musical foreground
            gc.SetBrush(wx.Brush(DCOLOR["Musical"]))

            # Draw stem
            gc.PushState()
            gc.Rotate(PI/180. * (-13))
            gc.DrawRoundedRectangle(.36753, .14713, .09335, .83629, .046675)
            gc.PopState()

            # Draw notehead
            gc.PushState()
            gc.Rotate(PI/180. * 12.1)
            gc.DrawEllipse(.45689, .5756, .37322, .25531)
            gc.PopState()

            # Draw note flag
            gc.PushState()
            gc.Rotate(PI/180. * (-38.8)) # Upper
            gc.DrawRoundedRectangle(.24297, .31483, .09026, .33067, .04513)
            gc.PopState()
            gc.PushState()
            gc.Rotate(PI/180. * (-52.3)) # Middle
            gc.DrawRoundedRectangle(.09495, .60602, .09016, .26987, .04508)
            gc.PopState()
            gc.PushState()
            gc.Rotate(PI/180. * (-7.68)) # Lower
            gc.DrawRoundedRectangle(.63816, .44793, .09016, .3368, .04508)
            gc.PopState()

        if img in ("Number", "NumberRevealed", "WrongNumber"):
            # Gets the number to be printed
            if img == "NumberRevealed":
                number = cell.num_mined_neighbors()
            else:
                number = cell.typed_number

            # Initilizes the font
            font_size = 32 # This is somehow arbitrary. The bigger is better
                           # (integers are unavoidable in some places)
            flags = wx.FONTFLAG_BOLD | wx.FONTFLAG_ANTIALIASED
            font = wx.FFont(font_size, wx.FONTFAMILY_DEFAULT, flags)

            # Makes "tile size" equals to "font width", with a workaround to
            # work both on Linux (ok) and Windows (negative height?)
            w = abs(min(font.GetPixelSize()))
            gc.PushState()
            gc.Scale(1./w, 1./w)

            # Draw at coordinates that centralize with real font size
            gc.SetFont(font, NCOLOR[number])
            msg = "12345678" * 3
            realw, realh = gc.GetTextExtent(msg)
            realw /= len(msg) # Why this works, yet the font isn't monotype?
            gc.DrawText(str(number), .5 * (w - realw), .5 * (w - realh))
            gc.PopState()

        if img in ("WrongFlag", "WrongNumber"): # Wrong symbol
            gc.SetBrush(wx.Brush(DCOLOR["Wrong"]))
            gc.PushState()
            gc.Translate(.5, .5)
            gc.Rotate(PI/4)
            gc.DrawRoundedRectangle(-.1, -.6, .2, 1.2, .1)
            gc.DrawRoundedRectangle(-.6, -.1, 1.2, .2, .1)
            gc.PopState()

        # Finishes
        gc.PopState()


class GameCustomizeDialog(wx.Dialog):

    def __init__(self, parent, rows, cols, nmines):
        super(GameCustomizeDialog, self).__init__(
            parent = parent,
            title = "Customize game parameters",
            size = (280, 200),
            style = wx.CAPTION,
        )

        # Widgets
        label1 = wx.StaticText(self, 16, 'Size (rows x cols)')
        label2 = wx.StaticText(self, 16, 'Number of mines')
        self.rows_entry = wx.TextCtrl(self, value=str(rows))
        self.cols_entry = wx.TextCtrl(self, value=str(cols))
        self.nmines_entry = wx.TextCtrl(self, value=str(nmines))
        button_ok = wx.Button(self, wx.ID_OK)
        button_cancel = wx.Button(self, wx.ID_CANCEL)

        # Layout organization
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.rows_entry, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        hbox1.Add(self.cols_entry, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(button_cancel, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 15)
        hbox2.Add(button_ok, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 15)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(label1, 1, wx.ALIGN_CENTER|wx.TOP, 20)
        vbox.Add(hbox1, 0, wx.EXPAND)
        vbox.Add(label2, 1, wx.ALIGN_CENTER|wx.TOP, 20)
        vbox.Add(self.nmines_entry, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 50)
        vbox.Add(hbox2, 0, wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, 20)
        self.SetSizer(vbox)

        # Buttons actions binding
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.on_finish, id=wx.ID_CANCEL)

    def on_ok(self, evt):
        #TODO: test invalid inputs
        self.EndModal(wx.ID_OK)

    def on_finish(self, evt):
        self.EndModal(wx.ID_CANCEL)


class GameMainWindow(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(GameMainWindow, self).__init__(*args, **kwargs)
        self.SetTitle("Musical Mines")
        self.SetSize((300, 300))
        self.CreateStatusBar()
        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # Game menu
        gamemenu = wx.Menu() # "General game menu"
        menubar.Append(gamemenu, "&Game")
        mi_new = gamemenu.Append(wx.ID_NEW,
                                 "&New\tCtrl+N",
                                 "Starts a new game")
        gamemenu.AppendSeparator()
        mi_quit = gamemenu.Append(wx.ID_EXIT,
                                  "&Quit\tCtrl+Q",
                                  "Closes the game")

        # Size menu
        sizemenu = wx.Menu() # "Choose game table size and number of bombs"
        menubar.Append(sizemenu, "&Size")
        self.size_dict = {} # Keys are menu item ids; Values are size tuples
        mi_help = "Sets up next game to have %d rows, %d columns and %d mines"
        for idx, size in enumerate(DEFAULT_GRID_SIZES):
            new_mi_text = "&%s" % (
              str(idx + 1) if idx < 9 else chr(idx + ord("A") - 9)
            )
            new_mi_text += ": %dx%d with %d mines" % size
            new_mi_help = mi_help % size
            new_mi = sizemenu.Append(wx.ID_ANY,
                                     new_mi_text,
                                     new_mi_help,
                                     wx.ITEM_NORMAL) # 1st checked by default
            self.size_dict[new_mi.Id] = size
        sizemenu.AppendSeparator()
        custom_mi_help = "Customizes the next game parameters, i.e., the " \
                         "number of rows, columns and mines"
        custom_mi = sizemenu.Append(wx.ID_ANY,
                                    "&0: Custom ...\tCtrl+M",
                                    custom_mi_help,
                                    wx.ITEM_NORMAL)
        self.custom_id = custom_mi.Id

        # Options menu
        optionsmenu = wx.Menu() # "Choose game rules"
        menubar.Append(optionsmenu, "&Options")
        mi_show_num = optionsmenu.Append(wx.ID_ANY,
                                        "&Show numbers", "", wx.ITEM_CHECK)
        optionsmenu.AppendSeparator()
        mi_asc = optionsmenu.Append(wx.ID_ANY,
                                    "&Ascending interval", "", wx.ITEM_RADIO)
        mi_des = optionsmenu.Append(wx.ID_ANY,
                                    "&Descending interval", "", wx.ITEM_RADIO)
        mi_rnd = optionsmenu.Append(wx.ID_ANY,
                                    "&Random interval direction", "",
                                    wx.ITEM_RADIO)
        self.intervals = {mi_asc.Id: True,
                          mi_des.Id: False,
                          mi_rnd.Id: None}

        # Help menu
        helpmenu = wx.Menu() # "Choose game rules"
        menubar.Append(helpmenu, "&Help")
        mi_about = helpmenu.Append(wx.ID_ANY, "&About ...", "")

        # Creates the screen grid widget
        self.next_size = DEFAULT_GRID_SIZES[0]
        self.screen = GameScreenArea(self, *self.next_size)
        self.screen.is_up = self.intervals[mi_asc.Id]
        self.on_new(None)

        # Binds the menu items to handlers
        self.Bind(wx.EVT_MENU, self.on_new, mi_new)
        self.Bind(wx.EVT_MENU, self.on_quit, mi_quit)
        for mi in sizemenu.GetMenuItems():
            self.Bind(wx.EVT_MENU, self.on_grid_size, mi)
        self.Bind(wx.EVT_MENU, self.on_toggle_numbers, mi_show_num)
        self.Bind(wx.EVT_MENU, self.on_change_interval, mi_asc)
        self.Bind(wx.EVT_MENU, self.on_change_interval, mi_des)
        self.Bind(wx.EVT_MENU, self.on_change_interval, mi_rnd)
        self.Bind(wx.EVT_MENU, self.on_about, mi_about)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_new(self, evt):
        if self.screen.game.started and not self.screen.game.finished:
            title = "New game"
            dbox = wx.MessageDialog(self,
                "Do you want to cancel this game and start a new one?",
                title,
                wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dbox.ShowModal() == wx.ID_NO:
                return
        self.screen.new_game(*self.next_size)

    def on_quit(self, evt):
        self.Close()

    def on_grid_size(self, evt):
        """
        Grid size change (rows, cols, nmines) event handler, this happens
        tipically from menus.
        """
        if evt.Id == self.custom_id: # Custom size
            custom_dbox = GameCustomizeDialog(self, *self.next_size)
            if custom_dbox.ShowModal() == wx.ID_CANCEL:
                return
            self.next_size = map(
                lambda p: int(getattr(custom_dbox, p + "_entry").GetValue()),
                ("rows", "cols", "nmines")
            )
        else:
            self.next_size = self.size_dict[evt.Id]
        if self.screen.game.started and not self.screen.game.finished:
            title = "New game size"
            dbox = wx.MessageDialog(self,
                "Do you want to cancel this game and start a new one?",
                title,
                wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dbox.ShowModal() == wx.ID_NO:
                wx.MessageDialog(self,
                    "Your next game will have the new size configuration.",
                    title,
                    wx.ICON_INFORMATION | wx.OK
                ).ShowModal()
                return # Avoids starting a new game
        self.screen.new_game(*self.next_size)

    def on_toggle_numbers(self, evt):
        self.screen.show_numbers = evt.Checked()

    def on_change_interval(self, evt):
        self.screen.is_up = self.intervals[evt.Id]

    def on_about(self, evt):
        abinfo = wx.AboutDialogInfo()
        abinfo.SetArtists([__author__])
        abinfo.SetCopyright("Copyright (C) 2012-2013 " + __author__)
        abinfo.SetDescription('Musical Mines is a musical version of the well '
                              'known game "minesweeper", using intervals (in '
                              'semitones) instead of directly writing the '
                              'number of mined neighbors in each cell.')
        abinfo.SetDevelopers(["Danilo de Jesus da Silva Bellini"])
        abinfo.SetVersion(__version__)
        wx.AboutBox(abinfo)

    def on_close(self, evt):
        # Ask for veto if the game is active
        if self.screen.game.started and not self.screen.game.finished:
            dbox = wx.MessageDialog(self,
                "Are you sure you want to quit?",
                "Game quit",
                wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_QUESTION
            )
            if dbox.ShowModal() == wx.ID_NO:
                return

        # From here, we know it has to close the window
        evt.Skip() # Resume closing the window


class GameApp(wx.App):

    def OnInit(self):
        self.SetAppName("Musical Mines")
        game_window = GameMainWindow(None, style=wx.DEFAULT_FRAME_STYLE)
        game_window.Show()
        self.SetTopWindow(game_window)
        return True

player = None
def main():
    global player
    with lz.AudioIO() as player:
        GameApp(False).MainLoop()

if __name__ == "__main__":
    main()
