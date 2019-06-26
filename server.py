import socket as sk
from socket import *
import os
import sys
import hashlib
import time
import datetime

SERVER_NAME = "Atharva/0.1"

os.system('cls' if os.name == 'nt' else 'clear')
print()
print("\t\tWelcome to the Atharva/0.1 UDP File Transfer Server...")
time.sleep(0.2)
print('''
                      Atharva/0.1
        copyrights 2018 reserved by Som Durgesh Gupta''')
time.sleep(0.1)
print('''
This server is designed by Som Durgesh Gupta, Rajeshwar Rathore, Ayush Dadich from JK Lakshmipat University,
Jaipur.

Project Name: UDP File transfer system (one client at a time)
Course Code: CSE503 (Computer Networking)
Submitted to: S Taruna Mam
''')
time.sleep(0.9)
print()

# Variables used for UDP transfer
host = "" # For server ip
serverPort = 10000 # Server bind port
clientPort = 10001 # client bind port
buffer = 1024 # Buffer size of server
data = "" # Data from client
filePath = os.getcwd()+ "\\ServerFiles" # Path where files are stored
logDict = {} #log datastructure for server

#list of all commands
LIST = "LIST" # Request for list of files
FILE = "FILE" # Request for file to send
NACK = "NACK" # negative acknowledge regarding file transfer
PACK =  "PACK" # positive acnowledge regarding file transfer
CHECK = "CHECK" #sends checksum to client

#Getting ip of server
host = sk.gethostbyname(sk.gethostname())

#checking for server directory and creating it if not exist
if not os.path.exists(filePath):
    os.mkdir(filePath) #creating if not exists

#Create server socket
print("Initializing server socket...")
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((host,serverPort))

clientAddr = (host,clientPort) # Temporary saving of server address into client address

def listen():
    'Server will listen to clients and responde according to the commands'
    print("Waiting for clients on port", serverPort, " for UDP connection...")
    global clientAddr
    try:
        global clientAddr
        data,clientAddr = serverSocket.recvfrom(buffer)
    except ConnectionResetError:
        print("Client connection lost due to some reason...")
        listen() #return to listing again
    print("Connected to client - ip:", clientAddr[0], " to port ", clientAddr[1])
    data = data.decode("utf-8").strip()
    if data == LIST:
        sendList()
        listen()
    elif data[:4] == FILE:
        data = data[5:].strip()
        sendFile(filePath + "\\"+data)
        listen()
    elif data[:4] == NACK:
        print("Data has not been received by client...")
        currentTime = datetime.datetime.now()
        putToLog(currentTime.strftime("%Y-%m-%d %H:%M"), clientAddr, data[4:].strip(),"FAILED")
        #resend data to the client
        print("Resending data to the client....")
        sendFile(data[4:].strip())
        listen()
    elif data[:4] == PACK:
        print("Data has been received by client...")
        currentTime = datetime.datetime.now()
        putToLog(currentTime.strftime("%Y-%m-%d %H:%M"), clientAddr, data[4:].strip(),"SUCCESS")
        listen()
    else:
        print("Command Error from Client: ")
        listen() #listen for clients
    return

def sendList():
    'Sending list of files from the server'
    print("Reading list of files from the server database....")
    global serverSocket
    global clientAddr
    filesList = [] # list of all files on server
    
    for root, dirs, files in os.walk(filePath):
        for file in files:
            relPath = os.path.relpath(root, filePath)
            filesList.append(os.path.join(relPath,file))
            
    allFiles = ""
    # Converting list of files into long string
    for item in filesList:
        allFiles += item + "\t"

    time.sleep(1)
    # Sending list of files to the client
    print("Sending list of files to the client - ip: ",clientAddr[0], " to port ", clientAddr[1])
    serverSocket.sendto(allFiles.encode("utf-8"), clientAddr)
    print("Server sending list of files has been completed...")
    time.sleep(1)
    return

def sendFile(fileName):
    'Sending file to the client'
    #read data from file in byte format
    #checking if file is exist or not!
    global serverSocket
    global clientAddr
    if not os.path.exists(fileName):
        global clientAddr
        print("Wrong file requested by client...")
        serverSocket.sendto("Wrong file requested.".encode("utf-8"), clientAddr)
        return
    print("Making checksum for file (md5)...")
    checkSum = hashlib.md5(open(fileName,"rb").read()).hexdigest()
    print("checksum complete.")
    time.sleep(0.5)
    print("Reading file data and sending it to the client....")
    file = open(fileName, "rb")
    print("Sending checksum to the client...")
    checkSum = CHECK + " " + checkSum
    serverSocket.sendto(checkSum.encode("utf-8"), clientAddr)
    print("chcksum has been sent to client - ip: ", clientAddr[0], " to port ", clientAddr[1])
    print("Sending file in Synchronous mode...")
    fileSize = int(os.path.getsize(fileName))
    count = int(fileSize/buffer)+1
    print(fileSize)
    print("Sending file", fileName, " to the client...." )
    time.sleep(0.5)
    while(count != 0) :
        fileData = file.read(buffer)
        serverSocket.sendto(fileData, clientAddr)
        time.sleep(0.02)
        count -= 1
    print("File has been sent to client")
    print()
    file.close() #closing file after sending the file
    time.sleep(0.5)

def putToLog(curDTime, cAddr, fName, message):
    "Save log on the server for file transfer"
    print("Managing log manager of server....")
    global logDict
    tempList = [cAddr,fName, message]
    logDict[curDTime] = tempList #saving in log of server
    print(logDict)


#///////////////////////////////////////SERVER START////////////////////////////////  
listen() #LISTEN TO CLIENT
