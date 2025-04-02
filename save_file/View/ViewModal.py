import Constants as cons
from View.View import View
from View.ViewButton import ViewButton
from View.ViewLabel import ViewLabel

class ViewModalPause(View):
    """
    Responsible for drawing paused modal view

    Draws "Exit" and "Continue" buttons centered in the screen.
    """
    def __init__(self):
        super().__init__()
        
        spacing_between_bttns = cons.vw_bttn_spacing * 6
        
        # Horizontally centerize buttons
        x_exit = int(cons.window_width / 2 - (cons.vw_bttn_width + spacing_between_bttns / 2))
        y_exit = int(cons.window_height * 0.4)
        x_exit_end = x_exit + cons.vw_bttn_width
        y_exit_end = y_exit + cons.vw_bttn_height
        # Layout exit button
        self.bttn_back = ViewButton(
            x=x_exit,
            y=y_exit,
            x_end=x_exit_end,
            y_end=y_exit_end,

            label=ViewLabel(text="Back"),
            # action=on_exit,
            center_label=True
        )

        x_continue = x_exit_end + spacing_between_bttns
        # Layout continue button
        self.bttn_continue = ViewButton(
            x=x_continue, 
            y=y_exit,
            x_end= x_continue + cons.vw_bttn_width,
            y_end= y_exit_end, 
            label=ViewLabel(text='Continue'),
            center_label=True
        )

        self.add_subview(self.bttn_back)
        self.add_subview(self.bttn_continue)


class ViewModalExit(View):
    """
    Responsible for drawing paused modal view

    Draws "Exit" and "Continue" buttons centered in the screen.
    """
    def __init__(self):
        super().__init__()
        
        spacing_between_bttns = cons.vw_bttn_spacing * 6
        
        # Horizontally centerize buttons
        x_exit = int(cons.window_width / 2 - (cons.vw_bttn_width + spacing_between_bttns / 2))
        y_exit = int(cons.window_height * 0.4)
        x_exit_end = x_exit + cons.vw_bttn_width
        y_exit_end = y_exit + cons.vw_bttn_height
        # Layout exit button
        self.bttn_yes = ViewButton(
            x=x_exit,
            y=y_exit,
            x_end=x_exit_end,
            y_end=y_exit_end,
            label=ViewLabel(text="Yes"),
            center_label=True
        )

        x_continue = x_exit_end + spacing_between_bttns
        # Layout continue button
        self.bttn_no = ViewButton(
            x=x_continue, 
            y=y_exit,
            x_end= x_continue + cons.vw_bttn_width,
            y_end= y_exit_end, 
            label=ViewLabel(text='No'),
            center_label=True
        )

        self.add_subview(self.bttn_yes)
        self.add_subview(self.bttn_no)