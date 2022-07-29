#docker run --name telebot -p 5477:5432 -e POSTGRES_DB=Trainee_db -e POSTGRES_USER=Trainee_admin -e
# POSTGRES_PASSWORD=GHF_36#_fd7_42f -d postgres
#import psycopg2
#from psycopg2 import Error


#conn_string= "user=Trainee_admin password=GHF_36#_fd7_42f host=172.17.0.1 port=5472 dbname=Trainee_db"
#def hhh():
#conn = psycopg2.connect("user=Trainee_admin password=GHF_36#_fd7_42f host=localhost port=5477 dbname=Trainee_db")
#cur = conn.cursor()

#cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
#cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
#cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

#cur.execute("SELECT * FROM test;")
#one_line = cur.fetchone()
#print(one_line)
    #with conn.cursor() as curs:

        #a = cur.fetchone()

#hhh()
#try:
    #with conn:
    #with conn.cursor() as curs:
        #curs.execute("SELECT * FROM tests_name_dict;")
        #print(curs.fetchall())

#finally:
    #cur.close()
    #conn.close()
######

class Employee:
    """Базовый класс для всех сотрудников"""
    emp_count = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.emp_count += 1

    def display_count(self):
        print('Всего сотрудников: %d' % Employee.emp_count)

    def display_employee(self):
        print('Имя: {}. Зарплата: {}'.format(self.name, self.salary))

    # Это создаст первый объект класса Employee




class Employee:
    """Базовый класс для всех сотрудников"""
    emp_count = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.emp_count += 1

    def display_count(self):
        print('Всего сотрудников: %d' % Employee.emp_count)

    def display_employee(self):
        print('Имя: {}. Зарплата: {}'.format(self.name, self.salary))

    # Это создаст первый объект класса Employee


emp1 = Employee("Андрей", 2000)
# Это создаст второй объект класса Employee
emp2 = Employee("Мария", 5000)
emp1.display_employee()
emp2.display_employee()
print("Всего сотрудников: %d" % Employee.emp_count)
emp1 = Employee("Андрей", 2000)
# Это создаст второй объект класса Employee
emp2 = Employee("Мария", 5000)
emp1.display_employee()
emp2.display_employee()
print("Всего сотрудников: %d" % Employee.emp_count)
