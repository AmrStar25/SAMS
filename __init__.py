#!/usr/bin/python
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, abort, jsonify
from flask import session as login_session
import random
import string
from flask import session as login_session
#import httplib2
from flask_socketio import SocketIO, emit
import json
from flask import make_response
import requests
import os
import MySQLdb
from flask_seasurf import SeaSurf
from flask_mail import Mail, Message
from werkzeug import secure_filename
import sys
import time

app = Flask(__name__)
csrf = SeaSurf(app)
socketio = SocketIO(app)
app.config.update(dict(
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USERNAME = 'amrstar25@gmail.com',
	MAIL_PASSWORD ='0882353984',
	MAIL_USE_TLS = False,
	MAIL_USE_SSL = True,
	MAIL_SUPPRESS_SEND = False,
	MAIL_DEFAULT_SENDER = 'amrstar25@gmail.com'
))
mail = Mail(app)

ALLOWED_EXTENSIONS = set(['jpg','gif'])
app.config['UPLOAD_FOLDER'] = 'D:/SAMS/SAMS/static/assets/uimg/'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/city', methods=['POST'])
def getallcit():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))
	if 'govid' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM  core_cities where GovernmentID="+request.json['govid']

		cursor.execute(query)
		results = cursor.fetchall()

		return jsonify(results)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM  core_governments"

		cursor.execute(query)
		results = cursor.fetchall()

		return jsonify(results)
		
	# db.close()

@app.route('/coregov', methods=['POST','GET'])
def GovAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query = "SELECT * From core_governments"

	 	cursor.execute(query)
		results = cursor.fetchall()
		db.close()

		return render_template('Core_governments.html',Govs=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from core_governments where GovernmentID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
			db.close()
			return jsonify('done')
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
	elif request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO core_governments(GovernmentName,GovernmentActive,Notes) values('%s','%s','%s')" % (request.json['gname'],1,request.json['gnote'])
		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		id=cursor.lastrowid
		query="SELECT * From core_governments where GovernmentID=%s" % id
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE core_governments SET GovernmentName='%s', Notes='%s' Where GovernmentID=%s" % (request.json['gname'],request.json['gnote'],request.json['id'])
		try:
			#return query
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
		
		id=cursor.lastrowid
		query="SELECT * From core_governments where GovernmentID=%s" % request.json['id']
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)

# class DB(object):
# 	db = None

# 	def connect(self):
# 		self.db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
# 	def cursor(self):
# 		try:
# 			c = self.db.cursor()
# 			return c
# 		except Exception as e:
# 			self.connect()
# 			c = self.db.cursor()
# 			return c
# 	def commit(self):
# 		self.db.commit()
# 		self.db.close()

# 	def rollback(self):
# 		self.db.rollback()
# 		self.db.close()


# class JSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if hasattr(obj, 'isoformat'): #handles both date and datetime objects
#             return obj.isoformat()
#         else:
#             return json.JSONEncoder.default(self, obj)
		
@app.route('/traineetestdates', methods=['POST','GET'])
def TraineeTestDatesAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))

	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT services_testsdatesmaster.*,services_levels.LevelDescription,hr_trainersdata.TrainerName "\
				"FROM services_testsdatesmaster,services_levels,hr_trainersdata "\
				"Where services_testsdatesmaster.LevelID = services_levels.LevelID and "\
				"services_testsdatesmaster.TrainerID = hr_trainersdata.TrainerID"

		cursor.execute(query)
		results = cursor.fetchall()
		db.close()

		return render_template('Services_TraineeTestDates.html',tests=results,STATE=state)


	# get all trainees assigned to specific test
	if 'getassignedtrainee' in request.json:
		testmasterid = request.json['testmasterid']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_traineesdata.* "\
				"FROM services_testsdatesdetails,services_testsdatesmaster,hr_traineesdata "\
				"Where services_testsdatesmaster.TestDateMasterID=services_testsdatesdetails.TestDateMasterID and "\
				"services_testsdatesdetails.TraineeID=hr_traineesdata.TraineeID and services_testsdatesmaster.TestDateMasterID="+str(testmasterid)
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)


	# get all trainees who not assign to test or absent in previous test
	if 'gettraineebylevel' in request.json:
		levelid = request.json['levelid']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM hr_traineesdata WHERE hr_traineesdata.LevelID = %s and hr_traineesdata.TraineeID NOT IN "\
			    "(select services_testsdatesdetails.TraineeID "\
		    	"from services_testsdatesmaster,services_testsdatesdetails "\
		    	"where services_testsdatesmaster.TestDateMasterID = services_testsdatesdetails.TestDateMasterID and "\
		    	"services_testsdatesmaster.LevelID = %s and (services_testsdatesdetails.IsAttended IN (1,3,2) or "\
		    	"services_testsdatesdetails.IsAttended IS NULL ) )"
		cursor.execute(query,(levelid,levelid))
		results = cursor.fetchall()
		db.close()
		return jsonify(results)
	if 'getfreetrainer' in request.json:
		dayid = request.json['dayid']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_trainersdata.TrainerID,hr_trainersdata.TrainerName "\
				"FROM  hr_trainersdata,hr_trainerworkdays,hr_days "\
			    "Where hr_trainersdata.TrainerID = hr_trainerworkdays.TrainerID "\
			    "and hr_trainerworkdays.DayID = hr_days.DayID and hr_trainerworkdays.AvailableHoursCount > 0  "\
			    "and hr_days.DayID="+str(dayid)
		
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)


	if 'iddel' in request.json:
		#return 'hello'
		iddel = request.json['iddel']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT Count(*) FROM services_testsdatesdetails Where "\
				"TestDateMasterID=%s and IsAttended IS NOT NULL"

		#query="DELETE from hr_employeesdata where EmployeeID=%s"%request.form['iddel']
		try:
			cursor.execute(query,(iddel,))
			data = cursor.fetchone()
			if int(data[0]) != 0:
				db.close()
				return jsonify('error')
			
			query = "SELECT TraineeID FROM services_testsdatesdetails Where TestDateMasterID="+str(iddel)
			cursor.execute(query)
			delids = [item[0] for item in cursor.fetchall()]

			query="DELETE from services_testsdatesdetails where TestDateMasterID="+str(iddel)
			cursor.execute(query)

			query="DELETE from services_testsdatesmaster where TestDateMasterID="+str(iddel)
			cursor.execute(query)

			
			for delid in delids:
				query = "SELECT TraineeEmail,TraineeName FROM hr_traineesdata Where TraineeID="+str(delid)
				cursor.execute(query)
				result = cursor.fetchone()
				
				msg = Message('',recipients=[])
				msg.body = "Dear "+result[1]+" Please don't go to club at "+request.json['iddeldate']+" "+request.json['iddeltime']+" to get swimming test "
				msg.subject = "Cancel Swimming Test Date"
				msg.add_recipient(result[0])
				mail.send(msg)

			db.commit()
			db.close()
			return jsonify('done')

		except Exception as e:
			db.rollback()
			db.close()
			return jsonify(str(e))

	testid = request.json['id']
	description = request.json['description']
	levelid = request.json['level']
	trainerid = request.json['trainer']
	employeeid = request.json['employee']
	swimmingpoolid = request.json['swimmingpool']
	testdate = request.json['testdate']
	testtime = request.json['testtime']
	notes = request.json['notes']
	traineenames = request.json['traineenames']
	traineeemails = request.json['traineeemails']
	traineeids = request.json['traineeids']

	db = None
	if testid == "-1":
		try:
			#db = DB()
			#db.connect()#MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()

			#return jsonify('error')
			#cursor.execute('SET GLOBAL connect_timeout=2147483')
			#cursor.execute('SET GLOBAL wait_timeout=2147483')
			

			#cursor.execute('SET GLOBAL interactive_timeout=2147483')

			#db.db.autocommit(False)log = asdamr.txt
			#cursor.close()
			query = "INSERT INTO services_testsdatesmaster(TestDateDescription,LevelID,TrainerID,EmployeeID,SwimmingPoolID,"\
					"TestDate,TestTime,Notes) Values(%s,%s,%s,%s,%s,STR_TO_DATE(%s,'%%m-%%d-%%Y'),%s,%s)"
			#db.ping(True)
			#cursor = db.cursor()
			cursor.execute(query,(description,levelid,trainerid,employeeid,swimmingpoolid,testdate,testtime,notes))
			id = cursor.lastrowid
			#cursor.close()

			#db.db.ping(True)
			#db.commit()

			#cursor.execute(query)
			#results = cursor.fetchone()
			#db.close()
			#return jsonify(results) #json.dumps(results, cls=JSONEncoder, ensure_ascii=False)


			#cursor = db.cursor()
			
			#must check level also or not
			query = "UPDATE services_testsdatesdetails SET "\
					"IsAttended=%s Where TraineeID=%s and IsAttended=0"
			temp = []
			for trainee in traineeids:
				temp.append((3,trainee))

			#db.ping(True)
			
			#cursor = db.cursor()
			cursor.executemany(query,temp)
			#cursor.close()


			query = "INSERT INTO services_testsdatesdetails(TestDateMasterID,TraineeID,IsSendEmail,"\
					"TestLevelID,Notes) Values(%s,%s,%s,%s,%s)"

			temp = []
			for trainee in traineeids:
				temp.append((id,trainee,1,levelid,''))

			#db.ping(True)
			
			#cursor = db.cursor()
			cursor.executemany(query,temp)
			#cursor.close()
			#db.rollback()
			#db.close()
			#return jsonify('wwwwwwwwwppp')
			#db.commit()
			#db.close()



		
			for name,email in zip(traineenames,traineeemails):
			 	msg = Message('',recipients=[])
			 	msg.body = "Dear "+name+" Please go to club at "+testdate+" "+testtime+" to get swimming test"
			 	msg.subject = "Swimming Test Date"
			 	msg.add_recipient(email)
			 	mail.send(msg)
			#time.sleep(20)

			#db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			#cursor = db.cursor()
			#db.commit()

			query = "SELECT services_testsdatesmaster.TestDateMasterID,services_testsdatesmaster.TestDateDescription,"\
					"services_testsdatesmaster.LevelID,services_testsdatesmaster.TrainerID,"\
					"services_testsdatesmaster.EmployeeID,services_testsdatesmaster.SwimmingPoolID,"\
					"DATE_FORMAT(services_testsdatesmaster.TestDate,'%Y-%m-%d'), TIME_FORMAT(services_testsdatesmaster.TestTime,'%H:%i'),"\
					"services_testsdatesmaster.Notes,services_testsdatesmaster.ModifiedDate,services_levels.LevelDescription,hr_trainersdata.TrainerName "\
					"FROM services_testsdatesmaster,services_levels,hr_trainersdata "\
					"Where services_testsdatesmaster.LevelID = services_levels.LevelID and "\
					"services_testsdatesmaster.TrainerID = hr_trainersdata.TrainerID "\
					"and services_testsdatesmaster.TestDateMasterID="+str(id)

			#db.db.ping(True)

			#cursor = db.cursor()
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)#json.dumps(results, cls=JSONEncoder, ensure_ascii=False))

		except Exception as e:
			db.rollback()
			db.close()
			return jsonify(str(e))
	else:
		try:
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()
		
			# query = "SELECT DATE_FORMAT(TestDate,'%Y-%m-%d'),TIME_FORMAT(TestTime,'%H:%i') "\
			#  		"FROM services_testsdatesmaster Where TestDateMasterID="+testid
			query = "SELECT Count(*) FROM services_testsdatesmaster Where "\
					"TestDateMasterID=%s and TestDate= STR_TO_DATE(%s,'%%m-%%d-%%Y') and TestTime=%s"
			cursor.execute(query,(testid,testdate,testtime))
			date = cursor.fetchone()
			datechanged = True
			#return jsonify(date)

			if int(date[0]) != 0:
				datechanged = False
			#return jsonify(datechanged)
			
			#if date[0][0] == testdate and date[0][1] == testtime:
				#datechanged = False
			#return jsonify(datechanged)

			query = "UPDATE services_testsdatesmaster SET TestDateDescription=%s, LevelID=%s, TrainerID=%s, EmployeeID=%s, "\
					"SwimmingPoolID=%s, TestDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), TestTime=%s, Notes=%s "\
					"Where TestDateMasterID=%s"
			cursor.execute(query,(description,levelid,trainerid,employeeid,swimmingpoolid,testdate,testtime,notes,testid))



			query = "SELECT TraineeID FROM services_testsdatesdetails Where TestDateMasterID="+testid
			cursor.execute(query)
			oldids = [item[0] for item in cursor.fetchall()]#cursor.fetchall()   list comprehensions
			#return jsonify(oldids)
			tempoldids = oldids
		
			temptraineeids = traineeids
			temptraineeemails = traineeemails
			temptraineename = traineenames



			for traineeid,traineename,traineeemail in zip(traineeids,traineenames,traineeemails):
				if traineeid in oldids:
					if datechanged:
						msg = Message('',recipients=[])
						msg.body = "Dear "+traineename+" Sorry Test Date Changed Please go to club at "+testdate+" "+testtime+" to get swimming test"
						msg.subject = "Swimming1 Test Date Changed"
						msg.add_recipient(traineeemail)
						mail.send(msg)
				
					temptraineeids.remove(traineeid)
					temptraineeemails.remove(traineeemail)
					temptraineename.remove(traineename)
					tempoldids.remove(traineeid)
				else:
					query = "UPDATE services_testsdatesdetails SET "\
							"IsAttended=%s Where TraineeID=%s and IsAttended=0"
					cursor.execute(query,(3,traineeid))

					query = "INSERT INTO services_testsdatesdetails(TestDateMasterID,TraineeID,IsSendEmail,"\
							"TestLevelID,Notes) Values(%s,%s,%s,%s,%s)"
					cursor.execute(query,(testid,traineeid,1,levelid,''))

					msg = Message('',recipients=[])
					msg.body = "Dear "+traineename+" Please go to club at "+testdate+" "+testtime+" to get swimming test"
					msg.subject = "Swimming2 Test Date"
					msg.add_recipient(traineeemail)
					mail.send(msg)

					temptraineeids.remove(traineeid)


			for old in tempoldids:
				query = "SELECT TraineeEmail,TraineeName FROM hr_traineesdata Where TraineeID="+str(old)
				cursor.execute(query)
				result = cursor.fetchone()

				query = "DELETE FROM services_testsdatesdetails Where TestDateMasterID=%s and TraineeID=%s"
				cursor.execute(query,(testid,old))

				msg = Message('',recipients=[])
				msg.body = "Dear "+result[1]+" Please don't go to club at "+testdate+" "+testtime+" to get swimming test "
				msg.subject = "Cancel Swimming Test Date"
				msg.add_recipient(result[0])
				mail.send(msg)
			
			for traineeid,traineename,traineeemail in zip(temptraineeids,temptraineename,temptraineeemails):
				query = "INSERT INTO services_testsdatesdetails(TestDateMasterID,TraineeID,IsSendEmail,"\
						"TestLevelID,Notes) Values(%s,%s,%s,%s,%s)"
				cursor.execute(query,(testid,traineeid,1,levelid,''))

				msg = Message('',recipients=[])
				msg.body = "Dear "+traineename+" Please go to club at "+testdate+" "+testtime+" to get swimming test"
				msg.subject = "Swimming3 Test Date"
				msg.add_recipient(traineeemail)
				mail.send(msg)

			query = "SELECT services_testsdatesmaster.TestDateMasterID,services_testsdatesmaster.TestDateDescription,"\
					"services_testsdatesmaster.LevelID,services_testsdatesmaster.TrainerID,"\
					"services_testsdatesmaster.EmployeeID,services_testsdatesmaster.SwimmingPoolID,"\
					"DATE_FORMAT(services_testsdatesmaster.TestDate,'%Y-%m-%d'), TIME_FORMAT(services_testsdatesmaster.TestTime,'%H:%i'),"\
					"services_testsdatesmaster.Notes,services_testsdatesmaster.ModifiedDate,services_levels.LevelDescription,hr_trainersdata.TrainerName "\
					"FROM services_testsdatesmaster,services_levels,hr_trainersdata "\
					"Where services_testsdatesmaster.LevelID = services_levels.LevelID and "\
					"services_testsdatesmaster.TrainerID = hr_trainersdata.TrainerID "\
					"and services_testsdatesmaster.TestDateMasterID="+str(testid)

			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)


		except Exception as e:
			db.rollback()
			db.close()
			return jsonify(str(e))
		
