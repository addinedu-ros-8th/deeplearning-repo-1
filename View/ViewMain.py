import Constants as cons
import Extensions as extn
from View.View import View
from View.ViewButton import ViewButton
from View.ViewLabel import ViewLabel
class ViewMain(View):
    """
    Responsible for drawing main view
    """
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self.set_mode("main")
        
    def set_mode(self, mode):
        self.clear_subviews()
        self.buttons.clear()
        if mode == "main":
            self.buttons["start"] = ViewButton(
                x=50, y=50,x_end=200, y_end=130,
                label=ViewLabel(text="START"),
                center_label=True)
            self.buttons["exit"] = ViewButton(
                x=220, y=50, x_end=370, y_end=130,
                label=ViewLabel(text="EXIT"), center_label=True)
            self.buttons["lookup"] = ViewButton(
                x=390, y=50, x_end=540, y_end=130,
                label=ViewLabel(text="LOOKUP"), center_label=True)
        
        elif mode == "working":
            self.buttons["pause"] = ViewButton(
                x=50, y=50, x_end=200, y_end=130,
                label=ViewLabel(text="PAUSE"), center_label=True)
            self.buttons["next"] = ViewButton(
                x=220, y=50, x_end=370, y_end=130,
                label=ViewLabel(text="NEXT"), center_label=True)

        elif mode == "lookup":
            self.buttons["back"] = ViewButton(
                x=50, y=50, x_end=200, y_end=130,
                label=ViewLabel(text="BACK"), center_label=True)
            self.buttons["next"] = ViewButton(
                x=220, y=50, x_end=370, y_end=130,
                label=ViewLabel(text="Silver"), center_label=True)
       
        for btn in self.buttons.values():
            self.add_subview(btn)

    def appear(self, frame):
        super().appear(frame)

    def set_button_action(self, name, action):
        if name in self.buttons:
            self.buttons[name].action = action