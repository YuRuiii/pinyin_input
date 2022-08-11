# pinyin_input
基于hmm和贪心算法的智能拼音输入法，暑期课程“程序设计实训”的作业之一。

### 使用指南

首先安装依赖

```
cd pinyin
pip install -r requirements.txt
```

智能拼音输入法提供两种模式——命令行模式和GUI模式。

#### 命令行模式

```
python code/main.py
```

根据提示在终端输入即可

#### GUI模式

```
python gui/server.py
```

然后在浏览器输入

```
http://localhost:5000/
```

即可运行
