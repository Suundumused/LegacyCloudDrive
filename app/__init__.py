import asyncio
import socket

from flask import *
from fileinput import filename
from waitress import serve
 #stores the users id and their currently accessed folders on the server. Prevents conflicts when many people access.

import zipfile
import pyzipper

import random
import re
import io
import json
import contextlib
import threading
import argparse
import os
import sys

if getattr(sys, 'frozen', False):  #-----ATUALIZADO-----
    # Executando como executable (PyInstaller)
    path = os.path.dirname(sys.executable)
else:   
    # Executando como  script .py
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

sys.path.insert(1, os.path.join(path))

from Users import Data

import ReadWrite #Used to process per-user read data.
import uuid
import shutil

class settings: #load config file (config.json).
    def read_json_file(filename):
        return ReadWrite.settings.read_json_file(filename)
            
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
        return ReadWrite.protection.zip_file_with_password(source_file, zip_filename, password)

    def antiescape(Paths): #Protect folders before the target folder from being accessed via escape parameters.
        return ReadWrite.protection.antiescape(Paths)

class program:
    async def StartServer():
        path = ""
        
        if getattr(sys, 'frozen', False):  #-----ATUALIZADO-----
        # Executando como executable (PyInstaller)
            path = os.path.dirname(sys.executable)
        else:   
            # Executando como  script .py
            path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        config_name = 'config'
        
        ConfigFolder = os.path.join(path, config_name)
        ConfigPath = ConfigFolder + r"\\" + "config.json"
        
        config_name2 = 'templates'
        
        template_folder1 = os.path.join(path, config_name2)
        
        config_name3 = 'static'
        
        static_folder = os.path.join(path, config_name3)
            
        app = Flask(__name__, template_folder=template_folder1)

        app.secret_key = settings.read_json_file(ConfigPath)["KEY"] #Key used to generate users id.
        
        #### "BROWSER BASED TRAVEL"###

        @app.route("/", methods=['GET'])
        async def main_home():
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
        async def home():
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
        async def root():
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
                        return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route("/download", methods=['GET'])
        async def download():
            if request.method == 'GET':

                user_id = user.VMKUser()

                ReadWrite.program.TargetUserID = user_id
                
                randomFileSeed = random.randint(0,999)

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

                        protection.zip_file_with_password(file_path, ReadWrite.program.TargetPath+ReadWrite.program.CPath+r"\\"+os.path.splitext(filename)[0] + str(randomFileSeed)+".zip", user_id) #convert it to zip before the download.

                        new_file_path=ReadWrite.program.TargetPath+ReadWrite.program.CPath + r"\\" + str(os.path.splitext(filename)[0] + str(randomFileSeed) + ".zip")

                        trash.PendingFilesToDelete.append(new_file_path) #add the zipfile to pending destroy.

                        return send_file(new_file_path, as_attachment=True) #set zipfile to download.

                except Exception as e:
                    return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route('/upload', methods=['POST']) #upload file to current user's_joined_folder.
        async def upload():
            if request.method == 'POST':
                user_id = user.VMKUser()

                ReadWrite.program.TargetUserID = user_id

                if request.method == 'POST':
                    # Check if the POST request has a file part
                    if 'file' not in request.files:
                        return render_template("index.html", ListFiles=["No file path"], CPath=ReadWrite.program.CPath, user_id=user_id)

                    file = request.files['file']
                    
                    if protection.antiescape(file.filename) == True:
                        return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
                    
                    else:
                        # If the user does not select a file, the browser submits an empty part without filename
                        if file.filename == '':
                            return render_template("index.html", ListFiles=["No selected file"], CPath=ReadWrite.program.CPath, user_id=user_id)
                        # If the file exists and is valid, save it to a designated folder (e.g., 'uploads')
                        
                        for value in trash.PendingFilesToDelete:
                            try:
                                os.remove(value)

                            except:
                                pass

                            finally: #Removes pending generated zip files for download.
                                trash.PendingFilesToDelete.remove(value)

                        if file:
                            try:
                                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath
                                
                                file.save(os.path.join(file_path, file.filename))
                                
                                filename = os.path.basename(file_path+ r"\\" + file.filename)
                                                            
                                protection.zip_file_with_password(file_path + r"\\" + file.filename, file_path+r"\\"+os.path.splitext(filename)[0]+".zip", user_id) #After uploading, delta the original file leaving only the generated .zip.
                                
                                old_file_path = file_path+ r"\\" + file.filename
                                
                                trash.PendingFilesToDelete.append(old_file_path)
                                
                                for value in trash.PendingFilesToDelete:
                                    try:
                                        os.remove(value)

                                    except:
                                        pass

                                    finally: #Removes pending generated zip files for download.
                                        trash.PendingFilesToDelete.remove(value)

                                return redirect("/refresh")

                            except Exception as e:
                                return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route('/mkdir', methods=['POST']) #create folder.
        async def mkdir():
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
                        return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route("/delete", methods=['DELETE']) #delete folder of file.
        async def delete():
            if request.method == 'DELETE':
                user_id = user.VMKUser()

                data = request.get_json()

                File = data.get('File')
                isfolder = data.get('isfolder')

                ReadWrite.program.TargetUserID = user_id
                
                if protection.antiescape(File) == True:
                    return render_template("index.html", ListFiles=["Access violation."], CPath=ReadWrite.program.CPath, user_id=user_id)
                
                else:
                    try: #Try deleting folder as folder, if not try as file.
                        if bool(isfolder) == True:
                            try:
                                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath

                                shutil.rmtree(file_path)

                                return redirect("/refresh")
                            
                            except:
                                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath
                                # Deleta o arquivo da máquina do hospedeiro
                                os.remove(file_path)

                                return redirect("/refresh")
                            
                        else: #Try deleting file as file, if not try as folder.
                            try: 
                                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath + r"\\"+ File
                                # Deleta o arquivo da máquina do hospedeiro
                                os.remove(file_path)

                                return redirect("/refresh")
                            
                            except:
                                file_path = ReadWrite.program.TargetPath+ReadWrite.program.CPath + r"\\"+ File

                                shutil.rmtree(file_path)

                                return redirect("/refresh")
                                
                    except OSError as e:
                        # Trata caso ocorra algum erro ao deletar o arquivo
                        return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET', 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route("/rename", methods=['POST']) #rename files or folders.
        async def rename():
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
                        return render_template("index.html", ListFiles=[repr(e)], CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'GET, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route("/return", methods=['GET'])
        async def back():
            if request.method == 'GET':
                user_id = user.VMKUser()

                ReadWrite.program.TargetUserID = user_id

                return render_template("index.html", ListFiles=ReadWrite.program.backone(), CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        @app.route("/refresh", methods=['GET'])
        async def refresh():
            if request.method == 'GET':
                user_id = user.VMKUser()

                ReadWrite.program.TargetUserID = user_id

                return render_template("index.html", ListFiles=ReadWrite.program.refresh(), CPath=ReadWrite.program.CPath, user_id=user_id)

            else:
                return render_template("index.html", ListFiles=ReadWrite.program.listdir("Wrong methods: 'POST, PULL, PATCH'"), CPath=ReadWrite.program.CPath, user_id=user_id)

        
        parser = argparse.ArgumentParser(
            description='My CloudDrive Server',
            epilog="Started!")
        
        parser.add_argument("-ip","--host", help="Set/Get Local IPV4, default = '0.0.0.0'", type=str, default="0.0.0.0")#criar argumento
        parser.add_argument("-p","--port", help="Set Port Forwarding, default = 80", type=int, default=80)
        
        args = parser.parse_args()
        
        if args.host == "0.0.0.0":
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('10.255.255.255', 1))
                
                IP = s.getsockname()[0]
            except:
                IP = '127.0.0.1'
            
            print(f"Server running Forwarded at: {IP}:" + str(args.port))
        
        else:
            print("Server running at: " + str(args.host) + ":" + str(args.port))
        
        try:
            #app.run(debug=True, threaded=True, port=args.port) #development only.
            serve(app, host=args.host, port=args.port)
            
        except Exception as e:
            print(repr(e))
            
class ServerMaster:
    def __init__(self):
        asyncio.run(program.StartServer())

if __name__ == "__main__":
    thread = threading.Thread(target=ServerMaster)
    thread.start()
    thread.join()