# -*- coding: utf-8 -*-
import platform
import re
import subprocess as sb

sb.call('pip install tomlkit==0.11.6', shell=True)

requirements_file = 'requirements.txt'
exceptions = ['python']

with open(requirements_file, 'w') as file:
    file.write('# -*- coding: utf-8 -*-\n')
with open("pyproject.toml") as t:
    import tomlkit
    lock = tomlkit.parse(t.read())
    with open(requirements_file, 'a') as file:
        for package, version in lock['tool']['poetry']['dependencies'].items():
            if package.lower() not in exceptions :
                version = re.sub(r'[*^]', '', version)
                if int(platform.python_version().rsplit(".", 1)[0].replace('.', '')) < 39:
                    if package.lower() == 'rich':
                        version = f'==12.6.0'
                    elif package.lower() == 'mss':
                        version = f'==7.0.1'
                    elif package.lower() == 'opencv-python':
                        version = f'==4.3.0.38'
                    else:
                        version = f'=={version}' if version else ''
                else:
                    version = f'=={version}' if version else ''
                file.write(f"{package}{version}\n")

sb.call(f'pip install -r {requirements_file}', shell=True)
