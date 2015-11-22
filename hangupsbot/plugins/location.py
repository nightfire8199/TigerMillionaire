import plugins
import asyncio
import aiohttp
import io
import logging

#logger = logging.getlogger(__name__)

def initialise():
    plugins.register_handler(watch_for_geodata, type='message')

@asyncio.coroutine
def watch_for_geodata(bot, event, command):
    if event.user.is_self:
        return

    if "https://maps.google.com/maps?q=" in event.text:
        print("Geodata Found")
        yield from bot.coro_send_message(event.conv_id, event.text)
