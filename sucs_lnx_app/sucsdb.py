import sqlite3
from sqlite3 import Error
import datetime
import settings as s
#!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!++!
#ToDo: prevent SQL injections with regex

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
        self.dbfile = dbfile
        self.conn = None
        self._create_connection()                                    # create a database connection

#####################################################################
#                Functions available for global use                 #
#####################################################################

    def close_connection(self):
        """Close connection to the database
        """
        if self.conn:
            self.conn.close()


    def valid_lecturer(self, lecturer_id):
        """Test for valid lecturer id

        Args:
            lecturer_id (int): lecturer id 

        Returns:
            bool: True / False
        """
        
        sql = """ SELECT name FROM lecturers 
                        WHERE us_number={}"""
        
        cur = self.conn.cursor()
        cur.execute(sql.format(lecturer_id))
        retrn = cur.fetchone()
        if retrn:
            # print(type(self).__name__,"Test success for ",retrn)     #Todo: remove after debug
            return True
        else: 
            return False


    def get_session_data(self):
        """Return  session data from the 'sessions' table

        Returns:
            list: id,us_number,log_datetime,name,photo
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql = ''' SELECT * FROM sessions 
                WHERE lecturer_id={}
                ; '''   
        cur = self.conn.cursor()
        cur.execute(sql.format(s.ACTIVE_LECTURER[0]))
        return cur.fetchall()    
        

    def get_student_logs(self):
        """Return all student logs from the 'student_logs' table

        Returns:
            list: us_number,log_datetime,name,student_logs.session_id 
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql = ''' SELECT us_number,log_datetime,name,student_logs.session_id FROM student_logs 
                JOIN sessions ON sessions.session_id = student_logs.session_id
                WHERE sessions.lecturer_id={}
                ; '''   
        cur = self.conn.cursor()
        cur.execute(sql.format(s.ACTIVE_LECTURER[0]))
        return cur.fetchall()


    def get_student_nums(self):
        """Get student numbers scanned by the active lecturer

        Returns:
            list: us_number
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql =''' SELECT us_number FROM student_logs 
                JOIN sessions ON sessions.session_id = student_logs.session_id
                WHERE sessions.lecturer_id={}
                ; '''   
        cur = self.conn.cursor()
        cur.execute(sql.format(s.ACTIVE_LECTURER[0]))
        sn_list = cur.fetchall()
        i =0
        for row in sn_list:
            sn_list[i] = row[0]
            i+=1
        return sn_list


    def get_student_nums_names(self):
        """Return student numbers from 'student_logs' table

        Returns:
            list: us_number
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql =''' SELECT us_number,name FROM student_logs 
                JOIN sessions ON sessions.session_id = student_logs.session_id
                WHERE sessions.lecturer_id={}
                ORDER BY student_logs.log_datetime
                ; '''  
        cur = self.conn.cursor()
        cur.execute(sql.format(s.ACTIVE_LECTURER[0]))
        sn_list = cur.fetchall()
        i =0
        for row in sn_list:
            sn_list[i] = row[0],row[1]
            print(type(self).__name__,sn_list[i])
            i+=1
        # print(type(self).__name__,sn_list)
        return sn_list


    def insert_student_logs(self, us_number, name, photo=None):   
        """Insert a new student log into the 'student_logs' table

        Args:
            us_number (int): student us number
            name (str): name and surname
            photo (str): char. Defaults to None.

        Returns:
            int: id of last entry to database
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql_insert_student_logs = ''' INSERT INTO student_logs(us_number, log_datetime, name, photo, session_id) 
                values(?, ?, ?, ?, ?); '''
        cur = self.conn.cursor()
        log = (us_number, Database.get_datetime(), name, photo, s.SESSION_ID)
        cur.execute(sql_insert_student_logs, log)
        self.conn.commit()
        print(type(self).__name__,"sucsdb log ",cur.lastrowid)              #Todo: remove after debug
        return cur.lastrowid


    def insert_lecturers(self, us_number, name):
        """Insert a new lecturer into the 'lecturers' table

        Args:
            us_number (int): lecturer us number
            name (str): name and surname

        Returns:
            int: id of last entry to database
        """
        if self.valid_lecturer(int(us_number)):
            # print(type(self).__name__,"Lecturer Exists: ",us_number)        #Todo: remove after debug
            return -1
        sql_insert_lecturers = ''' INSERT INTO lecturers(us_number, name) 
                values(?, ?); '''
        cur = self.conn.cursor()
        log = (us_number, name)
        cur.execute(sql_insert_lecturers, log)
        self.conn.commit()
        # print(type(self).__name__,("sucsdb lecturer ",cur.lastrowid))       #Todo: remove after debug
        return cur.lastrowid


    def insert_session(self, start_time, end_time, scan_count):   
        """Insert a new session log into the 'sessions' table

        Args:
            start_time (str): session start date time
            end_time (str): session start end time
            scan_count (int): number of scans counted for session

        Returns:
            int: id of last entry to database
        """
        if not s.ACTIVE_LECTURER[0]:
            return None
        sql_insert_session = ''' INSERT INTO sessions(start_datetime, end_datetime, scan_count, session_id) 
                values(?, ?, ?, ?); '''
        cur = self.conn.cursor()
        log = (start_time, end_time, scan_count, s.SESSION_ID)
        cur.execute(sql_insert_session, log)
        self.conn.commit()
        # print(type(self).__name__,"sucsdb session",cur.lastrowid)   #Todo: remove after debug
        return cur.lastrowid

#####################################################################
#                       Setup Database class                        #
#####################################################################

    ############################################### 
    #   create a database connection to a SQLite database 
    def _create_connection(self): 
        try:
            self.conn = sqlite3.connect(self.dbfile)
            # print(type(self).__name__,"sqlite: ", sqlite3.version)   #Todo: remove after debug
            #return conn
        except Error as e:
            # print(type(self).__name__,e)                             #Todo: remove after debug

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]
    @staticmethod    
    def get_datetime():
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d %H:%M:%S')

    ###############################################
    #   Create sucs tables in database 
    #   :param self:
    #   :return: None
    def _create_sucs_tables(self):
        sql_student_logs_table = """ CREATE TABLE "student_logs"(
                                        id 				INTEGER PRIMARY KEY AUTOINCREMENT, 
                                        us_number 		INTEGER NOT NULL, 
                                        log_datetime 	DATE NOT NULL, 
                                        name 			TEXT NOT NULL, 
                                        photo 			TEXT, 
                                        session_id 		INTEGER NOT NULL
                                        ); """

        sql_lecturers_table = """ CREATE TABLE lecturers(
                                        us_number 		INTEGER PRIMARY KEY,
                                        name    		TEXT NOT NULL,
                                        photo   		TEXT
                                        ); """

        sql_session_table = """ CREATE TABLE sessions(
                                        id              INTEGER PRIMARY KEY AUTOINCREMENT, 
                                        start_datetime 	DATE NOT NULL, 
                                        end_datetime 	DATE NOT NULL, 
                                        scan_count 		INTEGER NOT NULL,
                                        session_id 		TEXT NOT NULL, 
                                        lecturer_id 	INTEGER NOT NULL default 12345678
                                        );"""

        if self.conn is not None:
            # create database tables
            self.create_table(sql_student_logs_table)
            self.create_table(sql_lecturers_table)
            self.create_table(sql_session_table)
            self.conn.commit()
            # print(type(self).__name__,"Total number of rows updated :", self.conn.total_changes)     #Todo: remove after debug
        else:
            # print(type(self).__name__,"Error! cannot create the database connection.")       #Todo: remove after debug

#####################################################################
#                        Only for debug use                         #
#####################################################################

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
            # print(type(self).__name__,e)         #Todo: remove after debug


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
            # print(type(self).__name__,e)         #Todo: remove after debug



