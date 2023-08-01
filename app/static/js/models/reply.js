import User from "./user.js";
import Post from "./post.js";

class Reply {
    static #cache = new Map();

    /**
     * Create a new Reply object.
     * @param {number} id - The unique ID of the reply.
     * @param {User} author - The User object representing the author of the reply.
     * @param {Post} post - The Post object representing the post to which this reply belongs.
     * @param {string} reply - The content of the reply.
     * @param {Array} votes - An array of Vote objects representing the votes on the reply.
     * @param {Date} timestamp - The timestamp indicating when the reply was created.
     */
    constructor(id, author, post, reply, votes, timestamp) {
        if (Reply.#cache.has(id)) return Reply.#cache.get(id);

        this.id = id;
        this.author = author;
        this.post = post;
        this.reply = reply;
        this.votes = votes;
        this.timestamp = timestamp;
        Reply.#cache.set(id, this);
    }

    /**
     * Create a Reply object from a JSON representation.
     * @param {Object} json - The JSON data representing the reply.
     * @returns {Reply} - The created Reply object.
     */
    static async fromJson(json) {
        const { id, authorId, postId, reply, votes, timestamp } = json;
        const author = await User.getById(authorId);
        const post = await Post.getById(postId);
        return new Reply(id, author, post, reply, votes, moment.utc(timestamp));
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