@app.route('/traineetestresults', methods=['POST','GET'])
def TraineeTestResultsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT services_testsdatesdetails.*,hr_traineesdata.TraineeName,services_levels.LevelDescription,hr_trainersdata.TrainerName "\
				"FROM services_testsdatesmaster, services_testsdatesdetails,services_levels,hr_trainersdata, hr_traineesdata "\
				"Where services_testsdatesmaster.LevelID = services_levels.LevelID and services_testsdatesmaster.TrainerID = hr_trainersdata.TrainerID "\
				"and services_testsdatesmaster.TestDateMasterID = services_testsdatesdetails.TestDateMasterID "\
				"and services_testsdatesdetails.TraineeID = hr_traineesdata.TraineeID"
		cursor.execute(query)
		results = cursor.fetchall()
		return render_template('Services_TraineeTestResults.html',items=results,STATE=state)
	if 'gettestsbydate' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT services_testsdatesmaster.TestDateMasterID,services_testsdatesmaster.TestDateDescription,services_levels.LevelDescription "\
				"FROM services_testsdatesmaster, services_levels "\
				"WHERE services_levels.LevelID = services_testsdatesmaster.LevelID "\
				"AND services_testsdatesmaster.TestDate = STR_TO_DATE( %s,'%%m-%%d-%%Y' )"
		#return query
		cursor.execute(query,(request.json['date'],))
		results = cursor.fetchall()
		db.close()
		return jsonify(results)

	if 'getassignedtrainee' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT services_testsdatesdetails . * ,hr_traineesdata.TraineeName,"\
				"services_levels.LevelDescription, hr_trainersdata.TrainerName "\
				"FROM services_testsdatesdetails, services_testsdatesmaster, hr_traineesdata, services_levels, hr_trainersdata "\
				"WHERE services_testsdatesmaster.TestDateMasterID = services_testsdatesdetails.TestDateMasterID "\
				"AND services_testsdatesdetails.TraineeID = hr_traineesdata.TraineeID "\
				"AND services_testsdatesmaster.TestDateMasterID =%s "\
				"AND services_levels.LevelID = services_testsdatesdetails.TestLevelID "\
				"AND hr_trainersdata.TrainerID = services_testsdatesmaster.TrainerID"
		cursor.execute(query,(request.json['testid'],))
		results = cursor.fetchall()
		db.close()
		return jsonify(results)
	if 'updatetraineeresult' in request.json:
		
		level = request.json['level']
		detailid = request.json['detailid']
		degree = request.json['degree']
		attended = request.json['attended']
		notes = request.json['notes']

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()


		try:
			if attended == "0":
				query = "UPDATE services_testsdatesdetails SET IsAttended=%s, Notes=%s Where TestDateDetailsID=%s"
				cursor.execute(query,(attended,notes,detailid))

				query = "SELECT services_testsdatesdetails . * ,hr_traineesdata.TraineeName,"\
						"services_levels.LevelDescription, hr_trainersdata.TrainerName "\
						"FROM services_testsdatesdetails, services_testsdatesmaster, hr_traineesdata, services_levels, hr_trainersdata "\
						"WHERE services_testsdatesmaster.TestDateMasterID = services_testsdatesdetails.TestDateMasterID "\
						"AND services_testsdatesdetails.TraineeID = hr_traineesdata.TraineeID "\
						"AND services_testsdatesdetails.TestDateDetailsID =%s "\
						"AND services_levels.LevelID = services_testsdatesdetails.TestLevelID "\
						"AND hr_trainersdata.TrainerID = services_testsdatesmaster.TrainerID"
				
				cursor.execute(query,(detailid,))
				results = cursor.fetchone()

				db.commit()
				db.close()
				return jsonify(results)

			query = "UPDATE services_testsdatesdetails SET IsAttended=%s, TestDegree=%s, TestLevelID=%s, Notes=%s "\
					"Where TestDateDetailsID=%s"

			cursor.execute(query,(attended,degree,level,notes,detailid))

			query = "SELECT services_testsdatesdetails . * ,hr_traineesdata.TraineeName,"\
					"services_levels.LevelDescription, hr_trainersdata.TrainerName "\
					"FROM services_testsdatesdetails, services_testsdatesmaster, hr_traineesdata, services_levels, hr_trainersdata "\
					"WHERE services_testsdatesmaster.TestDateMasterID = services_testsdatesdetails.TestDateMasterID "\
					"AND services_testsdatesdetails.TraineeID = hr_traineesdata.TraineeID "\
					"AND services_testsdatesdetails.TestDateDetailsID =%s "\
					"AND services_levels.LevelID = services_testsdatesdetails.TestLevelID "\
					"AND hr_trainersdata.TrainerID = services_testsdatesmaster.TrainerID"
				
			cursor.execute(query,(detailid,))
			results = cursor.fetchone()
			
			db.commit()
			db.close()
			return jsonify(results)

		except Exception as e:
			db.rollback()
			db.close()
			return jsonify('error')

