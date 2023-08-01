import threading
import os
import sys
import contextlib
import json
import io

from Users import Data #stores the users id and their currently accessed folders on the server. Prevents conflicts when many people access.

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

class program:
    
    ConfigFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    ConfigPath = ConfigFolder + r"\\" + "config.json"
    
    TargetUserOrderID=0
    TargetUserID=''
    
    TargetPath = settings.read_json_file(ConfigPath)["Target_Path"] #Users cannot return from this folder.
    CPath = TargetPath
    List = []
    
    def __init__(self):
        pass
    
    def loadFromCurrentUser(): #Loads the user's current folder via id, when the user interacts with the server.                    
        for index, item in enumerate(Data):
            if item[0]==program.TargetUserID:
                program.TargetUserOrderID=index
                break
            
        program.CPath=Data[program.TargetUserOrderID][1]
                
        
    def saveToCurrentUser(): #Saves changes to user ID when interaction ends.
        Data[program.TargetUserOrderID][1]=program.CPath    

    def backone():
        
        program.loadFromCurrentUser() #load from user_id data for each interaction
        
        index = program.CPath.rfind("\\")
        program.CPath = program.CPath[:index]

        try:
            program.List = (os.listdir(program.TargetPath+"\\"+program.CPath))

            return program.List

        except Exception as e:
            return [str(e)]
        
        finally:
            program.saveToCurrentUser() #save to user_id for each interaction.
    
    def refresh():
        
        program.loadFromCurrentUser()

        try:
            program.List = (os.listdir(program.TargetPath+"\\"+program.CPath)) #lists the files and folders that will be displayed in the HTML page.

            return program.List

        except Exception as e:
            return [str(e)]
        
        finally:
            program.saveToCurrentUser()

    def listdir(SelectedFolder):
                
        program.loadFromCurrentUser()
        
        try:
            program.List = (os.listdir(program.TargetPath+"\\"+program.CPath+"\\"+SelectedFolder))
            program.CPath = program.CPath+"\\"+SelectedFolder

            return program.List #lists the files and folders that will be displayed in the HTML page.
        
        except Exception as e:
            
            program.CPath = program.CPath+"\\"+SelectedFolder
            
            return [str(e)]

        finally:
            program.saveToCurrentUser()