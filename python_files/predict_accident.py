#!/usr/bin/env python
from dbconnection import DBConnection
import datetime
import time
import cv2
import numpy as np
import time
from classify import Classify
import os
from shutil import copyfile

class PredictAccident:
    def predict_accident(self):
        insert_into_DB = 1
        db = DBConnection()
        conn = db.get_connection()
        mycursor = conn.cursor()
        mycursor.execute("SELECT path FROM buffer")
        buffer_items = mycursor.fetchall()
        for path_row in buffer_items:
            path = path_row[0]
            clf = Classify(path)
            class_name, percentage = clf.classify_image()
            if (class_name[0] is 'a' or class_name[0] is 'A') and (insert_into_DB is 1):
                insert_into_DB = 0
                print('accident detected')
                Camera_id = 'CAM001'
                db1 = DBConnection()
                conn1 = db1.get_connection()
                mycursor1 = conn1.cursor()
                mycursor1.execute("SELECT count(path) FROM Accident")
                count_row = mycursor1.fetchone()
                new_path = '../accident/Accident'+str(count_row[0])+'.jpg'
                copyfile(path, new_path)
                date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                timestamp = time.time()
                sql1 = "insert into Accident(Camera_id,path,date_time,timestampAcc) values(%s,%s,%s,%s);"
                mycursor1.execute(sql1,[Camera_id,new_path,date_time,int(timestamp)])
                conn1.commit()
                mycursor1.execute("UPDATE flag set flag_var = 1 where flag_key = 1;")
                conn1.commit()
                mycursor1.execute("UPDATE smbool set continue_buffer = 0 where flag_var = 0")
                conn1.commit()
            if(insert_into_DB is 0):
                print('skipping database entry')
            sql = "DELETE FROM buffer WHERE path = %s"
            mycursor.execute(sql,[path])
            conn.commit()
            os.remove(path)
            