from flask import Flask, jsonify, request
from uptime import uptime
from datetime import timedelta
from services import TZ_Bomber
from random import randint
from flask_cors import CORS

count=193827
all_task={}
app = Flask(__name__)
CORS(app)

def add_task(mobile, amount, unlimited):
	global count
	rand_num=randint(22, 52)
	count+=rand_num
	id=count
	all_task[id]=TZ_Bomber(mobile, amount, unlimited)
	all_task[id].start()
	return id

@app.route('/', methods=["GET", "POST"])
def index():
	sys_up=timedelta(seconds=int(uptime()))
	return f"<h3>System Uptime {sys_up} seconds</h3><p>v1.8</p>"

@app.route("/api/add", methods=["POST"])
def add():
	mobile=int(request.form.get('mob'))
	amount=int(request.form.get('amount'))
	unlimited=True if request.form.get('unlimited')=='true' else False
	success=False
	task_id=None
	if len(str(mobile))!=10:
		msg="Invalid Mobile Number"
	elif amount<1:
		msg="Amount must be greater than zero(0)"
	elif str(mobile)[0]!='1':
		msg="Only Bangladeshi Numbers are allowed"
	elif amount>300:
		msg="Amount is too long. Try to lower it than 300"
	else:
		task_id=add_task(mobile, amount, unlimited)
		success=True
		msg="Number successfully added"

	return jsonify({"success":success, "msg":msg, "id":task_id})

@app.route("/api/status", methods=["POST"])
def status():
	task_id=int(request.form.get("task_id"))
	success=False
	task=all_task.get(task_id)
	if not task:
		msg="Invalid Task ID, Thread Could Not Found"
	else:
		success=True
		msg={'mobile':task.mobile,'amount':task.amount,'unlimited':task.unlimited,'attempt':task.attempt,'sent':task.sent,'failed':task.failed,'run':task.run,'completed':task.completed,'remaining':task.remaining,'progress':task.progress}

	return jsonify({"success":success, "msg":msg})
		
@app.route("/api/delete", methods=["POST"])
def delete():
	task_id=int(request.form.get("task_id"))
	success=False
	task=all_task.get(task_id)
	if not task:
		msg="Invalid Task ID, Thread Could Not Found"
	elif not task.run:
		msg='Thread already stopped'
	else:
		task.stop()
		success=True
		msg='Thread Requested to be Stopped'

	return jsonify({"success":success, "msg":msg})
	
if __name__=='__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
