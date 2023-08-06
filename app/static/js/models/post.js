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
     * @param {string} subject - The subject of the post.
     * @param {User} author - The User object representing the author of the post.
     * @param {Number} replyCount - The number of replies the post has.
     * @param {string} attachment - The attachment of the post, if present.
     * @param {Array} votes - An array of Vote objects representing the votes on the post.
     * @param {Date} timestamp - The timestamp indicating when the post was created.
     */
    constructor(id, title, body, subject, author, votes, replyCount, attachment, timestamp) {
        if (Post.#cache.has(id)) return Post.#cache.get(id);

        this.id = id;
        this.title = title;
        this.body = body;
        this.subject = subject;
        this.author = author;
        this.votes = votes;
        this.replyCount = replyCount;
        this.attachment = attachment;
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
        const { id, title, body, subject, authorId, votes, replyCount, attachment, timestamp } = json;
        const user = await User.getById(authorId);
        return new Post(id, title, body, subject, user, votes, replyCount, attachment, moment.utc(timestamp));
    }

    /**
     * Create a new post with the given title and body.
     * @param {string} title - The title of the post.
     * @param {string} body - The body content of the post.
     * @param {string} subject - The subject of the post.
     * @returns {Promise<Post>} - A Promise that resolves to the created Post object.
     */
    static async create(title, body, subject, attachment) {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('body', body);
        formData.append('subject', subject);
        if (attachment !== undefined) formData.append('file', attachment);

        const response = await fetch(`/api/v1/posts/create`, {
            method: 'POST',
            body: formData,
            contentType: false,
            processData: false,
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
     * Get a list of posts with pagination and before timestamp.
     * @param {number} page - The page number to fetch.
     * @param {number} limit - The number of posts to fetch per page.
     * @param {string|null} before - The timestamp in 'YYYY-MM-DD HH:mm:ss' format to fetch posts created before this timestamp.
     * @param {Set|null} subjects - The set of subjects to filter the posts by.
     * @returns {Promise<Array<Post>>} - A Promise that resolves to an array of Post objects.
     */
    static async getPosts(page, limit, before = null, subjects = null) {
        try {
            let url = `/api/v1/posts/all?page=${page}&limit=${limit}${before ? `&before=${before}` : ''}`;
            if (subjects) url += `&subjects=${Array.from(subjects).join(',')}`;
            console.log(url)
            const response = await fetch(url);
            const postData = await response.json();
            return await Promise.all(postData.map(async post => await Post.fromJson(post)));
        } catch (error) {
            console.error(`Could not fetch posts with pagination`);
            return [];
        }
    }

    static async search(query) {
        try {
            const response = await fetch(`/api/v1/posts/search/${encodeURIComponent(query)}`);
            const postData = await response.json();
            return await Promise.all(postData.map(async post => await Post.fromJson(post)));
        } catch (error) {
            console.error(`Could not search for posts`);
            return [];
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
