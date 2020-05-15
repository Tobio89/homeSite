import setENV

import os
import click

from flask_migrate import Migrate
from homeSite_main import create_app, db
from homeSite_main.models import Grocery, Schedule, Tasks, ParcelInfo


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Grocery=Grocery, ParcelInfo=ParcelInfo, Tasks=Tasks, Schedule=Schedule)

# @app.cli.command()
# @click.argument()