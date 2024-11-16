from prettytable import PrettyTable
from database.models.accounts_redis import Accounts


async def main():
    table = PrettyTable()
    table.field_names = ["Email", "Point"]

    db = Accounts()
    accs = await db.get_accounts()
    for k, v in accs.items():
        table.add_row([k, v.point])


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())