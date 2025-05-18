from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from django.views import View

from cosite.settings import WOPI_FILE_DIR
from cosite.settings import BASE_DIR
import os
from pathlib import Path

User_Friendly_Name = 'default'
User_File_Dir = WOPI_FILE_DIR
User_Selected_File = ''
WOPI_Client_Host = ''

def set_User_Friendly_Name(value):
    global User_Friendly_Name
    User_Friendly_Name = value

def set_User_File_Dir(value):
    global User_File_Dir
    User_File_Dir = value

def set_User_Selected_File(value):
    global User_Selected_File
    User_Selected_File = value

def set_WOPI_Client_Host(value):
    global WOPI_Client_Host
    WOPI_Client_Host = value

def get_WOPI_Client_Host():
    global WOPI_Client_Host
    return WOPI_Client_Host

def file_reader(filename,chunk_size=512):  
    '''read file'''
    with open(filename,'rb') as f:  
        while True:  
            c=f.read(chunk_size)  
            if c:  
                yield c  
            else:  
                break  

#  wopi CheckFileInfo endpoint
#
#  Returns info about the file with the given document id.
#  The response has to be in JSON format and at a minimum it needs to include
#  the file name and the file size.
#  The CheckFileInfo wopi endpoint is triggered by a GET request at
#  https://HOSTNAME/wopi/files/<document_id>


@require_GET
def check_file_info(request, file_id):
    print(f"CheckFileInfo: file id: {file_id}, access token: {request.GET['access_token']}, user name: {User_Friendly_Name}")
    res = {
        'BaseFileName': User_Selected_File,
        'Size': 11,
        'UserId': 1,
        'UserCanWrite': True,
        'UserFriendlyName': User_Friendly_Name, 
    }
    return JsonResponse(res)


class FileContentView(View):

    #  wopi GetFile endpoint
    #
    #  Given a request access token and a document id, sends back the contents of the file.
    #  The GetFile wopi endpoint is triggered by a request with a GET verb at
    #  https://HOSTNAME/wopi/files/<document_id>/contents
    @staticmethod
    #def get(request, file_id="test.docx"):
    def get(request, file_id=User_Selected_File):
        print(f"GetFile: file id: {file_id}, access token: {request.GET['access_token']}")
        # we just return the content of a fake text file
        # in a real case you should use the file id
        # for retrieving the file from the storage and
        # send back the file content as response
        #file_path = os.path.join(WOPI_FILE_DIR, "test.docx")
        file_path = os.path.join(User_File_Dir, User_Selected_File)
        #return HttpResponse(file_path)
        return StreamingHttpResponse(file_reader(file_path))

    #  wopi PutFile endpoint
    #
    #  Given a request access token and a document id, replaces the files with the POST request body.
    #  The PutFile wopi endpoint is triggered by a request with a POST verb at
    #  https://HOSTNAME/wopi/files/<document_id>/contents
    @staticmethod
    def post(request, file_id):
        print(f"PutFile: file id: {file_id}, access token: {request.GET['access_token']}")
        if not request.body:
            return HttpResponseNotFound('Not possible to get the file content.')
        content = request.read()
        file_path = os.path.join(User_File_Dir, User_Selected_File)
        with open(file_path, 'wb+')  as f:
            f.write(request.body)
            f.close()
        # log to the console the content of the received file
        # print(content.decode("utf-8-sig"))
        return HttpResponse()  # status 200
