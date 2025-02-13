from flask import Flask, render_template 
from flask import request, jsonify  
from flask_cors import CORS
from flask.views import MethodView
import os  
import interface_totxt
import interface_train
import interface_predict
from extension import db

app = Flask(__name__)
CORS().init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1:3306/sa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/')
def index():
    return 'This is Trajectory Prediction Interface.'


# 设置上传文件夹（如果不设置，文件会被存储在内存中，上传大文件时可能会遇到问题）  
UPLOAD_FOLDER = './uploads'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  

# 确保上传文件夹存在  
if not os.path.exists(UPLOAD_FOLDER):  
    os.makedirs(UPLOAD_FOLDER)  
    
    
# 上传文件
@app.route('/upload', methods=['POST'])  
def upload():  
    if request.method == 'POST' and request.is_json:  
        # 从POST请求中解析JSON数据  
        data0 = request.get_json()  
        data = data0[0]['data']
        entity_id = data0[0]['entity_id'] # entity_id范围[0,49]
        
        # 把json数据转为txt格式
        interface_totxt.work(data, entity_id) 
        interface_train.work() 
        ans = interface_predict.work() # 预测 
                
        # 返回预测结果
        return jsonify({'y_hat': ans}), 200
        
    else:  
        # 如果不是POST请求或者不是JSON数据，返回错误信息  
        return jsonify({"error": "Invalid request"}), 400 
    

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5001, debug=True)
