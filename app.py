from flask import Flask, request, render_template, send_file
from flask_restful import Resource, Api
from flask_cors import CORS
import mysql.connector
import json

app = Flask(__name__)
CORS(app)
api = Api(app)

# Connect to the MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="database"
)
cursor = conn.cursor()
cursor.execute('set global max_allowed_packet=1048576000;')

class Signup(Resource):
    def post(self):
        # Get the request data
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        # Check if the email already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            return {"message": "Email already exists"}, 400

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        return {"message": "Signup successful"}, 201

class Login(Resource):
    def post(self):
        # Get the request data
        print("Login")
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        # Check if the email and password match
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        result = cursor.fetchone()
        if not result:
            return {"message": "Email and password do not match"}, 401

        return {"message": "Login successful1"}, 201

class SendFile(Resource):
    def post(self):
        # Get the request data
        print("start")
        form_data = request.form
        file = request.files.get("file")
        sender = form_data.get("sender")
        print(sender)
        receiver = form_data.get("receiver")

        # Check if the receiver exists

        cursor.execute("SELECT * FROM users WHERE email = %s", (receiver,))
        result = cursor.fetchone()
        if not result:
            print("Not found")
            return {"message": "Receiver not found"}, 400

        # Store the file in the receiver's database
        filename = file.filename
        file_data = file.read()
        cursor.execute("INSERT INTO files (email, filename, data, sender) VALUES (%s, %s, %s, %s)", (receiver, filename, file_data, sender))
        print("File Sent")
        conn.commit()
        return {"message": "File sent successfully"}, 200

class GetFiles(Resource):
    def post(self):
        # Get the request data
        data = request.get_json()
        email = data["email"]
        # Get the files associated with the email
        cursor.execute("SELECT * FROM files WHERE email = %s", (email,))
        result = cursor.fetchall()
        # Return the files in JSON format
        if result:
            files = []
            for file in result:
                files.append({"id": file[0], "sender" : file[4], "filename" : file[2]})
            json_data = json.dumps(files)
            return json_data, 200
        else:
            return {"message": "No files found for this user"}, 400

class DownloadFile(Resource):
    def get(self, file_id):
        # Get the file from the database using the file id
        cursor.execute("SELECT * FROM files WHERE id = %s", (file_id,))
        result = cursor.fetchone()
        if not result:
            return {"message": "File not found"}, 400
        
        # Send the file data to the client
        filename = result[2]
        file_data = result[3]
        with open("temp", 'wb') as outfile:
            outfile.write(file_data)
        return send_file("./temp", download_name=filename, as_attachment=True)

class DeleteFile(Resource):
    def post(self, file_id):
        # Delete the file from the database using the file id
        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        conn.commit()
        return {"message": "File Deleted successfully"}, 200




api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(SendFile, "/sendfile")
api.add_resource(GetFiles, "/getfiles")
api.add_resource(DownloadFile, "/download/<file_id>")
api.add_resource(DeleteFile, "/delete/<file_id>")

@app.route("/")
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
