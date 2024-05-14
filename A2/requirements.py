import pip

def import_or_install(package):
    pkg = package
    try:
        __import__(pkg)
        print(f'Requirement: {pkg} is pre-installed.')
    except ImportError:
        pip.main(['install', pkg])
        print(f'Installing package: {pkg}')

import_or_install('xlsxwriter')
import_or_install('openpyxl')