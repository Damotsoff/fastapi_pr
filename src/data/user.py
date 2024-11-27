from models.user import User
from data import curs, conn, get_db, IntegrityError
from errors import Duplicate, Missing


curs.execute(
    """
    CREATE TABLE IF NOT EXISTS user(
        name TEXT PRIMARY KEY,
        hash TEXT 
    )
"""
)

curs.execute(
    """
    CREATE TABLE IF NOT EXISTS xuser(
        name TEXT PRIMARY KEY,
        hash TEXT
    )"""
)
conn.commit()


def row_to_model(row: tuple) -> User:
    name, hash = row
    return User(name=name, hash=hash)


def model_to_dict(user: User) -> dict:
    return user.dict()


def get_one(name: str) -> User:
    qry = "select * from user where name=:name"
    params = {"name": name}
    print(params)
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"User {name} not found")


def get_all() -> list[User]:
    qry = "select * from user"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def create(user: User, table: str = "user"):
    """Добавление <пользователя> в таблицу user или xuser"""
    qry = f"""insert into {table}
    (name, hash)
    values
    (:name, :hash)"""
    params = model_to_dict(user)
    try:
        curs.execute(qry, params)
        conn.commit()
    except IntegrityError:
        raise Duplicate(msg=f"{table}: user {user.name} already exists")
    return user


def modify(name: str, user: User):
    qry = """update user set
    name=:name, hash=:hash
    where name=:name0"""
    params = {"name": user.name, "hash": user.hash, "name0": name}
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount == 1:
        return get_one(user.name)
    else:
        raise Missing(msg=f"User {name} not found")


def delete(name: str) -> bool | None:
    """Отбрасывание пользователя с именем <name> из таблицы пользователей,
    добавление его в таблицу xuser"""
    user = get_one(name)
    qry = "delete from user where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount != 1:
        raise Missing(msg=f"User {name} not found")
    create(user, table="xuser")
    return None
