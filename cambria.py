from db.models import User
from db.user_api import update_chests, update_proxy
from utils.create_files import get_random_proxy
import random
from eth_account import Account
from eth_account.messages import encode_defunct
from solders.keypair import Keypair
import base58
import aiohttp
from aiohttp import ClientSession
from datetime import datetime, timedelta
from uuid import uuid4
from faker import Faker

class Cambria:
    def __init__(self, user: User) -> None:
        self.user: User = user
        self.session: ClientSession
        self.privy_headers = {'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://lobby.cambria.gg',
            'priority': 'u=1, i',
            'privy-app-id': 'clrdyxkq5018ml90fcw61h764',
            'privy-ca-id': '8177aaff-bafb-4d34-ba03-b24950db6fcf',
            'privy-client': 'react-auth:3.32.2',
            'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"}
        self.cambria_headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.6',
            'origin': 'https://lobby.cambria.gg',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"}
        self.cambria_cookies = {
            'intercom-device-id-jkkmb3fp': str(uuid4()),
            'intercom-id-jkkmb3fp': str(uuid4()),
            'intercom-session-jkkmb3fp': '',
            'privy-token': '',
            'privy-id-token': '',
            'privy-session': 'privy.cambria.gg',
            'cambria_session': '',}

    async def check_proxy(self):
        try:
            response = await self.session.get(url="https://httpbin.org/ip", proxy=self.user.proxy)
            if response.status == 200:
                return True
        except Exception as e:
            print(f"{self.user.evm_address} can't connect to proxy: {e}")
            proxy = get_random_proxy()
            proxy = proxy.strip()
            update_proxy(user_id=self.user.id, new_proxy=proxy)
            self.user.proxy = proxy
            return await self.check_proxy()
        
    async def start_work(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            await self.check_proxy()
            await self.privy_login()
            await self.get_cambria_session()
            await self.create_account()
            await self.sign_drop()
            # if self.user.sol_address and not await self.get_solana_wallets():
            #     print("start link sol wallet")
            #     await self.link_sol_wallet()
            # await self.claim_loot_drop()

    async def get_solana_wallets(self):
        response = await self.session.get(url="https://lobby-api.cambria.gg/solana/wallets", cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        for wallet in data:
            if wallet['solanaAddress'] == self.user.sol_address:
                return True
        return False

    async def sign_drop(self):
        message = f'Cambria - Genesis Event Opt-in Agreement\n\nI acknowledge and agree to the terms and conditions of the Genesis Event Opt-In Agreement. This signature designates the wallet below as my primary wallet for interacting with token-related functionality for the Genesis Event.\n\nWallet: {self.user.evm_address}\nVersion: genesis-event-opt-in-2026-09-14-v3'
        signed = Account.sign_message(
            encode_defunct(text=message),
            self.user.evm_private
        )
        signature = signed.signature.hex()
        signature = "0x" + signature
        json_data = {
            'wallet_address': self.user.evm_address,
            'signature': signature,
        }
        response = await self.session.post(url="https://lobby-api.cambria.gg/genesis-event/notice/sign", json=json_data, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        print(data)
        if response.status == 200:
            print(f"{self.user.evm_address} success sign message")
        return True
        



    async def link_sol_wallet(self):
        params = {
            'solanaAddress': self.user.sol_address,
        }
        response = await self.session.get(url="https://lobby-api.cambria.gg/solana/auth/message", params=params, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        message = data["message"]
        nonce = data['nonce']
        keypair = Keypair.from_base58_string(self.user.sol_private)
        signature = keypair.sign_message(message.encode("utf-8"))
        signature_base58 = base58.b58encode(bytes(signature)).decode()
        json_data = {
            'solanaAddress': str(self.user.sol_address),
            'signature': str(signature_base58),
            'message': message,
            'nonce': nonce,
        }
        response = await self.session.post(url="https://lobby-api.cambria.gg/solana/auth/verify", json=json_data, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        verifed = data['verified']
        if verifed:
            print(f"{self.user.evm_address} success connect sol address: {self.user.sol_address}")
            await self.update_linked_wallets()
            return True
        if not verifed:
            print(f"{self.user.evm_address} can't connect sol address: {self.user.sol_address}")
            return False


    async def update_linked_wallets(self):
        await self.session.put(url="https://lobby-api.cambria.gg/user/update-linked-wallets", cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        return True

    async def claim_box(self, data_set: str):
        json_data = {
            'datasetVersion': data_set,
        }
        response = await self.session.post(url="https://lobby-api.cambria.gg/scores/loot-drop/claim", json=json_data, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        if response.status == 200:
            print(f"{self.user.evm_address} success claim box")
        return True

    async def claim_loot_drop(self):
        response = await self.session.get(url="https://lobby-api.cambria.gg/scores/loot-drop", headers=self.cambria_headers, cookies=self.cambria_cookies, proxy=self.user.proxy)
        data = await response.json()
        eligible = data['eligible']
        data_version = data['datasetVersion']
        claim = data['claim']
        claim_enable = data['claimsEnabled']
        if eligible:
            chests = data['chests']
            common_chest = chests['common']
            epic_chest = chests['epic']
            legendary_chest = chests['legendary']
            print(f"{self.user.evm_address} eligible for Common Chests: {common_chest}. Epic Chests: {epic_chest}. Legendary Chest: {legendary_chest}")
            update_chests(user_id=self.user.id, common_chests=common_chest, epic_chests=epic_chest, legendary_chests=legendary_chest)
        else:
            print(f"{self.user.evm_address} don't eligible for any chests")
        if claim_enable and not claim:
            return await self.claim_box(data_set=data_version)


    async def create_account(self):
        current = await self.get_current()
        player_name = current['player_name']
        character_layers = current['character_layers']
        invited = current['invited']
        if player_name and character_layers and invited:
            return True
        if not player_name:
            await self.set_nickname()
        if not character_layers:
            await self.set_character()
        if not invited:
            await self.set_invite()
        return True

    async def set_invite(self):
        json_data = {
            'code': 'thedescent',
        }
        await self.session.post(url="https://lobby-api.cambria.gg/invitation/validate", json=json_data, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        return

    async def check_avaliable_name(self, user_name: str):
        params = {
            'username': user_name,
        }
        response = await self.session.get(url="https://lobby-api.cambria.gg/user/username", params=params, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        return data['available']

    async def set_character(self):
        json_data = {
            'character_layers': [
                f'color{random.randint(1,3)}',
                f'eyes{random.randint(1,3)}',
                f'hair{random.randint(1,6)}',
                f'palette_{random.randint(1,8)}',
            ],
        }
        response = await self.session.put(url="https://lobby-api.cambria.gg/user/character", json=json_data, cookies=self.cambria_cookies, headers=self.cambria_headers, proxy=self.user.proxy)
        data = await response.json()
        if data['character_layers']:
            print(f"{self.user.evm_address} success set character")
            return True
        return await self.set_character()

    async def set_nickname(self):
        generate_name = Faker().user_name()
        check_avaliable = await self.check_avaliable_name(user_name=generate_name)
        if not check_avaliable:
            return await self.set_nickname()
        json_data = {
            'display_name_type': 'name',
            'player_name': generate_name,
        }
        response = await self.session.put(url="https://lobby-api.cambria.gg/user/username", headers=self.cambria_headers, cookies=self.cambria_cookies, json=json_data, proxy=self.user.proxy)
        data = await response.json()
        if data['player_name']:
            print(f"{self.user.evm_address} success set nickname: {generate_name}")
            return True
        return await self.set_nickname()

    async def get_current(self):
        response = await self.session.get(url="https://lobby-api.cambria.gg/user/current", headers=self.cambria_headers, cookies=self.cambria_cookies, proxy=self.user.proxy)
        data = await response.json()
        return data

    async def privy_login(self):
        json_data = {
            'address': self.user.evm_address,
        }
        response = await self.session.post(url="https://privy.cambria.gg/api/v1/siwe/init", headers=self.privy_headers, json=json_data, proxy=self.user.proxy)
        data = await response.json()
        nonce = data['nonce']
        expires_at = data['expires_at']
        dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        dt_minus_10 = dt - timedelta(minutes=10)
        issued_at = dt_minus_10.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        message = f'lobby.cambria.gg wants you to sign in with your Ethereum account:\n{self.user.evm_address}\n\nBy signing, you are proving you own this wallet and logging in. This does not initiate a transaction or cost any fees.\n\nURI: https://lobby.cambria.gg\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {issued_at}\nResources:\n- https://privy.io'
        signed = Account.sign_message(
            encode_defunct(text=message),
            self.user.evm_private
        )
        signature = signed.signature.hex()
        signature = "0x" + signature
        json_data = {
            'message': message,
            'signature': signature,
            'chainId': 'eip155:1',
            'walletClientType': 'rabby_wallet',
            'connectorType': 'injected',
            'mode': 'login-or-sign-up',
        }
        response = await self.session.post(url="https://privy.cambria.gg/api/v1/siwe/authenticate", headers=self.privy_headers, json=json_data, proxy=self.user.proxy)
        data = await response.json()
        self.cambria_cookies['privy-token'] = data['token']
        self.cambria_cookies['privy-id-token'] = data['identity_token']

    async def get_cambria_session(self):
        params = {
            'powChallengeId': '00000000-0000-0000-0000-000000000000',
        }
        response = await self.session.get(url="https://lobby-api.cambria.gg/auth/verify", params=params,cookies=self.cambria_cookies,headers=self.cambria_headers, proxy=self.user.proxy)
        cambria_session = response.cookies["cambria_session"].value
        self.cambria_cookies["cambria_session"] = cambria_session
