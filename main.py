import random
import sys

simple_transitions = {
    0:  {1: 1, 2: 1, 3: 1},
    1:  {1: 10, 2: 3, 3: 5, 4: 1},
    2:  {1: 7, 2: 5, 3: 1, 4: 1},
    3:  {1: 3, 2: 3, 3: 9, 4: 1, 5: 1},
    4:  {-1: 1}   # Terminate
}

def choose_token(weights):
    total = 0;
    for key in weights:
        total += weights[key]

    r = random.randrange(total);
    at = 0
    result = -1
    for key in weights:
        at += weights[key]
        if at > r:
            result = key
            break;

    return result


MAX_GENERATED_TOKENS = 1000
def markov_generate(transitions, state):
    output = []
    token = 0
    count = 0
    while token >= 0 and count < MAX_GENERATED_TOKENS:
        count += 1
        if state in transitions:
            token = choose_token(transitions[state])
        else:
            token = -2
        state = token
        output.append(token)
    return output

def read_file(filename):
    with open(filename) as file:
        text = file.read()
    return text

def generate_transitions(text, *args, debug_null_char=None, enable_debug_output=False):
    if len(args) > 0:
        raise Exception(f"Too many positional arguments: {args}")
    transitions = {}
    if enable_debug_output == True:
        print(f"generating transitions")
    for i in range(len(text) - 1):
        current_char = ord(text[i])
        next_char = ord(text[i+1])
        if debug_null_char != None:
            if current_char == ord(debug_null_char):
                current_char = 0
            if next_char == ord(debug_null_char):
                next_char = 0
        weights = {}
        if current_char in transitions:
            weights = transitions[current_char]
        count = 0
        if next_char in weights:
            count = weights[next_char]
        count += 1
        weights[next_char] = count
        transitions[current_char] = weights

    if 0 in transitions:
        print(f"Warning: found null transition in text, discarding: {transitions[0]}")

    null_weights = {}
    for key in transitions:
        null_weights[key] = 1
    transitions[0] = null_weights

    term_weights = {-1: 1}
    if enable_debug_output == True:
        if ord('\n') in transitions:
            # todo Use this for null_weights
            print(f"Replacing '\\n' ({transitions[ord('\n')]}) with {term_weights}")

    transitions[ord('\n')] = term_weights
    if enable_debug_output == True:
        print("done")

    return transitions

def tokens_to_string(tokens):
    # todo For now tokens are just ord(char)
    char_list = []
    for token in tokens:
        if (token >= 0):
            char_list.append(chr(token))
    return "".join(char_list)

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
            case "--enable-debug":
                enable_debug_output = True
            case _:
                usage(program_name)
                exit(1)
        arg_index += 1

    print("Hello from chattermak!")
    print()
    readme = read_file(filename);

    transitions = generate_transitions(readme)
    if enable_debug_output == True:
        print(transitions)
        print()

    for i in range(loop_count):
        generated = markov_generate(transitions, 0)
        if enable_debug_output == True:
            print(generated)
        print(tokens_to_string(generated))


if __name__ == "__main__":
    main()
