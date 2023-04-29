# By Martin v1.0.0
# One click submission
# push(remotegit,path,token,branch,commit)

import os
from github3 import login
import re

class GitAction:
    def __init__(self, echo=True):
        self.echo = echo


    def push(self, remotegit=None, path=None, token=None, branch='master', commit='New'):
        if not self.__parameter_filtering__(remotegit, path) or not token:
            return False
        repo_owner, repo_name = self.__detection__(remotegit)
        if not repo_owner or not repo_name:
            return False
        try:
            self.__repo__ = login(token=token).repository(repo_owner, repo_name)
        except Exception as e:
            if self.echo:
                print("Cannot connect to repository!")
            return False
        else:
            self.__git_add__(path, commit, branch)
            return True


    def __parameter_filtering__(self, remotegit, path):
        return bool(re.search(r'https://github\.com/(\w+)/(\w+)\.git', remotegit)) and os.path.isdir(path)


    def __detection__(self, remotegit):
        match = re.search(r'https://github\.com/(\w+)/(\w+)\.git', remotegit)
        return match.group(1, 2) if match else (None, None)


    def __git_add__(self, path, commit, branch):
        for root, dirs, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(root, filename)
                with open(file_path, 'rb') as f:
                    content = f.read()
                try:
                    self.__repo__.create_file(filename, message=commit, content=content, branch=branch)
                except Exception as e:
                    if self.echo:
                        print(f"{filename} File upload failed")
                else:
                    if self.echo:
                        print(f"{filename} File uploaded successfully")
        return True