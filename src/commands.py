from enum import Enum

import chatbot
import savefile
from main import Context
from collections.abc import Callable
from typing import Literal
import typing

class CommandAction(Enum):
    NOP = 0
    SAY = 1
    PASS = 2
    QUIT = 3


type CommandResult = tuple[CommandAction, str|None]

class Command:
    def __init__(self, name:str, desc:str, func:Callable[[str, Context], CommandResult], *, debug:bool = False):
        command_name = f"/{name}"
        self.name = command_name
        self.desc = desc
        self.func = func
        self.debug = debug
        commands[command_name] = self


def commandParseArgs(argStr:str) -> list[str]:
    return argStr.split()

def commandHelp(argStr:str, context:Context) -> CommandResult:
    debug = False
    args = commandParseArgs(argStr)
    for arg in args:
        print(f"args: {repr(args)}")
        print(f"arg: {arg}")
        if not debug and arg == "debug":
            debug = True
        else:
            print(f"Error: invalid argument: {arg}")
            print(f"    in {repr(args)}")
            return CommandAction.NOP, None

    else:
        for key in commands:
            if debug or not commands[key].debug:
                c = commands[key]
                name_length = len(c.name)
                print(c.name + " " * (16 - name_length) + c.desc)
    return CommandAction.NOP, None

def commandSay(argStr:str, context:Context) -> CommandResult:
    action = CommandAction.NOP
    text = None
    if len(argStr) == 0:
        print("Error: Argument required")
    else:
        action = CommandAction.SAY
        text = argStr

    return action, text

def commandPass(argStr:str, context:Context) -> CommandResult:
    action = CommandAction.NOP
    text = None
    if len(argStr) > 0:
        print("Error: No arguments permitted")
    else:
        action = CommandAction.PASS
        text = None

    return action, text
def commandListHistory(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
    else:
        print("History:")
        for message in context.generator.chatHistory:
            print(f"{message.user}> {chatbot.tokens_to_string(message.tokens)}")
    return CommandAction.NOP, None

def commandListTransitions(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
    else:
        chatbot.debug_print_weights(context.generator.transitions)
    return CommandAction.NOP, None


def printDict(name:str, item:dict[typing.Any, typing.Any], prefix:str = "    ") -> None:
    sep = ""
    if len(name) > 0:
        sep = ": "
    print(f"{prefix}{name}{sep}" + "{")
    for key in item:
        val = item[key]
        printItem(repr(key), val, prefix)
    print(f"{prefix}" + "}")

def printList(name:str, item:list[typing.Any], prefix:str = "    ") -> None:
    sep = ""
    if len(name) > 0:
        sep = ": "
    print(f"{prefix}{name}{sep}" + "[")
    for val in item:
        printItem("", val, prefix)
    print(f"{prefix}" + "]")

def printItem(name:str, item:typing.Any, prefix:str = "") -> None:
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


def commandPrintGenerator(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
    else:
        printItem("generator", context.generator)
    return CommandAction.NOP, None

def commandPrintGeneratorSerialized(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
    else:
        serialized = savefile.serializeGenerator(context.generator)
        print(serialized)
    return CommandAction.NOP, None

def commandQuit(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
        return CommandAction.NOP, None
    else:
        if context.generator.modified:
            i = input("Current chat is not saved. [S]ave/[Q]uit/[C]ancel: ")
            match i.lower():
                case "s":
                    savefile.saveChat(context)
                case "q":
                    print("Exiting without saving")
                    pass
                case _:
                    print("Cancelling")
                    return CommandAction.NOP, None
        return CommandAction.QUIT, None

def commandInspect(argStr:str, context:Context) -> CommandResult:
    length = 0
    for item in context.generator.debug_info:
        output = []
        output.append(f"{repr(chatbot.tokens_to_string(item['matched']))}")
        for key in item:
            output.append(f"{key}: {item[key]}") # type:ignore[literal-required]
        print("\t".join(output))

    return CommandAction.NOP, None

def commandSaveGenerator(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
        return CommandAction.NOP, None
    savefile.saveChat(context)
    return CommandAction.NOP, None

def commandLoadGenerator(argStr:str, context:Context) -> CommandResult:
    if len(argStr) > 0:
        print("Error: no arguments permitted") # todo
        return CommandAction.NOP, None
    if context.generator.modified:
        i = input("Current chat is not saved. Continue? [y/n] ")
        if i.lower() != "y":
            print("Aborting")
            return CommandAction.NOP, None
    print("Loading...")
    savefile.loadChat(context)
    #printItem("generator.transitions", context.generator.transitions)
    return CommandAction.NOP, None

commands:dict[str, Command] = {}
Command("say", "Send chat message, can start with '/'", commandSay),
Command("pass", "Skip your turn", commandPass),
Command("history", "List chat history", commandListHistory),
Command("inspect", "Inspect last generated message", commandInspect),
Command("transitions", "Print transition probabilities", commandListTransitions, debug=True),
Command("generator", "Print generator", commandPrintGenerator, debug=True),
Command("serialize", "Print serialized generator", commandPrintGeneratorSerialized, debug=True),
Command("save", "Save generator", commandSaveGenerator),
Command("load", "Load generator", commandLoadGenerator),
Command("help", "List available commands", commandHelp),
Command("quit", "Quit", commandQuit),
