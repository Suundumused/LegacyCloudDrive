from flask import *
from fileinput import filename
from waitress import serve
from Users import Data #stores the users id and their currently accessed folders on the server. Prevents conflicts when many people access.

import zipfile
import pyzipper

import re
import io
import json
import contextlib
import threading
import os
import sys
import ReadWrite #Used to process per-user read data.
import uuid
import shutil

class settings: #load config file (config.json).
    def read_json_file(filename):
        try:
            if not os.path.exists(filename):
                
                default_data={"KEY": "KSDJG43298Y543298TREKKJASYJR32459U432JREWNGM", "Target_Path": "C:\Users"}
                
                with contextlib.ExitStack() as stack:
                    file = stack.enter_context(open(filename, mode='w', encoding='utf-8', errors='ignore'))
                    json.dump(default_data, file, indent=4)
                                        
                return default_data
            
            else:
                with contextlib.ExitStack() as stack:
                    file = stack.enter_context(io.open(filename, mode='r', encoding='utf-8', errors='ignore'))
                    data = json.load(file)
                                        
                return data
            
        except Exception as e:
            default_data={"KEY": "KSDJG43298Y543298TREKKJASYJR32459U432JREWNGM", "Target_Path": "C:\Users"}
            
            print (e)
            
            return default_data
            
# Function to write JSON data to a file

class trash:
    PendingFilesToDelete = []

class user:
    UserFound = False

    def VMKUser():
        user.UserFound = False

        if 'user_id' not in session: #registers the user with the ID if not already.
            # If the 'user_id' key is not present in the session, generate a new ID
            session['user_id'] = str(uuid.uuid4())

            Data.append([session['user_id'], ""]) #add new user_id to list of users.

            return session['user_id']

        else:
            user_id = session.get('user_id')

            for x in Data: #if user exists but not sorted, add to list
                if x[0] == user_id:
                    user.UserFound = True
                    break

            if user.UserFound == False:
                Data.append([user_id, ""])

            return user_id


class protection: #It reduces the risk of data leakage by 50%, compressing the zip file with the password being the user id.
    def zip_file_with_password(source_file, zip_filename, password):
        try:
            # Read the contents of the source file
            with open(source_file, 'rb') as file:
                data = file.read()

            filename = os.path.basename(source_file)

        # Create a new zip file and encrypt it with a password
            with pyzipper.AESZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9, encryption=pyzipper.WZ_AES) as zf:
                password = password.encode("utf-8")
                zf.setpassword(password)

            # Add the source file to the zip file
                zf.writestr(filename, data)

        except Exception as e:
            print(e)

    def antiescape(Paths): #Protect folders before the target folder from being accessed via escape parameters.
        Filter = [r"cd", r"../", r"./", r".\\", r"..\\", r"~", r"..", r"cd..",
                  r"cd /", r"cd/", r"cd ..", r"cd.", r"cd .", r". .", r"cd \\", r"cd\\" , r"%", r"¨"]

        Found = False

        try:
            for word in Filter:
                if Paths.find(word) != -1:
                    Found = True

            if Paths.find("..\\") != -1 or Paths.find(".\\") != -1 or Found == True:
                return True

            else:
                return False

        except Exception as e:
            return True

