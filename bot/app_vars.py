from __future__ import annotations
import os
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from bot.translator import Translator

app_name = "TTMediaBot"
app_version = "2.3.1"
client_name = app_name + "-V" + app_version
about_text: Callable[[Translator], str] = lambda translator: translator.translate(
    """\
TTMediaBot-V4.0
Olá! Eu sou Nuno Costa. Este é o meu fork do TTMediaBot para TeamTalk 5.
Este repositório foca em estabilidade, performance e suporte para YouTube Music.
Repositório: https://www.github.com/nunotfc/TTMediaBot

Diferenças em relação ao original:
- Comando de fila (queue): modo de reprodução em fila com enfileiramento de tracks
- Comando /update: verifica e instala atualizações pip, reinicia o bot automaticamente
- Comando /bb: bass boost ajustável (0-10)
- Comando /pi: pitch control (-12 a +12 semitons)
- Comando /ep: salvar posição de reprodução ao pausar/parar
- Comandos encadeados com | (ex: t | v 30)
- Cache separada em arquivos (recents.dat, favorites.dat, queue.dat, meta.json)
- Correções de memory leak, uso de CPU e race condition na inicialização
- Resiliência: cache corrompido não crasha o bot
- Suporte a Dropbox como serviço de stream

Autores Originais: Amir Gumerov, Vladislav Kopylov, Beqa Gozalishvili, Kirill Belousov.\
"""
)
fallback_service = "yt"
loop_timeout = 0.1
max_message_length = 256
recents_max_lenth = 32
tt_event_timeout = 2

directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
