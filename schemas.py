from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]


    class Config:
        orm_mode=True
        schema_extra={
            'example':{
                "username":"example_username",
                "email":"example@gmail.com",
                "password":"password",
                "is_staff":False,
                "is_active":True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key:str='103ef297bc37387bcbe7e833efcb6e111def945a68ee2ce91c7e6a14d5272e4a'
    
class LoginModel(BaseModel):
    username:str
    password:str
    