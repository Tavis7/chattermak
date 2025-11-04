import random

simple_transitions = {
    0:  ({}, {1: 1, 2: 1, 3: 1}),
    1:  ({}, {1: 10, 2: 3, 3: 5, 4: 1}),
    2:  ({}, {1: 7, 2: 5, 3: 1, 4: 1}),
    3:  ({}, {1: 3, 2: 3, 3: 9, 4: 1, 5: 1}),
    4:  ({}, {-1: 1})   # Terminate
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
        print("Printing weights")
    for key in transitions:
        at = chr(key) + so_far
        print(f"{at}: {transitions[key][1]}")
        debug_print_weights(transitions[key][0], at)
    if so_far == "":
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
            if previous_token in parent[current_token][0]:
                parent = parent[current_token][0]
                current_token = previous_token
            else:
                break

        token = choose_token(parent[current_token][1])
    else:
        token = -2
    return token

def markov_generate(transitions, state = [0], *, max_generated_tokens=100, terminator=ord("\n")):
    state = state.copy()
    output = []
    token = 0
    count = 0
    while token >= 0 and count < max_generated_tokens and token != terminator:
        count += 1
        token = markov_generate_token(transitions, state)
        if token != terminator:
            state.append(token)
            output.append(token)
    return output


def generate_transitions(tokens, *, state_size=1, null_token=0,
                         enable_debug_output=False):
    transitions = {}
    for token_index in range(len(tokens) - 1):
        parent = transitions
        next_token = tokens[token_index + 1]
        for state_index in range(min(state_size, token_index + 1)):
            current_token = tokens[token_index - state_index]
            child = ({}, {})
            if current_token in parent:
                child = parent[current_token]
            weights = child[1]
            weight = 0
            if current_token in weights:
                weight = weights[current_token]
            weights[next_token] = weight + 1

            parent[current_token] = child
            parent = child[0]

    null_transitions = {}
    for key in transitions:
        null_transitions[key] = 1
        # print(f"null_transitions[{key}]: {null_transitions[key]}")
        # print(f"null_transitions: {null_transitions}")
    if null_token in transitions:
        print("Warning: replacing {null_token} ({transitions[null_token]}) with {null_transitions}")
    transitions[null_token] = ({}, null_transitions)

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
