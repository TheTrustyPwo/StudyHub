import { User, Message, Conversation } from "./models/index.js";

const socket = io.connect(`/messages/socket`, { rememberTransport: false });

$(document).ready(async function () {
    // DOM element references
    const chatUsername = document.getElementById('chat-username');
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    let selectedChatItem = null;

    const chatList = document.getElementById('chat-list');
    // Get all conversations and display them
    const conversations = await Conversation.getAll();
    console.log(conversations);
    for (const conversation of conversations) {
        console.log(conversation);
        await conversation.loadHistory();
        displayConversation(conversation);
    }

    /**
     * Display a conversation in the chat list
     * @param {Conversation} conversation - The conversation to display
     */
    function displayConversation(conversation) {
        const item = document.createElement('li');
        item.classList.add('chat-item');
        item.setAttribute('data-chat-id', conversation.id);

        const latestMessage = conversation.getLastMessage();
        item.innerHTML =
            `<div class='chat-info'>
                <div class='chat-name'>${conversation.name}</div>
                <div class='chat-preview'>${latestMessage === undefined ? '' : latestMessage.content}</div>
                <div class='timestamp'>${latestMessage === undefined ? '' : latestMessage.timestamp.local().calendar()}</div>
            </div>`;
        chatList.appendChild(item);

        item.addEventListener('click', function () {
            if (selectedChatItem) selectedChatItem.classList.remove('selected');

            this.classList.add('selected');
            selectedChatItem = this;
            chatUsername.innerText = this.querySelector('.chat-name').innerText;
            chatMessages.innerHTML = '';

            conversation.history.forEach(message => {
                const li = document.createElement('li');
                li.id = message.id.toLocaleString();
                li.classList.add('message');
                li.innerHTML = `
                    <span class="sender">${message.sender.username}</span>
                    <span class="content">${message.content}</span>
                    <span class="timestamp">(${moment.utc(message.timestamp).local().calendar()})</span>
                    <span class="bluetick">READ: ${message.readByAll()}</span>
                `;
                chatMessages.appendChild(li);
            })

            conversation.read();
        });
    }

    // Send message button click event
    sendButton.addEventListener('click', sendMessage);
    // Message input keypress event
    messageInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') sendMessage();
    });

    /**
     * Send a message
     */
    function sendMessage() {
        let messageToSend = messageInput.value;
        if (messageInput.value.trim() === '') return;
        messageInput.value = "";
        socket.emit('message', {
            'conversation_id': selectedChatItem.getAttribute('data-chat-id'),
            'content': messageToSend
        });
    }

    /**
     * Create a message element
     * @param {Message} message - The message object
     * @returns {HTMLElement} - The created message element
     */
    function createMessageElement(message) {
        const li = document.createElement("li");
        li.id = message.id.toLocaleString();
        li.classList.add('message');
        li.innerHTML = `
            <span class="sender">${message.sender.username}</span>
            <span class="content">${message.content}</span>
            <span class="timestamp">(${moment.utc(message.timestamp).local().calendar()})</span>
            <span class="bluetick">READ: ${message.readByAll()}</span>
        `;
        return li;
    }

    // Event listener for new messages
    socket.on('new_message', async function (data) {
        const message = await Message.fromJson(data);
        console.log(message);
        if (selectedChatItem && selectedChatItem.getAttribute('data-chat-id') === message.conversation.id) {
            chatMessages.appendChild(createMessageElement(message));
            socket.emit('read_message', {'message_id': message.id});
        }
    });

    // Event listener for bluetick (read confirmation)
    socket.on('bluetick', data => {
        console.log(data);
        data.forEach(messageId => {
            const element = document.getElementById(messageId.toLocaleString());
            if (element === undefined) return;
            element.querySelector('.bluetick').innerText = `READ: True`;
        });
    });

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

    // Create conversation button click event
    const createConversationButton = document.getElementById('create-conversation');
    createConversationButton.addEventListener('click', function () {
        const targetUserId = prompt('Enter the user ID to create a conversation with:');
        if (!targetUserId) return;

        Conversation.createPrivate(targetUserId).then(conversation => {
            displayConversation(conversation);
        });
    });

    // Create group conversation button click event
    const createGroupConversationButton = document.getElementById('create-group-conversation');
    createGroupConversationButton.addEventListener('click', function () {
        const groupName = prompt('Enter the group name:');
        if (!groupName) return;

        const userIDsString = prompt('Enter the user IDs (comma-separated) for the group members:');
        if (!userIDsString) return;

        const userIDs = userIDsString.split(',').map(id => id.trim());

        Conversation.createGroup(groupName, userIDs).then(conversation => {
            displayConversation(conversation);
        });
    });

});
