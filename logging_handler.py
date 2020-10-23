import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class log:
    def __init__(self, f):
        self.f = f
        self.logger = logging.getLogger(f.__module__)

    def __call__(self, *args):
        self.logger.info(
            'chat_id:[{}] user_name:[{}] enters:[{}]'.format(args[0].effective_chat.id, args[0].effective_user.username,
                                                             self.f.__name__))
        return self.f(*args)


class logInline:
    def __init__(self, f):
        self._f = f

    def __call__(self, *args):
        chat_id = args[0].effective_chat.id
        msg = "chat_id: {} || user_name: {} || function: {}".format(chat_id, args[0].effective_user.username, self._f.__name__)
        print("{} : {}".format(datetime.today(), msg))
        return self._f(*args)
