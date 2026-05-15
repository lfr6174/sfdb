from rest_framework import serializers

from .models import Page, Post


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "created_at"]


class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

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

    def get_author_name(self, obj):
        if not obj.author:
            return "管理員"
        return obj.author.display_name or "管理員"


class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "slug", "title", "updated_at"]


class PageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "slug", "title", "body", "updated_at"]
