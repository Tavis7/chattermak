import chatbot
import json

currentSaveFileVersion = 0

def serializeGenerator(generator):
    result = {}
    messages = []
    for message in generator.chatHistory:
        messages.append({"tokens": message.tokens, "user": message.user})

    transitions = chatbot.flattenPrefixNode(generator.transitions)

    result["version"] = currentSaveFileVersion
    result["messages"] = messages
    result["transitions"] = transitions
    return json.dumps(result, sort_keys=False, indent=4)

def deserializeGenerator(generator):
    pass

def saveGeneratorAs(generator, filename = "./data/chat_history.json"):
    with open(filename, 'w') as file:
        file.write(serializeGenerator(generator))
