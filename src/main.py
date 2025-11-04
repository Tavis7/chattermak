import sys
import chatbot

def read_file(filename):
    with open(filename) as file:
        text = file.read()
    return text


def usage(program_name):
    print(f"Usage: {program_name} [--line-count <count>] [--enable-debug-output]")


def main():
    print(sys.argv)
    loop_count = 1
    enable_debug_output = False;
    filename = "README.md"

    program_name = sys.argv[0]
    arg_index = 1;
    while (arg_index < len(sys.argv)):
        #print(f"Parsing arg {arg_index} (= {sys.argv[arg_index]})")
        match (sys.argv[arg_index]):
            case "--lines":
                arg_index += 1
                loop_count = int(sys.argv[arg_index])
            case "--state-size":
                arg_index += 1
                state_size = int(sys.argv[arg_index])
            case "--enable-debug-output":
                enable_debug_output = True
            case _:
                usage(program_name)
                exit(1)
        arg_index += 1

    print("Hello from chattermak!")
    print()
    readme = read_file(filename);
    readme = "abcbccacbacbbcbcb\n"

    readme_tokens = chatbot.string_to_tokens(readme)
    readme_string = chatbot.tokens_to_string(readme_tokens)
    if readme_string != readme:
        print(readme_tokens)
        print(readme_string)
        raise Exception("string_to_tokens failed to rount-trip")

    transitions = chatbot.generate_transitions(readme_tokens)
    if enable_debug_output == True:
        print(transitions)
        print()

    for i in range(loop_count):
        generated = chatbot.markov_generate(transitions, 0)
        if enable_debug_output == True:
            print(generated)
        print(chatbot.tokens_to_string(generated))


if __name__ == "__main__":
    main()
