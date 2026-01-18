import sys
import re
import os
import traceback

import chatbot
import commands
import savefile
from chatbot import TokenGenerator

try:
    import readline
except ModuleNotFoundError:
    print("Failed to import readline. Some line editing features may not be available.")
    readlinee = None

def init_readline() -> None:
    if readline != None:
        readline.set_auto_history(False)

def read_file(filename:str) -> str:
    with open(filename) as file:
        text = file.read()
    return text


def usage(program_name:str, arg:str|None = None) -> None:
    if arg != None:
        print(f"Unrecognized argument: '{arg}'")

    print(f"Usage: {program_name} [--help] [--initialization-file <filename>] [--chat | --line-count <count>] [--match-length <length>] [--match-decay <decay>] [--enable-debug-output]")
    print(f"    Note: '--line-count 0' is another name for '--chat'")


class Context:
    def __init__(self, generator:TokenGenerator):
        self.generator = generator

def main() -> None:
    #print(sys.argv)
    loop_count = 0
    enable_debug_output = False;
    filename = None
    match_length = 6
    prefix_decay = 1
    use_simple_transitions = False;

    program_name = sys.argv[0]
    arg_index = 1;
    while (arg_index < len(sys.argv)):
        #print(f"Parsing arg {arg_index} (= {sys.argv[arg_index]})")
        match (sys.argv[arg_index]):
            case "--initialization-file":
                arg_index += 1
                filename = sys.argv[arg_index]
            case "--line-count":
                arg_index += 1
                loop_count = int(sys.argv[arg_index])
            case "--chat":
                loop_count = 0
            case "--match-length":
                arg_index += 1
                match_length = int(sys.argv[arg_index])
            case "--match-decay":
                arg_index += 1
                prefix_decay = int(sys.argv[arg_index])
            case "--enable-debug-output":
                enable_debug_output = True
            case "--enable-debug-transitions":
                use_simple_transitions = True
            case "--help":
                usage(program_name)
                exit(0)
            case _:
                usage(program_name, sys.argv[arg_index])
                exit(1)
        arg_index += 1

    if loop_count > 0 and filename == None:
        filename = "README.md"

    print("Hello from chattermak!")
    print(f"Using match length: {match_length}, match decay: {prefix_decay}")
    print()

    initialization = "";
    if filename != None and len(filename) > 0:
        initialization = read_file(filename);

    initialization_tokens = chatbot.string_to_tokens(initialization)
    initialization_string = chatbot.tokens_to_string(initialization_tokens)

    generator = chatbot.TokenGenerator("chattermak",
                                       max_prefix_length = match_length,
                                       prefix_decay = prefix_decay)
    context = Context(generator)

    chatbot.calculate_transitions(generator, initialization_tokens)

    if use_simple_transitions:
        generator = chatbot.example_generator
        if enable_debug_output == True:
            print(generator.transitions)
            print()
            chatbot.debug_print_weights(generator.transitions)

    init_readline()

    if loop_count == 0:
        should_generate_message = True
        user_name = "user"
        prompt_indicator = "> "

        running = True
        aborted_filename = "data/aborted.json"
        recovered = False
        if os.path.exists(aborted_filename):
            got = input(f"{aborted_filename} exists. [R]ecover / [D]elete / [Q]uit: ")
            match got.lower():
                case "r":
                    if filename != None:
                        print(f"Ignoring specified initialization file '{filename}'")
                        filename = None

                    if savefile.loadChat(context, aborted_filename, True):
                        print(f"Recovered chat with {len(context.generator.chatHistory)} messages")
                        recovered = True
                        for message in context.generator.chatHistory[-5:]:
                            print(f"{message.user}> {chatbot.tokens_to_string(message.tokens)}")
                        while True:
                            got = input("Save recovered data now? [y/n] ")
                            match got.lower():
                                case 'y':
                                    if savefile.saveChat(context):
                                        break
                                case 'n':
                                    break
                                case _:
                                    print(f"Unrecognized option: {got}")
                        os.remove(aborted_filename)
                case "d":
                    os.remove(aborted_filename)
                case _:
                    running = False

        if running and not recovered and os.path.exists(savefile.defaultChatFile):
            load_chat = True
            if filename != None:
                while True:
                    print(f"Initialization file '{filename}' specified but chat already exists")
                    got = input("[R]estart chat or [C]ontinue without initialization? ")
                    match got.lower():
                        case 'r':
                            os.remove(savefile.defaultChatFile)
                            load_chat = False
                            break
                        case 'c':
                            filename = None
                            break
                        case _:
                            print(f"Unrecognized option: {got}")

            if load_chat and not savefile.loadChat(context, savefile.defaultChatFile):
                while True:
                    got = input("Restart chat? [y/n] ")
                    match got.lower():
                        case 'y':
                            os.remove(savefile.defaultChatFile)
                            running = True
                            break
                        case 'n':
                            print("Quitting")
                            running = False
                            break
                        case _:
                            print(f"Unrecognized option: {got}")


        try:
            while running:
                generator = context.generator
                user_input = None
                user_input = input(f"{user_name}{prompt_indicator}")

                if enable_debug_output == True:
                    print(f"Got user input: '{user_input}'")

                if len(user_input) > 0 and user_input[0] == '/':
                    if enable_debug_output == True:
                        print(f"Got command: {user_input}")
                    should_generate_message = False
                    command_parts = user_input.strip().split(maxsplit = 1)
                    user_input = None

                    if enable_debug_output:
                        print(command_parts)
                        print(command_parts[0])

                    action = commands.CommandAction.NOP
                    result = None
                    if command_parts[0] in commands.commands:
                        action, result = commands.commands[command_parts[0]].func(command_parts[1:], context)
                    else:
                        print(f"Unknown command: {command_parts[0]}")

                    match action:
                        case commands.CommandAction.QUIT:
                            break
                        case commands.CommandAction.SAY:
                            user_input = result
                            print(f"[{user_name}] said: {user_input}")
                        case commands.CommandAction.PASS:
                            should_generate_message = True
                        case commands.CommandAction.NOP:
                            pass
                        case _:
                            print(f"ERROR: Unhandled command action")

                if user_input != None:
                    message = chatbot.Message(chatbot.string_to_tokens(user_input), user_name)
                    chatbot.append_message(generator, message)
                    should_generate_message = True

                if should_generate_message:
                    generated = chatbot.markov_generate(generator)
                    if len(generated) > 0:
                        print(f"{generator.chatbot_name}{prompt_indicator}{chatbot.tokens_to_string(generated)}")
                        message = chatbot.Message(generated, generator.chatbot_name)
                        chatbot.append_message(generator, message, True)
        except BaseException as e:
            print()
            if (not isinstance(e, KeyboardInterrupt)
                and not isinstance(e, EOFError)):
                traceback.print_exception(e)
            if context.generator.modified:
                savefile.saveChat(context, aborted_filename)
            print("Exiting")

    else:
        if use_simple_transitions == True:
            enable_debug_output = True
        for i in range(loop_count):
            generated = chatbot.markov_generate(generator)
            if enable_debug_output == True:
                print(generated)
            if use_simple_transitions != True:
                print(f"-> |{chatbot.tokens_to_string(generated)}|")


if __name__ == "__main__":
    main()
