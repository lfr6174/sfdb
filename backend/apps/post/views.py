from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Page, Post, PostType
from .serializers import PageSerializer, PostDetailSerializer, PostListSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only API. Content is managed via Django Admin.
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    filterset_fields = ["post_type", "is_pinned"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    queryset = Post.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    @action(detail=False, methods=["get"], url_path="active-pinned")
    def active_pinned(self, request):
        post = self.get_queryset().filter(post_type=PostType.ANNOUNCEMENT, is_pinned=True).first()

        if not post:
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(PostDetailSerializer(post).data)


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only API for static pages.
    """

    queryset = Page.objects.all()
    serializer_class = PageSerializer
    lookup_field = "slug"
