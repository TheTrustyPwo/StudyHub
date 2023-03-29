from app.models import Post


def create_post(title: str, data: str, user_id: int):
    """
    Create a post, save it, and return the post id
    """
    post = Post(title, data, user_id)
    post.save()
    return post.id

def delete_post(post):
    """
    Removes a post from the database.
    """
    db.session.delete(post)
    db.session.commit()
