import os
import tempfile

import pytest
from mobilist.app import mkpath, app, db


@pytest.fixture
def client():
   elf.db_uri = ('sqlite:///'+mkpath('DBMOBILIST.db'))
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        self.app = app.test_client()

    os.close(db_fd)
    os.unlink(db_path)