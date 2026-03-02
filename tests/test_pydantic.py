from typing import Optional

from pydantic import BaseModel, Field

from muid import MagicID


def test_typing():

    class TestModel(BaseModel):
        uid: MagicID

    muid = MagicID()

    obj = TestModel(uid=muid)

    assert obj.uid == muid

    class TestModel(BaseModel):
        uid: MagicID = Field(default_factory=MagicID)

    obj = TestModel()
    assert isinstance(obj.uid, MagicID)


def test_nullable():
    class TestModel(BaseModel):
        uid: Optional[MagicID]

    obj = TestModel(uid=None)

    assert obj.uid is None


def test_str_bytes_validation():
    class TestModel(BaseModel):
        uid: MagicID

    muid = MagicID()

    obj1 = TestModel.model_validate({"uid": str(muid)})
    obj2 = TestModel.model_validate({"uid": bytes(muid)})

    assert muid == obj1.uid == obj2.uid


def test_serialization():
    class TestModel(BaseModel):
        uid: MagicID

    obj = TestModel(uid=MagicID())

    assert obj.model_dump(mode="python")["uid"] == str(obj.uid)

    assert obj.model_dump(mode="json")["uid"] == str(obj.uid)
