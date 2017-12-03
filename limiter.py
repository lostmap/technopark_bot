import time

class RateLimiter:
    """
    chat_id => last_send_time
    """
    def __init__(self):
        self.users = {}

    def can_send_to(self, chat_id):
        now = time.time()
        if not chat_id in self.users:
            self.users[chat_id] = now
            return True

        # 1 message per second 
        diff = now - self.users[chat_id]
        if diff <= 1:
            return False
        self.users[chat_id] = now
