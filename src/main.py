import sys
import chatbot

def read_file(filename):
    with open(filename) as file:
        text = file.read()
    return text


def usage(program_name, arg=None):
    if arg != None:
        print(f"Unrecognized argument: '{arg}'")

    print(f"Usage: {program_name} [--help] [--input-file <filename>] [--line-count <count>] [--state-size <size>] [--enable-debug-output]")


def main():
    #print(sys.argv)
    loop_count = 1
    enable_debug_output = False;
    filename = "README.md"
    state_size = 2

    program_name = sys.argv[0]
    arg_index = 1;
    while (arg_index < len(sys.argv)):
        #print(f"Parsing arg {arg_index} (= {sys.argv[arg_index]})")
        match (sys.argv[arg_index]):
            case "--input-file":
                arg_index += 1
                filename = int(sys.argv[arg_index])
            case "--line-count":
                arg_index += 1
                loop_count = int(sys.argv[arg_index])
            case "--state-size":
                arg_index += 1
                state_size = int(sys.argv[arg_index])
            case "--enable-debug-output":
                enable_debug_output = True
            case "--help":
                usage(program_name)
            case _:
                usage(program_name, sys.argv[arg_index])
                exit(1)
        arg_index += 1

    print("Hello from chattermak!")
    print()
    readme = read_file(filename);
    #readme = "abcdefghijklmnoponmlkjihgfedcba\n"
    #readme = "abcdefg\n"

    readme_tokens = chatbot.string_to_tokens(readme)
    readme_string = chatbot.tokens_to_string(readme_tokens)
    if readme_string != readme:
        print(readme_tokens)
        print(readme_string)
        raise Exception("string_to_tokens failed to rount-trip")

    transitions = chatbot.generate_transitions(readme_tokens, state_size = state_size)
    if enable_debug_output == True:
        print(transitions)
        print()
        chatbot.debug_print_weights(transitions)

    for i in range(loop_count):
        generated = chatbot.markov_generate(transitions)#chatbot.string_to_tokens("abc"))
        if enable_debug_output == True:
            print(generated)
        print(f"-> |{chatbot.tokens_to_string(generated)}|")


if __name__ == "__main__":
    main()
