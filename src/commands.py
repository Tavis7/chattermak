from enum import Enum

import chatbot

class Command:
    def __init__(self, name, desc, func):
        command_name = f"/{name}"
        self.name = command_name
        self.desc = desc
        self.func = func
        commands[command_name] = self



class CommandAction(Enum):
    NOP = 0
    SAY = 1
    QUIT = 2


def commandHelp(args, generator):
    if len(args) > 0:
        print("Error: No arguments permitted")
    else:
        for key in commands:
            c = commands[key]
            name_length = len(c.name)
            print(c.name + " " * (16 - name_length) + c.desc)
    return CommandAction.NOP, None

def commandSay(args, generator):
    action = CommandAction.NOP
    text = None
    if len(args) < 1:
        print("Error: at least one argument required")
    else:
        action = CommandAction.SAY
        text = args

    return action, text

def commandListHistory(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
    else:
        print("History:")
        print(f"{chatbot.tokens_to_string(generator.history)}")
    return CommandAction.NOP, None

def commandListTransitions(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
    else:
        chatbot.debug_print_weights(generator.transitions)
    return CommandAction.NOP, None

def commandQuit(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
        return CommandAction.NOP, None
    else:
        return CommandAction.QUIT, None

commands = {}
Command("say", "Send chat message, can start with '/'", commandSay),
Command("history", "List chat history", commandListHistory),
Command("transitions", "Print transition probabilities", commandListTransitions),
Command("help", "List available commands", commandHelp),
Command("quit", "Quit", commandQuit),
