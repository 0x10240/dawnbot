# -*- coding: utf-8 -*-

import json
import datetime
import pytz
from dataclasses import dataclass
from typing import Optional

from loguru import logger
from redis.asyncio import Redis
from redis.asyncio.connection import BlockingConnectionPool


@dataclass
class Account:
    email: str
    proxy: str = ''
    fail_count: int = 0
    headers: Optional[dict] = None
    sleep_until: Optional[datetime.datetime] = None
    session_blocked_until: Optional[datetime.datetime] = None
    point: int = 0

    @classmethod
    def from_dict(cls, data):
        sleep_until = datetime.datetime.fromisoformat(data['sleep_until']) if data['sleep_until'] else None
        session_blocked_until = datetime.datetime.fromisoformat(data['session_blocked_until']) if data[
            'session_blocked_until'] else None
        return cls(
            email=data['email'],
            proxy=data.get('proxy', ''),
            fail_count=data.get('fail_count', 0),
            headers=data['headers'],
            sleep_until=sleep_until,
            session_blocked_until=session_blocked_until,
            point=data.get('point', 0),
        )

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self):
        return {
            'email': self.email,
            'proxy': self.proxy,
            'fail_count': self.fail_count,
            'headers': self.headers,
            'sleep_until': self.sleep_until.isoformat() if self.sleep_until else None,
            'session_blocked_until': self.session_blocked_until.isoformat() if self.session_blocked_until else None,
            'point': self.point,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class Accounts:
    def __init__(self, **kwargs):
        self.name = "dawn_accounts"
        default_kwargs = {
            'db': '2',
            'host': 'redis_host',
            'password': 'redis_password',
            'port': 6379
        }
        default_kwargs.update(kwargs)
        self.db_conn = Redis(
            connection_pool=BlockingConnectionPool(
                decode_responses=True,
                timeout=5,
                socket_timeout=5,
                **default_kwargs
            )
        )

    async def get_account(self, email: str) -> Optional[Account]:
        account_data = await self.db_conn.hget(self.name, email)
        if account_data:
            account = Account.from_json(account_data)
            return account
        else:
            return None

    async def get_accounts(self):
        accounts_data = await self.db_conn.hgetall(self.name)
        accounts = {}
        for email, data_str in accounts_data.items():
            account = Account.from_json(data_str)
            accounts[email] = account
        return accounts

    async def create_account(self, email, headers=None, proxy='', fail_count=0):
        account = Account(
            email=email,
            proxy=proxy,
            fail_count=fail_count,
            headers=headers,
            sleep_until=None,
            session_blocked_until=None,
            point=0
        )
        await self.db_conn.hset(self.name, email, json.dumps(account.__dict__))
        return account

    async def delete_account(self, email: str):
        result = await self.db_conn.hdel(self.name, email)
        return result > 0

    async def set_sleep_until(self, email: str, sleep_until: datetime.datetime):
        account = await self.get_account(email=email)
        if account is None:
            return False

        if sleep_until.tzinfo is None:
            sleep_until = pytz.UTC.localize(sleep_until)
        else:
            sleep_until = sleep_until.astimezone(pytz.UTC)

        account.sleep_until = sleep_until
        await self.db_conn.hset(self.name, email, account.to_json())
        logger.info(f"Account: {email} | Set new sleep_until: {sleep_until}")
        return True

    async def set_account_point(self, email: str, point: int):
        account = await self.get_account(email=email)
        if account is None:
            return False

        account.point = point
        await self.db_conn.hset(self.name, email, account.to_json())

    async def set_session_blocked_until(self, email: str, session_blocked_until: datetime.datetime):
        account = await self.get_account(email=email)
        if account is None:
            account = await self.create_account(email=email)

        if session_blocked_until.tzinfo is None:
            session_blocked_until = pytz.UTC.localize(session_blocked_until)
        else:
            session_blocked_until = session_blocked_until.astimezone(pytz.UTC)

        account.session_blocked_until = session_blocked_until
        await self.db_conn.hset(self.name, email, account.to_json())
        logger.info(
            f"Account: {email} | Set new session_blocked_until: {session_blocked_until}"
        )
        return True

    async def get_fail_count(self, email: str):
        account = await self.get_account(email=email)
        return account.fail_count if account is not None else 0

    async def set_fail_count(self, email: str, fail_count):
        account = await self.get_account(email=email)
        if account is None:
            await self.create_account(email=email)

        account.fail_count = fail_count
        await self.db_conn.hset(self.name, email, account.to_json())
        logger.info(
            f"Account: {email} | sey fail_count: {fail_count}"
        )
        return True

async def main():
    accounts = Accounts()
    res = await accounts.get_accounts()
    return res


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(main()))
