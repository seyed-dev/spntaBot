import asyncio
import os
import re
from os.path import exists, join

from bot import config, save_config, load_plugins, WD
from message import Message


def add_plugin(plugin_name):
    if plugin_name in config['plugins']:
        return "This plugin is already active"
    if not exists(join(WD, "plugins", plugin_name + ".py")):
        return "There is no file that name is " + plugin_name + " in plugins directory"
    config['plugins'].append(plugin_name)
    save_config()
    load_plugins()
    return "Plugin " + plugin_name + " Enable Successfully"


def remove_plugin(plugin_name):
    if plugin_name == "plugins":
        return "You Can not disable plugins plugin !! :|"
    if plugin_name not in config['plugins']:
        return "This plugin is not active"
    config['plugins'].remove(plugin_name)
    save_config()
    load_plugins()
    return "Plugin " + plugin_name + " Disable Successfully"


def reload_plugin():
    load_plugins()
    return "Plugins Reloaded !"


def show_plugin():
    plugin_files = [files for files in os.listdir(join(WD, "plugins")) if re.search("^(.*)\.py$", files)]
    show_string = "*Plugins List* \n\n"
    for plugin_file in plugin_files:
        plugin_file = plugin_file.replace(".py", "")
        if plugin_file == "__init__":
            continue
        if plugin_file in config['plugins']:
            show_string += "✅ *" + plugin_file.capitalize() + "*\n"
        else:
            show_string += "❌ *" + plugin_file.capitalize() + "*\n"
    return show_string


@asyncio.coroutine
def run(message, matches, chat_id, step):
    response = Message(chat_id)
    if matches == "/plugins":
        response.set_text(show_plugin(), parse_mode="Markdown")
    if matches[0] == "enable":
        response.set_text(add_plugin(matches[1]))
    if matches[0] == "disable":
        response.set_text(remove_plugin(matches[1]))
    if matches == "reload":
        response.set_text(reload_plugin())
    return [response]


plugin = {
    "name": "Plugins",
    "desc": "Show the plugins",
    "run": run,
    "sudo": True,
    "patterns": ["^[!/#]plugins (enable) (.+?)$",
                 "^[!/#]plugins (disable) (.+?)$",
                 "^[!/#]plugins (reload)$",
                 "^[!/#]plugins$",
                 ]
}
