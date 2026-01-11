import pytest
from datetime import datetime
from proofreader.ghost.models import Post

@pytest.fixture
def sample_post():
    return Post(
        id="123",
        uuid="abc-123",
        title="Test Post",
        slug="test-post",
        html="<p>This is a test post with a typo.</p>",
        status="draft",
        visibility="public",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("proofreader.agent.utils.client")
