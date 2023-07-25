import {Post, Reply, User} from "./models/index.js";

$(document).ready(async function () {
    const currentUser = await User.getCurrent();

    const postId = parseInt(window.location.pathname.split('/').pop());
    const post = await Post.getById(postId);
    await post.loadReplies();

    const postTitle = document.getElementById('post-title');
    const postBody = document.getElementById('post-body');
    const postVotes = document.getElementById('post-votes');
    const postTimestamp = document.getElementById('post-timestamp');
    const postAuthor = document.getElementById('post-author');
    const postReplies = document.getElementById('post-replies');

    const postUpvoteButton = document.getElementById('post-upvote-button');
    const postDownvoteButton = document.getElementById('post-downvote-button');
    const postDeleteButton = document.getElementById('post-delete')

    const replyText = document.getElementById('reply-text');
    const replyButton = document.getElementById('reply-button');

    postUpvoteButton.onclick = async () => {
        await post.upvote();
        await renderPost();
    }

    postDownvoteButton.onclick = async () => {
        await post.downvote();
        await renderPost();
    }

    postDeleteButton.onclick = async () => {
        if (window.confirm('Are you sure you want to delete this post?')) {
            await post.delete();
            window.location.href = '/';
        }
    }

    await renderPost();
    await renderReplies();

    replyButton.onclick = async () => {
        const reply = await Reply.create(replyText.value, post);
        await renderReply(reply);
    }

    async function renderPost() {
        const userVote = post.votes.find(vote => vote.userId === currentUser.id)?.vote || 0;
        postUpvoteButton.classList.remove('active');
        postDownvoteButton.classList.remove('active');
        if (userVote === 1) postUpvoteButton.classList.add('active');
        else if (userVote === -1) postDownvoteButton.classList.add('active');

        postTitle.innerText = post.title;
        postBody.innerText = post.body;
        postVotes.innerText = post.getVoteCount().toLocaleString();
        postTimestamp.innerText = post.timestamp.calendar();
        postAuthor.innerText = post.author.username;
    }

    async function renderReplies() {
        post.replies.sort((a, b) => b.timestamp - a.timestamp).forEach(reply => postReplies.appendChild(renderReply(reply)));
    }

    function renderReply(reply) {
        const userVote = reply.votes.find(vote => vote.userId === currentUser.id)?.vote || 0;
        const element = document.createElement('div');
        element.id = reply.id;
        element.classList.add('card', 'mb-2');

        element.innerHTML =
            `<div class="row">
                <div class="col-2">
                    <div class="list-group text-center border-0">
                        <span></span>
                        <div class="upvote-button ${userVote === 1 ? 'active' : ''}"></div>
                        <span></span>
                        <span class="votes1" id="votes1-1">${reply.getVoteCount().toLocaleString()}</span>
                        <div class="downvote-button ${userVote === -1 ? 'active' : ''}"></div>
                        <span></span>
                    </div>
                </div>
                <div class="col-10">
                    <div class="card-body">
                        <div class="comment">
                            <div class="comment-header">
                                <span class="comment-author">${reply.author.username}</span>
                                <span class="comment-time text-muted">${reply.timestamp.calendar()}</span>
                            </div>
                            <div class="comment-body"><p>${reply.reply}</p></div>
                        </div>
                    </div>
                </div>
            </div>`;

        element.querySelector('.upvote-button').onclick = async () => {
            await reply.upvote();
            element.replaceWith(renderReply(reply));
        }

        element.querySelector('.downvote-button').onclick = async () => {
            await reply.downvote();
            element.replaceWith(renderReply(reply));
        }

        return element;
    }
});