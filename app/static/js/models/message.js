import User from './user.js';
import Conversation from "./conversation.js";
import { isEqualSets } from "../utils.js";

// Establish a socket connection
const socket = io.connect(`/messages/socket`, { rememberTransport: false });

// Listen for bluetick events
socket.on('bluetick', data => {
   // Update readUsers for each message
   data.forEach(async messageId => {
       const message = await Message.getById(messageId);
       message.readUsers = message.conversation.users;
   });
});

// Listen for edit events
socket.on('edit', async data => {
    // Update message content
    const message = await Message.getById(data.id);
    message.content = data.content;
});

class Message {
    // Static cache map for storing Message objects
    static #cache = new Map();

    /**
     * Message class constructor
     * @param {number} id - The ID of the message
     * @param {User} sender - The user who sent the message
     * @param {Conversation} conversation - The conversation the message belongs to
     * @param {string} content - The content of the message
     * @param {Date} timestamp - The timestamp of the message
     * @param {Set<User>} readUsers - The users who have read the message
     */
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

    /**
     * Create a Message object from JSON data
     * @param {object} json - The JSON data representing the message
     * @returns {Message} - The created Message object
     */
    static async fromJson(json) {
        const { id, senderId, conversationId, content, timestamp, readUserIds } = json;
        const sender = await User.getById(senderId);
        const conversation = await Conversation.getById(conversationId);
        const readUsers = await Promise.all(readUserIds.map(async userId => await User.getById(userId)));
        return new Message(id, sender, conversation, content, moment.utc(timestamp), new Set(readUsers));
    }

    /**
     * Get a message by ID
     * @param {number} messageId - The ID of the message to retrieve
     * @returns {Message} - The retrieved Message object
     */
    static async getById(messageId) {
        if (Message.#cache.has(messageId)) return Message.#cache.get(messageId);

        const response = await fetch(`/api/v1/messages/${messageId}`);
        const messageData = await response.json();

        return await Message.fromJson(messageData);
    }

    /**
     * Mark the message as read
     */
    read() {
        const data = { 'message_id': this.id };
        socket.emit('read_message', data);
    }

    /**
     * Edit the message content
     * @param {string} content - The new content of the message
     */
    edit(content) {
        const data = { 'message_id': this.id, 'new_content': content.trim() };
        socket.emit('edit_message', data);
    }

    /**
     * Delete the message
     */
    delete() {
        const data = { 'message_id': this.id };
        socket.emit('delete_message', data);
    }

    /**
     * Check if the message has been read by all users in the conversation
     * @returns {boolean} - True if the message is read by all users, false otherwise
     */
    readByAll() {
        return isEqualSets(this.readUsers, this.conversation.users);
    }
}

export default Message;
