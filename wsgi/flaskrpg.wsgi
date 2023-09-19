#!/usr/bin/env python3
# -*- mode: python; -*-

# pour activer l'environnement virtuel (créé nécessairement par
# 'virtualenv' et non pas 'python3 -m venv')
from pathlib import Path
wsgi_dir = Path(__file__).parent.absolute()
activate_this = wsgi_dir.joinpath('../venv-flaskrpg/bin/activate_this.py').resolve()
print(activate_this)
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# instanciation de l'application (en mode 'development')
import os
from flaskrpg import create_app
os.environ['FLASK_APP'] = 'flaskrpg'
os.environ['FLASKRPG_SETTINGS'] = 'development.py'
application = create_app()
