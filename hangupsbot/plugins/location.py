import plugins
import asyncio
import logging

#logger = logging.getlogger(__name__)

def _initialise():
    plugins.register_handler(_watch_for_geodata, type="message", priority=50)
    plugins.register_user_command(["location"])

def isLabel(bot, uID, label):
    if bot.memory.exists(['location',uID,label]):
        return True
    else
        return False

def getLoc(bot, uID, label):
    if not bot.memory.exists(['location',uID,label]):
        return ""
    else:
        return bot.memory.get_by_path(['location', uID]).get(label)

@asyncio.coroutine
def _watch_for_geodata(bot, event, command):
    if event.user.is_self:
        return

    if "https://maps.google.com/maps?q=" in event.text:
        if not bot.memory.exists(['location']):
            bot.memory.set_by_path(['location'], {})
        if not bot.memory.exists(['location',event.user_id]):
            bot.memory.set_by_path(['location', event.user_id], {})
        bot.memory.get_by_path(['location', event.user_id])['current'] = event.text[31:]
        yield from bot.coro_send_message(event.conv_id, _("<i>Current</i> location set for <b>{}</b>").format(event.user.full_name))

def location(bot, event, *args):
    ### This operation should not exist in a full release, included for development
    if len(args) == 1:
        label = args[0]
        if not bot.memory.exists(['location',event.user_id,label]):
             yield from bot.coro_send_message(event.conv_id, _("No location '<i>{}</i>' found for <b>{}</b>").format(label, event.user.full_name))
        else:
            bot.memory.get_by_path(['location', event.user_id])['current'] = bot.memory.get_by_path(['location', event.user_id]).get(label)
            yield from bot.coro_send_message(event.conv_id, _("<i>current</i> location set to <i>{}</i> for <b>{}</b>").format(label, event.user.full_name))
    elif len(args) > 1:
        subcmd = args[0]
        if subcmd == "set":
            label = args[1]
            if not bot.memory.exists(['location',event.user_id]):
                yield from bot.coro_send_message(event.conv_id, _("No location data found for <b>{}</b>").format(event.user.full_name))
            else:
                bot.memory.get_by_path(['location', event.user_id])[label] = bot.memory.get_by_path(['location', event.user_id]).get('current')
                yield from bot.coro_send_message(event.conv_id, _("<i>{}</i> set to <i>current</i> location for <b>{}</b>").format(label, event.user.full_name))
