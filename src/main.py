import sys
import chatbot

def read_file(filename):
    with open(filename) as file:
        text = file.read()
    return text


def usage(program_name, arg=None):
    if arg != None:
        print(f"Unrecognized argument: '{arg}'")

    print(f"Usage: {program_name} [--help] [--input-file <filename>] [--chat | --line-count <count>] [--state-size <size>] [--enable-debug-output]")
    print(f"    Note: '--chat' is short for '--line-count 0'")


def main():
    #print(sys.argv)
    loop_count = 0
    enable_debug_output = False;
    filename = None
    state_size = 2
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
            case "--state-size":
                arg_index += 1
                state_size = int(sys.argv[arg_index])
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

    generator = chatbot.TokenGenerator()
    generator.state_size = state_size;
    chatbot.calculate_transitions(generator, initialization_tokens)
    if use_simple_transitions:
        transitions = chatbot.example_transitions

    if enable_debug_output == True:
        print(transitions)
        print()
        chatbot.debug_print_weights(transitions)

    if loop_count == 0:
        chatbot.append_message(generator, chatbot.string_to_tokens("\n"));
        while True:
            generated = chatbot.markov_generate(generator)
            print(f"-> {chatbot.tokens_to_string(generated)}")
            chatbot.append_message(generator, generated, True)
            try:
                user_input = input("> ")
            except EOFError:
                print()
                print("end of input: quitting")
                break
            except KeyboardInterrupt:
                print()
                print("keyboard interrupt: quitting")
                break

            if enable_debug_output == True:
                print(f"Got user input: '{user_input}'")

            chatbot.append_message(generator, chatbot.string_to_tokens(user_input))
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
