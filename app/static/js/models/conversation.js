import User from './user.js';
import Message from "./message.js";

// Establish a socket connection
const socket = io.connect(`/messages/socket`, {rememberTransport: false});
const current = await User.getCurrent()

class Conversation {
    // Static cache map for storing Conversation objects
    static #cache = new Map();

    /**
     * Conversation class constructor
     * @param {number} id - The ID of the conversation
     * @param {string} name - The name of the conversation
     * @param {string} description - The description of the conversation
     * @param {boolean} isGroup - Indicates if the conversation is a group conversation
     * @param {Set} users - The users participating in the conversation
     * @param {moment} dateCreated - The date and time when the conversation was created
     */
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

    /**
     * Create a Conversation object from JSON data
     * @param {object} json - The JSON data representing the conversation
     * @returns {Conversation|undefined} - The created Conversation object or undefined if JSON data is invalid
     */
    static async fromJson(json) {
        const {id, name, description, isGroup, userIds, dateCreated} = json;

        try {
            // Get users participating in the conversation
            const users = await Promise.all(userIds.map(async userId => await User.getById(userId)));

            // Determine the real name based on the conversation type
            const realName = isGroup ? name : (users[0] === await User.getCurrent() ? users[1].username : users[0].username);

            // Create and return a new Conversation object
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
        return Promise.all(data.map(async conversationData => await Conversation.fromJson(conversationData)));
    }

    /**
     * Get a conversation by ID
     * @param {number} conversationId - The ID of the conversation to retrieve
     * @returns {Conversation|undefined} - The retrieved Conversation object or undefined if not found
     */
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

    /**
     * Create a private conversation
     * @param {number} targetUserId - The ID of the user to create the conversation with
     */
    static createPrivate(targetUserId) {
        socket.emit('create_private_conversation', { 'target_id': targetUserId });
    }

    /**
     * Create a group conversation
     * @param {string} groupName - The name of the group conversation
     * @param {Array<number>} memberIds - The IDs of the users to add to the group conversation
     */
    static createGroup(groupName, memberIds) {
        socket.emit('create_group_conversation', { name: groupName, users: memberIds });
    }

    /**
     * Load the conversation history
     */
    async loadHistory() {
        const response = await fetch(`/api/v1/conversations/history/${this.id}`);
        const history = await response.json();

        this.history = await Promise.all(history.map(async message => {
            const {id, senderId, content, timestamp, readUserIds} = message;
            const sender = await User.getById(senderId);
            const readUsers = await Promise.all(readUserIds.map(async userId => await User.getById(userId)));
            return new Message(id, sender, this, content, moment.utc(timestamp), new Set(readUsers));
        }));
        this.history.sort((a, b) => b.timestamp - a.timestamp);
    }

    /**
     * Mark the conversation as read
     */
    read() {
        const data = {'conversation_id': this.id};
        socket.emit('read_conversation', data);
    }

    /**
     * Send a message in the conversation
     * @param {string} content - The content of the message
     */
    sendMessage(content) {
        const data = {'conversation_id': this.id, 'content': content.trim()};
        socket.emit('message', data);
    }

    /**
     * Get the last message in the conversation
     * @returns {Message|undefined} - The last Message object in the conversation or undefined if no messages
     */
     get latestMessage() {
        if (this.history.length === 0) return undefined;
        return this.history[this.history.length - 1];
    }

    get image() {
         if (this.isGroup) return `/static/assets/default-group.png`;
         else return Array.from(this.users).find(user => user.id !== current.id).pfp;
    }
}

export default Conversation;
