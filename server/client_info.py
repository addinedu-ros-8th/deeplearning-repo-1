from collections import deque

class ClientInfo:
    def __init__(self, socket):
        self.socket = socket
        self.user_id = None
        self.user_name = None
        self.weight = 0
        self.height = 0
        self.tier = 0
        self.score = 0
        self.routine = []

    def set_user_info(self, user_id, user_name=None, weight=0, height=0, tier=0, score=0):
        self.user_id = user_id
        self.user_name = user_name
        self.weight = weight
        self.height = height
        self.tier = tier
        self.score = score

    def append_image_buffer(self, frame):
        self.image_buffer.append(frame)

    def get_image_buffer(self):
        return self.image_buffer

    def set_routine(self, routine):
        self.routine.append(routine)

    def get_routine(self):
        return self.routine

    def get_user_id(self):
        return self.user_id

    def get_user_name(self):
        return self.user_name

    def get_weight(self):
        return self.weight

    def get_height(self):
        return self.height

    def get_tier(self):
        return self.tier

    def get_score(self):
        return self.score