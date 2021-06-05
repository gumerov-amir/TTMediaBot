from bot.commands.command import InternalCommand


class SendMessageCommand(InternalCommand):
    def __call__(self, arg, user):
        cs = arg.split(' | ')
        if cs[0] == '1':
            self.ttclient.send_message(' | '.join(cs[2::]), user=int(cs[1]))
        else:
            self.ttclient.send_message(' | '.join(cs[1::]), type=int(cs[0]))

