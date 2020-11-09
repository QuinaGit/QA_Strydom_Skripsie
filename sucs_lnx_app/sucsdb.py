import sqlite3
from sqlite3 import Error
import datetime
#!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!
#ToDo: Maak die SQL table net id, student_no, datetime, lecturer
#ToDo: https://www.sqlitetutorial.net/sqlite-python/update/
#ToDo: prevent SQL injections with regex
#todo: ~ Add time to database
#todo: ~ Add a way to make time accurate 

#####################################################################
# Example:
# 
# from sucsdb import Database
# DATABASE_PATH = r"../sucs_pi_db.db"
# db = Database(DATABASE_PATH)
# db.insert_student_logs(20770316, "Name")
# db.close_connection()
#
#####################################################################


class Database:
    def __init__(self,dbfile):
        #self.filename = filename
        self.dbfile = dbfile
        #self.users = None
        #self.file = None
        self.active_lecturer_id = None
        self.conn = None
        self._create_connection()                                    # create a database connection


#####################################################################
#                Functions available for global use                 #
#####################################################################

    ###############################################
    #   Close connection to the database
    #   :param self:
    #   :return: None
    def close_connection(self):
        if self.conn:
            self.conn.close()

    ###############################################
    #   Test for valid lecturer id
    #   :param self:
    #   :param lecturer_id
    #   :return: None
    def valid_lecturer(self, lecturer_id):
        sql = """ SELECT name FROM lecturers 
                        WHERE us_number={}"""

        cur = self.conn.cursor()
        cur.execute(sql.format(lecturer_id))
        retrn = cur.fetchone()
        if retrn:
            print(type(self).__name__,"Test success for ",retrn)     #Todo: remove after debug
            return True
        else: 
            return False

    ###############################################
    #   Set active lecturer
    #   :param self:
    #   :param lecturer_id
    #   :return: None
    def set_active_lecturer(self, lecturer_id):
        self.active_lecturer_id = lecturer_id

    ###############################################
    #   Get active lecturer
    #   :param self:
    #   :return: lecturer_id
    def get_active_lecturer(self):
        return self.active_lecturer_id

    ###############################################
    #   Return all student logs from the 'student_logs' table
    #   :param self:
    #   :return: id, us_number, date, ... (list)
    def get_student_logs(self):
        if not self.active_lecturer_id:
            return None
        sql = ''' SELECT * FROM student_logs 
                WHERE lecturer_id={}
                ; '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    ###############################################
    #   Return student numbers from 'student_logs' table
    #   :param self:
    #   :return: us_number (list)
    def get_student_nums(self):
        """[returns student numbers scanned by the active lecturer]

        Returns:
            sn_list [list]: list of student numbers of active lecturer
        """
        if not self.active_lecturer_id:
            return None
        sql = ''' SELECT us_number FROM student_logs 
                
                ; '''#! WHERE lecturer_id={}
        cur = self.conn.cursor()
        cur.execute(sql.format(self.active_lecturer_id))
        sn_list = cur.fetchall()
        i =0
        for row in sn_list:
            sn_list[i] = row[0]
            i+=1
        return sn_list

    ###############################################
    #   Return student numbers from 'student_logs' table
    #   :param self:
    #   :return: us_number (list)
    def get_student_nums_names(self):
        if not self.active_lecturer_id:
            return None
        sql = ''' SELECT us_number, name FROM student_logs 
                
                ; '''   #! WHERE lecturer_id={}
        cur = self.conn.cursor()
        cur.execute(sql.format(self.active_lecturer_id))
        sn_list = cur.fetchall()
        i =0
        for row in sn_list:
            sn_list[i] = row[0],row[1]
            print(type(self).__name__,sn_list[i])
            i+=1
        print(type(self).__name__,sn_list)
        return sn_list

    ###############################################
    #   Insert a new student log into the 'student_logs' table
    #   :param self:
    #   :param us_number:       student us number
    #   :param name:            name and surname
    #   :param photo:           (default=NULL) 
    #   :return:                log id
    def insert_student_logs(self, us_number, name, photo=None):   
        if not self.active_lecturer_id:
            return None
        sql_insert_student_logs = ''' INSERT INTO student_logs(us_number, log_datetime, name, photo, lecturer_id) 
                values(?, ?, ?, ?, ?); '''
        cur = self.conn.cursor()
        log = (us_number, Database.get_date(), name, photo, self.active_lecturer_id)
        cur.execute(sql_insert_student_logs, log)
        self.conn.commit()
        print(type(self).__name__,"sucsdb log ",cur.lastrowid)   #Todo: remove after debug
        return cur.lastrowid

    ###############################################
    #   Insert a new lecturer into the 'lecturers' table
    #   :param self:
    #   :param us_number:       lecturer us number
    #   :param name:            name and surname
    #   :return:                log id
    def insert_lecturers(self, us_number, name):
        if self.valid_lecturer(int(us_number)):
            print(type(self).__name__,"Lecturer Exists: ",us_number)     #Todo: remove after debug
            return -1
        sql_insert_lecturers = ''' INSERT INTO lecturers(us_number, name) 
                values(?, ?); '''
        cur = self.conn.cursor()
        log = (us_number, name)
        cur.execute(sql_insert_lecturers, log)
        self.conn.commit()
        print(type(self).__name__,("sucsdb lecturer ",cur.lastrowid))     #Todo: remove after debug
        return cur.lastrowid

#####################################################################
#                       Setup Database class                        #
#####################################################################

    ############################################### 
    #   create a database connection to a SQLite database 
    def _create_connection(self): 
        try:
            self.conn = sqlite3.connect(self.dbfile)
            print(type(self).__name__,"sqlite: ", sqlite3.version)   #Todo: remove after debug
            #return conn
        except Error as e:
            print(type(self).__name__,e)                             #Todo: remove after debug

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]

#####################################################################
#                        Only for debug use                         #
#####################################################################

    ###############################################
    #   Create sucs tables in database 
    #   :param self:
    #   :return: None
    def create_sucs_tables(self):
        sql_student_logs_table = """ CREATE TABLE student_logs(
                                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                    us_number           INTEGER NOT NULL, 
                                    log_datetime        DATE    NOT NULL,
                                    name                TEXT    NOT NULL,
                                    photo               TEXT,
                                    lecturer_id         INTEGER NOT NULL
                                    ); """

        sql_lecturers_table = """ CREATE TABLE lecturers(
                                    us_number INTEGER PRIMARY KEY, 
                                    name    TEXT    NOT NULL,
                                    photo   TEXT
                                    ); """

        if self.conn is not None:
            # create database tables
            
            self.create_table(sql_student_logs_table)
            self.create_table(sql_lecturers_table)
            self.conn.commit()
            print(type(self).__name__,"Total number of rows updated :", self.conn.total_changes)     #Todo: remove after debug
        else:
            print(type(self).__name__,"Error! cannot create the database connection.")       #Todo: remove after debug

    ###############################################
    #   Create a table
    #   :param self: 
    #   :param create_table_sql:    sql statement
    #   :return:                    None
    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(type(self).__name__,e)         #Todo: remove after debug


    ###############################################
    #   Execute a given sql statement 
    #   :param self:
    #   :sql_command:   sql statement
    #   :return:        None
    def execute_sql(self, sql_command):
        try:
            cur = self.conn.cursor()
            cur.execute(sql_command)
            return cur.fetchall()
        except Error as e:
            print(type(self).__name__,e)         #Todo: remove after debug



