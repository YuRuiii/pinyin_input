from cgitb import text
from pinyin import input_method
from flask import Flask,jsonify,request,send_from_directory

app = Flask(__name__, static_url_path=None, static_folder=None)

def get_candidates():
    """获取HMM的候选词，要是一个数组"""
    res = input_method(request.args.get('text'))[1]
    ret = []
    for i in range(len(res)):
        ret.append(res[i][0])
    return ret

@app.route("/<path:route>", methods=['GET'])
def getStatic(route):
    return send_from_directory("static", route)


@app.route("/", methods=['GET'])
def getIndex():
    return send_from_directory("static", "index.html")

@app.route('/request',methods=['GET'])
def api():
    params=request.args
    text=params.get('text')
    res=get_candidates()
    return jsonify(["SUCCESS",[[text,res]]])
    
if __name__=='__main__':
    app.run(host='localhost',port=5000,debug=True)