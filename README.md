# ChatterMak

An experimental chat bot powered by Markov chains

- [Markov chain on wikipedia](https://en.wikipedia.org/wiki/Markov_chain)

Inspired by [tsoding](https://www.youtube.com/watch?v=6dCqR9p0yWY)

[byte pair encoding on wikipedia](https://en.wikipedia.org/wiki/Byte-pair_encoding)

The current version does not make use of byte pair encoding. Instead, the focus
has been on making short chats more chaotic.

# Running

Activate venv with `source .venv/bin/activate`

Run with `uv run src/main.py` or `./run.sh`

Use the `--help` command line argument and the `/help` chat command to list
available options.

## Match decay mechanism

Completions are chosen randomly from a weighted list of tokens for the longest
match on the last characters seen in the chat.

---

The `--match-decay <decay>` option is used to dynamically limit the match length when
choosing a contiunation. Higer decay decreases the length of uncommon matches,
making it less likely for the chatbot to repeat long strings that it has only
seen a few times.

A generator with even a very short match length can complete long sequences
surprisingly easily. With match length of 2 it can repeat an entire string
composed entirely of unique digraphs when completing the first two characters
of that string. Using a match length of 1 it can complete a string composed
entirely of unique characters.

---

The current implementation choses contiunations only from the longest available
match for the given input. For example, given the input "abc", if "c" has the
contiunations "d", "e", and "f", but "bc" only has the contiunations "d" and "e",
the contiunation "f" cannot be chosen.

Such a state can be created by sending the message "bcdbcecf" in a fresh chat.

---

Matches that do not meet the decay constraint are stored but considered
unavailable during text generation.

## Saving your chat history

Your chat is only saved when you type `/save`, or, optionally, when you recover
from a crash. Saving on every message can be slow with the current
implementation.

When the program experiences a soft crash it will save everything to a recovery
file. Your chat is *not* protected from hard crashes, e.g. power outages.

The program will overwrite modified save files without warning. This will cause
problems if you run more than one instance of the program, or if you edit the
save file manually.

Generator parameters are not saved.

## Initialization file

You can specify a file to read for input data using `--initialization-file <filename>`. No pre-processing is done to the
data.

Newline is used as a delimiter between messages, so manually wrapped
text may result in generated messages noticably starting and/or ending in the
middle of a sentence, and double newlines indicating paragraph breaks can cause
empty messages to be generated more frequently than usual.

## Generator size

The upper limit for the size of the generator is around O(n!), where n is the
match length.

The savefile currently uses json to store the contiunation probabilitiess. Using
contiunation probabilities calculated with the 428 kilobytes of data in
frankenstin.txt and the default match length of 6, saving results in a *35
megabyte* savefile. A match length of 3 produces a much smaller 2.4 megabyte
save file.

Running the savefile through gzip reduces it to around 3 megabytes, compared to
161 kilobytes for gzipped frankenstein.txt.

---

To set a reduced default match length, you can either edit the `match_length =
6` line in main.py, or, in run.sh, add a `--match-length <length>` before the `$@`.

Reducing the match length will not limit the match length of previously
calculated contiunations.

# Future

[TODO](TODO.md)

[Roadmap](ROADMAP.md)
