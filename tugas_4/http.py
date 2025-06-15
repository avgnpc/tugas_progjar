import sys
import os
import os.path
import uuid
from glob import glob
from datetime import datetime
import base64

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.types={}
		self.types['.pdf']='application/pdf'
		self.types['.jpg']='image/jpeg'
		self.types['.jpeg']='image/jpeg'
		self.types['.png']='image/png'
		self.types['.txt']='text/plain'
		self.types['.html']='text/html'

	def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")

		response_headers=''
		for i in resp:
			response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
		if (type(messagebody) is not bytes):
			messagebody = messagebody.encode()

		response = response_headers.encode() + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		requests = data.split("\r\n")
		baris = requests[0]
		all_headers = [n for n in requests[1:] if n!='']

		j = baris.split(" ")
		try:
			method=j[0].upper().strip()
			if (method=='GET'):
				object_address = j[1].strip()
				return self.http_get(object_address, all_headers)
			if (method=='POST'):
				object_address = j[1].strip()
				body = requests[-1] if len(requests) > 2 else ""
				return self.http_post(object_address, all_headers, body)
			if (method=='DELETE'):
				object_address = j[1].strip()
				return self.http_delete(object_address, all_headers)
			else:
				return self.response(400,'Bad Request','',{})
		except IndexError:
			return self.response(400,'Bad Request','',{})

	def http_get(self,object_address,headers):
		files = glob('./**/*', recursive=True)
		thedir='./'
		if (object_address == '/'):
			return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

		if (object_address == '/video'):
			return self.response(302,'Found','',dict(location='https://youtu.be/katoxpnTf04'))
		if (object_address == '/santai'):
			return self.response(200,'OK','santai saja',dict())

		if (object_address == '/list'):
			filelist = [f[2:] for f in files if os.path.isfile(f)]
			isi = "\n".join(filelist)
			return self.response(200,'OK',isi,{'Content-type':'text/plain'})

		object_address=object_address[1:]
		if thedir+object_address not in files:
			return self.response(404,'Not Found','',{})
		fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
		isi = fp.read()
		fext = os.path.splitext(thedir+object_address)[1]
		content_type = self.types.get(fext, 'application/octet-stream')
		headers={}
		headers['Content-type']=content_type
		return self.response(200,'OK',isi,headers)

	def http_post(self,object_address,headers,body):
		if not object_address.startswith('/upload/'):
			return self.response(400, 'Bad Request', 'Gunakan /upload/<nama.file>', {})
		filename = object_address[len('/upload/'):]
		try:
			with open(filename, 'wb') as f:
				f.write(base64.b64decode(body))
			header = {'Content-type': 'text/plain'}
			return self.response(200, 'OK', f'Upload berhasil: {filename}', header)
		except Exception as e:
			return self.response(500, 'Internal Server Error', str(e), {})

	def http_delete(self, object_address, headers):
		filename = object_address[1:]
		if not os.path.isfile(filename):
			return self.response(404, 'Not Found', 'File tidak ditemukan', {})
		try:
			os.remove(filename)
			return self.response(200, 'OK', f'File {filename} dihapus', {})
		except Exception as e:
			return self.response(500, 'Internal Server Error', str(e), {})

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET /list HTTP/1.0\r\n\r\n')
	print(d.decode())

