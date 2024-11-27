import os
from models.explorer import Explorer

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import explorer as data
else:
    from data import explorer as data


def get_all() -> list[Explorer]:
    return data.get_all()


def get_one(name: str) -> Explorer | None:
    return data.get_one(name)


def create(explorer: Explorer) -> Explorer | None:
    return data.create(explorer)


def modify(name: str, explorer: Explorer) -> Explorer | None:
    return data.modify(name, explorer)


def delete(name: str) -> bool | None:
    return data.delete(name)
