from app.models import Post


def create_post(title: str, data: str, user_id: int):
    post = Post(title, data, user_id)
    post.save()
    return post.id
