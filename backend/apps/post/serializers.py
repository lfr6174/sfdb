from rest_framework import serializers

from .models import Page, Post


class PostListSerializer(serializers.ModelSerializer):
    post_type_display = serializers.CharField(source="get_post_type_display", read_only=True)
    author_name = serializers.CharField(source="author.username", default="管理員", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "post_type", "post_type_display", "title", "is_pinned", "author_name", "created_at"]


class PostDetailSerializer(serializers.ModelSerializer):
    post_type_display = serializers.CharField(source="get_post_type_display", read_only=True)
    author_name = serializers.CharField(source="author.username", default="管理員", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "post_type",
            "post_type_display",
            "title",
            "body",
            "is_pinned",
            "author_name",
            "created_at",
            "updated_at",
        ]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "slug", "title", "body", "created_at", "updated_at"]
