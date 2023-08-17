import { Post } from "./models/index.js";

const subjects = [
    {name: 'All Subjects', icon: 'globe'},
    {name: 'English', icon: 'pen'},
    {name: 'Mathematics', icon: 'calculator'},
    {name: 'Physics', icon: 'lightning'},
    {name: 'Chemistry', icon: 'rocket-takeoff'},
    {name: 'Geography', icon: 'map'},
    {name: 'History', icon: 'book'},
    {name: 'Social Studies', icon: 'people'},
    {name: 'Biology', icon: 'lungs'},
    {name: 'Chinese', icon: 'translate'},
    {name: 'Computing', icon: 'code-slash'},
    {name: 'Literature', icon: 'journal'},
    {name: 'Music', icon: 'music-note-beamed'},
    {name: 'Art', icon: 'palette'}
];

const selectedSubjects = new Set();
selectedSubjects.add('all subjects');

let currentPage = 1;
const postsPerPage = 2;
let loading = false, reachedEnd = false, timestamp = moment();

window.addEventListener('scroll', handleScroll);

$(document).ready(async function () {
    createSubjectButtons();
    await fetchPosts();
});

async function fetchPosts() {
    loading = true;
    document.getElementById('loading-spinner').classList.remove('d-none');

    const posts = await Post.getPosts(currentPage, postsPerPage, timestamp, selectedSubjects);
    const postsContainer = document.getElementById('posts-container');

    if (posts.length > 0) {
        posts.forEach(post => {
            const postElement = createPostCard(post);
            postsContainer.appendChild(postElement);
        });
    } else reachedEnd = true;

    loading = false;
    document.getElementById('loading-spinner').classList.add('d-none');
}

