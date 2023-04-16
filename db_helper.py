import sqlite3

ON = 'turn_on'
POUR_INTO = 'pour_into'
POUR_OUT = 'pour_out'
OFF = 'turn_off'


def get_operation_by_name(conn: str, name: str) -> str:
    """
    Функция, которая найдет тип операции по имени и вернет id типа операции
    :param conn: подключение к БД, надо передать имя БД
    :param name: имя типа операции
    :return: id типа операции
    """
    req = '''SELECT id, operation_type FROM operation_type
            WHERE operation_type = ?'''
    cursor = conn.execute(req, (name,))
    return cursor.fetchall()


def add_operation(conn: str, name: str) -> None:
    """
    Функция, которая добавляет в БД тип операции
    :param conn: подключение к БД надо передать имя БД
    :param name: имя типа операции
    :return: None
    """
    if len(get_operation_by_name(conn, name)):
        return
    req = '''INSERT INTO operation_type
            (operation_type) values (?)'''
    conn.execute(req, (name,))
    conn.commit()


def add_history_record(conn: str, time: str, operation_id: str) -> None:
    """
    Функция, которая записывает действия пользователя
    :param conn: подключение к БД надо передать имя БД
    :param time: время, когда была сделана запись
    :param operation_id: id тип операции
    :return: None
    """
    req = '''INSERT INTO history
            (time, operation_type_id) values (?,?)'''
    conn.execute(req, (time, operation_id))
    conn.commit()


if __name__ == '__main__':
    conn = sqlite3.connect('history.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS history
                    (id INTEGER PRIMARY KEY,
                    time INTEGER,
                    operation_type_id INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS operation_type
                    (id INTEGER PRIMARY KEY,
                    operation_type TEXT)''')
    conn.commit()
    add_operation(conn, ON)
    add_operation(conn, POUR_INTO)
    add_operation(conn, POUR_OUT)
    add_operation(conn, OFF)
    conn.close()
