import chatbot
import json
import copy
import traceback
import os

currentSaveFileVersion = 0
defaultChatFile =  "./data/chat_history.json"

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

def deserializeVersion0(old, data):
    if data['version'] != 0:
        raise Exception("Invalid version: {data['version']}")

    generator = chatbot.TokenGenerator(old.chatbot_name,
                               max_prefix_length = old.max_prefix_length,
                               prefix_decay = old.prefix_decay,
                               delimiter = old.delimiter)

    for message in data['messages']:
        chatbot.append_message(
            generator,
            chatbot.Message(message['tokens'],
                            message['user']),
            message['user'] == 'user')

    generator.transitions = chatbot.unflattenPrefixNode(data['transitions'])

    return generator

def deserializeGenerator(currentGenerator, data):
    match data['version']:
        case 0:
            return deserializeVersion0(currentGenerator, data)
        case _:
            print(f"Error: unknown save version: {data['version']}")

def loadChat(context, filename = defaultChatFile, setModified = False):
    success = False
    print(f"Loading '{filename}'")
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        generator = deserializeGenerator(context.generator, data)
        if generator != None:
            context.generator = generator
            context.generator.modified = setModified
            success = True
            print("Success")
        else:
            print("Couldn't read save data")
    except Exception as e:
        print(f"Failed to load file '{filename}': {e}")
        traceback.print_exception(e)
    return success


def saveChat(context, filename = defaultChatFile):
    success = False
    generator = context.generator
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Saving '{filename}'")
    try:
        with open(filename, 'w') as file:
            file.write(serializeGenerator(generator))
        generator.modified = False
        success = True
    except Exception as e:
        print(f"Failed to save chat to '{filename}': {e}")
    return success
