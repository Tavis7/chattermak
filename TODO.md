# TODO list

- [x] Add type annotations for static type checking

- [x] Update README.md for initial release
- [ ] Update ROADMAP.md for initial release
- [ ] Update TODO.md for initial release

---

- [x] Save chat history
    - [x] Save messages
    - [x] Save transitions
- [x] Load chat history
    - [x] Load messages
    - [x] Load transitions
- [x] Check for 'data/aborted.json' on start
    - [x] Offer to save after recovery

---

- [ ] Chat names
- [ ] Save user name and other generator parameters
- [ ] Save /commands to readline history
- [ ] Warn before overwriting modified savefile
- [ ] Support multiple savefiles

---

- [ ] Merge --commands and /commands
- [ ] Option to print message generation stats
- [ ] Clean up input files
- [ ] Fractional decay

---

- [x] Dynamic prefix length / decay
- [x] Separate chat history into messages instead of single list of tokens
- [x] Readline
- [ ] Slash commands
    - [x] Print transition weights
        - /transitions
    - [x] /help
    - [x] /help [command]
    - [x] /quit
    - [x] /history
    - [ ] Print last n lines of /history
    - [ ] Pagination for command output
- [ ] Tests
- [ ] (Type annotations](https://docs.python.org/3/library/typing.html)
- [ ] Refactor

---

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
