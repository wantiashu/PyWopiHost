import os
from django.shortcuts import render
import requests
from lxml import etree
from .forms import CollaboraOnlineServerForm
from .forms import UserNameForm
from .forms import FileSelectionForm
from .forms import WOPIFileDirForm
from cosite.settings import WOPI_FILE_DIR
from cosite.settings import WOPI_CLIENT_IP
import wopi.views 
import socket


def index(request):
    scheme = request.scheme
    hostip = socket.gethostbyname(socket.gethostname())
    hostport = request.META["SERVER_PORT"]
    host = hostip + ':' + hostport
    print(f'index.host: ',host)
    #note:request.get_host() cannot transfer localhost
    wopi_src = f'{scheme}://{host}/wopi/files/1'
    print(wopi_src)
    wopi_url = ''
    user_name = ''


    if request.method == 'POST':
        #File Selection Cambo Form
        form_file_selection = FileSelectionForm(request.POST) 
        if form_file_selection.is_valid():
            selected_file = form_file_selection.cleaned_data['file_choice']
            wopi.views.set_User_Selected_File(selected_file)
            wopi_src = f'{scheme}://{host}/wopi/files/{selected_file}'

        #Collabora Online Server Form
        if request.is_local:
            form_collabora_server = CollaboraOnlineServerForm(request.POST)
            if form_collabora_server.is_valid():
                wopi.views.set_WOPI_Client_Host(
                    form_collabora_server.
                    cleaned_data['collabora_online_server']
                )
                wopi_client_host = wopi.views.get_WOPI_Client_Host()

        else:
            form_collabora_server = ''
            wopi_client_host = wopi.views.get_WOPI_Client_Host()
            print(f'wopi_client_host from guest:{wopi_client_host}')

        if wopi_client_host:
            wopi_client_url = get_collabora_url(
                wopi_client_host, 'text/plain'
            )
        if wopi_client_url:
            wopi_url = wopi_client_url + 'WOPISrc=' + wopi_src
        print(f'wopi client url: {wopi_url}')

        #User Name Form
        form_name = UserNameForm(request.POST)
        if form_name.is_valid():
            user_name = form_name.cleaned_data['user_name'] 
            wopi.views.set_User_Friendly_Name(user_name)
        
        #WOPI File Dir Form
        if request.is_local:
            form_wopi_file_dir = WOPIFileDirForm(request.POST)
            if form_wopi_file_dir.is_valid():
                wopi_file_dir = form_wopi_file_dir.cleaned_data['wopi_file_dir']
        else: form_wopi_file_dir = ''

    else:
        if request.is_local:
            form_collabora_server = CollaboraOnlineServerForm(initial={'collabora_online_server': f'{scheme}://{WOPI_CLIENT_IP}:9980'})
        else: form_collabora_server = ''
        form_name = UserNameForm()
        form_file_selection = FileSelectionForm()
        if request.is_local:
            form_wopi_file_dir = WOPIFileDirForm(initial={'wopi_file_dir': WOPI_FILE_DIR})
        else: form_wopi_file_dir = ''

    context = {
        'form_collabora_server': form_collabora_server,
        'form_name': form_name,
        'form_file_selection': form_file_selection,
        'form_wopi_file_dir': form_wopi_file_dir,
        'wopi_url': wopi_url,
        'access_token': 'test',
    }
    return render(request, 'index.html', context)


def get_collabora_url(server, mime_type):
    #
    # WARNING: `disable_verify_cert` should never be `True` on a production server.
    # This is only done to allow the use of self signed certificates on the Collabora
    # Online server for example purpose.
    #
    disable_verify_cert = 'DISABLE_TLS_CERT_VALIDATION' in os.environ and os.environ['DISABLE_TLS_CERT_VALIDATION']
    response = requests.get(server + '/hosting/discovery', verify=not disable_verify_cert)
    discovery = response.text
    #print('response.text : ' + response.text)
    if not discovery:
        print('No able to retrieve the discovery.xml file from the Collabora Online server with the submitted address.')
        return
    # print(discovery)
    parsed = etree.fromstring(discovery)
    if parsed is None:
        print('The retrieved discovery.xml file is not a valid XML file')
        return
    result = parsed.xpath(f"/wopi-discovery/net-zone/app[@name='{mime_type}']/action")
    if len(result) != 1:
        print('The requested mime type is not handled')
        return
    online_url = result[0].get('urlsrc')
    print('online url: ' + online_url)
    return online_url


