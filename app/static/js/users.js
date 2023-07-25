import { User, Conversation } from "./models/index.js";

$(document).ready(async function () {
    const username = window.location.pathname.split("/").pop();
    const user = await User.getByUsername(username);
    document.getElementById('username').innerText = user.username;
    document.getElementById('datecreated').innerText = user.dateCreated;
    document.getElementById('email').innerText = user.email;
    const current = await User.getCurrent();
    const message = document.getElementById('message');
    message.style.visibility = 'hidden';
    if (current.id !== user.id) {
        message.style.visibility = 'visible';
    }

    message.onclick = async () => {
        await Conversation.createPrivate(user.id);
        window.location.pathname = 'messages';
    };
});