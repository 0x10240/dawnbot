import os
import yaml
from itertools import cycle
from loguru import logger
from models import Config, Account
from better_proxy import Proxy
from typing import List, Dict, Generator
from utils.ip_utils import fetch_proxy_ip
from prettytable import PrettyTable

CONFIG_PATH = os.path.join(os.getcwd(), "config")
CONFIG_DATA_PATH = os.path.join(CONFIG_PATH, "data")
CONFIG_PARAMS = os.path.join(CONFIG_PATH, "settings.yaml")

REQUIRED_DATA_FILES = ("accounts.txt", "proxies.txt")
REQUIRED_PARAMS_FIELDS = (
    "threads",
    "keepalive_interval",
    "imap_settings",
    "captcha_module",
    "delay_before_start",
    "referral_code",
)


def read_file(
        file_path: str, check_empty: bool = True, is_yaml: bool = False
) -> List[str] | Dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if check_empty and os.stat(file_path).st_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    if is_yaml:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file]


def get_params() -> Dict:
    data = read_file(CONFIG_PARAMS, is_yaml=True)
    missing_fields = set(REQUIRED_PARAMS_FIELDS) - set(data.keys())
    if missing_fields:
        raise ValueError(f"Missing fields in config file: {', '.join(missing_fields)}")
    return data


def get_proxies() -> List[Proxy]:
    try:
        proxies = read_file(
            os.path.join(CONFIG_DATA_PATH, "proxies.txt"), check_empty=False
        )
        return [Proxy.from_str(line) for line in proxies] if proxies else []
    except Exception as exc:
        raise ValueError(f"Failed to parse proxy: {exc}")


def get_accounts(file_name: str) -> Generator[Account, None, None]:
    proxies = get_proxies()
    proxy_cycle = cycle(proxies) if proxies else None
    accounts = read_file(os.path.join(CONFIG_DATA_PATH, file_name), check_empty=False)

    for account in accounts:
        try:
            email, password = account.split(":")
            yield Account(
                email=email,
                password=password,
                proxy=next(proxy_cycle) if proxy_cycle else None,
            )
        except ValueError:
            logger.error(f"Failed to parse account: {account}")


def show_accounts(accounts: List[Account]) -> None:
    table = PrettyTable()
    table.field_names = ["Type", "Email", "Password", "Proxy", "OutboundIp"]
    for account in accounts:
        row = [account.type, account.email, account.password, account.proxy, account.ip]
        table.add_row(row)
    print(table)


def get_yaml_accounts(account_type: str) -> [Account]:
    data = read_file(os.path.join(CONFIG_DATA_PATH, 'accounts.yaml'), check_empty=False, is_yaml=True)
    items = data[account_type]
    accounts = []

    for item in items:
        proxy_str = item.get('proxy')
        proxy_ip = fetch_proxy_ip(proxy_str)
        account = Account(
            type=account_type,
            email=item.get('email', ''),
            password=item.get('password', ''),
            ip=proxy_ip,
            proxy=Proxy.from_str(proxy_str)
        )
        accounts.append(account)

    return accounts


def validate_domains(accounts: List[Account], domains: Dict[str, str]) -> List[Account]:
    for account in accounts:
        domain = account.email.split("@")[1]
        if domain not in domains:
            raise ValueError(
                f"Domain '{domain}' is not supported, please add it to the config file"
            )
        account.imap_server = domains[domain]
    return accounts


def load_config() -> Config:
    try:
        reg_accounts = get_yaml_accounts("register")
        farm_accounts = get_yaml_accounts("farm")

        show_accounts(reg_accounts + farm_accounts)

        if not reg_accounts and not farm_accounts:
            raise ValueError("No accounts found in data files")

        params = get_params()
        config = Config(
            **params, accounts_to_farm=farm_accounts, accounts_to_register=reg_accounts
        )

        if reg_accounts:
            config.accounts_to_register = validate_domains(
                reg_accounts, config.imap_settings
            )

        if config.captcha_module == "2captcha" and not config.two_captcha_api_key:
            raise ValueError("2Captcha API key is missing")
        elif config.captcha_module == "anticaptcha" and not config.anti_captcha_api_key:
            raise ValueError("AntiCaptcha API key is missing")

        return config

    except Exception as exc:
        logger.error(f"Failed to load config: {exc}")
        exit(1)


if __name__ == '__main__':
    load_config()