@app.route('/traineesattendance', methods=['POST','GET'])
def TraineesAttendanceAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))

	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state

		return render_template('Services_TraineesAttendance.html',STATE=state)

	if 'gettraininggroupbydate' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT TrainingGroupID,TrainingGroupDescription "\
				"FROM services_training_groups Where "\
				"TrainingGroupCompleted = 1 and TrainingGroupSessionsNO != TrainingGroupTakenSessions and "\
				"TrainingGroupStartDate <= STR_TO_DATE( %s,'%%m-%%d-%%Y' )"
		#return query
		cursor.execute(query,(request.json['date'],))
		results = cursor.fetchall()
		return jsonify(results)
	if 'getpreviouslytraineeesattendance' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_traineesdata.TraineeID,hr_traineesdata.TraineeName,"\
				"services_levels.LevelDescription,services_traineeattendance.AttendanceStatus "\
				"FROM services_training_groups,services_traineeattendance,services_levels,hr_traineesdata "\
				"Where services_training_groups.TrainingGroupID = services_traineeattendance.TrainingGroupID and "\
				"services_levels.LevelID = services_training_groups.LevelID and "\
				"hr_traineesdata.TraineeID = services_traineeattendance.TraineeID "\
				"and services_training_groups.TrainingGroupID = %s and "\
				"services_traineeattendance.AttendanceDate = STR_TO_DATE( %s,'%%m-%%d-%%Y' )"

		cursor.execute(query,(request.json['traininggroupid'],request.json['date']))
		results = cursor.fetchall()
		return jsonify(results)
	if 'getassignedtrainees' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_traineesdata.TraineeID,hr_traineesdata.TraineeName,services_levels.LevelDescription "\
				"FROM services_traineewithtraininggroups,services_training_groups,services_levels,hr_traineesdata "\
				"Where services_traineewithtraininggroups.TraineeID = hr_traineesdata.TraineeID and "\
				"services_traineewithtraininggroups.TrainingGroupID = services_training_groups.TrainingGroupID and "\
				"services_levels.LevelID = services_training_groups.LevelID and "\
				"services_training_groups.TrainingGroupID = %s"
		cursor.execute(query,(request.json['traininggroupid'],))
		results = cursor.fetchall()
		return jsonify(results)

	if 'getpreviouslytrainersattendance' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_trainersdata.TrainerID,hr_trainersdata.TrainerName,services_trainerattendance.AttendanceStatus "\
				"FROM services_training_groups, services_trainerattendance,hr_trainersdata "\
				"Where services_training_groups.TrainingGroupID = services_trainerattendance.TrainingGroupID and "\
				"hr_trainersdata.TrainerID = services_trainerattendance.TrainerID "\
				"and services_training_groups.TrainingGroupID = %s and "\
				"services_trainerattendance.AttendanceDate = STR_TO_DATE( %s,'%%m-%%d-%%Y' )"
		cursor.execute(query,(request.json['traininggroupid'], request.json['date']))
		results = cursor.fetchall()
		return jsonify(results)

	if 'getassignedtrainers' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_trainersdata.TrainerID,hr_trainersdata.TrainerName "\
				"FROM  services_traininggroups_trainers,services_training_groups,hr_trainersdata "\
				"Where  services_traininggroups_trainers.TrainingGroupID = services_training_groups.TrainingGroupID and "\
				"services_traininggroups_trainers.TrainerID = hr_trainersdata.TrainerID and "\
				"services_training_groups.TrainingGroupID = %s"
		cursor.execute(query,(request.json['traininggroupid'],))
		results = cursor.fetchall()
		return jsonify(results)
	if 'save' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		trainerids = request.json['trainerids']
		trainersstatus = request.json['trainersstatus']
		traineeids = request.json['traineeids']
		traineesstatus = request.json['traineesstatus']
		traininggroupid = request.json['traininggroupid']
		date = request.json['date']

		if request.json['edit'] == 1:
			query = "UPDATE services_traineeattendance SET AttendanceStatus=%s Where TraineeID=%s and TrainingGroupID=%s"

			temp = []

			for traineeid,traineestatus in zip(traineeids,traineesstatus):
				temp.append((traineestatus,traineeid,traininggroupid))

			cursor.executemany(query,temp)

			query = "UPDATE  services_trainerattendance SET AttendanceStatus=%s Where TrainerID=%s and TrainingGroupID=%s"

			temp = []

			for trainerid,trainerstatus in zip(trainerids,trainersstatus):
				temp.append((trainerstatus,trainerid,traininggroupid))

			cursor.executemany(query,temp)

			db.commit()
			db.close()
			return jsonify("done")
		else:
			query = "INSERT INTO services_traineeattendance(AttendanceDate,TraineeID,TrainingGroupID,AttendanceStatus) Values"\
					"(STR_TO_DATE( %s,'%%m-%%d-%%Y'),%s,%s,%s)"
			temp = []

			for traineeid,traineestatus in zip(traineeids,traineesstatus):
				temp.append((date,traineeid,traininggroupid,traineestatus))

			cursor.executemany(query,temp)


			query = "INSERT INTO services_trainerattendance(AttendanceDate,TrainerID,TrainingGroupID,AttendanceStatus) Values"\
					"(STR_TO_DATE( %s,'%%m-%%d-%%Y'),%s,%s,%s)"

			temp = []

			for trainerid,trainerstatus in zip(trainerids,trainersstatus):
				temp.append((date,trainerid,traininggroupid,trainerstatus))


			cursor.executemany(query,temp)

			query = "UPDATE  services_training_groups SET TrainingGroupTakenSessions = TrainingGroupTakenSessions + 1 Where "\
					"TrainingGroupID = %s"

			cursor.execute(query,(traininggroupid,))

			db.commit()
			db.close()

			return jsonify("done")


@app.route('/programeterms', methods=['POST','GET'])
def ProgrammeTermsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))

	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT services_programeeterms .*,services_levels.LevelDescription "\
				"FROM services_programeeterms , services_levels "\
				"where services_programeeterms.LevelId = services_levels.LevelID "


		cursor.execute(query)
		results = cursor.fetchall()


		return render_template('Services_ProgrammeTerms.html',STATE=state,Terms=results)
	



@app.route('/traineesfinalresults', methods=['POST','GET'])
def TraineesFinalResultsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state

		return render_template('Services_TraineesFinalResults.html',STATE=state)

	if 'traininggroups' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT services_training_groups.TrainingGroupID,services_training_groups.TrainingGroupDescription, "\
				"services_training_groups.LevelID "\
				"FROM services_training_groups "\
				"Where TrainingGroupSessionsNO = TrainingGroupTakenSessions"
		cursor.execute(query)
		results = cursor.fetchall()

		return jsonify(results)
	if 'getleveltestterms' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT ProgrammeTermsID,Content "\
				"FROM services_programeeterms Where LevelID	= %s and Type = 2"

		cursor.execute(query,(request.json['getleveltestterms'],))
		results = cursor.fetchall()

		return jsonify(results)

	if 'getprevioustestdate' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT * FROM services_masterfinaltest Where TrainingGroupID = %s"
		cursor.execute(query,(request.json['getprevioustestdate'],))
		results = cursor.fetchall()

		return jsonify(results)

	if 'gettrainees' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT hr_traineesdata.TraineeID,hr_traineesdata.TraineeName,services_levels.LevelDescription,services_detailsfinaltest.TraineeTermStatus "\
				"FROM hr_traineesdata,services_masterfinaltest,services_detailsfinaltest,services_levels "\
				"Where hr_traineesdata.TraineeID = services_detailsfinaltest.TraineeID and "\
				"services_masterfinaltest.MasterFinalTestID = services_detailsfinaltest.MasterFinalTestID and "\
				"services_masterfinaltest.TrainingGroupID = %s and services_levels.LevelID = %s and "\
				"services_detailsfinaltest.ProgrammeTermID = %s"
		cursor.execute(query,(request.json['traininggroup'],request.json['levelid'],request.json['testtermid']))
		results = cursor.fetchall()
		if len(results) > 0:
			return jsonify(results)
		else:
			query = "SELECT hr_traineesdata.TraineeID,hr_traineesdata.TraineeName,services_levels.LevelDescription,1 "\
					"FROM services_traineewithtraininggroups,hr_traineesdata,services_levels "\
					"Where services_traineewithtraininggroups.TraineeID = hr_traineesdata.TraineeID and "\
					"services_traineewithtraininggroups.TrainingGroupID = %s and services_levels.LevelID = %s"\

			cursor.execute(query,(request.json['traininggroup'],request.json['levelid']))
			results = cursor.fetchall()
			return jsonify(results)

	if 'save' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()

		query = "SELECT * FROM services_masterfinaltest Where TrainingGroupID = %s"
		cursor.execute(query,(request.json['traininggroup']))

		results = cursor.fetchone()

		MasterFinalTestID = 0

		traineeids = request.json['traineeids']
		traineesstatus = request.json['traineesstatus']
		traininggroupid = request.json['traininggroup']
		date = request.json['date']
		testtermid = request.json['testtermid']
		traininggroup = request.json['traininggroup']


		if cursor.rowcount > 0:
			MasterFinalTestID = results[0]
			query = "SELECT * FROM services_detailsfinaltest Where MasterFinalTestID = %s "\
					"and ProgrammeTermID = %s"

			cursor.execute(query,(MasterFinalTestID,testtermid))
			
			if cursor.rowcount > 0:

				query = "UPDATE services_detailsfinaltest SET TraineeTermStatus = %s "\
						"Where MasterFinalTestID = %s and ProgrammeTermID = %s and TraineeID = %s"

				temp = []
				for traineeid,traineestatus in zip(traineeids,traineesstatus):
					temp.append((traineestatus,MasterFinalTestID,testtermid,traineeid))

				cursor.executemany(query,temp)
			else:
				query = "INSERT INTO services_detailsfinaltest(MasterFinalTestID,TraineeID,ProgrammeTermID,TraineeTermStatus) "\
						"Values(%s,%s,%s,%s)"
				
				temp = []
				for traineeid,traineestatus in zip(traineeids,traineesstatus):
					temp.append((MasterFinalTestID,traineeid,testtermid,traineestatus))

				cursor.executemany(query,temp)
		else:
			query = "INSERT INTO  services_masterfinaltest(TrainingGroupID,FinalTestDate) "\
					"Values(%s,STR_TO_DATE( %s,'%%m-%%d-%%Y'))"

			cursor.execute(query,(traininggroup,date))

			MasterFinalTestID = cursor.lastrowid

			query = "INSERT INTO services_detailsfinaltest(MasterFinalTestID,TraineeID,ProgrammeTermID,TraineeTermStatus) "\
					"Values(%s,%s,%s,%s)"

			temp = []
			for traineeid,traineestatus in zip(traineeids,traineesstatus):
				temp.append((MasterFinalTestID,traineeid,testtermid,traineestatus))

			cursor.executemany(query,temp)


		db.commit()
		db.close()

		return jsonify("done")


@app.route('/video', methods=['POST','GET'])
def VideoAccess():
	if request.method == 'GET':
		if 'state' in login_session:
			return render_template('video.html',STATE=login_session['state'])
		else:
			return redirect(url_for('userlogin'))



		

@app.route('/instructions', methods=['POST','GET'])
def InstructionsAccess():
	if request.method == 'GET':
		if 'state' in login_session:
			return render_template('instructions.html',STATE=login_session['state'])
		else:
			return redirect(url_for('userlogin'))
	






@app.route('/corecity', methods=['POST','GET'])
def CityAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query = "SELECT core_cities.*,core_governments.GovernmentName "\
	 			"From core_cities,core_governments "\
	 			"Where core_cities.GovernmentID = core_governments.GovernmentID"

	 	cursor.execute(query)
		results = cursor.fetchall()
		db.close()

		return render_template('Core_cities.html',Cities=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from core_cities where CityID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
			db.close()
			return jsonify('done')
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
	elif request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO  core_cities(CityName,GovernmentID,CityActive,Notes) values('%s','%s','%s','%s')" % (request.json['gname']
																												  ,request.json['govid']
																												  ,1,request.json['gnote'])
		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		id=cursor.lastrowid
		query="SELECT * From core_cities where CityID=%s" % id
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE core_cities SET CityName='%s', GovernmentID='%s', Notes='%s' Where CityID=%s" % (request.json['gname']
																										 ,request.json['govid']
																					  					 ,request.json['gnote']
																					  					 ,request.json['id'])
		try:
			#return query
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
		
		id=cursor.lastrowid
		query="SELECT core_cities.*,core_governments.GovernmentName "\
	 		  "From core_cities,core_governments "\
	 		  "Where core_cities.GovernmentID = core_governments.GovernmentID and core_cities.CityID=%s" % request.json['id']
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)


