from posts.models import Post

class PostFactory:
    @staticmethod
    def create_post(*, author, content: str, privacy: str = "public") -> Post:
        if not content or not str(content).strip():
            raise ValueError("Content is required")
        return Post.objects.create(
            author=author,
            content=content.strip(),
            privacy=privacy
        )