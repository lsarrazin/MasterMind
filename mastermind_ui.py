'''
Mastermind User Interface

This module provides the class MainWindow that acts as the application window
'''

import math
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo
from game import Game


class MainWindow(Gtk.ApplicationWindow):
    '''
    Main window of the application
    '''

    pin_colors = [
        [0.0, 0.0, 0.0],  # Black (deep gray)
        [1.0, 1.0, 1.0],  # White
        [1.0, 0.0, 0.0],  # Red
        [1.0, 1.0, 0.0],  # Yellow
        [0.0, 1.0, 0.0],  # Green
        [0.4, 0.2, 0.0],  # Brown
        [0.0, 0.0, 1.0],  # Blue
        [1.0, 0.5, 1.0]   # Weird
    ]


    ############# Graphics --------------------------------------------------------#################

    @staticmethod
    def draw_pin(context, x, y, radius, color = (1.0, 0.5, 0.25)):
        '''
        Draw a pin

        Parameters:
            context (cairo): Cairo context where to draw
            x (int): x coordinate of pin center
            y (int): y coordinate of pin center
            radius (int): radius of pin
            color ((int,int,int)): RGB colors of pin

        Returns:
            no return
        '''

        (r,g,b) = color

        if r+g+b == 0.0:
            context.set_source_rgb(1.0, 1.0, 1.0)
        else:
            context.set_source_rgb(0.0, 0.0, 0.0)
        context.fill_preserve()
        context.arc(x, y, radius-1, 0, 2 * math.pi)
        context.fill()

        pattern = cairo.RadialGradient(x, y, radius, x - radius/3, y - radius/3, radius/4)
        if r+g+b == 0.0:
            pattern.add_color_stop_rgba(0, r, g, b, 1)
            pattern.add_color_stop_rgba(1, r, g, b, 0.5)
        else:
            pattern.add_color_stop_rgba(0, r, g, b, 0.5)
            pattern.add_color_stop_rgba(1, r, g, b, 1)

        context.set_source(pattern)
        context.arc(x, y, radius, 0, 2 * math.pi)
        context.fill()


    @staticmethod
    def draw_rectangle(context, x, y, width, height, aspect = 1.0):
        '''
        Draw a rectangle to materialize a pin location (can also be used for full board)

        Parameters:
            cr (cairo): Cairo context where to draw
            x (int): x coordinate of upper-left corner
            y (int): y coordinate of upper-left corner
            width (int): width of rectangle
            height (int): height of rectangle
            aspect (float): aspect of angles

        Returns:
            no return
        '''

        def inner_draw_rectangle(x, y, bg, color): #r, g, b, a):
            corner_radius = 4
            radius = corner_radius / aspect
            degrees = math.pi / 180.0

            context.new_sub_path()
            context.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
            context.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
            context.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
            context.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
            context.close_path()

            if bg:
                context.set_source_rgb(0.6, 0.3, 0.2)
            context.fill_preserve()
            context.set_source_rgba(*color) #(r, g, b, a)
            context.set_line_width(3.0)
            context.stroke()

        inner_draw_rectangle(x, y, True, (0.9, 0.9, 0.2, 0.25))
        inner_draw_rectangle(x+1, y+1, False, (0.7, 0.4, 0.2, 0.5))


    @staticmethod
    def compute_color_pin_square(row, pin):
        '''
        Compute the coordinates + size of a color (guess/solution) pin square

        Parameters:
            row (int): line (from 0 -- bottom to 11 -- top), or 99 for solution
            pin (int): pin number (from 0 to 5)
        '''
        return (120 + pin * 48, 40, 40, 40) if row == 99 \
               else (120 + pin * 48, 728 - row * 56, 40, 40)


    @staticmethod
    def compute_score_pin_square(row, pin):
        '''
        Compute the coordinates + size of a score pin square

        Parameters:
            row (int): line (from 0 -- bottom to 11 -- top)
            pin (int): pin number (from 0 to 5)
        '''
        return (20 + pin * 16, 728 - row * 56 + 12, 8, 8)


    def draw_score_pin(self, cairo_context, position, color):
        '''
        Draw a score pin

        Parameters:
            cairo_context (): cairo context where to output drawing
            position ((int,int,int,int)): x,y,w,h coordinates of pin square
            color (int): pin color (0: black, 1: white, -1: empty)
        '''
        (score_x, score_y, score_w, score_h) = position
        self.draw_rectangle(cairo_context, score_x, score_y, score_w, score_h, 1.2)

        if color >= 0:
            self.draw_pin(cairo_context, score_x + score_w // 2, score_y + score_h // 2,
                          (score_w * 2) // 3, self.pin_colors[color])


    def draw_color_pin(self, cairo_context, position, color):
        '''
        Draw a color pin

        Parameters:
            cairo_context (): cairo context where to output drawing
            position ((int,int,int,int)): x,y,w,h coordinates of pin square
            color (int): pin color (0: black, 1: white, ..., -1: empty)
        '''
        (color_x, color_y, color_w, color_h) = position
        self.draw_rectangle(cairo_context, color_x, color_y, color_w, color_h, 1.2)

        if color >= 0:
            self.draw_pin(cairo_context, color_x + color_w // 2, color_y + color_h // 2,
                          (color_w * 9) // 20, self.pin_colors[color])


    ############# Events --------------------------------------------------------###################


    def on_delete_event(self, *args):
        d = Gtk.MessageDialog(transient_for=self, modal=True,
                              buttons=Gtk.ButtonsType.OK_CANCEL)
        d.props.text = 'Are you sure you want to quit?'
        response = d.run()
        d.destroy()

        if response == Gtk.ResponseType.OK:
            self.on_destroy()
            return False

        return True


    def on_destroy(self, *args):
        self.app.quit()


    def on_pins_draw(self, dar, cr):

        for y in range(3):
            for x in range(3):
                sx = 8 + x * 48
                sy = 8 + y * 48

                color = y * 3 + x
                if color == self.selected_color:
                    self.draw_pin(cr, sx+20, sy+20, 20, self.pin_colors[color])
                elif (y*3+x) < 8:
                    self.draw_pin(cr, sx+20, sy+20, 18, self.pin_colors[color])


    def on_pins_event(self, box, event):

        if event.type == Gdk.EventType.BUTTON_PRESS:
            mx = int(event.x)
            my = int(event.y)

            self.selected_color = -1
            color = -1
            for y in range(3):
                for x in range(3):
                    sx = 8 + x * 48
                    sy = 8 + y * 48

                    if (sx < mx + 2) and (mx < sx + 36) and (sy < my + 2) and (my < sy + 36):
                        color = y * 3 + x

            if color >= 0 and color < len(self.pin_colors):
                self.selected_color = color

            self.dar_pins.queue_draw()


    def on_board_draw(self, dar, cairo_context):
        '''
        Draw the game board (backgroud and all content)
        '''

        # Draw board background
        self.draw_rectangle(cairo_context, 5, 5, 368, 790)

        for row in range(12):

            if row == self.current_line:
                line = self.current_guess
            else:
                line = self.game.get_line(row)
            score = self.game.get_score(row)

            sb = score[0]
            sw = score[1]

            for slot in range(5):

                score_pos = self.compute_score_pin_square(row, slot)
                self.draw_score_pin(cairo_context, score_pos,
                                    0 if sb > 0 else 1 if sw > 0 else -1)
                sb -= 1
                if sb < 0:
                    sw -= 1

                color_pos = self.compute_color_pin_square(row, slot)
                self.draw_color_pin(cairo_context, color_pos,
                                    -1 if line[slot] == 'x' else int(line[slot]))

        # Display solution
        if self.show_solution:
            solution = self.game.get_solution()
            for slot in range(5):
                color_pos = self.compute_color_pin_square(99, slot)
                self.draw_color_pin(cairo_context, color_pos, int(solution[slot]))
        else:
            self.draw_rectangle(cairo_context, 114, 32, 5 * 48 + 4, 56)


    def inside_square(self, box, pos_x, pos_y):
        (left, top, width, height) = box
        return (pos_x >= left) and (pos_x <= (left+width)) and\
               (pos_y >= top) and (pos_y <= (top+height))


    def on_board_event(self, box, event):

        if not self.game_in_progress:
            return

        if event.type == Gdk.EventType.BUTTON_PRESS:
            mouse_x = int(event.x)
            mouse_y = int(event.y)

            if self.selected_color >= 0:
                for slot in range(5):
                    square = self.compute_color_pin_square(self.current_line, slot)
                    if self.inside_square(square, mouse_x, mouse_y):
                        if str(self.selected_color) == self.current_guess[slot]:
                            # Zero slot
                            self.current_guess[slot] = 'x'
                        else:
                            self.current_guess[slot] = str(self.selected_color)
                        self.dar_board.queue_draw()


    def on_btn_solution_clicked(self, *args):
        self.show_solution = not self.show_solution
        self.dar_board.queue_draw()


    def on_btn_reset_clicked(self, *args):
        self.current_guess = ['x' for i in range(5)]
        self.dar_board.queue_draw()


    def on_btn_validate_clicked(self, *args):

        if 'x' in self.current_guess:
            return

        found = self.game.submit(self.current_guess)
        self.current_line = self.game.get_guess_line()
        self.current_guess = ['x' for i in range(5)]

        if found:
            self.game_in_progress = False
            self.on_btn_solution_clicked(args)
        elif self.current_line >= 12:
            self.game_in_progress = False
            self.current_line = 12
            self.on_btn_solution_clicked(args)
        else:
            self.dar_board.queue_draw()


    def on_mnu_new_clicked(self, *args):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True,
                              buttons=Gtk.ButtonsType.OK_CANCEL)
        dialog.props.text = 'Are you sure you want to restart a new game?'
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            self.new_game()


    def new_game(self):
        self.game.new_game()
        self.show_solution = False
        self.selected_color = -1
        self.current_guess = ['x' for i in range(5)]
        self.current_line = 0
        self.game_in_progress = True
        self.dar_pins.queue_draw()
        self.dar_board.queue_draw()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = self.props.application

        """
        self.selected_color = -1
        self.current_line = 0
        self.current_guess = ['x' for i in range(5)]
        self.game_in_progress = False
        self.show_solution = False
        """

        builder = Gtk.Builder()
        builder.add_from_file("MastermindUI.glade")

        self.window = builder.get_object("wndMain")
        self.window.connect('delete-event', self.on_delete_event)
        self.window.connect('destroy', self.on_destroy)

        self.dar_pins = builder.get_object("darPins")
        self.dar_pins.connect('draw', self.on_pins_draw)

        self.dar_board = builder.get_object("darBoard")
        self.dar_board.connect('draw', self.on_board_draw)

        builder.get_object("evtPins").connect('event', self.on_pins_event)
        builder.get_object("evtBoard").connect('event', self.on_board_event)
        builder.get_object("mnuNew").connect('activate', self.on_mnu_new_clicked)
        builder.get_object("mnuQuit").connect('activate', self.on_delete_event)
        builder.get_object("btnSolution").connect('clicked', self.on_btn_solution_clicked)
        builder.get_object("btnValidate").connect('clicked', self.on_btn_validate_clicked)
        builder.get_object("btnReset").connect('clicked', self.on_btn_reset_clicked)

        self.window.show_all()

        self.game = Game()
        self.new_game()
