import { User, Conversation } from "./models/index.js";


$(document).ready(async function () {
    const username = window.location.pathname.split("/").pop();
    const user = await User.getByUsername(username);
    const date = new Date(user.dateCreated.toLocaleString());
    document.getElementById('username').innerText = user.username;
    document.getElementById('datecreated').innerText = date.toDateString();
    document.getElementById('email').innerText = user.email;
    document.getElementById('pfp').innerHTML = user.pfp;
    const current = await User.getCurrent();
    const message = document.getElementById('message');
    const upload = document.getElementById('displayfile');

    if (current.id !== user.id) {
        message.style.visibility = 'visible';
    } else {
        upload.style.visibility = 'visible';
    }

    message.onclick = async () => {
        await Conversation.createPrivate(user.id);
        window.location.pathname = 'messages';
    };


});

async function uploadFile(file) {
    const formData = new FormData();

    formData.append('file', file);

    const response = await fetch('/api/v1/users/pfp/upload', {
        method: 'POST',
        body: formData,
        purpose: "PROFILE_PICTURE"
    });

    if (response.ok) {
        console.log('File uploaded successfully:', response);
    } else {
        console.error('Error uploading file:', response);
    }
}

async function refresh(){
    location.reload();
}
document.getElementById('upload-btn').addEventListener('change', async () => {
    const fileInput = document.getElementById('upload');
    const file = fileInput.files[0];
    if (file) {
        await uploadFile(file);
    }
    await refresh()
});