#!/usr/bin/env python3
from multiprocessing.sharedctypes import Value
import re
import socketserver
from traceback import print_tb
from urllib import request, response
import os
import json

"""
Written by: Raymon Skjørten Hansen
Email: raymon.s.hansen@uit.no
Course: INF-2300 - Networking
UiT - The Arctic University of Norway
May 9th, 2019
"""

class MyTCPHandler(socketserver.StreamRequestHandler):    
    """
    This class is responsible for handling a request. The whole class is
    handed over as a parameter to the server instance so that it is capable
    of processing request. The server will use the handle-method to do this.
    It is instantiated once for each request!
    Since it inherits from the StreamRequestHandler class, it has two very
    usefull attributes you can use:

    rfile - This is the whole content of the request, displayed as a python
    file-like object. This means we can do readline(), readlines() on it!

    wfile - This is a file-like object which represents the response. We can
    write to it with write(). When we do wfile.close(), the response is
    automatically sent.

    The class has three important methods:
    handle() - is called to handle each request.
    setup() - Does nothing by default, but can be used to do any initial
    tasks before handling a request. Is automatically called before handle().
    finish() - Does nothing by default, but is called after handle() to do any
    necessary clean up after a request is handled.
    """
    def handle(self):
        """
        Handles a HTTP-request.\n
        A request is parsed then sent to it's respective method to get handled
        """

        #Read request and place variables in dictionary for further use
        request_dict = self.read_request()

        #Check for directory traversal attack
        TraversalAttackString = "../"
        if(TraversalAttackString in request_dict["file-name"]):
            self.WriteHeader(403, 0, b"", b"")
        
        #Handle the request
        elif(request_dict["method"]) == "get":
            self.GET(request_dict["file-name"])

        elif(request_dict["method"]) == "post":
            self.POST(request_dict["file-name"], request_dict["body"].encode("utf-8"), request_dict["content-length"], request_dict["content-type"].encode("utf-8"))
        
        elif(request_dict["method"] == "put"):
            self.PUT(request_dict["file-name"], request_dict["body"].encode("utf-8"), request_dict["content-length"], request_dict["content-type"].encode("utf-8"))
        
        elif(request_dict["method"] == "delete"):
            self.DELETE(request_dict["file-name"])


    def read_request(self):
        """
        Returns a dictionary with the following keys:\n
        ["method"], ["file-name"], ["version"], ["content-length"], ["content-type"], ["body"]
        """

        request_dict = {}

        while(True):
            #Read the current line (this will iterate through all lines in request)
            byte_line = self.rfile.readline()
            
            #Decode from byte to string
            string_line = byte_line.decode()

            #Make string to lowercase
            string_line = string_line.lower()
            
            #Place status-line, headers and body in dictionary
            if(string_line.startswith("get")):
                met_code_ver = string_line.split(" ")
                request_dict["method"] = "get"              #Method
                request_dict["file-name"] = met_code_ver[1] #FilePathName                
                request_dict["version"] = met_code_ver[2]   #version
            
            #Check status-line
            if(string_line.startswith("post")):
                met_code_ver = string_line.split(" ")
                request_dict["method"] = "post"             #Method
                request_dict["file-name"] = met_code_ver[1] #FilePathName
                request_dict["file-name"] = request_dict["file-name"].replace("/", "")
                request_dict["version"] = met_code_ver[2]   #version

            #Check status-line
            if(string_line.startswith("put")):
                met_code_ver = string_line.split(" ")
                request_dict["method"] = "put"              #Method
                request_dict["file-name"] = met_code_ver[1] #FilePathNamelsee                
                request_dict["version"] = met_code_ver[2]   #version

            
            #Check status-line
            if(string_line.startswith("delete")):
                met_code_ver = string_line.split(" ")
                request_dict["method"] = "delete"           #Method
                request_dict["file-name"] = met_code_ver[1] #FilePathName                
                request_dict["version"] = met_code_ver[2]   #version

            #Check content-length
            if(string_line.startswith("content-length:")):
                value = string_line[15:]
                value = int(value)
                request_dict["content-length"] = value

            #Check content-type
            if(string_line.startswith("content-type:")):                
                content_type = string_line[14:]
                content_type = content_type[:-2]
                request_dict["content-type"] = content_type


            #Check blank line
            if(byte_line == b"\r\n"):

                #Read body IF "POST" or "PUT" function is called
                if(request_dict["method"] == "post" or request_dict["method"] == "put"):
                    body = self.rfile.read(int(request_dict["content-length"])).decode()
                    request_dict["body"] = body

                #Reached the end of file
                break
            
        return request_dict


    def DoesFileExist(self, FilePathName):
        """
        Returns TRUE if the file exists\n
        Return FALSE if the file does NOT exist
        """
        return os.path.exists(FilePathName)


    def WriteHeader(self, status_code:int, content_length:int, content_type:bytes, body:bytes):
        """Writes response header"""

        #Write status line
        if(status_code == 200):
            self.wfile.write(b"HTTP/1.1 200 - OK\r\n")
        if(status_code == 201):
            self.wfile.write(b"HTTP/1.1 201 - Created\r\n")
        if(status_code == 304):
            self.wfile.write(b"HTTP/1.1 304 - Not Modified\r\n")
        if(status_code == 403):
            self.wfile.write(b"HTTP/1.1 403 - Forbidden\r\n")
        if(status_code == 404):
            self.wfile.write(b"HTTP/1.1 404 - Not Found\r\n")
        if(status_code == 406):
            self.wfile.write(b"HTTP/1.1 404 - Not Acceptable\r\n")
        
        #Write Content-Length
        content = bytes(str(len(body)),encoding="utf-8")
        self.wfile.write(b"Content-Length: " + content + b"\r\n")

        #Write Content-type
        self.wfile.write(b"Content-Type: " + content_type + b"\r\n")

        #Close connection
        self.wfile.write(b"Connection: Close\r\n")

        #Write blank line before entity body
        self.wfile.write(b"\r\n")

        #Write entity body
        self.wfile.write(body)


    def GET(self, file_name:str):  
        """
        *Returns 1 if file exists and response is written succesfully\n
        *Returns 0 if file does not exist and bad response is written
        """
        #If "/messages" is requested, return list/json-file
        if(file_name == "/messages" or file_name == "messages.json"):
            if(self.DoesFileExist(file_name) == False):
                file = open("messages.json", "rb")                              #Open file
                body = file.read()                                              #Read file
                content_length = len(body)                                      #Fetch length of file
                self.WriteHeader(200, content_length, b"text.json", body)       #Write status line, headers and body
                return 1                                                        #Return successful
                
            else:
                print("ERROR: File does not exist...")
                self.WriteHeader(404, 0, b"", b"")                              #Write status line, headers and body
                return 0

        #Requested file DOES exist
        elif(self.DoesFileExist(file_name) == True):

            #If user is allowed to access given file
            if(file_name != "server.py"): 
                if(file_name == "/"):
                    file = open("index.html", "rb")                         #Open file
                    body = file.read()                                      #Read file
                    self.WriteHeader(200, len(body), b"text/html", body)    #Write status line, headers and body
                    file.close()                                            #Close file
                    return 1                                                #Return successful
                
                else:
                    file = open(file_name, "rb")                            #Open file 
                    body = file.read()                                      #Read file
                    self.WriteHeader(200, len(body), "text/html", body)     #Write status line, headers and body
                    file.close()                                            #Close file
                    return 1                                                #Return successful
            
            #If user is NOT allowed to open file
            else:
                self.WriteHeader(403, 0, b"", b"")                          #Write status line, headers and body
                return 0                                                    #Return not successful

        #File does NOT exist
        elif(self.DoesFileExist(file_name) == False):
            self.WriteHeader(404, 0, b"", b"")                              #Write status line, headers and body
            return 0                                                        #Return not successful
        

    def POST(self, file_name:str, body:bytes, body_length:int, content_type:bytes):
        """
        Creates a new file with the given "file_name", IF another file does not already exist\n
        Writes headers and appends "body" to the new created file
        """
        #If file already exists
        if(self.DoesFileExist(file_name) == True):
            #If file is of type ".json"
            if(".json" in file_name):
                #Open file_name
                with open(file_name) as file:
                    list_data = json.load(file)                                     #Load content of file_name into data
                    #If there is no content in given file
                    if(len(list_data) == 0):
                        content = {"id": 1, "text": body.decode("utf-8")}           #Create content to be written to file
                        list_data.append(content)                                   #Append content to list_data

                    #If there is content in given file
                    else:
                        content = {"id": len(list_data)+1, "text": body.decode("utf-8")}
                        list_data.append(content)                                   #Append content to list_data

                #Close file
                file.close()

                #Open file_name in "write" mode and replace list_data
                with open(file_name, "a") as file:
                    json.dump(list_data, file)
                    file.close()
                    self.WriteHeader(200, 0, b"", b"")


        
        #File does not exist, create new one...
        elif(self.DoesFileExist(file_name) == False):
            #If file is of type ".json"
            if(".json" in file_name):
                new_file = open(file_name, "w")                                         #Create new file
                content = {"id": 1, "text": body.decode()}                              #Make dictionary with content 
                json_list = []                                                          #Create list
                json_list.append(content)                                               #Append dictionary to list
                json.dump(json_list, new_file)                                          #Write list to file
                self.WriteHeader(201, len(json_list), b"list", b"")                     #Write response header
                new_file.close()                                                        #Close file
            
            #If file is not of type ".json"
            else:
                new_file = open(file_name, "wb")                                        #Create new file
                new_file.write(body)                                                    #Write body to new file
                new_file.close()                                                        #Close file
                
                #ReOpen file to write correct response body
                file = open(file_name, "rb")                                            #Open file
                response_body = file.read()                                             #Read content of file
                self.WriteHeader(201, len(response_body), content_type, response_body)  #Write response header


    def PUT(self, file_name:str, body:bytes, body_length:int, content_type:bytes):        
        """
        Replaces a message in a ".json" file based on an id
        """
        #If file exists
        if(self.DoesFileExist(file_name) == False):
            #Open file_name
            with open(file_name) as file:
                list_data = json.load(file)                                     #Load content of file_name into data

                #If there is no content in given file
                if(len(list_data) == 0):
                    print("ERROR: Can not replace text in file. The file is empty")
                    self.WriteHeader(304, 0, b"", b"")

                #If there is content in given file
                else:
                    id_input = input("Enter ID to replace: ")                   #Fetch which message id to replace
                
                    #Search for ID in content of file_name
                    for i in range(len(list_data)):
                        if(list_data[i]["id"] == int(id_input)):                #Found match
                            list_data[i]["text"] = body.decode("utf-8")         #Replace data
                            break                                               #Break out of loop
                
                #Close file
                file.close()

            #Open file_name in "write" mode and replace list_data
            with open(file_name, "w") as file:
                json.dump(list_data, file)
                file.close()
                self.WriteHeader(200, 0, b"", b"")
        
        #File does not exist
        else:
            print("ERROR, PUT.... file does not exist")
            self.WriteHeader(404, 0, b"", b"")


    def DELETE(self, file_name:str):
        """
        Deletes a specified message from file
        """

        #If file exists
        if(self.DoesFileExist(file_name) == True):
            id_input = input("Enter ID to delete: ") #Fetch which message ID to delete
            #Open file
            with open(file_name) as file:
                list_data = json.load(file)                                     #Load content of file into list

                #Search for ID in data from file
                for i in range(len(list_data)):
                    if(list_data[i]["id"] == int(id_input)):                    #Found match
                        del list_data[i]                                        #Delete match
                        file.close()                                            #Close file
                        break                                                   #Break out of loop
                
            #Opening file_name in "write" mode and overwrite with data
            with open(file_name, "w") as file:                 
                json.dump(list_data, file)                                      #Overwrite content in file with new content
                file.close()                                                    #Close file
                self.WriteHeader(200, 0, b"", b"")                              #Write OK header
                
        #File does NOT exist...
        else:
            print("ERROR: Can not DELETE from file, it does NOT exist...\n")
            self.WriteHeader(404, 0, b"", b"")

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080  #0.0.0.0, 80
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()