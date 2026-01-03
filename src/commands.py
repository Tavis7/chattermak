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
    PASS = 2
    QUIT = 3


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

def commandPass(args, generator):
    action = CommandAction.NOP
    text = None
    if len(args) != 0:
        print("Error: No arguments permitted")
    else:
        action = CommandAction.PASS
        text = None

    return action, text
def commandListHistory(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
    else:
        print("History:")
        for message in generator.chatHistory:
            print(f"{message.user}> {chatbot.tokens_to_string(message.tokens)}")
    return CommandAction.NOP, None

def commandListTransitions(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
    else:
        chatbot.debug_print_weights(generator.transitions)
    return CommandAction.NOP, None


def printDict(name, item, prefix = "    "):
    sep = ""
    if len(name) > 0:
        sep = ": "
    print(f"{prefix}{name}{sep}" + "{")
    for key in item:
        val = item[key]
        printItem(repr(key), val, prefix)
    print(f"{prefix}" + "}")

def printList(name, item, prefix = "    "):
    sep = ""
    if len(name) > 0:
        sep = ": "
    print(f"{prefix}{name}{sep}" + "[")
    for val in item:
        printItem("", val, prefix)
    print(f"{prefix}" + "]")

def printItem(name, item, prefix = ""):
    if hasattr(item, "__dict__"):
        printDict(f"{name} ({type(item).__name__})", item.__dict__, prefix + "    ")
    elif isinstance(item, dict):
        printDict(name, item, prefix + "    ")
    elif isinstance(item,list):
        printList(name, item, prefix + "    ")
    else:
        sep = ""
        if len(name) > 0:
            sep = ": "
        print(f"{prefix + '    '}{name}{sep}{item}")


def commandPrintGenerator(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
    else:
        printItem("generator", generator)
    return CommandAction.NOP, None

def commandQuit(args, generator):
    if len(args) > 0:
        print("Error: no arguments permitted") # todo
        return CommandAction.NOP, None
    else:
        return CommandAction.QUIT, None

commands = {}
Command("say", "Send chat message, can start with '/'", commandSay),
Command("pass", "Skip your turn", commandPass),
Command("history", "List chat history", commandListHistory),
Command("transitions", "Print transition probabilities", commandListTransitions),
Command("generator", "Print generator", commandPrintGenerator),
Command("help", "List available commands", commandHelp),
Command("quit", "Quit", commandQuit),
