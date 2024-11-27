from data import curs, conn
from models.creature import Creature
from errors import Missing, Duplicate

# Создание таблицы (если не существует) | Creating a table (if it does not exist)
curs.execute(
    """
    CREATE TABLE IF NOT EXISTS creature(
        name TEXT PRIMARY KEY,
        country TEXT,
        area TEXT,
        description TEXT,
        aka TEXT
    )
"""
)
conn.commit()


def row_to_model(row: tuple) -> Creature:
    """Конвертирует строку из базы данных в модель Creature."""
    name, country, area, description, aka = row
    return Creature(
        name=name, country=country, area=area, description=description, aka=aka
    )


def model_to_dict(creature: Creature) -> dict:
    """Конвертирует модель Creature в словарь для SQL-запросов."""
    return creature.dict()


def create(creature: Creature):
    """Добавляет запись в таблицу creature."""
    try:
        qry = """INSERT  INTO creature
                (name, country, area, description, aka)
                VALUES
                (:name, :country, :area, :description, :aka)"""
        params = model_to_dict(creature)
        curs.execute(qry, params)
        conn.commit()
        return creature
    except Exception as e:
        raise Duplicate(msg=e)


def get_one(name: str) -> Creature:
    qry = "select * from creature where name=:name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"Creature {name} not found")


def get_all() -> list[Creature]:
    """Возвращает все записи из таблицы creature."""
    qry = "SELECT * FROM creature"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def get_random_name() -> str:
    """Возвращает случайное имя из таблицы creature."""
    qry = "SELECT name FROM creature ORDER BY random() LIMIT 1"
    curs.execute(qry)
    row = curs.fetchone()
    if row:
        return row[0]


def modify(name: str, creature: Creature) -> Creature:
    qry = """update creature set
             name=:name,
             country=:country,
             area=:area,
             description=:description,
             aka=:aka
             where name=:orig_name"""
    params = model_to_dict(creature)
    params["orig_name"] = name
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount == 1:
        return get_one(creature.name)
    else:
        raise Missing(msg=f"Creature {name} not found")


def delete(name: str):
    qry = "delete from creature where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    conn.commit()
    if curs.rowcount != 1:
        raise Missing(msg=f"Creature {name} not found")
