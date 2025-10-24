import sys
import os
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient


sys.path.append (os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config.database import Base, get_session
from app.models.user import User
from app.config.security import hash_password
from datetime import datetime
from app.config.email import fm


USER_NAME = "Usama Hassan"
USER_EMAIL = "usamahassan311@gmail.com"
USER_PASSWORD = "#Usama123"

engine = create_engine("sqlite:///./fastapi.db")
SessionTesting = sessionmaker(autocommit = False,autoflush = False, bind = engine)


@pytest.fixture
def test_session() -> Generator:
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope = "function")
def app_test():
    Base.metadata.create_all(bind = engine)
    yield app
    Base.metadata.drop_all(bind = engine)


@pytest.fixture(scope = "function")
def client (app_test, test_session):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_session] = _test_db
    fm.config.SUPPRESS_SEND = 1 # yee mail service disable krta ha taa k kiu b mail na nzr aye
    return TestClient (app_test)

@pytest.fixture(scope="function")
def inactive_user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.is_active = False
    model.updated_at=datetime.utcnow()
    test_session.add(model)      # ✅ fixed
    test_session.commit()        # ✅ fixed
    test_session.refresh(model)  # ✅ fixed
    return model

@pytest.fixture(scope="function")
def inactive_user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.is_active = True
    model.updated_at=datetime.utcnow()
    model.verified_at=datetime.utcnow()
    test_session.add(model)      # ✅ fixed
    test_session.commit()        # ✅ fixed
    test_session.refresh(model)  # ✅ fixed
    return model

#fixture for unverified user
@pytest.fixture(scope="function")
def unverified_user(test_session):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.is_active = True
    model.updated_at=datetime.utcnow()
    test_session.add(model)      # ✅ fixed
    test_session.commit()        # ✅ fixed
    test_session.refresh(model)  # ✅ fixed
    return model