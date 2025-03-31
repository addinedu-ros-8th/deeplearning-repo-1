import cv2
import Constants as cons
from Camera import Camera
from Controller.Detector import analyze_user
from Controller.Hands import set as update_hand_coords
from View.ViewMain import ViewMain
from Controller.Controller import Controller

class ControllerMain(Controller):
    def __init__(self):
        super().__init__()
        self.cap = Camera()
        self.view = ViewMain(self)

    def run(self):
        while True:
            if self.cap.frame is None:
                continue

            frame = self.cap.frame.copy()
            analyze_user(frame)
            update_hand_coords()

            self.view.appear(frame)
            cv2.imshow(cons.window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.stop()
        cv2.destroyAllWindows()
