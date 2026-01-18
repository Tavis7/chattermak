import random
import json
from typing import TypedDict, NewType

Token = NewType("Token", int)

class TokenGenerator:
    def __init__(self, name:str, *, max_prefix_length:int = 1, prefix_decay:int = 0, delimiter:Token|None = None):
        if delimiter == None:
            delimiter = string_to_tokens("\n")[0]

        self.chatHistory:list[Message] = []
        self.transitions = PrefixNode()
        self.delimiter:Token = delimiter
        self.prefix:list[Token] = [self.delimiter]

        self.last_error_token:Token|None = None

        self.max_prefix_length = max_prefix_length
        self.prefix_decay = prefix_decay

        self.chatbot_name = name

        self.debug_info:list[GeneratedTokenInfo] = []

        self.modified = False


class Message:
    def __init__(self, message:list[Token], user:str):
        self.tokens = message
        self.user = user


class PrefixNode:
    def __init__(self, *, prefixes:dict[Token, "PrefixNode"] = {}, probabilities:dict[Token, int] = {}):
        self.prefixes = prefixes.copy()
        self.probabilities = probabilities.copy()
        self.occurance_count = 0


class flattenedCompletionList(TypedDict):
    token:Token
    weight:int
    comment:str

class flattenedPrefixNode(TypedDict):
    prefix:list[Token]
    next:list[flattenedCompletionList]
    comment:str

def flattenPrefixNode(node:PrefixNode, prefix:list[Token] = []) -> list[flattenedPrefixNode]:
    # [{prefix:p, {token:t, weight:w}}]
    result:list[flattenedPrefixNode] = []
    completionList:list[flattenedCompletionList] = []
    for probKey in node.probabilities:
        completionList.append({
            "token": probKey,
            "weight": node.probabilities[probKey],
            "comment": (tokens_to_string([probKey]))
        })
    result.append({
        "prefix": prefix,
        "next": completionList,
        "comment": (tokens_to_string(prefix))
    })
    for prefixKey in node.prefixes:
        before:list[Token] = [prefixKey]
        before.extend(prefix)
        result.extend(flattenPrefixNode(node.prefixes[prefixKey], before))

    return result


def unflattenPrefixNode(data:list[flattenedPrefixNode]) -> PrefixNode:
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


def choose_token(prefixNode:PrefixNode) -> Token:
    result:Token = Token(-1)
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




def debug_print_weights(transitions:PrefixNode) -> None:
    flattened = flattenPrefixNode(transitions)
    for node in flattened:
        text = f"{repr(node['comment'])} ({node['prefix']}):\n    ["
        parts = []
        for completion in node['next']:
            parts.append(f"{repr(completion['comment'])}({(completion['token'])}): " +
                f"{completion['weight']}")
        print("".join([text, ", ".join(parts), "]"]))


class GeneratedTokenInfo(TypedDict):
    token:Token
    decay:int
    depth:int
    matched:list[Token]

def markov_generate_token(transitions:PrefixNode, state:list[Token], decay:int) -> GeneratedTokenInfo:
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
        "token": token,
        "decay": decayed,
        "depth": depth,
        "matched": prefix
    }

def markov_generate(generator:TokenGenerator, *, max_generated_tokens:int=100, terminator:Token|None=None) -> list[Token]:
    if terminator == None:
        terminator = generator.delimiter
    output:list[Token] = []
    debug_info:list[GeneratedTokenInfo] = []
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


def append_message(generator:TokenGenerator, message:Message, generated:bool=False) -> None:
    generator.modified = True
    start_from = len(generator.prefix) - 1
    generator.prefix.extend(message.tokens)
    generator.prefix.append(generator.delimiter)
    if generated == False:
        calculate_transitions(generator, generator.prefix, start_from = start_from)
    generator.prefix = generator.prefix[-generator.max_prefix_length:]
    generator.chatHistory.append(message)



def calculate_transitions(generator:TokenGenerator, tokens:list[Token], *,
                          null_token:Token=Token(0), enable_debug_output:bool=False,
                          start_from:int=0) -> None:
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


def tokens_to_string(tokens:list[Token]) -> str:
    # todo For now tokens are just ord(char)
    char_list = []
    for token in tokens:
        if (token >= 0):
            char_list.append(chr(token))
    return "".join(char_list)


def string_to_tokens(string:str) -> list[Token]:
    tokens = []
    for character in string:
        tokens.append(Token(ord(character)))
    return tokens


example_generator = TokenGenerator("Example generator")
example_generator.transitions = PrefixNode(
    prefixes = {
        Token(1):  PrefixNode(probabilities={
            Token(1): 10, Token(2): 3, Token(3): 5, Token(4): 1
        }),
        Token(2):  PrefixNode(probabilities={
            Token(1): 7, Token(2): 5, Token(3): 1, Token(4): 1
        }),
        Token(3):  PrefixNode(probabilities={
            Token(1): 3, Token(2): 3, Token(3): 9, Token(4): 1, Token(5): 1
        }),
        Token(4):  PrefixNode(probabilities={})   # Terminate
    },
    probabilities={Token(1): 1, Token(2): 1, Token(3): 1})