@app.route('/getassociations', methods=['POST'])
def getassociations():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))

	db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	cursor = db.cursor()
	query = "SELECT AssociationID,AssociationName FROM  hr_associations"

	cursor.execute(query)
	results = cursor.fetchall()
	return jsonify(results)
		
	# db.close()

@app.route('/jobsqla', methods=['POST'])
def getjobsqla():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))
	if 'jobs' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM hr_jobs"
		cursor.execute(query)
		results=cursor.fetchall()

		return jsonify(results)

	elif 'qla' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM hr_qualifications"
		cursor.execute(query)
		results=cursor.fetchall()

		return jsonify(results)
###########
@app.route('/emp', methods=['POST','GET'])
def EmpAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query="SELECT hr_employeesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
	 		  "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	  	      "From hr_employeesdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	  	      "where hr_employeesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	  	      "and hr_jobs.JobID = hr_employeesdata.JobID and hr_qualifications.QualificationID = hr_employeesdata.QualificationID"
	 
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()
	 	return render_template('hr_EmployeeData.html',employess=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from hr_employeesdata where EmployeeID=%s"%request.form['iddel']

		try:
			cursor.execute(query)
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'EMP'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'EMP'+request.form['code'])
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		db.close()
		return jsonify('done')

		#return redirect(url_for('EmpAccess'))

	#return 'wwwwwwwwwww'


	empid=request.form['id']
	code=request.form['code']
	empname=request.form['empname']
	gov=request.form['gov']
	cit=request.form['cit']
	address=request.form['address']
	bdate=request.form['bdate']
	nationalid=request.form['nationalid']
	wats=request.form['wats']
	tno=request.form['tno']
	optionsRadiosInline=request.form['optionsRadiosInline']
	qla=request.form['qla']
	job=request.form['job']
	to=request.form['to']
	fromm=request.form['fromm']
	memberno=request.form['memberno']
	memberOptions=request.form['memberOptions']
	email=request.form['email']
	face=request.form['face']
	twiter=request.form['twiter']
	notes=request.form['notes']
	newfilename=""

	if empid == "-1":
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='EMP'+request.form['code']
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO hr_employeesdata(EmployeeCode,EmployeeName,EmployeeNationalID,EmployeeGender"\
				",EmployeeBirthDate,JobID,QualificationID,CityID,WorkTimeFrom,WorkTimeTo,EmployeeAddress,EmployeePhone"\
				",EmployeeWhatsApp,EmployeePhoto,EmployeeEmail,EmployeeFacebook,EmployeeTwitter,IsMember,MemberCode"\
				",EmployeeActive,Notes) values('%s','%s','%s','%s',STR_TO_DATE('%s','%%m-%%d-%%Y'),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'"\
				",'%s','%s','%s','%s','%s','%s')"%(code,empname,nationalid,optionsRadiosInline,bdate,job,qla,cit,\
												   fromm,to,address,tno,wats,newfilename,email,face,twiter,memberOptions,\
												   memberno,1,notes)
		try:
			cursor.execute(query)
			id=cursor.lastrowid


			query="SELECT hr_employeesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
			      "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	 		      "From hr_employeesdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	 	   	      "where hr_employeesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	 	   	      "and hr_jobs.JobID = hr_employeesdata.JobID and hr_qualifications.QualificationID = hr_employeesdata.QualificationID "\
	 	   	      "and hr_employeesdata.EmployeeID= "+str(id)

	 	   	cursor.execute(query)
	 	   	results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='EMP'+request.form['code']#+"."+filename.rsplit('.',1)[1]
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		else:
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'EMP'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'EMP'+request.form['code'])
				newfilename=""

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query=("UPDATE hr_employeesdata SET EmployeeCode=%s, EmployeeName=%s, EmployeeNationalID=%s, "
				"EmployeeGender=%s,EmployeeBirthDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), JobID=%s, QualificationID=%s, CityID=%s, "
				"WorkTimeFrom=%s, WorkTimeTo=%s, EmployeeAddress=%s, EmployeePhone=%s,  "
				"EmployeeWhatsApp=%s, EmployeePhoto=%s, EmployeeEmail=%s, EmployeeFacebook=%s, EmployeeTwitter=%s, "
				"IsMember=%s, MemberCode=%s, EmployeeActive=%s, Notes=%s Where EmployeeID=%s ")
		try:
			#return query
			cursor.execute(query,(code,empname,nationalid,optionsRadiosInline,bdate,job,
								  qla,cit,fromm,to,address,tno,wats,newfilename,email,
								  face,twiter,memberOptions,memberno,1,notes,empid))
			



			query="SELECT hr_employeesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
			      "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	 		      "From hr_employeesdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	 	   	      "where hr_employeesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	 	   	      "and hr_jobs.JobID = hr_employeesdata.JobID and hr_qualifications.QualificationID = hr_employeesdata.QualificationID "\
	 	   	      "and hr_employeesdata.EmployeeID= "+str(empid)

	 	   	cursor.execute(query)
	 	   	results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	


	
			

         	#return 'done'+request.form.get('optionsRadiosInline')
         	#return render_template('hr_EmployeeData.html')
		# f = request.files['file']
		# f.save(secure_filename(f.filename))

@app.route('/member', methods=['POST','GET'])
def MemberAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="SELECT hr_membersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
	 	      "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	  	      "From hr_membersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	   	      "where hr_membersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	   	      "and hr_jobs.JobID = hr_membersdata.JobID and hr_qualifications.QualificationID = hr_membersdata.QualificationID" 
	
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()
	 	return render_template('hr_MembersData.html',members=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from hr_membersdata where MemberID=%s"%request.form['iddel']

		try:
			cursor.execute(query)
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'MEM'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'MEM'+request.form['code'])
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		db.close()
		return jsonify('done')

		#return redirect(url_for('ShowMaster'))

	#return 'wwwwwwwwwww'


	memid=request.form['id']
	code=request.form['code']
	memname=request.form['memname']
	gov=request.form['gov']
	cit=request.form['cit']
	address=request.form['address']
	bdate=request.form['bdate']
	nationalid=request.form['nationalid']
	wats=request.form['wats']
	tno=request.form['tno']
	optionsRadiosInline=request.form['optionsRadiosInline']
	qla=request.form['qla']
	job=request.form['job']
	email=request.form['email']
	face=request.form['face']
	twiter=request.form['twiter']
	notes=request.form['notes']
	newfilename=""

	if memid == "-1":
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='MEM'+request.form['code']
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO hr_membersdata(MemberCode,MemberName,MemberNationalID,MemberGender"\
				",MemberBirthDate,JobID,QualificationID,CityID,MemberAddress,MemberPhone"\
				",MemberWhatsApp,MemberPhoto,MemberEmail,MemberFacebook,MemberTwitter,MemberActive"\
				",Notes) values('%s','%s','%s','%s',STR_TO_DATE('%s','%%m-%%d-%%Y'),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'"\
				",'%s','%s')"%(code,memname,nationalid,optionsRadiosInline,bdate,job,qla,cit,\
							   address,tno,wats,newfilename,email,face,twiter,1,notes)
		try:
			cursor.execute(query)
			id=cursor.lastrowid

			query="SELECT hr_membersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
		   		  "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	 	   		  "From hr_membersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	  	          "where hr_membersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	  	          "and hr_jobs.JobID = hr_membersdata.JobID and hr_qualifications.QualificationID = hr_membersdata.QualificationID "\
	  	          " and hr_membersdata.MemberID= "+str(id)
			
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='MEM'+request.form['code']#+"."+filename.rsplit('.',1)[1]
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		else:
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'MEM'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'MEM'+request.form['code'])
				newfilename=""

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query=("UPDATE hr_membersdata SET MemberCode=%s, MemberName=%s, MemberNationalID=%s, "
				"MemberGender=%s,MemberBirthDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), JobID=%s, QualificationID=%s, CityID=%s, "
				"MemberAddress=%s, MemberPhone=%s,  MemberWhatsApp=%s, MemberPhoto=%s, MemberEmail=%s, MemberFacebook=%s, "
				"MemberTwitter=%s, MemberActive=%s, Notes=%s Where MemberID=%s ")
		try:
			#return query
			cursor.execute(query,(code,memname,nationalid,optionsRadiosInline,bdate,job,
								  qla,cit,address,tno,wats,newfilename,email,
								  face,twiter,1,notes,memid))


			query="SELECT hr_membersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
		   		  "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	 	   		  "From hr_membersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	  	          "where hr_membersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	  	          "and hr_jobs.JobID = hr_membersdata.JobID and hr_qualifications.QualificationID = hr_membersdata.QualificationID "\
	  	          " and hr_membersdata.MemberID= "+str(memid)
			
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')			

         	#return 'done'+request.form.get('optionsRadiosInline')
         	#return render_template('hr_EmployeeData.html')
		# f = request.files['file']
		# f.save(secure_filename(f.filename))

