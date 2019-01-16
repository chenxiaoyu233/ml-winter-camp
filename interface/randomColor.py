
import random as rand

def gen_color(sentence):
    sentence = sentence.split(' ')
    ans_dict = {0: [], 1: [], 2: [], 3: []}
    docs_len = len(sentence)
    for i in range(4):
        for t in range(docs_len):
            color = [0, 0, 0, 0] # R, G, B, Y
            color[i] = 100 + rand.randint(-100, 100)
            color[1] += color[3] // 2
            color[2] += color[3] // 2
            ans_dict[i].append([sentence[t], [color[0], color[1], color[2]]])
    personality = []
    for i in range(4):
        personality.append(rand.randint(0, 1))
    return ans_dict, personality
