import User from './user.js';
import Reply from "./reply.js";

class Post {
    // Static cache map for storing Post objects
    static #cache = new Map();

    /**
     * Create a new Post object.
     * @param {number} id - The unique ID of the post.
     * @param {string} title - The title of the post.
     * @param {string} body - The body content of the post.
     * @param {User} author - The User object representing the author of the post.
     * @param {Array} votes - An array of Vote objects representing the votes on the post.
     * @param {Date} timestamp - The timestamp indicating when the post was created.
     */
    constructor(id, title, body, author, votes, timestamp) {
        if (Post.#cache.has(id)) return Post.#cache.get(id);

        this.id = id;
        this.title = title;
        this.body = body;
        this.author = author;
        this.votes = votes;
        this.timestamp = timestamp;
        this.replies = [];
        Post.#cache.set(id, this);
    }

    /**
     * Create a Post object from a JSON representation.
     * @param {Object} json - The JSON data representing the post.
     * @returns {Post} - The created Post object.
     */
    static async fromJson(json) {
        const { id, title, body, authorId, votes, timestamp } = json;
        const user = await User.getById(authorId);
        return new Post(id, title, body, user, votes, moment.utc(timestamp));
    }

    /**
     * Create a new post with the given title and body.
     * @param {string} title - The title of the post.
     * @param {string} body - The body content of the post.
     * @returns {Promise<Post>} - A Promise that resolves to the created Post object.
     */
    static async create(title, body) {
        const response = await fetch(`/api/v1/posts/create`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'title': title, 'body': body})
        });

        const jsonData = await response.json();
        return Post.fromJson(jsonData);
    }

    /**
     * Retrieve a post by its ID.
     * @param {number} postId - The ID of the post to retrieve.
     * @returns {Promise<Post|undefined>} - A Promise that resolves to the retrieved Post object,
     *                                      or undefined if the post does not exist.
     */
    static async getById(postId) {
        try {
            const response = await fetch(`/api/v1/posts/${postId}`);
            const postData = await response.json();
            return await Post.fromJson(postData);
        } catch (error) {
            console.error(`Could not retrieve Post by ID: ${postId}`);
            return undefined;
        }
    }

    /**
     * Load the replies associated with this post.
     * @returns {Promise<void>} - A Promise that resolves when the replies are loaded.
     */
    async loadReplies() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/replies`);
            const repliesData = await response.json();
            this.replies = await Promise.all(repliesData.map(async replyData => await Reply.fromJson(replyData)));
        } catch (error) {
            console.error(`Could not load replies for Post ID: ${this.id}`);
        }
    }

    /**
     * Get the total vote count for the post.
     * @returns {number} - The total vote count for the post.
     */
    getVoteCount() {
        return this.votes.map(vote => vote.vote).reduce((accumulator, currentValue) => {
            return accumulator + currentValue;
        }, 0);
    }

    /**
     * Upvote the post.
     * @returns {Promise<void>} - A Promise that resolves when the post is upvoted.
     */
    async upvote() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/upvote`, { method: 'POST' });
            const postData = await response.json();
            this.votes = postData.votes;
        } catch (error) {
            console.error(`Could not upvote post: ${this.id}`);
        }
    }

    /**
     * Downvote the post.
     * @returns {Promise<void>} - A Promise that resolves when the post is downvoted.
     */
    async downvote() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/downvote`, { method: 'POST' });
            const postData = await response.json();
            this.votes = postData.votes;
        } catch (error) {
            console.error(`Could not downvote post: ${this.id}`);
        }
    }

    /**
     * Delete the post.
     * @returns {Promise<void>} - A Promise that resolves when the post is deleted.
     */
    async delete() {
        try {
            await fetch(`/api/v1/posts/${this.id}/delete`, { method: 'DELETE' });
        } catch (error) {
            console.error(`Could not delete post: ${this.id}`);
        }
    }
}

export default Post;
