class User:
    all_users = dict()

    def __init__(self, user_id):
        self.city = None
        self.city_id = None
        self.amount_of_hotels = None
        self.if_photo_for_hotels = False
        self.amount_of_photos = None
        self.check_in_date = None
        self.check_out_date = None
        self.sort_order = None
        self.min_price = None
        self.max_price = None
        self.min_d = None
        self.max_d = None
        self.count_action = 0
        self.history = list()

        User.add_user(user_id, self)

    @classmethod
    def add_user(cls, user_id, user_info):
        cls.all_users[user_id] = user_info

    @staticmethod
    def get_user(user_id):
        if User.all_users.get(user_id) is None:
            new_user = User(user_id)
            return new_user
        return User.all_users.get(user_id)