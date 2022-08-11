from cut import cut
from greedy import gen_hanzi
import cowsay

def input_method(input_str, is_quanpin=True, has_separator=False, limit=10):
    cut_res = cut(input_str, is_quanpin, has_separator)
    hanzi_res = gen_hanzi(cut_res, limit)
    return cut_res, hanzi_res

# 命令行运行
def cli():
    cowsay.cow("欢迎使用智能拼音输入法")
    print("现进入命令行模式, 默认设置请输入\"Y\", 自定义参数请输入\"N\"，开始运行后，可输入\"!\"结束运行")
    is_quanpin = False
    has_separator = True
    limit = 10
    show_cut = False
    show_prob = False
    read_input = lambda x: True if x == "Y" else False

    # 自定义参数
    if input() == "N":
        print("拼音输入是否均为全拼?(Y/N)")
        is_quanpin = read_input(input())
        print("拼音输入是否包含分隔符「'」?(Y/N)")
        has_separator = read_input(input())
        print("每次输出的汉字序列数为?(请输入任意数字)")
        limit = int(input())
        print("是否显示划分相关数据?(Y/N)")
        show_cut = read_input(input())
        print("是否显示概率相关数据?(Y/N)")
        show_prob = read_input(input())

    while True:
        print("请输入拼音:")
        input_str = input()
        if input_str == "!":
            print("yr's智能输入法结束运行")
            return
        cut_raw_info, hanzi_raw_info = input_method(input_str, is_quanpin, has_separator, limit)
        if show_cut:
            print("可能的划分有:", cut_raw_info)
        if show_prob:
            for i in range(len(hanzi_raw_info)):
                print(i, hanzi_raw_info[i][0], hanzi_raw_info[i][1])
        else:
            for i in range(len(hanzi_raw_info)):
                print(i, hanzi_raw_info[i][0])

if __name__ == "__main__":
    cli()




        