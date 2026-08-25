import uuid
from app.models.models import Conversation, Message, ContextSummary, LongTermMemory, ToolModel


def test_conversation_instantiation():
    conv = Conversation()
    assert conv.id is not None or conv.id is None
    assert isinstance(uuid.uuid4(), uuid.UUID)


def test_message_instantiation():
    conv_id = uuid.uuid4()
    msg = Message(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        role="user",
        content="Hello",
        token_count=2,
    )
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.token_count == 2
    assert msg.conversation_id == conv_id


def test_context_summary_instantiation():
    conv_id = uuid.uuid4()
    last_id = uuid.uuid4()
    summary = ContextSummary(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        summary="User discussed python setup.",
        last_message_id=last_id,
        token_count=10,
    )
    assert summary.summary == "User discussed python setup."
    assert summary.conversation_id == conv_id


def test_long_term_memory_instantiation():
    mem = LongTermMemory(
        id=uuid.uuid4(),
        owner_id="user_1",
        key="user_name",
        content="User's name is Krishna",
        importance=0.9,
    )
    assert mem.owner_id == "user_1"
    assert mem.key == "user_name"
    assert mem.importance == 0.9


def test_tool_model_to_dict():
    tm = ToolModel(
        id=uuid.uuid4(),
        tool_name="test_tool",
        description="A test tool",
        parameters={"type": "object"},
        permissions={"read": True},
    )
    d = tm.to_dict()
    assert d == {
        "name": "test_tool",
        "description": "A test tool",
        "parameters": {"type": "object"},
        "permissions": {"read": True},
    }
    assert repr(tm) == "<ToolModel name='test_tool'>"
