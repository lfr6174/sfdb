import pytest
from django.core.exceptions import ValidationError

from apps.post.models import Post, PostType


# Prevents general posts or news from bypassing UI logic and sticking to the top
def test_post_clean_validation():
    post = Post(title="Test", post_type=PostType.ARTICLE, is_pinned=True)
    with pytest.raises(ValidationError, match="只有「公告」"):
        post.clean()
