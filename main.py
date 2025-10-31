import random

transitions = [
    [(1, 1), (2, 1), (3, 1)],
    [(1, 10), (2, 3), (3, 5), (-1, 1)],
    [(1, 7), (2, 5), (3, 1), (-1, 1)],
    [(1, 3), (2, 3), (3, 9), (-1, 1)],
    [(-1, 1)] # Terminate
]

def choose_token(weights):
    total = 0;
    for _, count in weights:
        total += count

    r = random.randrange(total);
    at = 0
    result = -1
    for token, count in weights:
        at += count
        if at > r:
            result = token
            break;

    return result


def markov_generate(state):
    output = []
    if (state < len(transitions)):
        while state != -1:
            token = choose_token(transitions[state])
            output.append(token)
            state = token
    return output


def main():
    print("Hello from chattermak!")
    generated = markov_generate(0)
    print(generated)


if __name__ == "__main__":
    main()
