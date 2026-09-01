from sqlalchemy.orm import Session
from models import User

def add_user_with_limit(db: Session, identifier: str, test_count: int = 5):
    """
    identifier: Username (@username yoki username) yoki Telegram ID (12345678)
    test_count: Beriladigan testlar soni (default: 5)
    """
    identifier = str(identifier).strip()
    
    # Username'dan '@' belgisini olib tashlaymiz
    if identifier.startswith("@"):
        identifier = identifier[1:]

    # ID yoki Username ekanligini aniqlash
    is_id = identifier.isdigit()

    if is_id:
        user = db.query(User).filter(User.telegram_id == int(identifier)).first()
    else:
        user = db.query(User).filter(User.username.ilike(identifier)).first()

    if user:
        # Foydalanuvchi mavjud bo'lsa, limitiga 5 ta qo'shiladi
        user.tests_limit += test_count
        db.commit()
        db.refresh(user)
        return {"status": "updated", "msg": f"Mavjud foydalanuvchiga {test_count} ta test qo'shildi. Jami limit: {user.tests_limit}"}
    else:
        # Yangi foydalanuvchi yaratiladi
        if is_id:
            new_user = User(telegram_id=int(identifier), tests_limit=test_count)
        else:
            new_user = User(username=identifier, tests_limit=test_count)
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "created", "msg": f"Yangi foydalanuvchi yaratildi va {test_count} ta test limiti berildi."}