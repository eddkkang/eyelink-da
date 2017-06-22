# SERVER
import socket
import json

#HOST='192.168.10.27' 
HOST = 'localhost'
PORT=5229 #포트지정

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind((HOST,PORT))

s.listen(1) #접속이 있을때까지 기다림

print('The server is ready to receive')

while 1:
	conn, addr=s.accept() #접속 승인
	print('accepted connection')

	data=conn.recv(1024)
	dict = json.loads(data.decode("utf-8"))

	print("data:" + data.decode("utf-8"))
	print(dict['start_date'])

	if not data: break

	conn.send(data) #받은 데이터를 그대로 클라이언트에 전송

conn.close()
