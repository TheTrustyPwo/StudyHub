import {Conversation, User} from "./models/index.js";

const username = window.location.pathname.split("/").pop();
const user = await User.getByUsername(username);
$(document).ready(async function () {
    document.getElementById('username').innerText = user.username;
    document.getElementById('email').innerText = user.email;
    document.getElementById('pfp').src = user.pfp;

    document.getElementById('message').onclick = async () => {
        await Conversation.createPrivate(user.id);
        window.location.pathname = 'messages';
    };

    if (user.id === (await User.getCurrent()).id) {
        document.getElementById("pfp-text").style.visibility = "visible";
        const profileImage = document.getElementById("pfp");
        const fileInput = document.getElementById("profile-picture");
        fileInput.addEventListener("change", async function (event) {
            const selectedFile = fileInput.files[0];
            await uploadFile(selectedFile);
        });
    } else {
        document.getElementById("message").style.visibility = "visible";
        document.getElementById("profile-picture").remove();
    }


    // profileImage.addEventListener("click", function() {
    //     fileInput.click();
    // });

    await fetchUserPosts();
});

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/v1/users/pfp/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            location.reload();
        } else {
            console.error('Error uploading file:', response);
        }
    } catch (error) {
        console.error('Error uploading file:', error);
    }
}

window.addEventListener('scroll', handleScroll);

let currentPage = 1;
const postsPerPage = 2;
let reachedEnd = false;
let lastPostTimestamp = null;

async function fetchUserPosts() {
    const posts = await User.getUserPosts(currentPage, postsPerPage, user.id);
    const postsContainer = document.getElementById('posts');

    if (posts.length > 0) {
        lastPostTimestamp = posts[posts.length - 1].timestamp;
        posts.forEach(post => {
            createPostCard(post);
        });
    } else reachedEnd = true;
}

function createPostCard(post) {
    document.getElementById('posts').innerHTML += `<div class="card w-100 shadow-xss rounded-xxl border-0 p-4 mb-3">
                            <div class="card-body p-0 d-flex">
                                <figure class="avatar me-3"><img alt="avater" class="shadow-sm rounded-circle w45"
                                                                 src=${document.getElementById("pfp").src}></figure>
                                <h4 class="fw-700 text-grey-900 font-xssss mt-1">${user.username}
                                    <span class="d-block font-xssss fw-500 mt-1 lh-3 text-grey-500">${post.timestamp}</span>
                                </h4>
                                <div class="ms-auto pointer">
                                    <i class="ti-more-alt text-grey-900 btn-round-md bg-greylight font-xss"></i></div>
                            </div>
                            <div class="card-body p-0 me-lg-5">
                                <p class="fw-500 text-grey-500 lh-26 font-xssss w-100 mb-2">
                                    <h1 class="fw-700 mb-0 mt-0 font-md text-grey-900 d-flex">${post.title}</h1>
                                </p>
                            </div>
<!--                            <div class="card-body p-0 mb-3 rounded-3 overflow-hidden uttam-die">-->
<!--                                <a class="video-btn" href="/defaultvideo">-->
<!--                                    <video autoplay="" class="float-right w-100" loop="">-->
<!--                                        <source src="assets/images/v-1.mp4" type="video/mp4">-->
<!--                                    </video>-->
<!--                                </a>-->
<!--                            </div>-->
                            <div class="card-body p-0 me-lg-5"><p
                                    class="fw-500 text-grey-500 lh-26 font-xssss w-100 mb-2">${post.body}<a
                                        class="fw-600 text-primary ms-2" href=${window.location.href.split("/")[0] + "/post/" + post.id}>See more</a></p></div>
                            <div class="card-body d-flex p-0">
                                <div class="emoji-bttn pointer d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss me-2">
                                    <i class="feather-thumbs-up text-white bg-primary-gradiant me-1 btn-round-xs font-xss"></i>
                                    <i class="feather-heart text-white bg-red-gradiant me-2 btn-round-xs font-xss"></i>${post.votes.length}
                                    Like
                                </div>
                                <a class="d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss"><i
                                        class="feather-message-circle text-dark text-grey-900 btn-round-sm font-lg"></i><span
                                        class="d-none-xss">${post.votes.length}</span></a>
                            </div>
                        </div>`;
}

async function handleScroll() {
    const {scrollTop, scrollHeight, clientHeight} = document.documentElement;
    if (!reachedEnd && scrollTop + clientHeight >= scrollHeight - 200) {
        currentPage += 1;
        await fetchUserPosts();
    }
}