class program:
    ConfigFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    ConfigPath = ConfigFolder + r"\\" + "config.json"
        
    template_folder1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    
    app = Flask(__name__, template_folder=template_folder1)

    app.secret_key = settings.read_json_file(ConfigPath)["KEY"] #Key used to generate users id.
    
    #### "BROWSER BASED TRAVEL"###

    @app.route("/", methods=['GET'])
    def main_home():
        if request.method == 'GET':
            user_id = user.VMKUser() #register new user with id or login old user.

            for index, item in enumerate(Data): #Clears the current folder accessed by the specific user who interacted with the server.
                if item[0] == user_id:
                    Data[index][1] = ""
                    break

            ReadWrite.program.TargetUserID = user_id #Updates current folder accessed on the server, loading user id data. Prevents conflicts when many people access.

            return render_template("index.html", ListFiles=ReadWrite.program.listdir(""), CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/host", methods=['GET'])
    def home():
        if request.method == 'GET':
            user_id = user.VMKUser()

            for index, item in enumerate(Data):
                if item[0] == user_id:
                    Data[index][1] = ""
                    break

            ReadWrite.program.TargetUserID = user_id

            return render_template("index.html", ListFiles=ReadWrite.program.listdir(""), CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/root", methods=['GET'])
    def root():
        if request.method == 'GET':

            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            Paths = request.args.get('Paths')

            if protection.antiescape(Paths) == True: #If the user tries to invade previous folders, the server interrupts access.
                return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                try:
                    return render_template("index.html", ListFiles=ReadWrite.program.listdir(Paths), CPath=ReadWrite.program.CPath, user_id=user_id) #Paths is the address of the loaded folder, ReadWrite.py returns a list of folders and files, the list is passed here to CPath in HTML.

                except Exception as e:
                    return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/download", methods=['GET'])
    def download():
        if request.method == 'GET':

            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            try: #File is the name of the selected file. the download will be the folder the current user is in + File
                File = request.args.get('File')
                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath+r"\\"+File
                filename = os.path.basename(file_path)

                if protection.antiescape(File) == True:
                    return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
                
                else:
                    for value in trash.PendingFilesToDelete:
                        try:
                            os.remove(value)

                        except:
                            pass

                        finally: #Removes pending generated zip files for download.
                            trash.PendingFilesToDelete.remove(value)

                    protection.zip_file_with_password(file_path, ReadWrite.program.TargetPath+ReadWrite.program.CPath+r"\\"+os.path.splitext(filename)[0]+".zip", user_id) #convert it to zip before the download.

                    new_file_path=ReadWrite.program.TargetPath+ReadWrite.program.CPath + r"\\" + str(os.path.splitext(filename)[0] + ".zip")

                    trash.PendingFilesToDelete.append(new_file_path) #add the zipfile to pending destroy.

                    return send_file(new_file_path, as_attachment=True) #set zipfile to download.

            except Exception as e:
                return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route('/upload', methods=['POST']) #upload file to current user's_joined_folder.
    def upload():
        if request.method == 'POST':
            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            if request.method == 'POST':
                # Check if the POST request has a file part
                if 'file' not in request.files:
                    return render_template("index.html", ListFiles=["No file part"], CPath=ReadWrite.program.CPath, user_id=user_id)

                file = request.files['file']
                
                if protection.antiescape(file.filename) == True:
                    return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
                
                else:
                    # If the user does not select a file, the browser submits an empty part without filename
                    if file.filename == '':
                        return render_template("index.html", ListFiles=["No selected file"], CPath=ReadWrite.program.CPath, user_id=user_id)
                    # If the file exists and is valid, save it to a designated folder (e.g., 'uploads')

                    if file:
                        try:
                            file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath
                            file.save(os.path.join(file_path, file.filename))

                            return redirect("/refresh")

                        except Exception as e:
                            return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route('/mkdir', methods=['POST']) #create folder.
    def mkdir():
        if request.method == 'POST':

            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            dir_name = request.form.get('dir_name')
            
            if protection.antiescape(dir_name) == True:
                return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
            
            else:
                if not dir_name:
                    return render_template("index.html", ListFiles=["Folder name is required"], CPath=ReadWrite.program.CPath, user_id=user_id)

                try:
                    file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath+r"\\"+dir_name
                    os.makedirs(file_path)

                    return redirect(str("/root?Paths=" + dir_name))

                except Exception as e:
                    return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/delete", methods=['DELETE']) #delete folder of file.
    def delete():
        if request.method == 'DELETE':
            user_id = user.VMKUser()

            data = request.get_json()

            File = data.get('File')
            isfolder = data.get('isfolder')

            ReadWrite.program.TargetUserID = user_id
            
            if protection.antiescape(File) == True:
                return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
            
            else:
                try:
                    if bool(isfolder) == True:

                        file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath

                        shutil.rmtree(file_path)

                        return redirect("/refresh")

                    else:
                        file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath+r"\\"+File
                        # Deleta o arquivo da máquina do hospedeiro
                        os.remove(file_path)

                        return redirect("/refresh")

                except OSError as e:
                    # Trata caso ocorra algum erro ao deletar o arquivo
                    return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET', 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/rename", methods=['POST']) #rename files or folders.
    def rename():
        if request.method == 'POST':
            user_id = user.VMKUser()

            data = request.get_json()

            old = data.get('old')
            File = data.get('File')
            isfolder = data.get('isfolder')

            ReadWrite.program.TargetUserID = user_id
            
            if protection.antiescape(old) == True or protection.antiescape(File) == True:
                return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
            
            else:
                try:
                    file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath

                    os.rename(file_path+r"\\" + old, file_path + r"\\" + File)

                    return redirect("/refresh")

                except OSError as e:
                    # Trata caso ocorra algum erro ao deletar o arquivo
                    return render_template("index.html", ListFiles=[str(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/return", methods=['GET'])
    def back():
        if request.method == 'GET':
            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            return render_template("index.html", ListFiles=ReadWrite.program.backone(), CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    @app.route("/refresh", methods=['GET'])
    def refresh():
        if request.method == 'GET':
            user_id = user.VMKUser()

            ReadWrite.program.TargetUserID = user_id

            return render_template("index.html", ListFiles=ReadWrite.program.refresh(), CPath=ReadWrite.program.CPath, user_id=user_id)

        else:
            return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

    #app.run(debug=True, threaded=True, port=8080)
    serve(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":

    thread = threading.Thread(target=program)

    # thread = threading.Thread(target=program.app.run(debug=False, threaded=True, host="0.0.0.0", port=8080))

    thread.start()