@app.route('/trainer', methods=['POST','GET'])
def TrainerAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="SELECT hr_trainersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
	 	      "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	   	      "From hr_trainersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	    	  "where hr_trainersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	    	  "and hr_jobs.JobID = hr_trainersdata.JobID and hr_qualifications.QualificationID = hr_trainersdata.QualificationID" 
	
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()
	 	return render_template('hr_TrainersData.html',trainers=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from  hr_trainerworkdays where TrainerID=%s"%request.form['iddel']

		try:
			cursor.execute(query)
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'TRAINER'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'TRAINER'+request.form['code'])
			

			query="DELETE from hr_trainersdata where TrainerID=%s"%request.form['iddel']
			cursor.execute(query)

			db.commit()


		except:
			db.rollback()
	
		db.close()
		return jsonify('done')

		#return redirect(url_for('ShowMaster'))

	#return 'wwwwwwwwwww'


	trainerid=request.form['id']
	code=request.form['code']
	trainername=request.form['trainername']
	gov=request.form['gov']
	cit=request.form['cit']
	address=request.form['address']
	bdate=request.form['bdate']
	nationalid=request.form['nationalid']
	wats=request.form['wats']
	tno=request.form['tno']
	optionsRadiosInline=request.form['optionsRadiosInline']
	qla=request.form['qla']
	job=request.form['job']
	memberno=request.form['memberno']
	memberOptions=request.form['memberOptions']
	email=request.form['email']
	face=request.form['face']
	twiter=request.form['twiter']
	notes=request.form['notes']
	experience=request.form['experience']
	hday1=""
	hday2=""
	hday3=""
	hday4=""
	hday5=""
	hday6=""
	hday7=""
	if request.form.get('day_1'):
		hday1=request.form['hday_1']

	if request.form.get('day_2'):
		hday2=request.form['hday_2']

	if request.form.get('day_3'):
		hday3=request.form['hday_3']

	if request.form.get('day_4'):
		hday4=request.form['hday_4']

	if request.form.get('day_5'):
		hday5=request.form['hday_5']

	if request.form.get('day_6'):
		hday6=request.form['hday_6']

	if request.form.get('day_7'):
		hday7=request.form['hday_7']

	#return jsonify(day1+'   '+day_2)
	newfilename=""

	if trainerid == "-1":
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='TRAINER'+request.form['code']
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO hr_trainersdata(TrainerCode,TrainerName,TrainerNationalID,TrainerGender"\
				",TrainerBirthDate,JobID,QualificationID,CityID,TrainerCategoryID,IsMember"\
				",MemberCode,TrainerExperience,TrainerAddress,TrainerPhone"\
				",TrainerWhatsApp,TrainerPhoto,TrainerEmail,TrainerFacebook,TrainerTwitter,TrainerActive"\
				",Notes) values('%s','%s','%s','%s',STR_TO_DATE('%s','%%m-%%d-%%Y'),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'"\
				",'%s','%s','%s','%s','%s','%s')"%(code,trainername,nationalid,optionsRadiosInline,bdate,job,qla,cit,6,memberOptions,memberno,\
							   				  	   experience,address,tno,wats,newfilename,email,face,twiter,1,notes)
		try:
			cursor.execute(query)
			db.commit()
			id=cursor.lastrowid
			#db.close()

			#db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			#cursor = db.cursor()

			data=[
			(id,1,hday1,1,'aaa'),
			(id,2,hday2,1,'bbb'),
			(id,3,hday3,1,'ccc'),
			(id,4,hday4,1,'hhh'),
			(id,5,hday5,1,'eee'),
			(id,6,hday6,1,'fff'),
			(id,7,hday7,1,'ddd')]

			query = "INSERT INTO hr_trainerworkdays(TrainerID,DayID,AvailableHoursCount,TrainerWorkDayActive,Notes) "\
					"values(%s,%s,%s,%s,%s)"

			cursor.executemany(query,data)

			query="SELECT hr_trainersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
			  "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	  	   	  "From hr_trainersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	   	      "where hr_trainersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	   	      "and hr_jobs.JobID = hr_trainersdata.JobID and hr_qualifications.QualificationID = hr_trainersdata.QualificationID "\
	   	      " and hr_trainersdata.TrainerID="+str(id)
			
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='TRAINER'+request.form['code']#+"."+filename.rsplit('.',1)[1]
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		else:
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'TRAINER'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'TRAINER'+request.form['code'])
				newfilename=""

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query=("UPDATE hr_trainersdata SET TrainerCode=%s, TrainerName=%s, TrainerNationalID=%s, "
				"TrainerGender=%s, TrainerBirthDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), JobID=%s, QualificationID=%s, CityID=%s, "
				"TrainerCategoryID=%s, IsMember=%s, MemberCode=%s, TrainerExperience=%s, "
				"TrainerAddress=%s, TrainerPhone=%s,  TrainerWhatsApp=%s, TrainerPhoto=%s, TrainerEmail=%s, TrainerFacebook=%s, "
				"TrainerTwitter=%s, TrainerActive=%s, Notes=%s Where TrainerID=%s ")
		try:
			#return query
			cursor.execute(query,(code,trainername,nationalid,optionsRadiosInline,bdate,job,
								  qla,cit,6,memberOptions,memberno,experience,address,tno,wats,newfilename,email,
								  face,twiter,1,notes,trainerid))
			


			data=[
			(trainerid,1,hday1,1,'aaa',trainerid,1),
			(trainerid,2,hday2,1,'bbb',trainerid,2),
			(trainerid,3,hday3,1,'ccc',trainerid,3),
			(trainerid,4,hday4,1,'hhh',trainerid,4),
			(trainerid,5,hday5,1,'eee',trainerid,5),
			(trainerid,6,hday6,1,'fff',trainerid,6),
			(trainerid,7,hday7,1,'ddd',trainerid,7)

			]

			query = "UPDATE hr_trainerworkdays SET TrainerID=%s, DayID=%s, AvailableHoursCount=%s, TrainerWorkDayActive=%s, Notes=%s "\
					"Where TrainerID=%s and DayID=%s"

			cursor.executemany(query,data)

			query="SELECT hr_trainersdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_jobs.JobName, hr_jobs.JobID, "\
			  "hr_qualifications.QualificationName, hr_qualifications.QualificationID "\
	  	   	  "From hr_trainersdata, core_governments , core_cities, hr_jobs, hr_qualifications "\
	   	      "where hr_trainersdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	   	      "and hr_jobs.JobID = hr_trainersdata.JobID and hr_qualifications.QualificationID = hr_trainersdata.QualificationID "\
	   	      " and hr_trainersdata.TrainerID="+str(trainerid)
			
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')			

         	#return 'done'+request.form.get('optionsRadiosInline')
         	#return render_template('hr_EmployeeData.html')
		# f = request.files['file']
		# f.save(secure_filename(f.filename))


@app.route('/trainee', methods=['POST','GET'])
def TraineeAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
	 	query="SELECT hr_traineesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_fathers.FatherID,"\
	  	      "hr_fathers.FatherName,hr_fathers.FatherJob,hr_swimmingaims.SwimmingAimName, "\
	  	      "hr_associations.AssociationID,hr_associations.AssociationName, services_levels.LevelDescription "\
	    	  "From hr_traineesdata, core_governments , core_cities, hr_fathers, hr_swimmingaims, hr_associations, services_levels "\
	    	  "where hr_traineesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	    	  "and hr_fathers.FatherID = hr_traineesdata.FatherID and hr_swimmingaims.SwimmingAimID = hr_traineesdata.SwimmingAimID "\
	    	  "and hr_associations.AssociationID = hr_traineesdata.AssociationID and services_levels.LevelID = hr_traineesdata.LevelID"
	 	
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()
	 	return render_template('hr_TraineeData.html',trainees=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from   hr_traineesdata where TraineeID=%s"%request.form['iddel']

		try:

			cursor.execute(query)
			db.commit()
			
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'TRAINEE'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'TRAINEE'+request.form['code'])

		except:
			db.rollback()
	
		db.close()
		return jsonify('done')

		#return redirect(url_for('ShowMaster'))

	#return 'wwwwwwwwwww'


	traineeid=request.form['id']
	code=request.form['code']
	traineename=request.form['traineename']
	gov=request.form['gov']
	cit=request.form['cit']
	address=request.form['address']
	bdate=request.form['bdate']
	nationalid=request.form['nationalid']
	wats=request.form['wats']
	tno=request.form['tno']
	optionsRadiosInline=request.form['optionsRadiosInline']
	pastswim=request.form['pastswim']
	swimaim=request.form['swimaim']
	period=request.form['period']
	associations=request.form['associations']
	responsible=request.form['responsible']
	memberno=request.form['memberno']
	memberOptions=request.form['memberOptions']
	email=request.form['email']
	face=request.form['face']
	twiter=request.form['twiter']
	notes=request.form['notes']
	levelid=request.form['level']
	fatherjob=request.form['fatherjob']
	fathernameselect = ""
	fathername = ""
	
	if request.form['responsible'] == "1":
		fathernameselect=request.form['fathernameselect']
	else:
		fathername=request.form['fathername']


	#return jsonify(day1+'   '+day_2)
	newfilename=""

	if traineeid == "-1":
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='TRAINEE'+request.form['code']
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = ""
		try:
			if request.form['responsible'] == "0":
				query = "INSERT INTO hr_fathers(FatherName,FatherJob) values('%s','%s')"%(fathername,fatherjob)
				cursor.execute(query)
				id=cursor.lastrowid

				query = "INSERT INTO hr_traineesdata(TraineeCode,TraineeName,CityID,TraineeAddress"\
						",TraineeNationalID,TraineeBirthDate,TraineePhone,TraineeWhatsApp,TraineeGender,IsMember"\
						",MemberCode,TraineePhoto,TraineeEmail,TraineeFacebook"\
						",TraineeTwitter,PeriodType,IsLearnningSwimming,SwimmingAimID,AssociationID,Notes"\
						",FatherID,LevelID,TraineeActive) values('%s','%s','%s','%s','%s',STR_TO_DATE('%s','%%m-%%d-%%Y'),'%s','%s','%s','%s','%s','%s','%s','%s'"\
						",'%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(code,traineename,cit,address,nationalid,bdate,tno,wats,\
																	 	  optionsRadiosInline,memberOptions,memberno,newfilename,email,\
									   				  	   			 	  face,twiter,period,pastswim,swimaim,associations,notes,id,levelid,1)
			else:
				query = "INSERT INTO hr_traineesdata(TraineeCode,TraineeName,CityID,TraineeAddress"\
						",TraineeNationalID,TraineeBirthDate,TraineePhone,TraineeWhatsApp,TraineeGender,IsMember"\
						",MemberCode,TraineePhoto,TraineeEmail,TraineeFacebook"\
						",TraineeTwitter,PeriodType,IsLearnningSwimming,SwimmingAimID,AssociationID,Notes"\
						",FatherID,LevelID,TraineeActive) values('%s','%s','%s','%s','%s',STR_TO_DATE('%s','%%m-%%d-%%Y'),'%s','%s','%s','%s','%s','%s','%s','%s'"\
						",'%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(code,traineename,cit,address,nationalid,bdate,tno,wats,\
																	 	  optionsRadiosInline,memberOptions,memberno,newfilename,email,\
									   				  	   			 	  face,twiter,period,pastswim,swimaim,associations,notes,fathernameselect,levelid,1)
		
			cursor.execute(query)
			id=cursor.lastrowid
			#db.close()
			#db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			#cursor = db.cursor()
			query="SELECT hr_traineesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_fathers.FatherID,"\
	 	   	  	  "hr_fathers.FatherName,hr_fathers.FatherJob,hr_swimmingaims.SwimmingAimName, "\
	 	          "hr_associations.AssociationID,hr_associations.AssociationName, services_levels.LevelDescription "\
	   	          "From hr_traineesdata, core_governments , core_cities, hr_fathers, hr_swimmingaims, hr_associations, services_levels "\
	   	          "where hr_traineesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	   	          "and hr_fathers.FatherID = hr_traineesdata.FatherID and hr_swimmingaims.SwimmingAimID = hr_traineesdata.SwimmingAimID "\
	   	          "and hr_associations.AssociationID = hr_traineesdata.AssociationID and services_levels.LevelID = hr_traineesdata.LevelID "\
	   	          "and hr_traineesdata.TraineeID="+str(id)
			
			cursor.execute(query)
			results = cursor.fetchone()
			
			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		if 'file' in request.files:
			file = request.files['file']
			if allowed_file(file.filename):
				filename = secure_filename(file.filename)
				newfilename='TRAINEE'+request.form['code']#+"."+filename.rsplit('.',1)[1]
				file.save(app.config['UPLOAD_FOLDER']+newfilename)
		else:
			if os.path.isfile(app.config['UPLOAD_FOLDER']+'TRAINEE'+request.form['code']):
				os.remove(app.config['UPLOAD_FOLDER']+'TRAINEE'+request.form['code'])
				newfilename=""

		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = ""


		try:
			#return "aaaaaaaaaa"+request.form['responsible']
			if request.form['responsible'] == "0":

				query="UPDATE hr_fathers SET FatherName='%s',FatherJob='%s' Where FatherID=%s"%(fathername,fatherjob,request.form['fatherid'])
				#return query
				cursor.execute(query)

				query=("UPDATE hr_traineesdata SET TraineeCode=%s, TraineeName=%s, CityID=%s, "
				   "TraineeAddress=%s, TraineeNationalID=%s, TraineeBirthDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), TraineePhone=%s, TraineeWhatsApp=%s, "
				   "TraineeGender=%s, IsMember=%s, MemberCode=%s, TraineePhoto=%s, "
				   "TraineeEmail=%s, TraineeFacebook=%s,  TraineeTwitter=%s, PeriodType=%s, IsLearnningSwimming=%s, SwimmingAimID=%s, "
				   "AssociationID=%s, Notes=%s, LevelID=%s, TraineeActive=%s Where TraineeID=%s ")

				#return query

				cursor.execute(query,(code,traineename,cit,address,nationalid,bdate,tno,wats,
								      optionsRadiosInline,memberOptions,memberno,newfilename,email,
								      face,twiter,period,pastswim,swimaim,associations,notes,levelid,1,traineeid))
				#return query
			
			else:

				query="UPDATE hr_fathers SET FatherJob='%s' Where FatherID=%s"%(fatherjob,request.form['fatherid'])
				cursor.execute(query)
			
				query=("UPDATE hr_traineesdata SET TraineeCode=%s, TraineeName=%s, CityID=%s, "
				       "TraineeAddress=%s, TraineeNationalID=%s, TraineeBirthDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'), TraineePhone=%s, TraineeWhatsApp=%s, "
				       "TraineeGender=%s, IsMember=%s, MemberCode=%s, TraineePhoto=%s, "
				       "TraineeEmail=%s, TraineeFacebook=%s,  TraineeTwitter=%s, PeriodType=%s, IsLearnningSwimming=%s, SwimmingAimID=%s, "
				       "AssociationID=%s, Notes=%s, FatherID=%s, LevelID=%s, TraineeActive=%s Where TraineeID=%s ")
				
				cursor.execute(query,(code,traineename,cit,address,nationalid,bdate,tno,wats,
								      optionsRadiosInline,memberOptions,memberno,newfilename,email,
								      face,twiter,period,pastswim,swimaim,associations,notes,fathernameselect,levelid,1,traineeid))
			


			
			query="SELECT hr_traineesdata.*, core_governments.GovernmentName, core_governments.GovernmentID, hr_fathers.FatherID,"\
	 	   	      "hr_fathers.FatherName,hr_fathers.FatherJob,hr_swimmingaims.SwimmingAimName, "\
	 	          "hr_associations.AssociationID,hr_associations.AssociationName, services_levels.LevelDescription "\
	   	          "From hr_traineesdata, core_governments , core_cities, hr_fathers, hr_swimmingaims, hr_associations, services_levels "\
	   	          "where hr_traineesdata.CityID=core_cities.CityID and core_cities.GovernmentID = core_governments.GovernmentID "\
	   	          "and hr_fathers.FatherID = hr_traineesdata.FatherID and hr_swimmingaims.SwimmingAimID = hr_traineesdata.SwimmingAimID "\
	   	          "and hr_associations.AssociationID = hr_traineesdata.AssociationID and services_levels.LevelID = hr_traineesdata.LevelID "\
	   	          "and hr_traineesdata.TraineeID="+str(traineeid)
			
			cursor.execute(query)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')			

         	#return 'done'+request.form.get('optionsRadiosInline')
         	#return render_template('hr_EmployeeData.html')
		# f = request.files['file']
		# f.save(secure_filename(f.filename))

