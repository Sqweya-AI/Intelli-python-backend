from rest_framework import generics
from .models import Post
from .serializers import PostSerializer

# List all posts and create a new post
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer



# Retrieve, update, or delete a specific post
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
