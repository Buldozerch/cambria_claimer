from .db import DB
from .models import User

db = DB()
db.create_tables()

def create_user(evm_private: str,evm_address: str, sol_private: str | None, sol_address: str | None, proxy: str | None):
    user = User(
        evm_private=evm_private,
        evm_address=evm_address,
        sol_private=sol_private,
        sol_address=sol_address,
        proxy=proxy
    )
    db.session.add(user)
    db.session.commit()
    print(f"Success add user {evm_address}")

def get_user(user_id: int):
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    return user
def get_user_private_evm(private_evm: str):
    user = db.session.query(User).filter(User.evm_private == private_evm).first()
    if not user:
        return None
    return user

def get_users():
    all_users = db.session.query(User).all()
    return all_users

def update_proxy(user_id: int, new_proxy: str):
    user = get_user(user_id=user_id)
    if not user:
        print("user not found")
        return
    user.proxy = new_proxy
    db.session.commit()
    print(f"[{user_id}] Success update user proxy!")

def update_chests(user_id: int, common_chests: int = 0, epic_chests: int = 0, legendary_chests: int = 0):
    user = get_user(user_id=user_id)
    if not user:
        print("user not found")
        return
    user.common_chests = common_chests
    user.epic_chests = epic_chests
    user.legendary_chests = legendary_chests
    db.session.commit()


def delete_user(user_id: int):
    user = get_user(user_id)

    if not user:
        return
    db.session.delete(user)
    db.session.commit()
