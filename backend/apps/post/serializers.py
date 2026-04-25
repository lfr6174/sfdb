from rest_framework import serializers

from .models import Post


class PostListSerializer(serializers.ModelSerializer):
    post_type_display = serializers.CharField(source="get_post_type_display", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "post_type", "post_type_display", "title", "is_pinned", "created_at"]


class PostDetailSerializer(serializers.ModelSerializer):
    post_type_display = serializers.CharField(source="get_post_type_display", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "post_type", "post_type_display", "title", "body", "is_pinned", "created_at", "updated_at"]
