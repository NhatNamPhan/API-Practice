from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

#Đinh nghĩa schema dữ liệu
class User(BaseModel):
    id: int
    name: str
    email: str
    
#Dữ liệu giả lập
users: List[User] = [
    User(id=1,name='Phan Ho Nhat Nam',email='namphan12345@gmail.com'),
    User(id=2,name='Nguyen Tuan Anh',email='anh123@gmail.com')
]

@app.get('/users', response_model=List[User])
async def get_users():
    return users

@app.get('/users/{user_id}',response_model=User)
async def get_users_id(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    return {'error':'User not found'}

@app.post('/users',response_model=User)
async def add_user(user: User):
    users.append(user)
    return user

@app.put('/users/{user_id}',response_model=User)
async def update_user(user_id:int, updated_user:User):
    for idx, user in enumerate(users):
        if user.id == user_id:
            users[idx] = updated_user
            return updated_user
    return {'error':'User not found'}

@app.delete('/users/{user_id}',response_model=User)
async def delete_user(user_id:int):
    for user in users:
        if user.id == user_id:
            users.remove(user)
            return user
    return {'error':'User not found'}