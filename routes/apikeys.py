from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/apikeys", tags=["API Keys"])

# CREATE API Key
@router.post("/{user_id}", response_model=ApiKeyOut)
def create_apikey(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_key = ApiKey( user_id=user_id)
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    return new_key

# DELETE API Key
@router.delete("/{apikey_id}")
def delete_apikey(apikey_id: str, db: Session = Depends(get_db)):
    key = db.query(ApiKey).filter(ApiKey.id == apikey_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(key)
    db.commit()
    return {"message": "API key deleted successfully"}