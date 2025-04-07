class ClientInfo:

    client_list = {}

    def __init__(self, socket):
        self.socket = socket
        self.user_id = None
        self.user_name = None
        self.weight = 0
        self.height = 0
        self.tier = 0
        self.score = 0
        self.routine = []

        ClientInfo.client_list[socket] = self

    @classmethod
    def get_client(cls, socket):
        return cls.client_list.get(socket)
    
    @classmethod
    def remove_client(cls, socket):
        if socket in cls.client_list:
            del cls.client_list[socket]

    @classmethod
    def set_user_info(cls, socket, user_id, user_name, weight, height, tier, score):
        client = cls.get_client(socket)

        if client:
            client.user_id = user_id
            client.user_name = user_name
            client.weight = weight
            client.height = height
            client.tier = tier
            client.score = score

    @classmethod
    def set_routine(cls, socket, routine):
        client = cls.get_client(socket)
        if client:
            client.routine.append(routine)

    @classmethod
    def get_routine(cls, socket):
        client = cls.get_client(socket)
        return client.routine if client else None

    @classmethod
    def get_user_id(cls, socket):
        client = cls.get_client(socket)
        return client.user_id if client else None

    @classmethod
    def get_user_name(cls, socket):
        client = cls.get_client(socket)
        return client.user_name if client else None

    @classmethod
    def get_weight(cls, socket):
        client = cls.get_client(socket)
        return client.weight if client else None

    @classmethod
    def get_height(cls, socket):
        client = cls.get_client(socket)
        return client.height if client else None

    @classmethod
    def get_tier(cls, socket):
        client = cls.get_client(socket)
        return client.tier if client else None

    @classmethod
    def get_score(cls, socket):
        client = cls.get_client(socket)
        return client.score if client else None

