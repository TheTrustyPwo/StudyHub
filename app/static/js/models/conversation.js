import User from './user.js';
import Message from "./message.js";

const socket = io.connect(`/messages/socket`, {rememberTransport: false});

socket.on('new_message', async message => {
    const { id, senderId, conversationId, content, timestamp, readUserIds } = message;
    const sender = await User.getById(senderId);
    const conversation = await Conversation.getById(conversationId);
    const readUsers = await readUserIds.map(async userId => await User.getById(userId));
    conversation.history.push(new Message(id, sender, conversation, content, new Date(timestamp), new Set(readUsers)));
});

class Conversation {
    static #cache = new Map();

    constructor(id, name, description, isGroup, users, dateCreated) {
        if (Conversation.#cache.has(id)) return Conversation.#cache.get(id);

        this.id = id;
        this.name = name;
        this.description = description;
        this.isGroup = isGroup;
        this.users = users;
        this.dateCreated = dateCreated;
        this.history = [];
        Conversation.#cache.set(id, this);
    }

    static async fromJson(json) {
        const { id, name, description, isGroup, userIds, dateCreated } = json;

        try {
            const users = await Promise.all(userIds.map(async userId => await User.getById(userId)));
            const realName = isGroup ? name : (users[0] === await User.getCurrent() ? users[1].username : users[0].username);
            return new Conversation(id, realName, description, isGroup, new Set(users), moment.utc(dateCreated));
        } catch (error) {
            console.error(`Cannot parse invalid Conversation JSON of ID: ${id}`);
            console.debug(json);
            return undefined;
        }
    }

    static async getAll() {
        const response = await fetch(`/api/v1/conversations/all`);
        const data = await response.json();
        console.log(data);
        const conversations = await Promise.all(data.map(async conversationData => await Conversation.fromJson(conversationData)));
        return conversations.filter(convo => convo !== undefined);
    }

    static async getById(conversationId) {
        if (Conversation.#cache.has(conversationId)) return Conversation.#cache.get(conversationId);

        try {
            const response = await fetch(`/api/v1/conversations/${conversationId}`);
            const conversationData = await response.json();

            return await Conversation.fromJson(conversationData);
        } catch (error) {
            console.error(`Could not retrieve Conversation by ID: ${conversationId}`);
            return undefined;
        }
    }

    static async createPrivate(targetUserId) {
        const data = { target: targetUserId };
        const response = await fetch('/api/v1/conversations/new/private', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        const conversationData = await response.json();

        return await Conversation.fromJson(conversationData);
    }

    static async createGroup(groupName, memberIds) {
        const data = { name: groupName, users: memberIds };
        const response = await fetch('/api/v1/conversations/new/group', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        const conversationData = await response.json();

        return await Conversation.fromJson(conversationData);
    }

    async loadHistory() {
        const response = await fetch(`/api/v1/conversations/history/${this.id}`);
        const history = await response.json();

        this.history = await Promise.all(history.map(async message => {
            const { id, senderId, content, timestamp, readUserIds } = message;
            const sender = await User.getById(senderId);
            const readUsers = await Promise.all(readUserIds.map(async userId => await User.getById(userId)));
            return new Message(id, sender, this, content, moment.utc(timestamp), new Set(readUsers));
        }));
    }

    read() {
        const data = {'conversation_id': this.id};
        socket.emit('read_conversation', data);
    }

    sendMessage(content) {
        const data = {'conversation_id': this.id, 'content': content.trim()};
        socket.emit('message', data);
    }

    getLastMessage() {
        if (this.history.length === 0) return undefined;
        return this.history[this.history.length - 1];
    }
}

export default Conversation;