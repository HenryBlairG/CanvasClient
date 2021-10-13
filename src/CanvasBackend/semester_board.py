from json import loads, dumps
from requests import get

import os


import src.CanvasBackend.board_exceptions as bErr
import src.CanvasBackend.misc_utils as msc

def null(x):
    # Solo para llevar cuenta de lo que no conozco
    return str(x)


class Profile:

    URL_COURSES = 'https://cursos.canvas.uc.cl/api/v1/courses'
    JSON_PATH = 'profile.json'
    TOKEN = None

    def __init__(self, token):
        Profile.TOKEN = token
        if os.path.isfile(Profile.JSON_PATH):
            self.load_json()
        else:
            self.courses = []
            resp = get(Profile.URL_COURSES, headers={'Authorization': f'Bearer {Profile.TOKEN}'}, timeout=60*45)
            if not resp:
                print('UPS')
            for c in resp.json():
                # print(f'{c}\n\n\n')
                self.courses.append(Course(**c))
    
    def load_json(self):
        pass
    

class Course: 

    URL_FOLDERS = 'https://cursos.canvas.uc.cl/api/v1/courses/{}/folders'
    # URL_FILES = 'https://cursos.canvas.uc.cl/api/v1/courses/{}/files'
    
    def __init__(self, **kw):
        # Request Atributes
        whitelist = {
            'id': int,
            'name': null,
            'account_id': int,
            'uuid': str,
            'start_at': msc.str2datetime, 
            'grading_standard_id': null,
            'is_public': bool,
            'created_at': msc.str2datetime,
            'course_code': str,
            'default_view': null,
            'root_account_id': int,
            'enrollment_term_id': int,
            'license': str,
            'grade_passback_setting': null,
            'end_at': msc.str2datetime,
            'public_syllabus': null,
            'public_syllabus_to_auth': null,
            'storage_quota_mb': int,
            'is_public_to_auth_users': bool,
            'apply_assignment_group_weights': null,
            'calendar': str,
            'time_zone': str,
            'original_name': str,
            'blueprint': str,
            'enrollments': str,
            'hide_final_grades': str,
            'workflow_state': null,
            'course_format': null,
            'restrict_enrollments_to_course_dates': str}
        blacklist = {}
        self.args = {}
        for k, v in kw.items():
            if k in whitelist.keys():
                type_convert = whitelist[k]
                setattr(self, k.replace('-', '_'), type_convert(v))
            elif k in blacklist:
                raise ValueError("unexpected kwarg value", k)
            else:
                self.args.update({k: v})
        # Request Atributes
        
        # Local Atributes
        if not self.end_at or self.end_at >= msc.dt.today():
            self.path = os.path.abspath(os.getcwd())
            self.folders = set()
            self.files = set()
            self.__setUpFolders__()
    
    def __setUpFolders__(self):            
        if Profile.TOKEN is None:
            raise bErr.NoTokenError
        
        rsp = get(Course.URL_FOLDERS.format(self.id) + Folders.URL_SIZE.format(50), headers={'Authorization': f'Bearer {Profile.TOKEN}'}, timeout=60*45)
        if not rsp:
            raise bErr.GetContentError
        
        for f  in rsp.json():
            Folders(self, **f)


