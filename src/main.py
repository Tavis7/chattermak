import sys
import re

import chatbot
import commands
import savefile
import traceback

try:
    import readline
except ModuleNotFoundError:
    print("Failed to import readline. Some line editing features may not be available.")
    readlinee = None

def init_readline():
    if readline != None:
        readline.set_auto_history(False)

def read_file(filename):
    with open(filename) as file:
        text = file.read()
    return text


def usage(program_name, arg=None):
    if arg != None:
        print(f"Unrecognized argument: '{arg}'")

    print(f"Usage: {program_name} [--help] [--input-file <filename>] [--chat | --line-count <count>] [--max-prefix-length <size>] [--prefix-decay <decay_rate>] [--enable-debug-output]")
    print(f"    Note: '--chat' is short for '--line-count 0'")


class Context:
    def __init__(self, generator):
        self.generator = generator

def main():
    #print(sys.argv)
    loop_count = 0
    enable_debug_output = False;
    filename = None
    max_prefix_length = 6
    prefix_decay = 1
    use_simple_transitions = False;

    program_name = sys.argv[0]
    arg_index = 1;
    while (arg_index < len(sys.argv)):
        #print(f"Parsing arg {arg_index} (= {sys.argv[arg_index]})")
        match (sys.argv[arg_index]):
            case "--input-file":
                arg_index += 1
                filename = sys.argv[arg_index]
            case "--line-count":
                arg_index += 1
                loop_count = int(sys.argv[arg_index])
            case "--chat":
                loop_count = 0
            case "--max-prefix-length":
                arg_index += 1
                max_prefix_length = int(sys.argv[arg_index])
            case "--prefix-decay":
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
    print(f"Using state size: {max_prefix_length}, decay: {prefix_decay}")
    print()

    initialization = "";
    if filename != None and len(filename) > 0:
        initialization = read_file(filename);

    initialization_tokens = chatbot.string_to_tokens(initialization)
    initialization_string = chatbot.tokens_to_string(initialization_tokens)
    if initialization_string != initialization:
        print(initialization_tokens)
        print(initialization_string)
        raise Exception("string_to_tokens failed to rount-trip")

    generator = chatbot.TokenGenerator("chattermak",
                                       max_prefix_length = max_prefix_length,
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
        try:
            while True:
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
                    command_parts.append("")
                    user_input = None

                    if enable_debug_output:
                        print(command_parts)
                        print(command_parts[0])

                    action = commands.CommandAction.NOP
                    result = None
                    if command_parts[0] in commands.commands:
                        action, result = commands.commands[command_parts[0]].func(command_parts[1], context)
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
            if enable_debug_output:
                traceback.print_exception(e)
            if context.generator.modified:
                savefile.saveChat(context, "data/aborted.json")
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
