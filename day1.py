from flask import Flask, jsonify

app = Flask(__name__)
#Dữ liệu giả lập
users = [
    {'id':1,'name':'Phan Ho Nhat Nam','email':'phannam28082004@gmail.com'},
    {'id':2,'name':'Nguyen Tuan Anh','email':'tuananh@gmail.com'}
]

@app.route('/users',methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users/<int:user_id>',methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id']==user_id),None)
    if user:
        return jsonify(user)
    return jsonify({'error':"User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
    