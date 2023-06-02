# -*- coding: utf-8 -*-
import subprocess as sb

sb.call('pip install tomlkit==0.11.6', shell=True)

with open("requirements.txt", 'w') as file:
    file.write('# -*- coding: utf-8 -*-\n')
with open("pyproject.toml") as t:
    import tomlkit
    lock = tomlkit.parse(t.read())
    with open("requirements.txt", 'a') as file:
        for package in lock['tool']['poetry']['dependencies']:
            if package.lower() != 'python':
                file.write(f"{package}\n")
        try:
            for group in lock['tool']['poetry']['group']:
                for package in lock['tool']['poetry']['group'][group]['dependencies']:
                    file.write(f"{package}\n")
        except Exception as e:
            print(e)
