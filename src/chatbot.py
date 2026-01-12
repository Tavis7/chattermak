import random
import json

class TokenGenerator:
    def __init__(self, name, *, max_prefix_length = 1, prefix_decay = 0, delimiter=None):
        if delimiter == None:
            delimiter = string_to_tokens("\n")[0]

        self.chatHistory = []
        self.transitions = PrefixNode()
        self.delimiter = delimiter
        self.prefix = [self.delimiter]

        self.last_error_token = None

        self.max_prefix_length = max_prefix_length
        self.prefix_decay = prefix_decay

        self.chatbot_name = name

        self.debug_info = []

        self.modified = False


class Message:
    def __init__(self, message, user):
        self.tokens = message
        self.user = user


class PrefixNode:
    def __init__(self, *, prefixes = {}, probabilities = {}):
        self.prefixes = prefixes.copy()
        self.probabilities = probabilities.copy()
        self.occurance_count = 0

def flattenPrefixNode(node, prefix = []):
    # [{prefix:p, {token:t, weight:w}}]
    result = []
    completionList = []
    for key in node.probabilities:
        completionList.append({
            "token": key,
            "weight": node.probabilities[key],
            "comment": (tokens_to_string([key]))
        })
    result.append({
        "prefix": prefix,
        "next": completionList,
        "comment": (tokens_to_string(prefix))
    })
    for key in node.prefixes:
        before = [key]
        before.extend(prefix)
        result.extend(flattenPrefixNode(node.prefixes[key], before))

    return result


def unflattenPrefixNode(data):
    prefixNode = PrefixNode()
    #print()
    for completion in data:
        #print(f"inserting completion {completion}")
        prefix = completion['prefix']
        current = prefixNode
        for token in prefix[::-1]:
            #print(token)
            if token not in current.prefixes:
                current.prefixes[token] = PrefixNode()
            current = current.prefixes[token]

        weightList = completion['next']
        for weight in weightList:
            current.probabilities[weight['token']] = weight['weight'];
            current.occurance_count += weight['weight']

    return prefixNode


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
    flattened = flattenPrefixNode(transitions)
    for node in flattened:
        text = f"{repr(node['comment'])} ({node['prefix']}):\n    ["
        parts = []
        for completion in node['next']:
            parts.append(f"{repr(completion['comment'])}({(completion['token'])}): " +
                f"{completion['weight']}")
        print("".join([text, ", ".join(parts), "]"]))


def markov_generate_token(transitions, state, decay):
    state_index = len(state) - 1

    parent = transitions
    decayed = parent.occurance_count
    depth = 0
    prefix = []
    while state_index > 0 and decayed > 0:
        current_token = state[state_index]
        if current_token in parent.prefixes:
            state_index -= 1
            maybe = parent.prefixes[current_token]
            decayed = min(maybe.occurance_count, decayed) - decay
            if decayed > 0:
                prefix.append(current_token)
                depth += 1
                parent = maybe
        else:
            break

    token = choose_token(parent)
    prefix.reverse()
    return {
        "token":token,
        "decay": decayed,
        "depth": depth,
        "matched": prefix
    }

def markov_generate(generator, *, max_generated_tokens=100, terminator=None):
    if terminator == None:
        terminator = generator.delimiter
    output = []
    debug_info = []
    token = 0
    count = 0
    prefixes = generator.prefix.copy()
    # print(f"Generating from {tokens_to_string(prefixes)}")
    while token >= 0 and count < max_generated_tokens and token != terminator:
        count += 1
        got = markov_generate_token(generator.transitions, prefixes, generator.prefix_decay)
        token = got["token"]
        debug_info.append(got)
        if token == terminator:
            break
        else:
            if token < 0:
                generator.last_error_token = token
                print(f"Encountered error token: {token}")
                break;
            prefixes.append(token)
            output.append(token)
    generator.debug_info = debug_info
    return output


def append_message(generator, message, generated=False):
    generator.modified = True
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
    generator.modified |= len(tokens) > 0
    transitions = generator.transitions

    for token_index in range(start_from, len(tokens)):
        debug_depth = 0
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

                if current_token not in node.prefixes:
                    node.prefixes[current_token] = PrefixNode()
                node = node.prefixes[current_token]

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
    prefixes = {
        1:  PrefixNode(probabilities={1: 10, 2: 3, 3: 5, 4: 1}),
        2:  PrefixNode(probabilities={1: 7, 2: 5, 3: 1, 4: 1}),
        3:  PrefixNode(probabilities={1: 3, 2: 3, 3: 9, 4: 1, 5: 1}),
        4:  PrefixNode(probabilities={})   # Terminate
    },
    probabilities={1: 1, 2: 1, 3: 1})
