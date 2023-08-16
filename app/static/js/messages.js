import { User, Message, Conversation } from "./models/index.js";

const timestampFormat = {
    sameDay: '[Today] LT',           // Today, show only the time
    lastDay: '[Yesterday] LT',       // Yesterday, show only the time
    lastWeek: 'dddd LT',             // Within the last week, show the day and time
    sameElse: 'DD/MM/YYYY LT'        // Older messages, show full date and time
}

const socket = io.connect(`/messages/socket`, { rememberTransport: false });
const current = await User.getCurrent();

$(document).ready(async function () {
    const messageInput = document.getElementById('message');
    let selectedChatItem = null;

    const chatList = document.getElementById('chat-list');

    const conversations = await Conversation.getAll();
    for (const conversation of conversations) {
        console.log(conversation);
        await conversation.loadHistory();
        displayConversation(conversation);
    }

    const search1 = document.getElementById("search-input1");
    const result1 = document.getElementById("searchResults1");

    search1.addEventListener("input", async function () {
        let limit = 0
        let request = await User.search(search1.value);
        let results = []
        if (request === []) {
            return
        }
        result1.innerHTML = '';

        request.forEach((ele, i) => {
            let out = document.createElement("div");
            out.innerHTML += `<div class="list-group-item list-group-item-action card w-100 shadow-xss border-0 rounded-0 px-4 py-0">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <button aria-label="Close" class="close" type="button">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                                <div class="card-body p-0 d-flex">
                                    <figure class="avatar me-3"><img alt="avater" class="shadow-sm rounded-circle w25"
                                                                     src=${request[i].pfp}></figure>
                                    <h3 class="fw-600 text-grey-900 font-xsss lh-28">${request[i].username}</h3>
                                </div>
                            </div>
                        </div>`;
            out.addEventListener("click", async () => {
                await Conversation.createPrivate(ele.id)
            });
            results.push(out);
        });

        results.forEach(ele => {
            result1.appendChild(ele);
        });
    });

    const searchGroup = document.getElementById("search-group");
    const searchResultGroup = document.getElementById("searchResults2");
    let selectedUsers = [current]

    searchGroup.addEventListener("input", async function () {
        let results = await User.search(searchGroup.value);
        results = results.filter(user => selectedUsers.find(u => u.id === user.id) === undefined);
        searchResultGroup.innerHTML = '';

        results.forEach((ele, i) => {
            let out = document.createElement("div");
            out.innerHTML = `<div class="list-group-item list-group-item-action card w-100 shadow-xss border-0 rounded-0 px-4 py-0" style="z-index: 10;">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <button aria-label="Close" class="close" type="button">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                                <div class="card-body p-0 d-flex">
                                    <figure class="avatar me-3"><img alt="avater" class="shadow-sm rounded-circle w25"
                                                                     src=${results[i].pfp}></figure>
                                    <h3 class="fw-600 text-grey-900 font-xsss lh-28">${results[i].username}</h3>
                                </div>
                            </div>
                        </div>`;
            searchResultGroup.appendChild(out);
            out.addEventListener("click", async () => {
                selectedUsers.push(ele);
                out.remove();
                console.log(selectedUsers);
                document.getElementById("pending").innerHTML += `<div class="list-group-item list-group-item-action card w-100 shadow-xss border-0 rounded-0 px-4 py-0">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <button aria-label="Close" class="close" type="button">
                                    <span aria-hidden="true">&times;</span>
                                </button>
                                <div class="card-body p-0 d-flex">
                                    <figure class="avatar me-3"><img alt="avater" class="shadow-sm rounded-circle w25"
                                                                     src=${ele.pfp}></figure>
                                    <h3 class="fw-600 text-grey-900 font-xsss lh-28">${ele.username}</h3>
                                </div>
                            </div>
                        </div>`
            });
        });
    });

    document.getElementById('close-group').onclick = async () => {
        selectedUsers = [current];
        console.log(selectedUsers)
    }

    document.getElementById('submit-group').onclick = async () => {
        console.log(selectedUsers);
        Conversation.createGroup("Me group", selectedUsers.map(user => user.id));
    }

    /**
     * Display a conversation in the chat list
     * @param {Conversation} conversation - The conversation to display
     */
    function displayConversation(conversation) {
        const item = document.createElement('div');
        item.setAttribute('data-chat-id', conversation.id);

        const latestMessage = conversation.latestMessage;
        item.innerHTML =
            DOMPurify.sanitize(latestMessage ?
                `<div class="card w-100 border-0 py-2 px-3">
                    <div class="card-body p-0 d-flex">
                        <figure class="avatar me-3"><img src="${conversation.image}" alt="avater" class="shadow-sm rounded-circle w40"></figure>
                        <div>
                            <h4 class="fw-700 text-grey-900 font-xsss">${conversation.name}</h4>
                            <span class="d-block font-xssss fw-500 lh-3 text-grey-500">${latestMessage.content}</span>
                        </div>
                        <span class="ms-auto font-xssss fw-600 text-grey-700">${latestMessage.timestamp.calendar(null, timestampFormat)}</span>
                    </div>
                </div>` :
                `<div class="card w-100 border-0 py-2 px-3">
                    <div class="card-body p-0 d-flex">
                        <figure class="avatar me-3"><img src="${conversation.image}" alt="avater" class="shadow-sm rounded-circle w40"></figure>
                        <div>
                            <h4 class="fw-700 text-grey-900 font-xsss">${conversation.name}</h4>
                            <span class="d-block font-xssss fw-500 lh-3 text-grey-500">No messages yet.</span>
                        </div>
                        <span class="d-none ms-auto font-xssss fw-600 text-grey-700"></span>
                    </div>
                </div>`);

        document.getElementById('conversations').appendChild(item);

        item.addEventListener('click', async function () {
            if (selectedChatItem) selectedChatItem.classList.remove('selected');
            this.classList.add('selected');
            selectedChatItem = this;

            document.getElementById('chat-pfp').src = conversation.image;
            document.getElementById('chat-username').innerText = conversation.name;

            await conversation.loadHistory();
            displayMessages(conversation);
            document.getElementById('chat-wrap').scrollTop = document.getElementById('chat-wrap').scrollHeight;

            conversation.read();
        });
    }

    function displayMessages(conversation) {
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = ``;
        conversation.history.forEach(msg => messagesDiv.prepend(renderMessage(msg)))
    }

    function renderMessage(message) {
        const div = document.createElement('div');
        div.classList = `message-item ${message.sender.id === current.id ? `outgoing-message` : ``}`;
        div.setAttribute('data-message-id', message.id);

        div.innerHTML = DOMPurify.sanitize(
            `<div class="message-user">
                <figure class="avatar"><img src="${message.sender.pfp}" alt="avatar"></figure>
                <div><h5>${message.sender.username}</h5>
                    <div class="time">${message.timestamp.calendar(null, timestampFormat)}</div>
                </div>
            </div>
            <div class="message-wrap">${message.content}</div>`
        );

        return div;
    }

    document.getElementById('message-button').addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') sendMessage();
    });

    function sendMessage() {
        const messageInput = document.getElementById('message');
        if (messageInput.value.trim() === '') return;

        const messageToSend = messageInput.value;
        messageInput.value = '';

        socket.emit('message', {
            'conversation_id': selectedChatItem.getAttribute('data-chat-id'),
            'content': messageToSend
        });
    }

    socket.on('new_message', async function (data) {
        const message = await Message.fromJson(data);
        message.conversation.history.push(message);
        if (selectedChatItem && selectedChatItem.getAttribute('data-chat-id') === message.conversation.id) {
            console.log(message)
            document.getElementById('messages').appendChild(renderMessage(message));
            document.getElementById('chat-wrap').scrollTop = document.getElementById('chat-wrap').scrollHeight;
            socket.emit('read_message', {'message_id': message.id});
        }
    });

    // Event listener for bluetick (read confirmation)
    // socket.on('bluetick', data => {
    //     console.log(data);
    //     data.forEach(messageId => {
    //         const element = document.getElementById(messageId.toLocaleString());
    //         if (element === undefined) return;
    //         element.querySelector('.bluetick').innerText = `READ: True`;
    //     });
    // });

    // Event listener for message edits
    socket.on('edit', data => {
        console.log(data);
        const element = document.getElementById(data.id.toLocaleString());
        if (element === undefined) return;
        element.querySelector('.content').innerText = data.content;
    });

    // Event listener for message deletions
    socket.on('delete', data => {
        console.log(data);
        const element = document.getElementById(data.id.toLocaleString());
        if (element === undefined) return;
        element.remove();
    });

    socket.on('error', data => console.log(data));

    socket.on('new_conversation', async data => displayConversation(await Conversation.fromJson(data)));

});
