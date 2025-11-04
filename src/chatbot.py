import random

simple_transitions = {
    0:  (None, {1: 1, 2: 1, 3: 1}),
    1:  (None, {1: 10, 2: 3, 3: 5, 4: 1}),
    2:  (None, {1: 7, 2: 5, 3: 1, 4: 1}),
    3:  (None, {1: 3, 2: 3, 3: 9, 4: 1, 5: 1}),
    4:  (None, {-1: 1})   # Terminate
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


def markov_generate(transitions, state, *, max_generated_tokens=1000):
    output = []
    token = 0
    count = 0
    while token >= 0 and count < max_generated_tokens:
        count += 1
        if state in transitions:
            #print(state)
            #print(transitions[state])
            #print(transitions[state][1])
            token = choose_token(transitions[state][1])
        else:
            token = -2
        state = token
        output.append(token)
    return output


def generate_transitions(tokens, *, state_size=1,
                         debug_null_token=None, enable_debug_output=False):
    transitions = {}

    if enable_debug_output == True:
        print("generating transitions")

    for i in range(len(tokens) - 1):
        next_token = tokens[i+1]
        current_token = tokens[i]
        if debug_null_token != None:
            if current_token == debug_null_token:
                current_token = 0
            if next_token == debug_null_token:
                next_token = 0
        transition = (None, {})
        if current_token in transitions:
            transition = transitions[current_token]

        weights = transition[1]
        count = 0
        if next_token in weights:
            count = weights[next_token]
        count += 1

        weights[next_token] = count
        transitions[current_token] = transition

    if 0 in transitions:
        print(f"Warning: found null transition in text, discarding: {transitions[0]}")

    null_weights = {}
    for key in transitions:
        null_weights[key] = 1
    transitions[0] = (None, null_weights)

    term_weights = {-1: 1}
    if enable_debug_output == True:
        if ord('\n') in transitions:
            # todo Use this for null_weights
            print(f"Replacing '\\n' ({transitions[ord('\n')]}) with {term_weights}")

    transitions[ord('\n')] = (None, term_weights)
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


def string_to_tokens(string):
    tokens = []
    for character in string:
        tokens.append(ord(character))
    return tokens
