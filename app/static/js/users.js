import { User, Conversation } from "./models/index.js";

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
});