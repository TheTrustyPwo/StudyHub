import { Post, Reply, User } from "./models/index.js";

const currentUser = await User.getCurrent();
const searchParams = new URLSearchParams(window.location.search);
const sortBy = searchParams.get('sortBy')?.toLowerCase() || 'recent';

let post;
const postId = parseInt(window.location.pathname.split('/').pop());

$(document).ready(async function () {
    post = await Post.getById(postId);
    await post.loadReplies();
    renderPost(post);
    renderReplies(post.replies);

    document.getElementById('post-container').classList.remove('loading-skeleton');

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

    document.getElementById('post-title').textContent = DOMPurify.sanitize(post.title);
    document.getElementById('post-body').textContent = DOMPurify.sanitize(post.body);
    document.getElementById('post-votes').textContent = post.getVoteCount().toLocaleString();
    document.getElementById('post-reply-count').textContent = post.replyCount.toLocaleString();
    document.getElementById('post-timestamp').textContent = post.timestamp.local().calendar();

    document.getElementById('post-author').textContent = DOMPurify.sanitize(post.author.username);
    document.getElementById('post-author-pfp').src = post.author.pfp;

    if (post.resolvedBy) {
        document.getElementById('post-solved').classList.remove('d-none');
    }

    if (post.attachment) {
        document.getElementById('post-attachment-wrap').style.display = 'flex';
        document.getElementById('post-attachment').src = post.attachment;
    }

    postUpvoteButton.onclick = async () => {
        console.log("UPVOTED")
        await post.upvote();
        await renderPost(post);
    }

    postDownvoteButton.onclick = async () => {
        await post.downvote();
        await renderPost(post);
    }

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
        replyDiv.scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });
    }
}

function renderReplies(replies) {
    const postReplies = document.getElementById('post-replies');
    const sorting = {
        'recent': (a, b) => b.timestamp - a.timestamp,
        'popular': (a, b) => b.getVoteCount() - a.getVoteCount() || b.timestamp - a.timestamp
    }

    const markedReply = replies.find(reply => reply.id === post.resolvedBy?.id);
    if (markedReply) postReplies.appendChild(renderReply(markedReply));
    replies.filter(reply => reply.id !== post.resolvedBy?.id).sort(sorting[sortBy]).forEach(reply => postReplies.appendChild(renderReply(reply)));
}

function renderReply(reply) {
    const userVote = reply.votes.find(vote => vote.userId === currentUser.id)?.vote || 0;
    const replyDiv = document.createElement('div');
    replyDiv.setAttribute('data-reply-id', reply.id);
    replyDiv.classList.add('card', 'post-card', 'w-100', 'shadow-xss', 'rounded-xxl', 'border-0', 'p-4', 'mb-3');

    replyDiv.innerHTML = DOMPurify.sanitize(
        `<div class="card-body p-0 d-flex">
            <figure class="avatar me-3"><img src=${reply.author.pfp} alt="avater" class="shadow-sm rounded-circle w45"></figure>
            <div><h4 class="fw-700 text-grey-900 font-xssss mt-1">${reply.author.username}<span class="d-block font-xssss fw-500 mt-1 lh-3 text-grey-500">${reply.timestamp.fromNow()}</span></h4></div>
            <div class="ms-auto pointer d-flex align-items-center">
                ${post.resolvedBy?.id === reply.id ? `<div id="post-solved" class="rounded-pill bg-success text-white px-4 py-2 me-3 font-xssss">Marked as Answer</div>` : ``}
                <div class="pointer" id="reply${reply.id}Dropdown" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="ti-more-alt text-grey-900 btn-round-md bg-greylight font-xss"></i>
                </div>
                <div class="dropdown-menu dropdown-menu-end p-2 rounded-xxl border-0 shadow-lg fw-700 font-xss text-grey-900" aria-labelledby="reply${reply.id}Dropdown">
                    <div class="dropdown-item"><i class="ti-flag-alt me-1"></i>Report</div>
                    ${post.resolvedBy ? `` : `<div class="dropdown-item mark-answer"><i class="ti-check me-1"></i>Mark as Answer</div>`}
                </div>
            </div>
        </div>
        <h4 class="mont-font fw-600 font-xss text-dark">${reply.reply}</h4>
        <div class="card-body d-flex p-0">
            <div class="d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss me-2">
                <i class="upvote ${userVote === 1 ? 'active' : ''}"></i>
                <span id="post-votes" class="mx-2">${reply.getVoteCount().toLocaleString()}</span>
                <i class="downvote ${userVote === -1 ? 'active' : ''}"></i>
            </div>
        </div>`);

    replyDiv.querySelector('.upvote').addEventListener('click', async () => {
        await reply.upvote();
        replyDiv.replaceWith(renderReply(reply));
    });

    replyDiv.querySelector('.downvote').addEventListener('click', async () => {
        await reply.downvote();
        replyDiv.replaceWith(renderReply(reply));
    });

    replyDiv.querySelector('.mark-answer')?.addEventListener('click', async () => {
        await post.resolve(reply);
        replyDiv.replaceWith(renderReply(reply));
        renderPost(post);
    });

    return replyDiv;
}

function renderRelatedPosts(posts) {
    const relatedPosts = document.getElementById('related-posts');
    posts.forEach(post => {
        const postDiv = document.createElement('a');
        postDiv.href = `/post/${post.id}`;
        postDiv.classList.add('list-group-item', 'list-group-item-action', 'card', 'w-100', 'border-0', 'rounded-0', 'pt-1');

        postDiv.innerHTML = DOMPurify.sanitize(
            `<div class="card-body p-0 d-flex">
                <figure class="avatar me-1"><img src="${post.author.pfp}" alt="avater" class="shadow-sm rounded-circle w25"></figure>
                <h3 class="fw-600 text-grey-900 font-xsss lh-28">${post.author.username}</h3>
                <span class="fw-900 font-x mx-1">&#183;</span>
                <span class="font-xsss fw-500 text-grey-500">${post.timestamp.fromNow()}</span>
            </div>
            <h4 class="fw-bold font-xsss mt--1">${post.title}</h4>`
        );

        relatedPosts.appendChild(postDiv);
    });
}
