import User from './user.js';
import Conversation from "./conversation.js";
import { isEqualSets } from "../utils.js";

const socket = io.connect(`/messages/socket`, { rememberTransport: false });

socket.on('bluetick', data => {
   data.forEach(async messageId => {
       const message = await Message.getById(messageId);
       message.readUsers = message.conversation.users;
   });
});

socket.on('edit', async data => {
    const message = await Message.getById(data.id);
    message.content = data.content;
});

class Message {
    static #cache = new Map();

    constructor(id, sender, conversation, content, timestamp, readUsers) {
        if (Message.#cache.has(id)) return Message.#cache.get(id);

        this.id = id;
        this.sender = sender;
        this.conversation = conversation;
        this.content = content;
        this.timestamp = timestamp;
        this.readUsers = readUsers;
        Message.#cache.set(id, this);
    }

    static async fromJson(json) {
        const { id, senderId, conversationId, content, timestamp, readUserIds } = json;
        const sender = await User.getById(senderId);
        const conversation = await Conversation.getById(conversationId);
        const readUsers = await Promise.all(readUserIds.map(async userId => await User.getById(userId)));
        return new Message(id, sender, conversation, content, moment.utc(timestamp), new Set(readUsers));
    }

    static async getById(messageId) {
        if (Message.#cache.has(messageId)) return Message.#cache.get(messageId);

        const response = await fetch(`/api/v1/messages/${messageId}`);
        const messageData = await response.json();

        return await Message.fromJson(messageData);
    }

    read() {
        const data = { 'message_id': this.id };
        socket.emit('read_message', data);
    }

    edit(content) {
        const data = { 'message_id': this.id, 'new_content': content.trim() };
        socket.emit('edit_message', data);
    }

    delete() {
        const data = { 'message_id': this.id };
        socket.emit('delete_message', data);
    }

    readByAll() {
        return isEqualSets(this.readUsers, this.conversation.users);
    }
}

export default Message;