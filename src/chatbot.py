import random

example_transitions = {
    0:  {"history": {}, "probabilities": {1: 1, 2: 1, 3: 1}},
    1:  {"history": {}, "probabilities": {1: 10, 2: 3, 3: 5, 4: 1}},
    2:  {"history": {}, "probabilities": {1: 7, 2: 5, 3: 1, 4: 1}},
    3:  {"history": {}, "probabilities": {1: 3, 2: 3, 3: 9, 4: 1, 5: 1}},
    4:  {"history": {}, "probabilities": {-1: 1}}   # Terminate
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

def debug_print_weights(transitions, so_far=""):
    if so_far == "":
        #print("raw")
        #print(transitions)
        print("Printing weights")
    for key in transitions:
        at = chr(key) + so_far
        print(f"{at} ({key}): {transitions[key]['probabilities']}")
        debug_print_weights(transitions[key]["history"], at)
    if so_far == "":
        print("Done printing weights")
        print()

def debug_print_weights_raw(transitions, level=0):
    if level == 0:
        #print("raw")
        #print(transitions)
        print("Printing weights")
    for key in transitions:
        print(f"{4 * level * ' '}{key}: {transitions[key]['probabilities']}")
        debug_print_weights_raw(transitions[key]["history"], level + 1)
    if level == 0:
        print("Done printing weights")
        print()

def markov_generate_token(transitions, state):
    state_index = len(state) - 1
    if state[state_index] in transitions:
        parent = transitions
        current_token = state[state_index]
        debug_depth = 1
        while state_index > 0:
            debug_depth += 1
            state_index -= 1
            previous_token = state[state_index]
            if previous_token in parent[current_token]["history"]:
                parent = parent[current_token]["history"]
                current_token = previous_token
            else:
                break

        token = choose_token(parent[current_token]["probabilities"])
    else:
        token = -2
    return token

def markov_generate(generator, *,
                    max_generated_tokens=100, terminator=None):
    if terminator == None:
        terminator = generator.delimiter
    output = []
    token = 0
    count = 0
    history = [generator.delimiter]
    history.extend(generator.history)
    # print(f"Generating from {tokens_to_string(history)}")
    while token >= 0 and count < max_generated_tokens and token != terminator:
        count += 1
        token = markov_generate_token(generator.transitions, history)
        if token == terminator:
            break
        else:
            if token < 0:
                generator.last_error_token = token
                print(f"Encountered error token: {token}")
                break;
            history.append(token)
            output.append(token)
    return output


class TokenGenerator:
    def __init__(self):
        self.history = []
        self.transitions = {}
        self.last_error_token = None
        self.state_size = 1
        self.delimiter = string_to_tokens("\n")[0]


def append_message(generator, message, generated=False):
    start_from = len(generator.history) - 1
    generator.history.extend(message)
    generator.history.append(generator.delimiter)
    if generated == False:
        calculate_transitions(generator, generator.history, start_from = start_from)


def calculate_transitions(generator, tokens, *,
                          null_token=0, enable_debug_output=False,
                          start_from=0):
    transitions = generator.transitions
    if null_token in transitions:
        del transitions[null_token]
    # print(f"token count: {len(tokens)}")
    # print(f"tokens: {tokens}")
    for token_index in range(start_from, len(tokens) - 1):
        # print(f"{token_index} ({start_from} -> {len(tokens) - 1})")
        parent = transitions
        next_token = tokens[token_index + 1]
        for state_index in range(min(generator.state_size, token_index + 1)):
            current_token = tokens[token_index - state_index]
            child = {"history": {}, "probabilities": {}}
            if current_token in parent:
                child = parent[current_token]
            weights = child["probabilities"]
            weight = 0
            if current_token in weights:
                weight = weights[current_token]
            weights[next_token] = weight + 1

            parent[current_token] = child
            parent = child["history"]

    null_transitions = {}
    for key in transitions:
        null_transitions[key] = 1
    if null_token in transitions:
        print(f"Warning: replacing {null_token} ({transitions[null_token]}) with {null_transitions}")
    transitions[null_token] = {"history": {}, "probabilities": null_transitions}
    #debug_print_weights_raw(transitions)

    return transitions


def tokens_to_string(tokens):
    # todo For now tokens are just ord(char)
    char_list = []
    for token in tokens:
        if (token >= 0):
            char_list.append(chr(token))
    return "".join(char_list)


def string_to_tokens(string):
    tokens = []
    for character in string:
        tokens.append(ord(character))
    return tokens
