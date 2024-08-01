#  HTTP server

#To run the server, type the following in the terminal and go to http://localhost:8080.
python3 server.py

#To run the pre-implemented tests type the following:
python3 test_client.py 

#To run the RESTful API implementation type the following:
python3 RESTfulAPI_tests.py

#When running "RESTfulAPI_tests.py" you can input the following methods: get, post, put, delete and quit(quit the program)

#The methods will perform different actions on files that already exists or files that you create in the program. 

#Explanation of the methods:
	GET: fetch information from a .json file and print it to the terminal
	POST: create a new .json file or append to one that already exists
	PUT: Replace a message in a .json file based on an ID
	DELETE: Delete a message from a .json file 
