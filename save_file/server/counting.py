class ExerciseCounter:
    def __init__(self, exercise):
        self.exercise = exercise
        self.state = {0: "up", 1: "down"}
        self.count = 0
        self.up_angle = 0
        self.down_angle = 0
        self.set_exercise_thresholds()

    def set_exercise_thresholds(self):
        if self.exercise == "squat":
            self.up_angle = 160
            self.down_angle = 130
        elif self.exercise == "shoulder":
            self.up_angle = 130
            self.down_angle = 50
        elif self.exercise == "knee":
            self.up_angle = 70
            self.down_angle = 160

    def update(self, index, angle):
        if self.exercise == "shoulder":
            if self.state[index] == "up" and angle > self.up_angle:
                self.state[index] = "down"
                if self.state[0] == "down" and self.state[1] == "down":
                    self.count += 1
            elif self.state[index] == "down" and angle < self.down_angle:
                self.state[index] = "up"
        elif self.exercise == "squat":
            if self.state[index] == "down" and angle < self.down_angle:
                self.state[index] = "up"
                if self.state[0] == "up" and self.state[1] == "up":
                    self.count += 1
            elif self.state[index] == "up" and angle > self.up_angle:
                self.state[index] = "down"
        elif self.exercise == "knee":
            if self.state[index] == "up" and angle < self.up_angle:
                self.state[index] = "down"
                self.count += 0.5
            elif self.state[index] == "down" and angle > self.down_angle:
                self.state[index] = "up"

    def get_count(self):
        return self.count

    def reset_count(self):
        self.count = 0