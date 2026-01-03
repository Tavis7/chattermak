import random

class TokenGenerator:
    def __init__(self, name, *, delimiter=None):
        if delimiter == None:
            delimiter = string_to_tokens("\n")[0]

        self.chatHistory = []
        self.transitions = PrefixNode()
        self.delimiter = delimiter
        self.prefix = [self.delimiter]

        self.last_error_token = None

        self.max_prefix_length = 1
        self.prefix_decay = 0

        self.username = name


class Message:
    def __init__(self, message, user):
        self.tokens = message
        self.user = user


class PrefixNode:
    def __init__(self, *, history = {}, probabilities = {}):
        self.history = history.copy()
        self.probabilities = probabilities.copy()
        self.occurance_count = 0


def choose_token(prefixNode):
    result = -1
    total = prefixNode.occurance_count;
    probabliities = prefixNode.probabilities

    if total > 0:
        r = random.randrange(total);
        at = 0
        for key in probabliities:
            at += probabliities[key]
            if at > r:
                result = key
                break;

    return result

def debug_print_weights(transitions, so_far=([],[])):
    if len(so_far[0]) == 0:
        #print("raw")
        #print(transitions)
        print("Printing weights")
    print(f"{so_far[1]} -> {transitions.probabilities}")
    for key in transitions.history:
        at = ([key],[chr(key)])
        at[0].extend(so_far[0])
        at[1].extend(so_far[1])
        debug_print_weights(transitions.history[key], at)
    if len(so_far[0]) == 0:
        print("Done printing weights")
        print()

def debug_print_weights_raw(transitions, level=0):
    if level == 0:
        #print("raw")
        #print(transitions)
        print("Printing weights")
    for key in transitions:
        print(f"{4 * level * ' '}{key}: {transitions[key].probabilities}")
        debug_print_weights_raw(transitions[key].history, level + 1)
    if level == 0:
        print("Done printing weights")
        print()

def markov_generate_token(transitions, state, decay, *, debug_print_decay = False):
    state_index = len(state) - 1

    parent = transitions
    decayed = parent.occurance_count - decay
    debug_depth = 0
    while state_index > 0 and decayed > 0:
        current_token = state[state_index]
        if current_token in parent.history:
            debug_depth += 1
            state_index -= 1
            parent = parent.history[current_token]
            decayed = min(parent.occurance_count, decayed) - decay
        else:
            break

    if debug_print_decay:
        print("decayed: ", decayed, ", depth: ", debug_depth)

    token = choose_token(parent)
    return token

def markov_generate(generator, *, max_generated_tokens=100, terminator=None):
    if terminator == None:
        terminator = generator.delimiter
    output = []
    token = 0
    count = 0
    history = generator.prefix.copy()
    # print(f"Generating from {tokens_to_string(history)}")
    while token >= 0 and count < max_generated_tokens and token != terminator:
        count += 1
        token = markov_generate_token(generator.transitions, history, generator.prefix_decay)
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


def append_message(generator, message, generated=False):
    start_from = len(generator.prefix) - 1
    generator.prefix.extend(message.tokens)
    generator.prefix.append(generator.delimiter)
    if generated == False:
        calculate_transitions(generator, generator.prefix, start_from = start_from)
    generator.prefix = generator.prefix[-generator.max_prefix_length:]
    generator.chatHistory.append(message)



def calculate_transitions(generator, tokens, *,
                          null_token=0, enable_debug_output=False,
                          start_from=0):
    # todo fixme This throws away starting transitions
    transitions = generator.transitions
    #print(f"calculate_transitions({generator}, {tokens}, *, {null_token}, {enable_debug_output}, {start_from})")
    # print(f"token count: {len(tokens)}")

    # todo fixme currently broken
    for token_index in range(start_from, len(tokens)):
        debug_depth = 0
        # print(f"{token_index} ({start_from} -> {len(tokens) - 1})")
        node = transitions
        next_token = tokens[token_index]

        max_state_index = min(generator.max_prefix_length, token_index)
        for state_index in range(max_state_index + 1):
            weight = 0
            if next_token in node.probabilities:
                weight = node.probabilities[next_token]

            node.probabilities[next_token] = weight + 1
            node.occurance_count += 1

            if max_state_index > state_index:
                current_token = tokens[token_index - state_index - 1]

                if current_token not in node.history:
                    node.history[current_token] = PrefixNode()
                node = node.history[current_token]

    return


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


example_generator = TokenGenerator("Example generator")
example_generator.transitions = PrefixNode(
    history = {
        1:  PrefixNode(probabilities={1: 10, 2: 3, 3: 5, 4: 1}),
        2:  PrefixNode(probabilities={1: 7, 2: 5, 3: 1, 4: 1}),
        3:  PrefixNode(probabilities={1: 3, 2: 3, 3: 9, 4: 1, 5: 1}),
        4:  PrefixNode(probabilities={})   # Terminate
    },
    probabilities={1: 1, 2: 1, 3: 1})
