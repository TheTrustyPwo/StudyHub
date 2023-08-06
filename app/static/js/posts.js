import { Post, Reply, User } from "./models/index.js";
import { hideLoadingScreen } from "./index.js";

const currentUser = await User.getCurrent();
const searchParams = new URLSearchParams(window.location.search);
const sortBy = searchParams.get('sortBy')?.toLowerCase() || 'recent';
const postId = parseInt(window.location.pathname.split('/').pop());

$(document).ready(async function () {
    const post = await Post.getById(postId);
    await post.loadReplies();
    renderPost(post);
    renderReplies(post.replies);

    hideLoadingScreen();

    const relatedPosts = await Post.getPosts(1, 10, null, new Set([post.subject]));
    renderRelatedPosts(relatedPosts.filter(relatedPost => relatedPost.id !== post.id));
});

function renderPost(post) {
    const postUpvoteButton = document.getElementById('post-upvote');
    const postDownvoteButton = document.getElementById('post-downvote');
    const userVote = post.votes.find(vote => vote.userId === currentUser.id)?.vote || 0;

    postUpvoteButton.classList.remove('active');
    postDownvoteButton.classList.remove('active');

    if (userVote === 1) postUpvoteButton.classList.add('active');
    else if (userVote === -1) postDownvoteButton.classList.add('active');

    document.getElementById('post-title').innerText = post.title;
    document.getElementById('post-body').innerText = post.body;
    document.getElementById('post-votes').innerText = post.getVoteCount().toLocaleString();
    document.getElementById('post-reply-count').innerText = post.replyCount.toLocaleString();
    document.getElementById('post-timestamp').innerText = post.timestamp.local().calendar();

    document.getElementById('post-author').innerText = post.author.username;
    document.getElementById('post-author-pfp').src = post.author.pfp;

    if (post.attachment) {
        document.getElementById('post-attachment-wrap').style.display = 'flex';
        document.getElementById('post-attachment').src = post.attachment;
    }

    document.getElementById('post-upvote').onclick = async () => {
        await post.upvote();
        await renderPost(post);
    }

    document.getElementById('post-downvote').onclick = async () => {
        await post.downvote();
        await renderPost(post);
    }

    // postDeleteButton.onclick = async () => {
    //     if (window.confirm('Are you sure you want to delete this post?')) {
    //         await post.delete();
    //         window.location.href = '/';
    //     }
    // }

    document.getElementById('reply-button').onclick = async () => {
        const replyText = document.getElementById('reply-text');
        const text = replyText.value;
        replyText.value = '';

        document.getElementById('reply-button').classList.add('d-none');
        document.getElementById('reply-button-loading').classList.remove('d-none');
        const reply = await Reply.create(text, post);
        document.getElementById('reply-button-loading').classList.add('d-none');
        document.getElementById('reply-button').classList.remove('d-none');

        const replyDiv = renderReply(reply);
        document.getElementById('post-replies').prepend(replyDiv);
        replyDiv.scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});
    }
}

function renderReplies(replies) {
    const postReplies = document.getElementById('post-replies');
    const sorting = {
        'recent': (a, b) => b.timestamp - a.timestamp,
        'popular': (a, b) => b.getVoteCount() - a.getVoteCount() || b.timestamp - a.timestamp
    }
    replies.sort(sorting[sortBy]).forEach(reply => postReplies.appendChild(renderReply(reply)));
}

function renderReply(reply) {
    const userVote = reply.votes.find(vote => vote.userId === currentUser.id)?.vote || 0;
    console.log(userVote)
    const replyDiv = document.createElement('div');
    replyDiv.setAttribute('data-reply-id', reply.id);
    replyDiv.classList = 'card post-card w-100 shadow-xss rounded-xxl border-0 p-4 mb-3'

    replyDiv.innerHTML =
        `<div class="card-body p-0 d-flex">
            <figure class="avatar me-3"><img src=${reply.author.pfp} alt="avater" class="shadow-sm rounded-circle w45"></figure>
            <div><h4 class="fw-700 text-grey-900 font-xssss mt-1">${reply.author.username}<span class="d-block font-xssss fw-500 mt-1 lh-3 text-grey-500">${reply.timestamp.fromNow()}</span></h4></div>
        </div>
        <h4 class="mont-font fw-600 font-xss text-dark">${reply.reply}</h4>
        <div class="card-body d-flex p-0">
            <div class="d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss me-2">
                <i class="upvote ${userVote === 1 ? 'active' : ''}"></i>
                <span id="post-votes" class="mx-2">${reply.getVoteCount().toLocaleString()}</span>
                <i class="downvote ${userVote === -1 ? 'active' : ''}"></i>
            </div>
        </div>`;

    replyDiv.querySelector('.upvote').onclick = async () => {
        await reply.upvote();
        replyDiv.replaceWith(renderReply(reply));
    }

    replyDiv.querySelector('.downvote').onclick = async () => {
        await reply.downvote();
        replyDiv.replaceWith(renderReply(reply));
    }

    return replyDiv;
}

function renderRelatedPosts(posts) {
    const relatedPosts = document.getElementById('related-posts');
    posts.forEach(post => {
        const postDiv = document.createElement('div');
        postDiv.innerHTML =
            `<a href="/post/${post.id}" class="list-group-item list-group-item-action card w-100 border-0 rounded-0 pt-1">
                <div class="card-body p-0 d-flex">
                    <figure class="avatar me-1"><img src="${post.author.pfp}" alt="avater" class="shadow-sm rounded-circle w25"></figure>
                    <h3 class="fw-600 text-grey-900 font-xsss lh-28">${post.author.username}</h3>
                    <span class="fw-900 font-x mx-1">&#183;</span>
                    <span class="font-xsss fw-500 text-grey-500">${post.timestamp.fromNow()}</span>
                </div>
                <h4 class="fw-bold font-xsss mt--1">${post.title}</h4>
            </a>
            <hr class="p-0 my-2">`;
        relatedPosts.appendChild(postDiv);
    })
}
