import random

simple_transitions = {
    0:  ({}, {1: 1, 2: 1, 3: 1}),
    1:  ({}, {1: 10, 2: 3, 3: 5, 4: 1}),
    2:  ({}, {1: 7, 2: 5, 3: 1, 4: 1}),
    3:  ({}, {1: 3, 2: 3, 3: 9, 4: 1, 5: 1}),
    4:  ({}, {-1: 1})   # Terminate
}


def choose_token(weights):
    #print(f"Choosing token from {weights}")
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
    #print("markov_generate_token")
    state_index = len(state) - 1
    if state[state_index] in transitions:
        parent = transitions
        current_token = state[state_index]
        debug_depth = 1
        while state_index > 0:
            #print("loop")
            #print(f"character: {state[state_index]}({chr(state[state_index])})")
            #print(f"state index: {state_index}")
            debug_depth += 1
            state_index -= 1
            previous_token = state[state_index]
            if previous_token in parent[current_token][0]:
                parent = parent[current_token][0]
                current_token = previous_token
            else:
                #print(f"breaking: {previous_token} not in {parent[current_token]}")
                break
        #print("after")
        #print(f"character: {state[state_index]}({chr(state[state_index])})")
        #print(f"state index: {state_index}")

        #print(f"Depth: {debug_depth}")
        #print(f"Parent: {parent}")
        #print(f"Current token: {current_token}")
        token = choose_token(parent[current_token][1])
    else:
        token = -2
    return token

def markov_generate(transitions, state, *, max_generated_tokens=2):
    output = []
    token = 0
    count = 0
    while token >= 0 and count < max_generated_tokens:
        count += 1
        token = markov_generate_token(transitions, state)
        state.append(token)
        print(state)
        output.append(token)
    return output


def generate_transitions(tokens, *, state_size=1,
                         debug_null_token=None, enable_debug_output=False):
    transitions = {}
    for token_index in range(len(tokens) - 1):
        #print(f"token: {token_index}")
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
            weights[current_token] = weight + 1
            #print(weights)

            parent[current_token] = child
            #print(parent)
            parent = child[0]

    return transitions
    #transitions_ = {}

    #if enable_debug_output == True:
    #    print("generating transitions")

    #for i in range(len(tokens) - 1):
    #    next_token = tokens[i+1]
    #    if debug_null_token != None:
    #        if next_token == debug_null_token:
    #            next_token = 0
    #    lookback = state_size
    #    parent = transitions_
    #    while lookback > 0 and lookback <= i:
    #        lookback -= 1
    #        current_token = tokens[i - lookback]
    #        if debug_null_token != None:
    #            if current_token == debug_null_token:
    #                current_token = 0
    #        transition = ({}, {})
    #        if current_token in parent:
    #            transition = parent[current_token]

    #        weights = transition[1]
    #        count = 0
    #        if next_token in weights:
    #            count = weights[next_token]
    #        count += 1

    #        weights[next_token] = count
    #        parent[current_token] = transition
    #        parent = parent[current_token][0]

    #transitions = transitions_
    #if 0 in transitions:
    #    print(f"Warning: found null transition in text, discarding: {transitions[0]}")

    #null_weights = {}
    #for key in transitions:
    #    null_weights[key] = 1
    #transitions[0] = ({}, null_weights)

    #term_weights = {-1: 1}
    #if enable_debug_output == True:
    #    if ord('\n') in transitions:
    #        # todo Use this for null_weights
    #        print(f"Replacing '\\n' ({transitions[ord('\n')]}) with {term_weights}")

    #transitions[ord('\n')] = ({}, term_weights)
    #if enable_debug_output == True:
    #    print("done")

    #return transitions


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
