import sqlite3
import os
import random

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    async def add_user(self, user_id, name, surname, group):
        with self.connection:
            self.cursor.execute(f"INSERT INTO 'trainee' ('user_id', 'name', 'surname', 'signup', 'group') VALUES (?, ?, ?, 'done', ?)",(user_id, name, surname, group,))

    async def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * from 'trainee' where user_id= ?", (user_id,)).fetchall()
            return bool(len(result))

    async def upload_test(self, test_name, test_body, max_test_code):
        with self.connection:
            self.cursor.execute(f"INSERT INTO tests_name_dict (test_code, test_name) VALUES ('{max_test_code}', '{test_name}')")
            self.cursor.execute(f"INSERT INTO test_dict VALUES {test_body}")

    async def max_test_code(self):
        with self.connection:
            max_test_code = self.cursor.execute("SELECT max(test_code) from tests_name_dict")
            return list(max_test_code)[0][0]

    def set_notstarted_tasks(self, user_id):
        number_files = len(os.listdir("static/answers"))
        task_ids = ["2.1", "2.2", "2.3", "2.4", "2.5",
                    "2.6", "2.7", "2.8",
                    "2.9", "2.10", "2.11",
                    "2.12", "2.13", "2.14",
                    "2.15", "3.1", "3.2", "3.3",
                    "3.4", "3.5", "3.6", "3.7", "3.8",
                    "3.9", "3.10", "3.11", "3.12",
                    "3.13", "3.14", "3.15"]
        with self.connection:
            for task_id in task_ids:
                 self.cursor.execute("INSERT INTO 'tasks' ('user_id','task_id') VALUES (?, ?)", (user_id,str(task_id)))

    def change_status_of_task_completed(self,user_id,task_id):
        with self.connection:
            status = 'completed'
            self.cursor.execute("UPDATE 'tasks' set 'status'=? where user_id=? and task_id=?  ", (status,user_id,str(task_id)))

    def change_status_of_task_in_progress(self,user_id,task_id):
        with self.connection:
            status = 'in_progress'
            self.cursor.execute("UPDATE 'tasks' set 'status'=? where user_id=? and task_id=?  ", (status,user_id,task_id))

    def check_status(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT task_id, status from tasks where user_id=? ",(user_id,)).fetchall()
        return result

    def update_comment_on_task(self,user_id,task_id,user_comment):
        with self.connection:
            self.cursor.execute("UPDATE 'tasks' set 'comments'=? where user_id=? and task_id=?  ", (user_comment, user_id, str(task_id)))

    # Заполнение таблицы фактов данными пользователя, если они не начаты
    async def set_notstarted_test(self, user_id):
        test_codes_id = list(self.cursor.execute(
            "SELECT s2.test_code, s2.test_id FROM tests_name_dict s1 INNER JOIN test_dict s2 ON s1.test_code = s2.test_code WHERE s1.active_flag = 'Y' and end_date > datetime('now') AND s2.test_code NOT IN (SELECT test_code FROM test_result WHERE user_id = ?)",
            (user_id,)).fetchall())
        test_codes = list(self.cursor.execute("SELECT test_code FROM tests_name_dict  WHERE active_flag = 'Y' and end_date > datetime('now') EXCEPT SELECT test_code FROM test_result WHERE user_id = ?", (user_id,)).fetchall())
        with self.connection:
            for code_id in test_codes_id:
                self.cursor.execute("INSERT INTO 'test_fact' ('user_id', 'test_code', 'test_id') VALUES (?, ?, ?)",
                                    (user_id, str(code_id[0]), str(code_id[1])))
            for code in test_codes:
                 self.cursor.execute("INSERT INTO 'test_result' ('user_id', 'test_code') VALUES (?, ?)", (user_id, str(code[0]),))

    # выбор незаконченных тестов:
    async def choiсe_list_test(self, user_id):
        with self.connection:
            list_test = self.cursor.execute(
                "SELECT test_name, test_code FROM tests_name_dict WHERE active_flag = 'Y' and end_date > datetime('now') EXCEPT SELECT test_name, test_code FROM tests_name_dict WHERE test_code IN (SELECT test_code FROM test_result WHERE user_id = ? AND amount_exercise_2 > 0)",
                (user_id,)).fetchall()
        return list_test

    # проверка статуса теста:
    async def check_status_test(self, user_id, test_code):
        with self.connection:
            list_test = self.cursor.execute(
                "SELECT test_name, test_code FROM tests_name_dict WHERE active_flag = 'Y' AND end_date > datetime('now') AND test_code=? EXCEPT SELECT test_name, test_code FROM tests_name_dict WHERE test_code IN (SELECT test_code FROM test_result WHERE user_id = ? AND amount_exercise_2 > 0) and test_code = ?",
                (test_code, user_id, test_code,)).fetchall()
            return list_test

    #наименование теста:
    async def test_name(self, test_code):
        with self.connection:
            list_test = self.cursor.execute(
                "SELECT test_name FROM tests_name_dict WHERE test_code=?",
                (test_code,))
        return list(list_test)[0][0]

    # выбор неактивных тестов:
    async def adm_activate_test(self):
        test_names = list(self.cursor.execute("SELECT test_name, test_code FROM tests_name_dict WHERE active_flag = 'N'"))
        return test_names

    # ставим активный флаг на тест, устанвливаем текущую дату и дата окончания +2 суток:
    async def adm_test_to_Y(self, test_code):
        with self.connection:
            self.cursor.execute("UPDATE tests_name_dict set active_flag = 'Y', start_date = (SELECT datetime('now')), end_date = (SELECT datetime('now','+2 days')) where test_code=? AND active_flag = 'N'", (test_code,))

    # выбор активных тестов:
    async def adm_deactivate_test(self):
        test_names = list(
            self.cursor.execute("SELECT test_name, test_code FROM tests_name_dict WHERE active_flag = 'Y'"))
        return test_names

    # ставим неактивный флаг на тест, устанвливаем MIN и MAX date:
    async def adm_test_to_N(self, test_code):
        with self.connection:
            self.cursor.execute("UPDATE tests_name_dict set active_flag = 'N', start_date = '2000-00-00 00:00:00', end_date = '2999-12-31 23:59:59' where test_code=? AND active_flag = 'Y'", (test_code,))

    # Номер попытки пользователя
    async def num_try(self, user_id, test_code):
        with self.connection:
            try_1 = list(self.cursor.execute("SELECT 2 from test_result where user_id=? AND test_code=? AND amount_exercise_1 > 0", (user_id, test_code,)))
            try_2 = list(self.cursor.execute(
                "SELECT 2 from test_result where user_id=? AND test_code=? AND amount_exercise_2 > 0",
                (user_id, test_code,)))
            if try_2:
                return None #вторая попытка произведена возвращаем none
            elif try_1:
                return '2'
            else:
                return '1'

    # Выбор случайного номера из доступных
    async def random_question(self, user_id, test_code, num_try):
        with self.connection:
            numb = list(self.cursor.execute(f"SELECT test_id from test_fact where test_code=? and user_id=? and answer_{num_try} = 0", (test_code, user_id, )))
            if numb:
                return await self.select_question(random.choice(numb)[0], test_code)
            else:
             return None


    # Выбор вопроса для отправки пользователю
    async def select_question(self, test_id, test_code):
        with self.connection:
            question = self.cursor.execute("SELECT * from test_dict where test_id=? and test_code=?", (test_id, test_code,))
        return question

    # Проверка статуса 1 попытки
    async def check_status_try_1(self, user_id, test_code):
        with self.connection:
            return self.cursor.execute("SELECT 1 from test_result where user_id=? AND test_code=? AND amount_exercise_1>0", (user_id, test_code,))

    # Проверка корректности ответа
    async def check_answer(self, test_id):
        with self.connection:
            return self.cursor.execute("SELECT * from test_dict where test_id=?", (test_id,))

    # запись варианта ответа пользователя
    async def record_answer(self, user_id, test_code, test_id, num_try, num):
        with self.connection:
            self.cursor.execute(f"UPDATE test_fact set answer_{num_try}=? where user_id=? AND test_id=? AND test_code=? ", (num, user_id, test_id, test_code,))

    # количество всех и оставшихся вопросов
    async def amount_answer(self, user_id, test_code, num_try):
        with self.connection:
            amount_total = self.cursor.execute(
                f"SELECT count(*) FROM test_fact where user_id=? AND test_code=? "
                f"UNION ALL "
                f"SELECT count(*) FROM test_fact where user_id=? AND test_code=? AND answer_{num_try} > 0",
                (user_id, test_code, user_id, test_code,))
            return amount_total

    # commit результат
    async def commit_test(self, user_id, test_code, num_try):
        with self.connection:
            return self.cursor.execute(f"UPDATE test_result set correct_result_{num_try} = "
                                f"(SELECT COUNT(*) FROM test_dict s1 INNER JOIN test_fact s2 ON s1.test_code = s2.test_code AND s1.true_answer = s2.answer_{num_try} AND s1.test_id = s2.test_id WHERE s2.user_id=? AND s2.test_code=?), "
                                f"amount_exercise_{num_try} = (SELECT COUNT(*) FROM test_dict WHERE test_code=?)"
                                f" where user_id=? AND test_code=? ",
                                (user_id, test_code, test_code, user_id, test_code,))

    # итог попытки
    async def print_result(self,user_id,test_code,num_try):
        with self.connection:
            # a =
            return self.cursor.execute(f"SELECT correct_result_{num_try}, amount_exercise_{num_try} from test_result where user_id=? and test_code=?  ", (user_id, test_code,))

    # итог теста
    async def print_total_result(self,user_id,test_code):
        with self.connection:
            return self.cursor.execute(f"SELECT MAX(correct_result_1, correct_result_2), surname, name, test_name from test_result s1 INNER JOIN trainee s2 "
                                       f"ON s1.user_id = s2.user_id INNER JOIN tests_name_dict s3 ON s1.test_code = s3.test_code "
                                       f" where s1.user_id=? and s1.test_code=?", (user_id, test_code,))

    # установка времени попытки
    async def set_start_date_try(self, user_id, test_code, num_try):
        with self.connection:
            self.cursor.execute(f"UPDATE test_result set start_try_{num_try} = datetime('now') where test_code=? AND user_id=?", (test_code, user_id, ))

    # проверка 2 часов
    async def check_time_try(self, user_id, test_code, num_try):
        with self.connection:
            return self.cursor.execute(
                f"SELECT 1 from test_result where user_id=? AND test_code=? AND (SELECT datetime(start_try_{num_try},'+2 hours')) < datetime('now')",
                (user_id, test_code,))