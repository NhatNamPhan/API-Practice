from flask import Flask, jsonify, request

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

@app.route('/users',methods=['POST'])
def add_user():
    new_user = request.get_json()
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>',methods=["DELETE"])
def delete_user(user_id):
    user = next((u for u in users if u['id'] == user_id),None)
    if not user:
        return jsonify({'error':"User not found"}), 404
    users.remove(user)
    return jsonify({'message':f'User with ID {user_id} has been deleted'})

@app.route('/users/<int:user_id>',methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u['id'] == user_id),None)
    if not user:
        return jsonify({'error':'User not found'}), 404
    updated_data = request.get_json()
    user.update(updated_data)
    return jsonify(user)    

if __name__ == '__main__':
    app.run(debug=True)
    