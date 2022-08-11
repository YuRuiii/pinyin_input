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