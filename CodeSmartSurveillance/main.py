# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request, session, Response, send_file, after_this_request, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd
from datetime import datetime
import os
import json
from fall import *
from detection_status import detection_tracker
import cv2
import base64

name = ''

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('video'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')


@app.route('/video', methods=['GET', 'POST'])
def video():
	global name
	return render_template('video.html',name=name)



# Flask Routes
@app.route('/video_stream')
def video_stream():
    return Response(
        video_feed('f:/BEproject/XYZ/AE242_SmartSurveillance/fallingvideo.mp4'),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/take_screenshot', methods=['POST'])
def take_screenshot():
    try:
        frame = get_current_frame()  # You'll need to implement this in fall.py
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        
        detection_tracker.add_activity("Screenshot", f"Screenshot saved as {filename}")
        return jsonify({"status": "success", "filename": filename})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    if 'activity' in data:
        detection_tracker.add_activity(data['type'], data['activity'])
    return jsonify(detection_tracker.get_status())

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(debug=False, threaded=True)