function createPostCard(post) {
    const postCard = document.createElement('div');
    postCard.className = `card post-card w-100 shadow-xss rounded-xxl border-0 p-4 mb-3`;
    postCard.innerHTML = DOMPurify.sanitize(
        `<div class="card-body p-0 d-flex">
            <a href="/users/${post.author.username}"><figure class="avatar me-3"><img src=${post.author.pfp} alt="avater" class="shadow-sm rounded-circle w45"></figure></a>
            <div><h4 class="fw-700 text-grey-900 font-xssss mt-1"> ${post.author.username} <span class="d-block font-xssss fw-500 mt-1 lh-3 text-grey-500"> ${post.timestamp.fromNow()}</span></h4></div>
            <div class="ms-auto pointer d-flex align-items-center">
                ${post.resolvedBy ? `<div class="rounded-pill bg-success text-white px-4 py-2 me-3 font-xssss">Solved</div>` : ``}
                <i class="ti-more-alt text-grey-900 btn-round-md bg-greylight font-xss"></i>
            </div>
        </div>
    
        <h4 class="fw-bold font-xs">${post.title}</h4>
        <div class="card-body p-0 me-lg-5">
            <p class="fw-500 text-grey-500 lh-26 font-xssss w-100 mb-2">
                ${post.body.length > 150 ? `${post.body.slice(0, 150)} <a href="/post/${post.id}" class="fw-600 text-primary ms-2">See more</a>` : post.body}
            </p>
        </div>
    
        ${post.attachment ? `
        <div class="card-body d-block p-0 mb-3">
            <div class="row ps-2 pe-2">
                <div class="col-sm-12 p-1"><img src=${post.attachment} class="rounded-3 w-100" alt="post"></div>
            </div>
        </div>` : ''
        }
    
        <div class="card-body d-flex p-0">
            <div class="emoji-bttn pointer d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss me-2">
                <i class="feather-thumbs-up text-white bg-primary-gradiant me-1 btn-round-xs font-xss"></i>
                <i class="feather-heart text-white bg-red-gradiant me-2 btn-round-xs font-xss"></i>
                ${post.getVoteCount()} Upvotes
            </div>
    
            <a href="/post/${post.id}" class="d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss">
                <i class="feather-message-circle text-dark text-grey-900 btn-round-sm font-lg"></i>
                <span class="d-none-xss">${post.replyCount} Replies</span>
            </a>
    
            <div class="pointer ms-auto d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss" id="dropdownMenu32" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="feather-share-2 text-grey-900 text-dark btn-round-sm font-lg"></i>
                <span class="d-none-xs">Share</span>
            </div>
    
            <div class="dropdown-menu dropdown-menu-end p-4 rounded-xxl border-0 shadow-lg right-0 " aria-labelledby="dropdownMenu32">
                <h4 class="fw-700 font-xss text-grey-900 d-flex align-items-center">Share <i class="feather-x ms-auto font-xssss btn-round-xs bg-greylight text-grey-900 me-2"></i></h4>
                <div class="card-body p-0 d-flex">
                    <ul class="d-flex align-items-center justify-content-between mt-2">
                        <li class="me-1"><span class="btn-round-lg pointer bg-tumblr"><i class="font-xs ti-tumblr text-white"></i></span></li>
                        <li class="me-1"><span class="btn-round-lg pointer bg-youtube"><i class="font-xs ti-youtube text-white"></i></span></li>
                        <li class="me-1"><span class="btn-round-lg pointer bg-flicker"><i class="font-xs ti-flickr text-white"></i></span></li>
                        <li class="me-1"><span class="btn-round-lg pointer bg-black"><i class="font-xs ti-vimeo-alt text-white"></i></span></li>
                        <li><span class="btn-round-lg pointer bg-whatsup"><i class="font-xs feather-phone text-white"></i></span></li>
                    </ul>
                </div>
                <h4 class="fw-700 font-xssss mt-4 text-grey-500 d-flex align-items-center mb-3">Copy Link</h4>
                <i class="feather-copy position-absolute right-35 mt-3 font-xs text-grey-500"></i>
                <input type="text" placeholder="https://studyhub.thepwo.com/post/${post.id}" class="bg-grey text-grey-500 font-xssss border-0 lh-32 p-2 font-xssss fw-600 rounded-3 w-100 theme-dark-bg">
            </div>
        </div>`)

    postCard.onclick = () => window.location.href = `/post/${post.id}`;
    return postCard;
}

async function handleScroll() {
    const {scrollTop, scrollHeight, clientHeight} = document.documentElement;
    if (!loading && !reachedEnd && scrollTop + clientHeight >= scrollHeight - 200) {
        currentPage += 1;
        await fetchPosts();
    }
}

function createSubjectButtons() {
    const subjectButtonsContainer = document.getElementById('subject-buttons');
    subjectButtonsContainer.innerHTML = '';

    subjects.forEach(subject => {
        const buttonDiv = document.createElement('div');
        buttonDiv.classList.add('d-flex', 'flex-row', 'align-items-start');

        const button = document.createElement('button');
        button.type = 'button';
        button.classList.add('btn', 'font-weight-bold', 'me-2', 'mb-2');
        button.innerHTML = `
            <input type="checkbox" class="form-check-input me-2" name="subject" ${subject.name === 'All Subjects' ? 'checked' : ''}>
            <span class="me-2"><i class="bi bi-${subject.icon}"></i></span>
            ${subject.name}
        `;

        async function onclick() {
            const checkbox = button.querySelector('input[type="checkbox"]');
            const subjectName = subject.name.toLowerCase();

            checkbox.checked = !checkbox.checked;

            if (checkbox.checked) selectedSubjects.add(subjectName);
            else selectedSubjects.delete(subjectName);

            document.getElementById('posts-container').innerHTML = '';
            currentPage = 1;
            timestamp = moment();
            reachedEnd = false;
            await fetchPosts();
        }

        button.addEventListener('click', onclick);

        buttonDiv.appendChild(button);
        subjectButtonsContainer.appendChild(buttonDiv);
    });
}
