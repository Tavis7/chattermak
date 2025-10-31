# Roadmap and planning

## Markov Generator

- [ ] Calculate transition probabilities for each token
- [ ] Select next token from most recent tokens and transition probabilities
- [ ] Bias transition probabilities for recency, generated text vs user input, etc.

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
    - [ ] Ascii only for now
- [ ] Generate tokenizer parameters from text