@app.route('/assigntraineetraininggroup',methods=['POST','GET'])
def AssignTraineeTrainingGroupAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))

	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state']=state

		return render_template('Services_AssignTraineesToTrainingGroups.html',STATE=state)

	if 'getfreetraininggroupsbylevel' in request.json:
		levelid = request.json['getfreetraininggroupsbylevel']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT services_training_groups.*,services_groupscategories.TraineesCounts,services_groupscategories.TraineeCost "\
				"FROM services_training_groups,services_groupscategories "\
				"Where services_groupscategories.GroupCategoryID =services_training_groups.GroupCategoryID and "\
				"services_training_groups.TrainingGroupTakenSessions = 0 and "\
				"services_training_groups.LevelID = "+str(levelid)
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)

	if 'getfreetraineesbylevel' in request.json:
		levelid = request.json['getfreetraineesbylevel']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_traineesdata.* "\
				"FROM services_testsdatesdetails,hr_traineesdata "\
				"Where hr_traineesdata.TraineeID = services_testsdatesdetails.TraineeID and services_testsdatesdetails.IsAttended=1 and "\
				"services_testsdatesdetails.AssignedToGroup IS NULL and services_testsdatesdetails.TestLevelID = "+str(levelid)
		#return jsonify(query)
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)

	if 'getassignedtraineesbygroup' in request.json:
		groupid = request.json['getassignedtraineesbygroup']
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT hr_traineesdata.*,services_traineewithtraininggroups.Cost "\
				"FROM  hr_traineesdata,services_training_groups,services_traineewithtraininggroups "\
				"Where services_traineewithtraininggroups.TrainingGroupID = services_training_groups.TrainingGroupID and "\
				"services_traineewithtraininggroups.TraineeID = hr_traineesdata.TraineeID and "\
				"services_training_groups.TrainingGroupID = "+str(groupid)
		#return jsonify(query)
		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)
	
	if 'save' in request.json:
		
		traininggroupid = request.json['traininggroupid']
		iscompleted = request.json['iscompleted']
		traineeids = request.json['traineeids']
		traineescost = request.json['traineecost']
		levelid = request.json['levelid']
		
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		
		query = "UPDATE  services_training_groups SET TrainingGroupCompleted = %s Where TrainingGroupID = %s"
		cursor.execute(query,(iscompleted,traininggroupid))

		query = "SELECT TraineeID,Cost FROM services_traineewithtraininggroups Where TrainingGroupID = %s"
		cursor.execute(query,(traininggroupid,))
		results = cursor.fetchall()

		oldtraineeids = []
		oldtraineescost = []

		for item in results:
			oldtraineeids.append(item[0])
			oldtraineescost.append(item[1])
		
		#oldtraineeids,oldtraineecost = [item[0],item[1] for item in cursor.fetchall()]

		temptraineeids = traineeids
		temptraineescost = traineescost

		tempoldtraineeids = oldtraineeids
		tempoldtraineescost = oldtraineescost
		
		for traineeid,traineecost in zip(traineeids,traineescost):
			if traineeid in oldtraineeids:
				query = "UPDATE services_traineewithtraininggroups SET Cost=%s Where TrainingGroupID=%s and TraineeID=%s"
				cursor.execute(query,(traineecost,traininggroupid,traineeid))

				index = temptraineeids.index(traineeid)

				del temptraineeids[index]
				del temptraineescost[index]

				index = tempoldtraineeids.index(traineeid)
				
				del tempoldtraineeids[index]
				del tempoldtraineescost[index]

		for traineeid in tempoldtraineeids:
			query = "DELETE FROM services_traineewithtraininggroups Where TrainingGroupID=%s and TraineeID=%s"
			cursor.execute(query,(traininggroupid,traineeid))

			query = "UPDATE  services_testsdatesdetails SET AssignedToGroup = NULL Where TraineeID=%s and "\
					"IsAttended = 1 and TestLevelID=%s"
			cursor.execute(query,(traineeid,levelid))

		for traineeid,traineecost in zip(temptraineeids,temptraineescost):
			query = "INSERT INTO services_traineewithtraininggroups(TrainingGroupID,TraineeID,Cost) Values(%s,%s,%s)"
			cursor.execute(query,(traininggroupid,traineeid,traineecost))

			query = "UPDATE  services_testsdatesdetails SET AssignedToGroup = 1 Where TraineeID=%s and "\
					"IsAttended = 1 and TestLevelID=%s"
			cursor.execute(query,(traineeid,levelid))

		db.commit()
		db.close()

		return jsonify('done')







@app.route('/traininggroups',methods=['POST','GET'])
def TrainingGroupsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state']=state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT services_training_groups.*,services_training_days.TrainingDayDescription,services_groupscategories.GroupCategoryDescription "\
			  "FROM services_training_groups, services_training_days, services_groupscategories "\
			  "where services_training_groups.TrainingDayID = services_training_days.TrainingDayID and "\
			  "services_groupscategories.GroupCategoryID=services_training_groups.GroupCategoryID"
		cursor.execute(query)
		results=cursor.fetchall()

		db.close()
		return render_template('Services_TrainingGroups.html',Groups=results,STATE=state)


	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE FROM  services_traininggroups_swimmingpool Where TrainingGroupID=%s"%request.form['iddel']
		

		try:
			query="DELETE FROM  services_traininggroups_trainers Where TrainingGroupID=%s"%request.form['iddel']
			cursor.execute(query)

			query="DELETE from  services_training_groups where TrainingGroupID=%s"%request.form['iddel']
			cursor.execute(query)

			db.commit()
			db.close()
			return jsonify('done')

		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		



	gid = request.form['id']
	code = request.form['code']
	category = request.form['category']
	description = request.form['description']
	trainingdays = request.form['trainingdays']
	level = request.form['level']
	trainers = request.form.getlist('trainers')
	employee = request.form['employee']
	swimmingpools = request.form['swimmingpools']
	sections = request.form.getlist('sections')
	period = request.form['period']
	etime = request.form['etime']
	stime = request.form['stime']
	edate = request.form['edate']
	sdate = request.form['sdate']
	notes = request.form['notes']
	sessionsno = request.form['trainingsessionsno']

	if gid == "-1":
		try:
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()
			query = "INSERT INTO  services_training_groups(TrainingGroupCode,TrainingGroupDescription,GroupCategoryID,"\
			    	"TrainingDayID,LevelID,EmployeeID,SwimmingPoolID,TrainingGroupPeriod,TrainingGroupStartTime,"\
			    	"TrainingGroupEndTime,TrainingGroupStartDate,TrainingGroupEndDate,TrainingGroupCompleted,"\
			    	"TrainingGroupSessionsNO,TrainingGroupTakenSessions,TrainingGroupActive,Notes) "\
			    	"values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,STR_TO_DATE(%s,'%%m/%%d/%%Y'),STR_TO_DATE(%s,'%%m-%%d-%%Y'),"\
			    	"%s,%s,%s,%s,%s)"

			#return edate
			cursor.execute(query,(code,description,category,trainingdays,level,employee,swimmingpools,period,
							      stime,etime,sdate,edate,0,sessionsno,0,1,notes))
			#return query
			id = cursor.lastrowid

			query = "INSERT INTO services_traininggroups_trainers(TrainingGroupID,TrainerID) values(%s,%s)"

			temp=[]
			for trainer in trainers:
				temp.append((id,trainer))

			cursor.executemany(query,temp)

			query = "INSERT INTO services_traininggroups_swimmingpool(TrainingGroupID,SwimmingPoolID,SectionNumber) values(%s,%s,%s)"

			temp=[]
			for section in sections:
				temp.append((id,swimmingpools,section))

			cursor.executemany(query,temp)

			query="SELECT services_training_groups.*,services_training_days.TrainingDayDescription,services_groupscategories.GroupCategoryDescription "\
			  	  "FROM services_training_groups, services_training_days,services_groupscategories "\
			      "where services_training_groups.TrainingDayID = services_training_days.TrainingDayID "\
			      "and services_groupscategories.GroupCategoryID=services_training_groups.GroupCategoryID "\
			      "and services_training_groups.TrainingGroupID="+str(id)
			
			cursor.execute(query)
			results = cursor.fetchone()


			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		try:
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()
			query = "UPDATE services_training_groups SET TrainingGroupCode=%s,TrainingGroupDescription=%s,"\
				    "GroupCategoryID=%s,TrainingDayID=%s,LevelID=%s,EmployeeID=%s,SwimmingPoolID=%s,TrainingGroupPeriod=%s,"\
				    "TrainingGroupStartTime=%s,TrainingGroupEndTime=%s,TrainingGroupStartDate=STR_TO_DATE(%s,'%%m/%%d/%%Y'),"\
				    "TrainingGroupEndDate=STR_TO_DATE(%s,'%%m-%%d-%%Y'),TrainingGroupActive=%s,Notes=%s,TrainingGroupSessionsNO=%s "\
				    "Where TrainingGroupID=%s"

			cursor.execute(query,(code,description,category,trainingdays,level,employee,swimmingpools,period,
							      stime,etime,sdate,edate,1,notes,sessionsno,gid))

			
			query = "DELETE FROM  services_traininggroups_trainers Where TrainingGroupID=%s"
			cursor.execute(query,gid)

			query = "INSERT INTO services_traininggroups_trainers(TrainingGroupID,TrainerID) values(%s,%s)"

			temp=[]
			for trainer in trainers:
				temp.append((gid,trainer))

			cursor.executemany(query,temp)

			
			query = "DELETE FROM services_traininggroups_swimmingpool Where TrainingGroupID=%s"
			cursor.execute(query,gid)

			query = "INSERT INTO services_traininggroups_swimmingpool(TrainingGroupID,SwimmingPoolID,SectionNumber) values(%s,%s,%s)"

			temp=[]
			for section in sections:
				temp.append((gid,swimmingpools,section))

			cursor.executemany(query,temp)


			query="SELECT services_training_groups.*,services_training_days.TrainingDayDescription,services_groupscategories.GroupCategoryDescription "\
			      "FROM services_training_groups, services_training_days,services_groupscategories "\
			      "where services_training_groups.TrainingDayID = services_training_days.TrainingDayID "\
			      "and services_groupscategories.GroupCategoryID=services_training_groups.GroupCategoryID "\
			      "and services_training_groups.TrainingGroupID="+str(gid)



			cursor.execute(query)
			results = cursor.fetchone()


			db.commit()
			db.close()
			return jsonify(results)

		except Exception as e:
			db.rollback()
			db.close()
			return jsonify(str(e))


