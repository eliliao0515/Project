import sqlite3
from sqlite3 import Error

FILE = "manager.db"
TABLE_USER = "users"
TABLE_DDLS = "ddls"
TABLE_COUR = "courses"

class Database:

    def __init__(self):
        self.conn = None
        self.cursor = None

        try:
            self.conn = sqlite3.connect(FILE, check_same_thread=False)
        except Error as e:
            print(e)

        print(self.conn)
        self.cursor = self.conn.cursor()
        self._create_table()
    
    def close(self):
        self.conn.close()

    def _create_table(self):
        query_users = f"""CREATE TABLE IF NOT EXISTS {TABLE_USER} (
                     username TEXT NOT NULL,
                     password TEXT NOT NULL,
                     id INTEGER PRIMARY KEY AUTOINCREMENT
                     );"""

        query_ddls = f"""CREATE TABLE IF NOT EXISTS {TABLE_DDLS} (
                     id INTEGER PRIMARY KEY,
                     information TEXT NOT NULL,
                     Date TEXT NOT NULL,
                     courseID INTEGER NOT NULL,
                     FOREIGN KEY(courseID) REFERENCES courses(id)
                     );"""

        query_cour = f"""CREATE TABLE IF NOT EXISTS {TABLE_COUR} (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     courseName TEXT NOT NULL,
                     instituteName TEXT NOT NULL,
                     courseAbout TEXT NOT NULL,
                     enrollDate TEXT NOT NULL,
                     endDate TEXT NOT NULL,
                     creator TEXT NOT NULL,
                     FOREIGN KEY(creator) REFERENCES users(username)
                     );"""

        self.cursor.execute(query_users)
        self.cursor.execute(query_ddls)
        self.cursor.execute(query_cour)
        self.conn.commit()

    def user_exist(self, username):
        query = f"SELECT username FROM {TABLE_USER} WHERE username='{username}';"
        self.cursor.execute(query)
        if self.cursor.fetchall():
            return True
        else:
            return False

    def add_user(self, username, password):
        query = f"INSERT INTO {TABLE_USER} VALUES (?, ?, ?);"
        self.cursor.execute(query, (username, password, None))
        self.conn.commit()

    def add_course(self, coursename, instituteName, courseAbout, enrollDate, endDate, ddl_pairs, user):
        # check if course repeated
        query = f"SELECT coursename FROM {TABLE_COUR} WHERE coursename='{coursename}' AND creator='{user}';"
        self.cursor.execute(query)
        if self.cursor.fetchall():
            return False

        # insert new course
        query = f"INSERT INTO {TABLE_COUR} VALUES (?, ?, ?, ?, ?, ?, ?);"
        self.cursor.execute(query, (None, coursename, instituteName, courseAbout, enrollDate, endDate, user))
        self.conn.commit()

        # insert ddls
        # fetch id
        query = f"SELECT id FROM {TABLE_COUR} WHERE coursename='{coursename}';"
        self.cursor.execute(query)
        id = self.cursor.fetchall()[0][0]
        # iterate ddls
        for ddl in ddl_pairs:
            query = f"INSERT INTO {TABLE_DDLS} VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (None, ddl, ddl_pairs[ddl], id))
            self.conn.commit()

        return True

    def get_all_course(self, username):
        query = f"SELECT * FROM {TABLE_COUR} WHERE creator='{username}';"
        self.cursor.execute(query)
        # get a list of many tuple
        return self.cursor.fetchall()

    def get_nearest_ddl(self, courses):
        ddls = []
        for course in courses:
            query = f"SELECT information, Date FROM {TABLE_DDLS} WHERE courseID={course[0]} ORDER BY Date ASC LIMIT 1;"
            self.cursor.execute(query)
            curr = self.cursor.fetchall()
            if (len(curr)==1):
                ddls.append(curr)
            else:
                ddls.append([("non", "non")])
        return ddls

    def get_course_id(self, course, username):
        query = f"SELECT id FROM {TABLE_COUR} WHERE courseName='{course}' AND creator='{username}';"
        self.cursor.execute(query)
        id = self.cursor.fetchall()[0][0]
        return id

    def delete_course(self, course, username):
        # delete ddls
        id = self.get_course_id(course, username)
        query = f"DELETE FROM {TABLE_DDLS} WHERE courseID='{id}';"
        self.cursor.execute(query)

        # delete course
        query = f"DELETE FROM {TABLE_COUR} WHERE courseName='{course}' AND creator='{username}';"
        self.cursor.execute(query)

        self.conn.commit()