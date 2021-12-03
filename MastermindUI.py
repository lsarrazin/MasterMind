import math

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import cairo

from Game import Game


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


    ############# Graphics --------------------------------------------------------#####################

    def draw_pin(self, cr, x, y, radius, color = (1.0, 0.5, 0.25)):

        (r,g,b) = color

        if r+g+b == 0.0:
            cr.set_source_rgb(1.0, 1.0, 1.0)
        else:
            cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.fill_preserve()
        cr.arc(x, y, radius-1, 0, 2 * math.pi)
        cr.fill()

        pat = cairo.RadialGradient(x, y, radius, x - radius/3, y - radius/3, radius/4)
        if r+g+b == 0.0:
            pat.add_color_stop_rgba(0, r, g, b, 1)
            pat.add_color_stop_rgba(1, r, g, b, 0.5)
        else:
            pat.add_color_stop_rgba(0, r, g, b, 0.5)
            pat.add_color_stop_rgba(1, r, g, b, 1)

        cr.set_source(pat)
        cr.arc(x, y, radius, 0, 2 * math.pi)
        cr.fill()


    def draw_rectangle(self, cr, x, y, width, height, aspect = 1.0):
        '''
        Draw a rectangle to materialize a pin location (can also be used for full board)
        
        Parameters:
            cr (cairo): Cairo context where to draw
            x (int): 
            y (int):

        Returns:
            no return       
        '''
        
        def inner_draw_rectangle(x, y, bg, r, g, b, a):
            corner_radius = 4
            radius = corner_radius / aspect
            degrees = math.pi / 180.0

            cr.new_sub_path()
            cr.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
            cr.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
            cr.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
            cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
            cr.close_path()

            if bg:
                cr.set_source_rgb(0.6, 0.3, 0.2)
            cr.fill_preserve()
            cr.set_source_rgba(r, g, b, a)
            cr.set_line_width(3.0)
            cr.stroke()

        inner_draw_rectangle(x, y, True, 0.9, 0.9, 0.2, 0.25)
        inner_draw_rectangle(x+1, y+1, False, 0.7, 0.4, 0.2, 0.5)


    ############# Events --------------------------------------------------------#####################


    def on_delete_event(self, *args):
        d = Gtk.MessageDialog(transient_for=self, modal=True,
                              buttons=Gtk.ButtonsType.OK_CANCEL)
        d.props.text = 'Are you sure you want to quit?'
        response = d.run()
        d.destroy()

        if response == Gtk.ResponseType.OK:
            return self.on_destroy()
        else:
            return False
        

    def on_destroy(self, *args):
        self.app.quit()
        return True

    
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

        pass


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

                    if sx < mx + 2 and mx < sx + 36:
                        if sy < my + 2 and my < sy + 36:
                            color = y * 3 + x
            
            if color >= 0 and color < len(self.pin_colors):
                self.selected_color = color

            self.dar_pins.queue_draw()

        pass


    def on_board_draw(self, dar, cairo_context):

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

                px = 20 + slot * 16
                py = 728 - row * 56 + 12
                self.draw_rectangle(cairo_context, px, py, 8, 8, 1.2)

                if sb > 0:
                    self.draw_pin(cairo_context, px+4, py+4, 6, self.pin_colors[0])
                    sb -= 1
                elif sw > 0:
                    self.draw_pin(cairo_context, px+4, py+4, 6, self.pin_colors[1])
                    sw -= 1

                sx = 120 + slot * 48
                sy = 728 - row * 56
                self.draw_rectangle(cairo_context, sx, sy, 40, 40)

                if line[slot] != 'x':
                    self.draw_pin(cairo_context, sx+20, sy+20, 18, self.pin_colors[int(line[slot])])


        if self.show_solution:
            solution = self.game.get_solution()
            for slot in range(5):
                sx = 120 + slot * 48
                self.draw_rectangle(cairo_context, sx, 40, 40, 40)

                if solution[slot] != 'x':
                    self.draw_pin(cairo_context, sx+20, 60, 18, self.pin_colors[int(solution[slot])])
        else:
            self.draw_rectangle(cairo_context, 116, 32, 5 * 48 + 4, 56)
        
        pass


    def on_board_event(self, box, event):

        if not self.game_in_progress:
            return False

        if event.type == Gdk.EventType.BUTTON_PRESS:
            mx = int(event.x)
            my = int(event.y)

            if self.selected_color >= 0:
                
                lys = 728 - self.current_line * 56
                lye = lys + 40

                if lys <= my and my <= lye:

                    for slot in range(5):

                        sxs = 120 + slot * 48
                        sxe = sxs + 40

                        if sxs <= mx and mx <= sxe:
                            self.current_guess[slot] = str(self.selected_color)
                            self.dar_board.queue_draw()

        return True


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

        self.selected_color = -1
        self.current_line = 0
        self.current_guess = ['x' for i in range(5)]
        self.game_in_progress = False
        self.show_solution = False

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

