from queue import Queue
from bot.TeamTalk.structs import *
from bot.console.thread import ConsoleThread


class Console:
    def __init__(self):
        self.message_queue: Queue[Message] = Queue()
        self.thread = ConsoleThread(self)
        self.channel_mock = Channel(
            id=1, name="ConsoleChannel", topic="", max_users=1, type=ChannelType.Default
        )
        account = UserAccount(
            username="Console",
            password="",
            note="",
            type=UserType.Admin,
            rights=UserRight.OperatorEnable,
            init_channel="",
        )
        self.user_mock = User(
            id=2**14 - 1,
            nickname="Console",
            username="Console",
            status="",
            gender=UserStatusMode.N,
            state=UserState.Null,
            channel=self.channel_mock,
            client_name="Console",
            version=1,
            user_account=account,
            type=UserType.Admin,
            is_admin=True,
            is_banned=False,
        )

    def run(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.thread.close()

    def build_message(self, text: str) -> Message:
        return Message(
            text=text,
            user=self.user_mock,
            channel=self.channel_mock,
            type=MessageType.User,
        )
