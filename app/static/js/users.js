import { Post, User, Conversation } from "./models/index.js";

$(document).ready(async function () {
    const username = window.location.pathname.split("/").pop();
    const user = await User.getByUsername(username);
    const date = new Date(user.dateCreated.toLocaleString());
    document.getElementById('username').innerText = user.username;
    document.getElementById('email').innerText = user.email;

    await setLatestPosts(user.id)
    // document.getElementById('pfp').innerHTML = user.pfp;
    // const current = await User.getCurrent();
    // const message = document.getElementById('message');
    // const upload = document.getElementById('displayfile');
    //
    // if (current.id !== user.id) {
    //     message.style.visibility = 'visible';
    // } else {
    //     upload.style.visibility = 'visible';
    // }
    //
    // message.onclick = async () => {
    //     await Conversation.createPrivate(user.id);
    //     window.location.pathname = 'messages';
    // };


});

async function setLatestPosts(user_id) {
    const post = await Post.getLatestPostByUser(user_id);
    document.getElementById('latestpost').innerHTML = `<div class="card w-100 shadow-xss rounded-xxl border-0 p-4 mb-3">
                            <div class="card-body p-0 d-flex">
                                <figure class="avatar me-3"><img alt="avater" class="shadow-sm rounded-circle w45"
                                                                 src="/static/assets/pwo.png"></figure>
                                <h4 class="fw-700 text-grey-900 font-xssss mt-1">${post.author.username}
                                    <span class="d-block font-xssss fw-500 mt-1 lh-3 text-grey-500">${timeSince(post.timestamp)}</span>
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
                                    class="fw-500 text-grey-500 lh-26 font-xssss w-100 mb-2">${post.body}}<a
                                        class="fw-600 text-primary ms-2" href=${window.location.href.split("/")[0] + "/post/" + post.id}>See more</a></p></div>
                            <div class="card-body d-flex p-0">
                                <div class="emoji-bttn pointer d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss me-2">
                                    <i class="feather-thumbs-up text-white bg-primary-gradiant me-1 btn-round-xs font-xss"></i>
                                    <i class="feather-heart text-white bg-red-gradiant me-2 btn-round-xs font-xss"></i>${post.getVoteCount()}
                                    Like
                                </div>
                                <a class="d-flex align-items-center fw-600 text-grey-900 text-dark lh-26 font-xssss"><i
                                        class="feather-message-circle text-dark text-grey-900 btn-round-sm font-lg"></i><span
                                        class="d-none-xss">${post.votes.length}</span></a>
                            </div>
                        </div>`;
}

function timeSince(date) {
    const seconds = Math.floor((new Date() - Date.parse(date)) / 1000);

    let interval = seconds / 31536000;

    if (interval > 1) {
        return Math.floor(interval) + " years";
    }
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " months";
    }
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " days";
    }
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hours";
    }
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minutes";
    }
    return Math.floor(seconds) + " seconds";
}

// async function uploadFile(file) {
//     const formData = new FormData();
//
//     formData.append('file', file);
//
//     const response = await fetch('/api/v1/users/pfp/upload', {
//         method: 'POST',
//         body: formData,
//         purpose: "PROFILE_PICTURE"
//     });
//
//     if (response.ok) {
//         console.log('File uploaded successfully:', response);
//     } else {
//         console.error('Error uploading file:', response);
//     }
// }
//
// async function refresh(){
//     location.reload();
// }
// document.getElementById('upload-btn').addEventListener('change', async () => {
//     const fileInput = document.getElementById('upload');
//     const file = fileInput.files[0];
//     if (file) {
//         await uploadFile(file);
//     }
//     await refresh()
// });