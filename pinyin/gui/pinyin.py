from math import log
import json

def input_method(input_str, is_quanpin=True, has_separator=False, limit=10):
    cut_res = cut(input_str, is_quanpin, has_separator)
    hanzi_res = gen_hanzi(cut_res, limit)
    return cut_res, hanzi_res


# '../data/possible_pinyin.txt'中存储的是所有可能的拼音序列，pinyin_set即所有可能的全拼序列
quanpin_set = set()
with open('data/possible_pinyin.txt', 'r', encoding='utf-8') as f:
    quanpin_set = set(s for s in f.read().split('\n'))


# 对用户输入的字符串进行分割 
def pinyin_cut(input_str: str, is_quanpin=True, has_separator=False) -> list:
    # input:  s: 用户输入的字符串,可能包括以下情况: 1.全拼；2.拼音首字母（包括zh，sh，ch）；3.分隔符号「'」
    #         is_quanpin: 输入是否一定是全拼，default为True
    #         has_split: 输入是否有分隔符，default为False
    # output: ret_list: 列表，包含所有可能的拼音分割情况
    # example: pinyin_cut("nihao") == [["ni", "hao"], ["ni", "h", "ao"]]
    
    # 如果是全拼的话，pinyin_set就是所有可能的全拼的集合
    if is_quanpin:
        pinyin_set = quanpin_set
    # 否则，pinyin_set就是全拼集合与声母集合的并集
    else:
        shengmu = {'b','p','m','f','d','t','n','l','g','k','h','j','q','x','zh','ch','sh','r','z','c','s','y','w'}
        pinyin_set = quanpin_set.union(shengmu)
    
    ret_list = []
    # 如果允许使用分割符号「'」进行分割的话，按照分割符分割，输出res_list
    if has_separator and '\'' in input_str:
        separated_strs = input_str.split('\'')
        # print("separated_strs", separated_strs)
        # 对于分割后的每个子字符串，递归调用pinyin_cut再进行分割
        for i in range(len(separated_strs)):
            sub_list = pinyin_cut(separated_strs[i], is_quanpin=is_quanpin, has_separator=False)
            # print("sub_list", sub_list)
            # 如果两个列表都非空，则进行叠加
            if ret_list and sub_list:
                new_list = []
                for e1 in ret_list:
                    for e2 in sub_list:
                        new_list.append(e1.copy()+e2.copy())
                ret_list = new_list
            elif not ret_list:
                ret_list = sub_list
            # print("ret_list", ret_list)
        return ret_list
    else:
        # 如果输入的字符串就在pinyin_set中
        if input_str in pinyin_set:
            ret_list = [[input_str]]
        # 否则递归调用
        for i in range(1, len(input_str)):
            if input_str[:i] in pinyin_set:
                sub_list = pinyin_cut(input_str[i:], is_quanpin=is_quanpin, has_separator=False)
                for e in sub_list:
                    e.insert(0, input_str[:i])
                ret_list += sub_list
    return ret_list

def normalize(pinyins):
    for py in pinyins:
        for i in range(len(py)):
            # print("py: ", py)
            if 'ue' in py[i] and py[i][0] not in ['j', 'q', 'x', 'y']:
                # print(py[i], py[i].replace('u', 'v'))
                py[i] = py[i].replace('u', 'v')
    return pinyins

def cut(pinyins, is_quanpin=True, has_separator=False):
    return normalize(pinyin_cut(pinyins, is_quanpin, has_separator))

# print(cut("lue", has_separator=True))


wordfreq_filepath = "data/global_wordfreq.release.txt"
hmm_start_freq_path = "data/generated/hmm_start_freq.json"
hmm_start_vector_path = "data/generated/hmm_start_vector.json"
hmm_transition_freq_matrix_path = "data/generated/hmm_transition_freq_matrix.json"
hmm_transition_matrix_path = "data/generated/hmm_transition_matrix.json"
hmm_emission_freq_matrix_path = "data/generated/hmm_emission_freq_matrix.json"
hmm_emission_matrix_path = "data/generated/hmm_emission_matrix.json"
hmm_emission_reversed_freq_matrix_path = "data/generated/hmm_emission_reversed_freq_matrix.json"
hmm_emission_reversed_matrix_path = "data/generated/hmm_emission_reversed_matrix.json"

# 将字典保存为json文件
def dict2json(dictionary, path):
    # input:  dictionary: 待保存的字典
    #         path:       字典所应保存的位置
    json_str = json.dumps(dictionary, ensure_ascii=False, indent=4, sort_keys=True)
    with open(path, 'w') as f:
        f.write(json_str)

# 将json文件转换为字典
def json2dict(path):
    # input:  path:       字典保存的位置
    # output: ret_dict:   转换的字典
    ret_dict = {}
    with open(path, 'r') as f:
        ret_dict = json.load(f)
    return ret_dict


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