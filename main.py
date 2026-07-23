from utils.create_files import create_files, create_users 
create_files()
from cambria import Cambria
import asyncio
from db.user_api import User, get_users

# CHANGE FOR MORE ACCOUNTS 
semaphore = asyncio.Semaphore(2)

async def start_action(user: User):
    async with semaphore:
        try:
            cambria = Cambria(user=user)
            await cambria.start_work()
        except Exception as e:
            print(f"{user.evm_address} has error: {e}")

async def main():
    user_input = int(input(f"Choose action:\n1. Init DB\n2. Start Actions\nAction: "))
    if user_input == 1:
        create_users()
    elif user_input == 2:
        users = get_users()
        tasks = []
        for user in users:
            tasks.append(start_action(user=user))
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        print(f"No action {user_input}")

if __name__ == "__main__":
    create_files()
    asyncio.run(main())