@app.route('/trainingdays',methods=['POST','GET'])
def TrainingDaysAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state']=state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT services_training_days.TrainingDayID,services_training_days.TrainingDayCode,"\
		      "services_training_days.TrainingDayDescription, GROUP_CONCAT(hr_days.DayName SEPARATOR ','),services_training_days.Notes "\
		      "From services_training_days,services_trainingdays_days,hr_days "\
		      "where services_training_days.TrainingDayID=services_trainingdays_days.TrainingDayID and "\
		      "services_trainingdays_days.DayID=hr_days.DayID "\
		      "group by services_training_days.TrainingDayID,services_training_days.TrainingDayDescription,"\
		      "services_training_days.TrainingDayCode,services_training_days.Notes"

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()
		return render_template('Services_TrainingDays.html',Days=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE FROM  services_trainingdays_days Where TrainingDayID=%s"%request.form['iddel']
		

		try:
			cursor.execute(query)


			query="DELETE from  services_training_days where TrainingDayID=%s"%request.form['iddel']
			cursor.execute(query)

			db.commit()
			db.close()
			return jsonify('done')

		except:
			db.rollback()
			db.close()
			return jsonify('error')


	dayid = request.form['id']
	code = request.form['code']
	description = request.form['description']
	notes = request.form['notes']
	day_1=""
	day_2=""
	day_3=""
	day_4=""
	day_5=""
	day_6=""
	day_7=""
	data=[]

	

	if dayid == "-1":
		try:
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()
			query = "INSERT INTO services_training_days(TrainingDayCode,TrainingDayDescription,TrainingDayActive,Notes) "\
				    "values(%s,%s,%s,%s)"
			cursor.execute(query,(code,description,1,notes))
			id=cursor.lastrowid

			if request.form.get('day_1'):
				data.append((1,id))

			if request.form.get('day_2'):
				data.append((2,id))

			if request.form.get('day_3'):
				data.append((3,id))

			if request.form.get('day_4'):
				data.append((4,id))
	
			if request.form.get('day_5'):
				data.append((5,id))
	
			if request.form.get('day_6'):
				data.append((6,id))
	
			if request.form.get('day_7'):
				data.append((7,id))

			query = "INSERT INTO services_trainingdays_days(DayID,TrainingDayID) values(%s,%s)"
			cursor.executemany(query,data)

			query="SELECT services_training_days.TrainingDayID,services_training_days.TrainingDayCode,"\
		          "services_training_days.TrainingDayDescription, GROUP_CONCAT(hr_days.DayName SEPARATOR ','),services_training_days.Notes "\
		          "From services_training_days,services_trainingdays_days,hr_days "\
		          "where services_training_days.TrainingDayID=services_trainingdays_days.TrainingDayID and "\
		          "services_trainingdays_days.DayID=hr_days.DayID and services_training_days.TrainingDayID=%s "\
		          "group by services_training_days.TrainingDayID,services_training_days.TrainingDayDescription,"\
		          "services_training_days.TrainingDayCode,services_training_days.Notes"


			cursor.execute(query,id)
			results = cursor.fetchone()

			db.commit()
			db.close()
			return jsonify(results)
		except:
			db.rollback()
			db.close()
			return jsonify('error')

	else:
		try:
			db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
			cursor = db.cursor()
			query="UPDATE services_training_days SET TrainingDayCode=%s,TrainingDayDescription=%s,"\
				  "TrainingDayActive=%s,Notes=%s"
			cursor.execute(query,(code,description,1,notes))

			query="DELETE FROM services_trainingdays_days Where TrainingDayID=%s"
			cursor.execute(query,dayid)

			if request.form.get('day_1'):
				data.append((1,dayid))

			if request.form.get('day_2'):
				data.append((2,dayid))

			if request.form.get('day_3'):
				data.append((3,dayid))

			if request.form.get('day_4'):
				data.append((4,dayid))
	
			if request.form.get('day_5'):
				data.append((5,dayid))
	
			if request.form.get('day_6'):
				data.append((6,dayid))
	
			if request.form.get('day_7'):
				data.append((7,dayid))

			query = "INSERT INTO services_trainingdays_days(DayID,TrainingDayID) values(%s,%s)"
			cursor.executemany(query,data)

			query="SELECT services_training_days.TrainingDayID,services_training_days.TrainingDayCode,"\
		          "services_training_days.TrainingDayDescription, GROUP_CONCAT(hr_days.DayName SEPARATOR ','),services_training_days.Notes "\
		          "From services_training_days,services_trainingdays_days,hr_days "\
		          "where services_training_days.TrainingDayID=services_trainingdays_days.TrainingDayID and "\
		          "services_trainingdays_days.DayID=hr_days.DayID and services_training_days.TrainingDayID=%s "\
		          "group by services_training_days.TrainingDayID,services_training_days.TrainingDayDescription,"\
		          "services_training_days.TrainingDayCode,services_training_days.Notes"
			
			cursor.execute(query,dayid)
			results = cursor.fetchone()

			db.commit()
			db.close()

			return jsonify(results)

		except:

			db.rollback()
			db.close()
			return jsonify('error')


@app.route('/groupscategories', methods=['POST','GET'])
def GroupsCategoriesAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query = "SELECT * FROM services_groupscategories"
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()

	 	return render_template('Services_GroupsCategories.html',Categories=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from services_groupscategories where GroupCategoryID=%s"%request.form['iddel']

		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		db.close()
		return jsonify('done')

	categoryid=request.form['id']
	code = request.form['code']
	description = request.form['description']
	traineeno = request.form['traineeno']
	cost = request.form['cost']
	notes = request.form['notes']

	if categoryid == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query="INSERT INTO  services_groupscategories(GroupCategoryCode,GroupCategoryDescription,TraineesCounts,"\
	 		  "TraineeCost,GroupCategoryActive,Notes) values(%s,%s,%s,%s,%s,%s)"
	 	try:
	 		cursor.execute(query,(code,description,traineeno,cost,1,notes))
	 		id = cursor.lastrowid

	 		query = "SELECT * FROM services_groupscategories Where GroupCategoryID="+str(id)
	 		cursor.execute(query)
	 		results = cursor.fetchone()

	 		db.commit()
	 		db.close()
	 		return jsonify(results)
	 	except:
	 		db.rollback()
	 		db.close()
	 		return jsonify('error')
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query="UPDATE services_groupscategories SET GroupCategoryCode=%s,GroupCategoryDescription=%s,"\
	 		  "TraineesCounts=%s,TraineeCost=%s,GroupCategoryActive=%s,Notes=%s Where GroupCategoryID=%s"
	 	
	 	try:
	 		cursor.execute(query,(code,description,traineeno,cost,1,notes,categoryid))

	 		query = "SELECT * FROM services_groupscategories Where GroupCategoryID="+str(categoryid)
	 		cursor.execute(query)
	 		results = cursor.fetchone()
	 		db.commit()
	 		db.close()

	 		return jsonify(results)
	 	except:
	 		db.rollback()
	 		db.close()
	 		return jsonify('error')


@app.route('/levels', methods=['POST','GET'])
def LevelsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query = "SELECT * FROM services_levels"
	 	cursor.execute(query)
	 	results=cursor.fetchall()
	 	db.close()

	 	return render_template('Services_Levels.html',levels=results,STATE=state)

	if 'iddel' in request.form:
		#return 'hello'
		db = MySQLdb.connect("localhost","root","","SAMS")
		cursor = db.cursor()
		query="DELETE from services_levels where LevelID=%s"%request.form['iddel']

		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		db.close()
		return jsonify('done')

	levelid=request.form['id']
	description=request.form['description']


	if levelid == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query="INSERT INTO  services_levels(LevelDescription) values(%s)"
	 	try:
	 		cursor.execute(query,description)
	 		id = cursor.lastrowid
	 		query = "SELECT * FROM services_levels Where LevelID="+str(id)
	 		
	 		cursor.execute(query)
	 		results = cursor.fetchone()

	 		db.commit()
	 		db.close()
	 		return jsonify(results)
	 	except:
	 		db.rollback()
	 		db.close()
	 		return jsonify('error')
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
	 	cursor = db.cursor()
	 	query="UPDATE services_levels SET LevelDescription=%s Where LevelID=%s"
	 	
	 	try:
	 		cursor.execute(query,(description,levelid))
	 		query = "SELECT * FROM services_levels Where LevelID="+str(levelid)

	 		cursor.execute(query)
	 		results = cursor.fetchone()

	 		db.commit()
	 		db.close()
	 		return jsonify(results)
	 	except:
	 		db.rollback()
	 		db.close()
	 		return jsonify('error')
##############################
@app.route('/traininggroupshelper',methods=['POST'])
def TrainingGroupsHelper():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if 'trainingdays' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT services_training_days.TrainingDayID,services_training_days.TrainingDayDescription,"\
		      "GROUP_CONCAT(hr_days.DayName SEPARATOR ',') "\
		      "From services_training_days,services_trainingdays_days,hr_days "\
		      "where services_training_days.TrainingDayID=services_trainingdays_days.TrainingDayID and services_trainingdays_days.DayID=hr_days.DayID "\
		      "group by services_training_days.TrainingDayID,services_training_days.TrainingDayDescription"

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'employee' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT EmployeeID,EmployeeName "\
			  "From hr_employeesdata"
		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'trainingdayid' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT hr_trainersdata.TrainerID,hr_trainersdata.TrainerName,GROUP_CONCAT(hr_days.DayName SEPARATOR ',') "\
		      "From services_training_days,services_trainingdays_days,hr_days,hr_trainerworkdays,hr_trainersdata "\
		      "Where services_training_days.TrainingDayID='%s' and services_trainingdays_days.TrainingDayID=services_training_days.TrainingDayID and "\
		      "hr_days.DayID=services_trainingdays_days.DayID and hr_trainerworkdays.DayID = services_trainingdays_days.DayID and "\
		      "hr_trainerworkdays.AvailableHoursCount > 0 and hr_trainersdata.TrainerID = hr_trainerworkdays.TrainerID "\
		      "group by hr_trainersdata.TrainerID,hr_trainersdata.TrainerName" % request.json['trainingdayid']

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)

	elif 'traininggrouptrainers' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT TrainerID FROM services_traininggroups_trainers Where TrainingGroupID='%s'" % request.json['traininggrouptrainers']

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'level' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT LevelID,LevelDescription FROM services_levels ORDER BY LevelID"

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'category' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT GroupCategoryID,GroupCategoryDescription FROM services_groupscategories"

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'swimmingpools' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT SwimmingPoolID,SwimmingPoolName,Sectionsno FROM services_swimmingpool"

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
	elif 'swimmingpoolsections' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query="SELECT SectionNumber FROM services_traininggroups_swimmingpool Where TrainingGroupID='%s'" % request.json['swimmingpoolsections']

		cursor.execute(query)
		results=cursor.fetchall()
		db.close()

		return jsonify(results)
			
@app.route('/daysoftraingingday',methods=['POST'])		
def DaysofTrainingDay():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))
	if 'trainingdayid' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "select DayID from  services_trainingdays_days "\
				"where TrainingDayID="+str(request.json['trainingdayid'])

		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)

