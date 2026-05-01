from rest_framework import serializers

from .models import Page, Post


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "created_at"]


class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", default="管理員", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
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
