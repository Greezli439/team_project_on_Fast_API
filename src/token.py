from fastapi import FastAPI, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer 
from fastapi.responses import JSONResponse 
from pydantic import BaseModel 
from typing import List 

app = FastAPI() 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # Припустимо, у вас є такий маршрут для отримання токену 
blacklisted_tokens = set() # Список для збереження чорного списку токенів (в реальному застосунку використовуйте базу даних) 

class TokenData(BaseModel): 
    access_token: str 
    token_type: str 
    
@app.post("/logout/") 
async def logout(token_data: TokenData = Depends(oauth2_scheme)):  
    blacklisted_tokens.add(token_data.access_token)  # Додаємо access token до чорного списку
    return JSONResponse(content={"message": "Successfully logged out"})  # Опціонально: повертаємо підтвердження про вихід зі системи


@app.get("/secure-page/") 
async def secure_page(token_data: TokenData=Depends(oauth2_scheme)):
# Перевірка, чи токен не міститься в чорному списку 
    if token_data.access_token in blacklisted_tokens: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") 
        # Код для захищеного маршруту тут 
    return {"message": "This is a secure page"}

