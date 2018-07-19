# -*- coding:utf-8 -*-

import pymysql

class MysqlConnection():

    def __init__(self):
        self.conn = self.GetConnection()
        self.cur  = pymysql.cursors.Cursor(self.conn)
    
    def GetConnection(self):
        conn = pymysql.connect(host = 'localhost',
                                db = 'finnews',
                                port = 3306,
                                user = 'root',
                                password = '123456',
                                use_unicode = True,
                                charset = 'utf8')
        return conn
    
    def Query(self, sql):
        self.conn.ping()
        self.cur.execute(sql)
        return self.cur.fetchall()
    
    def Insert(self, sql):
        self.conn.ping()
        status = self.cur.execute(sql)
        self.conn.commit()
        return status
    
    def Update(self, sql):
        self.conn.ping()
        status = self.cur.execute(sql)
        self.conn.commit()
        return status