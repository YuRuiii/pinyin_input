from math import log
from tqdm import tqdm
from pypinyin import Style, pinyin
import json

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
    # input:  path:       字典所应保存的位置
    # output: ret_dict:   转换的字典
    ret_dict = {}
    with open(path, 'r') as f:
        ret_dict = json.load(f)
    return ret_dict


# 读入词汇频率数据
def read_wordfreq():
    # output: 词汇-频率的generator
    with open(wordfreq_filepath, 'r', encoding='ANSI') as f:
        for line in f:
            try:
                word, freq = line.split()
                # 判断字符串word中的每个字符是否都是中文
                if all('\u4e00' <= ch <= '\u9fff' for ch in word):
                    yield word, int(freq)
            except:
                print(line)
                
# 生成状态转移概率矩阵
def gen_transition_matrix():
    # 生成状态频数矩阵
    freq_matrix = {}
    for word, freq in tqdm(read_wordfreq()):
        for i in range(1, len(word)):
            former_ch = word[i-1]
            latter_ch = word[i]
            if former_ch in freq_matrix:
                if latter_ch in freq_matrix[former_ch]:
                    freq_matrix[former_ch][latter_ch] += freq
                else:
                    freq_matrix[former_ch][latter_ch] = freq
            else:
                freq_matrix[former_ch] = {latter_ch: freq}
    dict2json(freq_matrix, hmm_transition_freq_matrix_path) # 将生成内容保存在json文件中

    # 生成状态转移概率矩阵
    transition_matrix = {}
    for key_i in freq_matrix:
        freq_sum = sum(freq_matrix[key_i].values())
        transition_matrix[key_i] = {}
        for key_j in freq_matrix[key_i]:
            transition_matrix[key_i][key_j] = log(freq_matrix[key_i][key_j]/freq_sum)
    dict2json(transition_matrix, hmm_transition_matrix_path)

# 生成估计观测概率矩阵
def gen_emission_matrix(initial_weight=0.1):
    # input: initial_weight，在估计观测概率预测中的，缩拼的权重（全拼的权重为1），default为0.1

    # 首先计算估计观测频数矩阵
    ## 计算全拼的观测频数
    freq_matrix = {}
    for word, freq in tqdm(read_wordfreq()):
        pinyins = pinyin(word, style=Style.NORMAL)
        for i in range(len(word)):
            ch = word[i]
            py = pinyins[i][0]
            if ch in freq_matrix:
                if py in freq_matrix[ch]:
                    freq_matrix[ch][py] += freq
                else:
                    freq_matrix[ch][py] = freq
            else:
                freq_matrix[ch] = {py: freq}

    ## 加入缩拼的观测频数
    ## 规则: 缩拼的观测频数 = 以该缩拼为首的所有拼音中的最大频数 * 缩拼的权重initial_weight
    for ch in freq_matrix:
        #pys = freq_matrix[ch].keys()
        #print(pys)
        for py in list(freq_matrix[ch]):
            initial = py[0]
            #print(freq_matrix[ch][py], initial_weight, type(freq_matrix[ch][py]), type(initial_weight))
            initial_freq = freq_matrix[ch][py] * initial_weight
            if initial in freq_matrix[ch]:
                if freq_matrix[ch][initial] < initial_freq:
                    freq_matrix[ch][initial] = initial_freq
            else:
                freq_matrix[ch][initial] = initial_freq
            # 特别考虑"zh", "ch", "sh"
            if py[0:2] == "zh" or py[0:2] == "ch" or py[0:2] == "sh":
                x = py[0:2]
                x_freq = freq_matrix[ch][py] * initial_weight
                if x in freq_matrix[ch]:
                    if freq_matrix[ch][x] < x_freq:
                        freq_matrix[ch][x] = x_freq
                else:
                    freq_matrix[ch][x] = x_freq
    dict2json(freq_matrix, hmm_emission_freq_matrix_path)

    # 接着计算估计观测概率矩阵
    emission_matrix = {}
    for key_i in freq_matrix:
        freq_sum = sum(freq_matrix[key_i].values())
        emission_matrix[key_i] = {}
        for key_j in freq_matrix[key_i]:
            emission_matrix[key_i][key_j] = log(freq_matrix[key_i][key_j]/freq_sum)
    dict2json(emission_matrix, hmm_emission_matrix_path)
    

    # 接着计算估计观测矩阵的反向查找矩阵(为了计算方便)
    reversed_freq_matrix = {}
    for ch in freq_matrix:
        for py in freq_matrix[ch]:
            if py in reversed_freq_matrix:
                reversed_freq_matrix[py][ch] = freq_matrix[ch][py]
            else:
                reversed_freq_matrix[py] = {ch: freq_matrix[ch][py]}
    dict2json(reversed_freq_matrix, hmm_emission_reversed_freq_matrix_path)

    # 接着计算估计观测矩阵的反向查找矩阵(为了计算方便)
    reversed_matrix = {}
    for ch in emission_matrix:
        for py in emission_matrix[ch]:
            if py in reversed_matrix:
                reversed_matrix[py][ch] = emission_matrix[ch][py]
            else:
                reversed_matrix[py] = {ch: emission_matrix[ch][py]}
    dict2json(reversed_matrix, hmm_emission_reversed_matrix_path)

# 生成初始状态概率向量
def gen_start_vector():
    # 生成初始状态频数向量
    start_freq = {}
    total_freq = 0
    for word, freq in tqdm(read_wordfreq()):
        total_freq += freq
        ch = word[0]
        if ch in start_freq:
            start_freq[ch] += freq
        else:
            start_freq[ch] = freq
    dict2json(start_freq, hmm_start_freq_path)
    # 生成初始状态概率向量
    start_vector = {}
    for key in start_freq:
        start_vector[key] = log(start_freq[key]/total_freq)
    dict2json(start_vector, hmm_start_vector_path)



if __name__ == "__main__":
    #gen_transition_matrix()
    gen_emission_matrix()
    #gen_start_vector()