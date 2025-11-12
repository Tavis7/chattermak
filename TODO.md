# TODO list

- [ ] readline
- [ ] Slash commands
    - [ ] Print transition weights
    - [x] /help
    - [ ] /help [command]
    - [x] /quit
    - [ ] /history [n]
- [ ] Tokenizer tests
- [ ] Refactor
- [ ] save chat history
- [ ] separate chat history into messages instead of single list of tokens
- [ ] dynamic transition lookback length

- [x] Basic chat interface
    - [x] Chat input loop
    - [x] Add most recent message to transition probabilities
- [x] Generate using multi-token state
- [x] Implement Markov generator for single token state
    - Initially using hardcoded or random weights
- [x] Calculate transition probabilities from text
    - [x] Read file
    - [x] Calculate transitions
- [x] Translate token list to text