class Folders:

    URL_SIZE = '?per_page={}'

    def __init__(self, course, parent=None,**kw):
        # Request Atributes
        whitelist = {'id': int,
                     'name': lambda x: str(x).replace(' ', '_').replace('course_files', course.name),
                     'full_name': lambda x: str(x).replace(' ', '_').replace('course_files', course.name),
                     'context_id': int,
                     'context_type': null,
                     'parent_folder_id': lambda x: None if x is None else int(x),
                     'created_at': msc.str2datetime,
                     'updated_at': msc.str2datetime,
                     'lock_at': msc.str2datetime,
                     'unlock_at': msc.str2datetime,
                     'position': null,
                     'locked': bool,
                     'folders_url': str,
                     'files_url': str,
                     'folders_count': int,
                     'files_count': int,
                     'hidden': bool,
                     'locked_for_user': null,
                     'hidden_for_user': null,
                     'for_submissions': null,
                     'can_upload': null}
        blacklist = {}
        self.args = {}
        for k, v in kw.items():
            if k in whitelist.keys():
                type_convert = whitelist[k]
                setattr(self, k.replace('-', '_'), type_convert(v))
            elif k in blacklist:
                raise ValueError("unexpected kwarg value", k)
            else:
                self.args.update((k,v))
        # print(f'FOLDER: {self.full_name}\n')
        if self not in course.folders:
            # Local Atributes
            self.parent_folder = parent
            self.subfolders = None
            self.files = None
            course.folders.add(self)
            if self.files_count or self.folders_count:
                os.makedirs(os.path.join(course.path, self.full_name), exist_ok=True)
                if self.folders_count:
                    rsp = get(self.folders_url + Folders.URL_SIZE.format(self.folders_count+1), headers={'Authorization': f'Bearer {Profile.TOKEN}'}, timeout=60*45)
                    if rsp:
                        self.subfolders = {Folders(course, self, **f) for f in rsp.json() if int(f['folders_count']) or int(f['files_count'])}
                if self.files_count:
                    rsp = get(self.files_url + Folders.URL_SIZE.format(self.files_count+1), headers={'Authorization': f'Bearer {Profile.TOKEN}'}, timeout=60*45)
                    if rsp:
                        self.files = {Files(self, course, **f) for f in rsp.json()}
    
    def __repr__(self):
        return f'\n{self.id}: {self.full_name}\n'
    
    def __eq__(self, other):
        if isinstance(other, Files):
            return self.id == other.folder_id
        return self.id == other.id
    
    def __hash__(self):
        return self.id


class Files:

    def __init__(self, parent, course, **kw):
        # Request Atributes
        whitelist = {'id': int, 
                     'uuid': str, 
                     'folder_id': int, 
                     'display_name': lambda x: str(x).replace(' ', '_'),
                     'filename': str,
                     'upload_status': null,
                     'content-type': null,
                     'url': str,
                     'size': int,
                     'created_at': msc.str2datetime,
                     'updated_at': msc.str2datetime,
                     'lock_at': msc.str2datetime,
                     'unlock_at': msc.str2datetime,
                     'locked': bool,
                     'hidden': null,
                     'lock_at': msc.str2datetime,
                     'hidden_for_user': null,
                     'thumbnail_url': str,
                     'modified_at': msc.str2datetime,
                     'mime_class': null,
                     'media_entry_id': null,
                     'locked_for_user': null}
        blacklist = {}
        self.args = {}
        for k, v in kw.items():
            if k in whitelist.keys():
                type_convert = whitelist[k]
                setattr(self, k.replace('-', '_'), type_convert(v))
            elif k in blacklist:
                raise ValueError("unexpected kwarg value", k)
            else:
                # print(f'k:{k}\nv:{v}')
                self.args.update({k: str(v)})
        # print(f'FILE: {self.display_name}\n')
        if self not in course.files:
            # Local Atributes
            self.parent = parent
            self.path = os.path.join(course.path, parent.full_name, self.display_name)
            course.files.add(self)
            if os.path.isfile(self.path):
                modified_at = msc.dt.fromtimestamp(round(os.path.getmtime(self.path)))
                if modified_at >= self.updated_at:
                    # print(f'Skipping:   {self.path}')
                    pass
            elif 'lock_info' in self.args:
                print(f'Locked:     {self.path}')
                pass
            elif self.url:
                rsp = get(self.url, headers={'Authorization': f'Bearer {Profile.TOKEN}'}, timeout=60*45)
                if not rsp:
                    raise bErr.GetContentError
                print(f'Downloading: {self.path}')
                open(self.path, 'wb').write(rsp.content)

    def __repr__(self):
        return f'\n({self.path}({self.locked})'
    
    def __eq__(self, other):
        if isinstance(other, Folders):
            return self.folder_id == other.id
        return self.uuid == other.uuid
    
    def __hash__(self):
        return self.id


if __name__ == '__main__':
    pass
