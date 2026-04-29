from .models import Post, PostType


def get_active_pinned_post() -> Post | None:
    """
    取得目前有效的置頂公告。
    商業邏輯定義：必須是「公告 (Announcement)」類型，且設定為「置頂 (is_pinned)」。
    """
    return Post.objects.filter(post_type=PostType.ANNOUNCEMENT, is_pinned=True).first()
