from pathlib import Path
import random
from eth_account import Account
from solders.keypair import Keypair
from db.user_api import create_user, get_user_private_evm


def create_files():
    Path("files").mkdir(exist_ok=True)
    Path("files/private_evm.txt").touch(exist_ok=True)
    Path("files/private_sol.txt").touch(exist_ok=True)
    Path("files/proxy.txt").touch(exist_ok=True)

with open("files/private_evm.txt", "r") as file_evm_private:
    evm_privates = file_evm_private.readlines()
with open("files/proxy.txt", "r") as file_proxy:
    proxys = file_proxy.readlines()
with open("files/private_sol.txt", "r") as file_sol_private:
    sol_privates = file_sol_private.readlines()


def get_random_proxy():
    return random.choice(proxys)

def create_users():
    count = 0
    for evm_private in evm_privates:
        evm_private = evm_private.strip()
        if get_user_private_evm(private_evm=evm_private):
            continue
        proxy = None
        sol_address = None
        sol_private = None
        if proxys and len(proxys) >= count:
            proxy = proxys[count].strip()
        if sol_privates and len(sol_privates) >= count:
            sol_private = sol_privates[count].strip()
            keypair = Keypair.from_base58_string(sol_private)
            sol_address = keypair.pubkey()
        sol_address = str(sol_address) if sol_address else None
        evm_address = Account.from_key(evm_private).address
        create_user(evm_private=evm_private, evm_address=evm_address,sol_private=sol_private, sol_address=sol_address,proxy=proxy)
        count += 1

