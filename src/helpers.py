# unsorted shit

import os


project_dir = ''
while not os.path.exists(os.path.join(project_dir, '.project')):
    project_dir = os.path.join(project_dir, '..')

def project_path(path):
    return os.path.join(project_dir, path)

def limit_string(s, maxlen=10):
    if len(s) <= maxlen:
        return ''.join(s)
    return '{0}... ({1} bases)'.format(''.join(s[:maxlen]), len(s))

   
