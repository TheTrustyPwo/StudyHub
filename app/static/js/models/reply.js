import User from "./user.js";
import Post from "./post.js";

class Reply {
    static #cache = new Map();

    constructor(id) {
        if (Reply.#cache.has(id)) return Reply.#cache.get(id);
        this.id = id;
        Reply.#cache.set(id, this);
    }

    get author() {
        return this._author;
    }

    set author(author) {
        this._author = author;
    }

    get post() {
        return (async () => {
            this._post = this._post || await Post.getById(this._postId);
            return this._post;
        })();
    }

    set postId(postId) {
        this._postId = postId;
    }

    get reply() {
        return this._reply;
    }

    set reply(value) {
        this._reply = value;
    }

    get votes() {
        return this._votes;
    }

    set votes(value) {
        this._votes = value;
    }

    get timestamp() {
        return this._timestamp;
    }

    set timestamp(value) {
        this._timestamp = value;
    }

    /**
     * Create a Reply object from a JSON representation.
     * @param {Object} json - The JSON data representing the reply.
     * @returns {Reply} - The created Reply object.
     */
    static async fromJson(json) {
        const { id, authorId, postId, text, votes, timestamp } = json;
        const reply = new Reply(id);

        reply.reply = text;
        reply.votes = votes;
        reply.timestamp = moment.utc(timestamp);
        reply.postId = postId;
        reply.author = await User.getById(authorId);

        return reply;
    }

    /**
     * Create a new reply for a specific post.
     * @param {string} reply - The content of the reply.
     * @param {Post} post - The Post object to which the reply will be associated.
     * @returns {Promise<Reply>} - A Promise that resolves to the created Reply object.
     */
    static async create(reply, post) {
        const response = await fetch(`/api/v1/replies/create`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'post_id': post.id, 'reply': reply})
        });

        const jsonData = await response.json();
        return Reply.fromJson(jsonData);
    }

    /**
     * Retrieve a reply by its ID.
     * @param {number} replyId - The ID of the reply to retrieve.
     * @returns {Promise<Reply|undefined>} - A Promise that resolves to the retrieved Reply object,
     *                                       or undefined if the reply does not exist.
     */
    static async getById(replyId) {
        if (Reply.#cache.has(replyId)) return Reply.#cache.get(replyId);

        try {
            const response = await fetch(`/api/v1/replies/${replyId}`);
            const replyData = await response.json();
            return Reply.fromJson(replyData);
        } catch (error) {
            console.error(`Could not retrieve Reply by ID: ${replyId}`);
            return undefined;
        }
    }

    /**
     * Get the total vote count for the reply.
     * @returns {number} - The total vote count for the reply.
     */
    getVoteCount() {
        return this.votes.map(vote => vote.vote).reduce((accumulator, currentValue) => {
            return accumulator + currentValue;
        }, 0);
    }

    /**
     * Upvote the reply.
     * @returns {Promise<void>} - A Promise that resolves when the reply is upvoted.
     */
    async upvote() {
        try {
            const response = await fetch(`/api/v1/replies/${this.id}/upvote`, { method: 'POST' });
            const replyData = await response.json();
            this.votes = replyData.votes;
        } catch (error) {
            console.error(`Could not upvote reply: ${this.id}`);
        }
    }

    /**
     * Downvote the reply.
     * @returns {Promise<void>} - A Promise that resolves when the reply is downvoted.
     */
    async downvote() {
        try {
            const response = await fetch(`/api/v1/replies/${this.id}/downvote`, { method: 'POST' });
            const replyData = await response.json();
            this.votes = replyData.votes;
        } catch (error) {
            console.error(`Could not downvote reply: ${this.id}`);
        }
    }
}

export default Reply;
