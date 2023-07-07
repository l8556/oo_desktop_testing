# -*- coding: utf-8 -*-
import platform
import re
import subprocess as sb

requirements_file = 'requirements.txt'
poetry_requirements = 'pyproject.toml'
exceptions = ['python']

def write(text, mode='w'):
    with open(requirements_file, mode) as f:
        f.write(text)

def old_system_package_version(package):
    if package.lower() == 'opencv-python':
        return '==4.3.0.38'
    elif package.lower() == 'rich':
        return '==12.6.0'
    elif package.lower() == 'mss':
        return '==7.0.1'
    return ''

def create_requirements():
    with open(poetry_requirements) as t:
        for package, version in tomlkit.parse(t.read())['tool']['poetry']['dependencies'].items():
            if package.lower() not in exceptions:
                if int(platform.python_version().rsplit(".", 1)[0].replace('.', '')) < 39:
                    version = old_system_package_version(package)
                else:
                    version = re.sub(r'[*^]', '', version)
                    version = f"=={version}" if version else ''
                write(f"{package}{version}\n", 'a')

def upgrade_pip():
    sb.call('python -m pip install --upgrade pip', shell=True)

def install_requirements():
    sb.call(f'pip install -r {requirements_file}', shell=True)

def install_tomlkit():
    sb.call('pip install tomlkit==0.11.6', shell=True)

if __name__ == "__main__":
    install_tomlkit()
    import tomlkit
    upgrade_pip()
    write('# -*- coding: utf-8 -*-\n', 'w')
    create_requirements()
    install_requirements()
