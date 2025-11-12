# Roadmap and planning

## Markov Generator

- [x] Calculate transition probabilities for each token
- [x] Select next token from most recent tokens and transition probabilities
    - [x] Single token state
    - [x] Multi token state
- [ ] Bias transition probabilities for recency, generated text vs user input, etc.
- [ ] Dynamically adjust state size based on average depth of transitions

## Chat Interface

- [ ] Basic TUI line i/o
- [ ] Regenerate transition probabilities for each output
- [ ] Regenerate tokenizer parameters for each output

Improvements:

- [ ] Wait a short time for more user input before generating next output
- [ ] Detect typing as user input
- [ ] Colorize tokens
    - background/foreground colors:
        - one for tokenization at text generation
        - the other for current tokenization
- [ ] Web interface
- [ ] Native GUI interface

## Tokenizer

- [ ] Include end of messages, end of line, etc. tokens
- [ ] Generate tokenizer parameters from text
