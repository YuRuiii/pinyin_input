from audioop import reverse
from cut import cut
from hmm import json2dict, hmm_start_vector_path, hmm_transition_matrix_path, hmm_emission_matrix_path, hmm_emission_reversed_matrix_path
from math import log

# pre work
start_vector = json2dict(hmm_start_vector_path)
transition_matrix = json2dict(hmm_transition_matrix_path)
emission_matrix = json2dict(hmm_emission_matrix_path)
emission_matrix_T = json2dict(hmm_emission_reversed_matrix_path)

def update_routes(word, prob, routes, limit):
    if len(routes) >= limit:
        to_be_deleted = min(routes, key=routes.get)
        if routes[to_be_deleted] < prob:
            routes.pop(to_be_deleted)
            routes[word] = prob
    else:
        routes[word] = prob
    return routes

def update_wordlist(new_list, original_list, limit):
    # input: 已经排好序的original_list
    return sorted((original_list+new_list), key = lambda kv:(kv[1], kv[0]), reverse=True)[:limit]
        

def greedy(pinyins, limit):
    # initialization
    py = pinyins[0]
    possible_routes = {}
    for ch in emission_matrix_T[py]:
        prob = emission_matrix_T[py][ch]
        if ch in start_vector:
            prob += start_vector[ch]
        else:
            prob += float('-inf')
        possible_routes = update_routes(ch, prob, possible_routes, limit)

    # recursion
    for i in range(1, len(pinyins)):
        last_possible_routes = possible_routes.copy()
        possible_routes = {}
        py = pinyins[i]
        for ch in emission_matrix_T[py]:
            for word in last_possible_routes:
                last_ch = word[-1]
                prob = last_possible_routes[word] + emission_matrix_T[py][ch]
                if last_ch in transition_matrix and ch in transition_matrix[last_ch]:
                    prob += transition_matrix[last_ch][ch]
                else:
                    prob += float('-inf')
                prob += log(len(pinyins)) # 平衡不同长度的划分
                possible_routes = update_routes(word + ch, prob, possible_routes, limit)
    return sorted(possible_routes.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)

def gen_hanzi(pinyin_list, limit=10):
    result_wordlist = list([])
    for pinyins in pinyin_list:
        wordlist = greedy(pinyins, limit)
        # print(pinyins, wordlist)
        result_wordlist = update_wordlist(wordlist, result_wordlist, limit)
    return result_wordlist


# print(greedy(("ni", "hao"), 10))