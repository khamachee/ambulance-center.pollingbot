import os 
import glob


super_login = os.getenv('DEV_SUPERUSER_LOGIN', 'admin')
super_email = os.getenv('DEV_SUPERUSER_EMAIL', '') 
super_password = os.getenv('DEV_SUPERUSER_PASSWORD' , '123')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colortext(text, color):
    border = ''.center(len(text) + 2 , '=')
    print(f"{color}{border}\n {text} \n{border}{bcolors.ENDC}")

venv = os.getenv('VIRTUAL_ENV')
if venv:
    error = os.system('pip list | grep Django')
    if error:
        print_colortext("Install Django to continue" , bcolors.WARNING)
    else:
        items = glob.glob('*/migrations/*.*')
        for item in items:
            if not item.endswith("__init__.py"):
                os.remove(item)
        try:
            os.remove('db.sqlite3')
        except:
            print_colortext('No database db.sqlite3 found ', bcolors.WARNING)

        py = f"{venv}/bin/python"
        os.system(f'{py} manage.py makemigrations')
        os.system(f'{py} manage.py migrate')
        os.system(f"""export DJANGO_SUPERUSER_PASSWORD={super_password} ;python manage.py createsuperuser --username={super_login} --email=kwutzee@gmail.com --noinput""")

else:
    print_colortext("ONLY USE IN VIRTUALENV", bcolors.FAIL)