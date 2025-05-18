import os
from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
#from cosite.settings import WOPI_FILE_DIR
import wopi.views

class CollaboraOnlineServerForm(forms.Form):
    collabora_online_server = forms.CharField(label='Collabora Online Server')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        self.scheme = 'http'

    def set_scheme(self, scheme):
        self.scheme = scheme

    def clean_collabora_online_server(self):
        url = self.cleaned_data['collabora_online_server']
        if not url.startswith('http'):
            raise ValidationError("Warning! You have to specify the scheme protocol too (http|https) for the server "
                                  "address.")
        if not url.startswith(f'{self.scheme}://'):
            raise ValidationError('Collabora Online server address scheme does not match the current page url scheme')

        return url


class UserNameForm(forms.Form):
    user_name = forms.CharField(label='User Name', max_length=50)

class WOPIFileDirForm(forms.Form):
    #wopi_file_dir = forms.CharField(label='WOPI File Dir', initial=WOPI_FILE_DIR ,max_length=200)
    wopi_file_dir = forms.CharField(label='WOPI File Dir', max_length=200)

class FileSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FileSelectionForm, self).__init__(*args, **kwargs)
        self.fields['file_choice'].choices = self.get_file_choices()

    file_choice = forms.ChoiceField(choices=[])

    def get_file_choices(self):
        directory = wopi.views.User_File_Dir
        print(f'get_file_choices_directory:{directory}')
        files = [(f, f) 
                for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))
                and f.lower().endswith(('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'))
        ]
        print(f'get_file_choices_files:{files}')
        return files
