# TODO list

- [ ] save chat history
- [ ] Update README.md for initial release
- [ ] Update ROADMAP.md for initial release
- [ ] Update TODO.md for initial release


- [ ] Merge --commands and /commands
- [ ] Option to print message generation stats
- [ ] Clean up input files
- [ ] Fractional decay


- [x] dynamic prefix length / decay
- [x] separate chat history into messages instead of single list of tokens
- [x] readline
- [ ] Slash commands
    - [x] Print transition weights
        - /transitions
    - [x] /help
    - [x] /help [command]
    - [x] /quit
    - [x] /history
    - [ ] last n lines of /history
- [ ] Tokenizer tests
- [ ] Refactor

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
