import { Post } from "./models/index.js";

$(document).ready(async function () {
    const title = document.getElementById('title');
    const body = document.getElementById('body');
    const subject = document.getElementById('subject');
    const submit = document.getElementById('submit');

    submit.onclick = async () => {
        const post = await Post.create(title.value, body.value, subject.value);
        window.location.pathname = `/post/${post.id}`
    }
});