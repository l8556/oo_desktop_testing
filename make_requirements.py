# -*- coding: utf-8 -*-
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
    print(lock)
    with open(requirements_file, 'a') as file:
        for package, version in lock['tool']['poetry']['dependencies'].items():
            if package.lower() not in exceptions :
                version = re.sub(r'[*^]', '', version)
                version = f'=={version}' if version else ''
                file.write(f"{package}{version}\n")
