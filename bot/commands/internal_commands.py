from bot.commands.command import InternalCommand


class SendMessageCommand(InternalCommand):
    def __call__(self, arg, user):
        cs = arg.split(' | ')
        if cs[1] == '2':
            self.ttclient.send_message(cs[0], type=2)
        else:
            self.ttclient.send_message(cs[0], user=cs[1])