@app.route('/workdays',methods=['POST'])
def TrainerWorkDaysAccess():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))
	if 'trainerid' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "select * from  hr_trainerworkdays "\
				"where TrainerID="+str(request.json['trainerid'])

		cursor.execute(query)
		results = cursor.fetchall()
		db.close()
		return jsonify(results)

@app.route('/', methods=['POST','GET'])
def userlogin():
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		return render_template('index.html',STATE=state)
	else:
		if request.args.get('state') != login_session['state']:
			return jsonify('error')
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor=db.cursor()
		query = "SELECT * FROM accounts_users WHERE UserName=%s and UserPassword=%s"
		cursor.execute(query,(request.form['name'],request.form['pass']))
		result=cursor.fetchone()
		if cursor.rowcount == 0:
			db.close()
			return jsonify('error')
		else:
			db.close()
			login_session['username']=result[1]
			login_session['userpass']=result[2]
			login_session['role']=result[3]
			login_session['id']=result[4]

			return jsonify(login_session['role'])

			#if login_session['role'] == 29:
			#	return #redirect(url_for('EmpAccess'))
			#elif login_session['role'] == 30:
			#	return redirect(url_for('MemberAccess'))
			#elif login_session['role'] == 31:
			#	return redirect(url_for('TrainerAccess'))
			#elif login_session['role'] == 32:
			#	return redirect(url_for('TraineeAccess'))

@app.route('/home', methods=['POST','GET'])
def HomeAccess():
	if request.method == 'GET':
		if 'state' in login_session:
			return render_template('home.html',STATE=login_session['state'])
		else:
			return redirect(url_for('userlogin'))

@app.route('/history', methods=['POST','GET'])
def HistoryAccess():
	if request.method == 'GET':
		if 'state' in login_session:
			return render_template('history.html',STATE=login_session['state'])
		else:
			return redirect(url_for('userlogin'))


@app.route('/eating', methods=['POST','GET'])
def EatingAccess():
	if request.method == 'GET':
		if 'state' in login_session:
			return render_template('eating.html',STATE=login_session['state'])
		else:
			return redirect(url_for('userlogin'))

@app.route('/swimmingpools', methods=['POST','GET'])
def SwimmingPoolsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM services_swimmingpool"
		cursor.execute(query)
		results = cursor.fetchall()
		
		db.close()

		return render_template('Services_SwimmingPools.html', pools=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from services_swimmingpool where SwimmingPoolID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
			db.close()
			return jsonify('done')
		except:
			db.rollback()
			db.close()
			return jsonify('error')

	name = request.json['name']
	notes = request.json['note']
	sectionsno = request.json['sectionsno']

	if request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO services_swimmingpool(SwimmingPoolName,Sectionsno,SwimmingPoolActive,Notes) values(%s,%s,%s,%s)"
		try:
			cursor.execute(query,(name,sectionsno,1,notes))
			id = cursor.lastrowid

			query = "SELECT * From services_swimmingpool where SwimmingPoolID=%s" % id
			cursor.execute(query)
			re = cursor.fetchone()
			db.commit()
			db.close()
			return jsonify(re)
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE services_swimmingpool SET SwimmingPoolName=%s, Sectionsno=%s, SwimmingPoolActive=%s, Notes=%s "\
		        "Where SwimmingPoolID=%s"
		try:
			#return query
			cursor.execute(query,(name,sectionsno,1,notes,request.json['id']))

			query="SELECT * From services_swimmingpool where SwimmingPoolID=%s" % request.json['id']
			cursor.execute(query)
			re = cursor.fetchone()
			
			db.commit()
			db.close()
			return jsonify(re)
		except:
			db.rollback()
			db.close()
			return jsonify('error')

@app.route('/rolesaccess', methods=['POST','GET'])
def RolesAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM accounts_roles"
		cursor.execute(query)
		results = cursor.fetchall()
		
		db.close()

		return render_template('Accounts_roles.html', roles=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from accounts_roles where RoleID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
			db.close()
			return jsonify('done')
		except:
			db.rollback()
			db.close()
			return jsonify('error')

	elif request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO accounts_roles(RoleName,RoleActive,Notes) values('%s','%s','%s')" % (request.json['gname'],1,request.json['gnote'])
		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		id=cursor.lastrowid
		query="SELECT * From accounts_roles where RoleID=%s" % id
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE accounts_roles SET RoleName='%s', Notes='%s' Where RoleID=%s" % (request.json['gname'],request.json['gnote'],request.json['id'])
		try:
			#return query
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
		
		id=cursor.lastrowid
		query="SELECT * From accounts_roles where RoleID=%s" % request.json['id']
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)

@app.route('/jobsaccess', methods=['POST','GET'])
def JobsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM hr_jobs"

		cursor.execute(query)
		results = cursor.fetchall()
		
		db.close()

		return render_template('hr_jobs.html', jobs=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from hr_jobs where JobID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
			db.close()
			return jsonify('done')
		except:
			db.rollback()
			db.close()
			return jsonify('error')

	elif request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO hr_jobs(JobName,JobActive,Notes) values('%s','%s','%s')" % (request.json['jname'],1,request.json['jnote'])
		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		id=cursor.lastrowid
		query="SELECT * From hr_jobs where JobID=%s" % id
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE hr_jobs SET JobName='%s', Notes='%s' Where JobID=%s" % (request.json['jname'],request.json['jnote'],request.json['id'])
		try:
			#return query
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
		
		id=cursor.lastrowid
		query="SELECT * From hr_jobs where JobID=%s" % request.json['id']
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)


@app.route('/qualificationsaccess', methods=['POST','GET'])
def QualificationsAccess():
	if 'username' not in login_session or (request.args.get('state') != login_session['state'] and request.method == 'POST'):
		return redirect(url_for('userlogin'))
	if request.method == 'GET':
		state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
		login_session['state'] = state
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT * FROM  hr_qualifications"

		cursor.execute(query)
		results = cursor.fetchall()
		
		db.close()

		return render_template('hr_qualification.html', qualifications=results,STATE=state)

	if 'iddel' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="DELETE from  hr_qualifications where QualificationID=%s" % request.json['iddel']

		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
			db.close()
			return jsonify('error')
	
		db.close()
		return jsonify('done')

	elif request.json['id'] == "-1":
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "INSERT INTO hr_qualifications(QualificationName,QualificationActive,Notes) values('%s','%s','%s')" % (request.json['qname'],1,request.json['qnote'])
		try:
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
	
		id=cursor.lastrowid
		query="SELECT * From hr_qualifications where QualificationID=%s" % id
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)
	else:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "UPDATE hr_qualifications SET QualificationName='%s', Notes='%s' Where QualificationID=%s" % (request.json['qname'],request.json['qnote'],request.json['id'])
		try:
			#return query
			cursor.execute(query)
			db.commit()
		except:
			db.rollback()
		
		id=cursor.lastrowid
		query="SELECT * From hr_qualifications where QualificationID=%s" % request.json['id']
		cursor.execute(query)
		re=cursor.fetchone()
		db.close()

		return jsonify(re)

@app.route('/getcode', methods=['POST'])
def GetCode():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return redirect(url_for('userlogin'))
	if 'employee' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT EmployeeCode FROM  hr_employeesdata order by EmployeeID	DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

	
		return jsonify(results)
	elif 'member' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT MemberCode FROM  hr_membersdata order by MemberID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

	
		return jsonify(results)

	elif 'trainer' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT TrainerCode FROM  hr_trainersdata order by TrainerID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

	
		return jsonify(results)

	elif 'trainee' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query = "SELECT TraineeCode FROM  hr_traineesdata order by TraineeID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

	
		return jsonify(results)

	elif 'traininggroups' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="SELECT TrainingGroupCode FROM services_training_groups order by TrainingGroupID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

		return jsonify(results)
	elif 'trainingdays' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="SELECT TrainingDayCode FROM  services_training_days order by TrainingDayID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

		return jsonify(results)
	elif 'groupscategories' in request.json:
		db = MySQLdb.connect("localhost","root","","SAMS",use_unicode=True, charset='utf8')
		cursor = db.cursor()
		query="SELECT GroupCategoryCode FROM  services_groupscategories order by GroupCategoryID DESC limit 1"

		cursor.execute(query)
		results = cursor.fetchone()
		db.close()

		return jsonify(results)

@socketio.on('disconnect')
def disconnect_user():
    #logout_user()
    login_session.pop('username', None)
    login_session.pop('userpass', None)
    login_session.pop('role', None)
    login_session.pop('id', None)

@app.route('/logout', methods=['POST'])
def logout():
	if 'username' not in login_session or request.args.get('state') != login_session['state']:
		return jsonify('error') #render_template('index.html')
	login_session.pop('username', None)
	login_session.pop('userpass', None)
	login_session.pop('role', None)
	login_session.pop('id', None)
	return jsonify('done') #render_template('index.html')

# @app.route('/reload', methods=['GET'])
# def reload():
# 	db = MySQLdb.connect("localhost","root","","SAMS")
# 	cursor = db.cursor()
# 	query="SELECT RoleID,RoleName,Notes From accounts_roles"
# 	cursor.execute(query)
# 	re=cursor.fetchall()
# 	db.close()

# 	return jsonify(re)
if __name__ == '__main__':
	app.secret_key = os.urandom(32)
	
	#app.config['UPLOAD_FOLDER']	= '/static/assets/uimg'
	# reload(sys)
	# sys.setdefaultencoding('utf-8')
	app.debug = True
	app.run()