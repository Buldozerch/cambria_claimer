from pathlib import Path
import random

from eth_account import Account
from solders.keypair import Keypair

proxys = []


def create_files():
    global proxys
    Path("files").mkdir(exist_ok=True)
    Path("files/private_evm.txt").touch(exist_ok=True)
    Path("files/private_sol.txt").touch(exist_ok=True)
    Path("files/proxy.txt").touch(exist_ok=True)
    with open("files/proxy.txt", "r") as f:
        proxys = [line.strip() for line in f.readlines() if line.strip()]


def get_random_proxy():
    if not proxys:
        return None
    return random.choice(proxys)


def create_users():
    global proxys
    from db.user_api import create_user, get_user_private_evm

    with open("files/private_evm.txt", "r") as f:
        evm_privates = [line.strip() for line in f.readlines()]
    with open("files/proxy.txt", "r") as f:
        proxys = [line.strip() for line in f.readlines()]
    with open("files/private_sol.txt", "r") as f:
        sol_privates = [line.strip() for line in f.readlines()]

    count = 0
    for evm_private in evm_privates:
        if not evm_private:
            continue
        if get_user_private_evm(private_evm=evm_private):
            count += 1
            continue
        proxy = None
        sol_address = None
        sol_private = None
        if proxys and count < len(proxys) and proxys[count]:
            proxy = proxys[count]
        if sol_privates and count < len(sol_privates) and sol_privates[count]:
            sol_private = sol_privates[count]
            keypair = Keypair.from_base58_string(sol_private)
            sol_address = str(keypair.pubkey())
        evm_address = Account.from_key(evm_private).address
        create_user(evm_private=evm_private, evm_address=evm_address, sol_private=sol_private, sol_address=sol_address, proxy=proxy)
        count += 1

