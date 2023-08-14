import User from './user.js';
import Reply from "./reply.js";

class Post {
    static #cache = new Map();

    constructor(id) {
        if (Post.#cache.has(id)) return Post.#cache.get(id);
        this.id = id;
        Post.#cache.set(id, this);
    }

    get title() {
        return this._title;
    }

    set title(title) {
        this._title = title;
    }

    get body() {
        return this._body;
    }

    set body(body) {
        this._body = body;
    }

    get subject() {
        return this._subject;
    }

    set subject(subject) {
        this._subject = subject;
    }

    get author() {
        return this._author;
    }

    set author(author) {
        this._author = author;
    }

    get votes() {
        return this._votes;
    }

    set votes(votes) {
        this._votes = votes;
    }

    get replyCount() {
        return this._replyCount;
    }

    set replyCount(replyCount) {
        this._replyCount = replyCount;
    }

    get attachment() {
        return this._attachment;
    }

    set attachment(attachment) {
        this._attachment = attachment;
    }

    get timestamp() {
        return this._timestamp;
    }

    set timestamp(timestamp) {
        this._timestamp = timestamp;
    }

    get resolvedBy() {
        return this._resolvedBy;
    }

    set resolvedBy(resolvedBy) {
        this._resolvedBy = resolvedBy;
    }

    get replies() {
        return this._replies;
    }

    set replies(replies) {
        this._replies = replies;
    }

    /**
     * Create a Post object from a JSON representation.
     * @param {Object} json - The JSON data representing the post.
     * @returns {Post} - The created Post object.
     */
    static async fromJson(json) {
        const { id, title, body, subject, authorId, votes, replyCount, attachment, resolvedById, timestamp } = json;
        const user = await User.getById(authorId);

        const post = new Post(id);
        post.title = title;
        post.body = body;
        post.subject = subject;
        post.author = user;
        post.votes = votes;
        post.replyCount = replyCount;
        post.attachment = attachment;
        post.timestamp = moment.utc(timestamp);
        post.resolvedBy = resolvedById ? await Reply.getById(resolvedById) : undefined;

        return post;
    }

    /**
     * Create a new post with the given title and body.
     * @param {string} title - The title of the post.
     * @param {string} body - The body content of the post.
     * @param {string} subject - The subject of the post.
     * @param attachment
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
     * @param {Moment|null} before - The timestamp to fetch posts created before this timestamp.
     * @param {Set|null} subjects - The set of subjects to filter the posts by.
     * @returns {Promise<Array<Post>>} - A Promise that resolves to an array of Post objects.
     */
    static async getPosts(page, limit, before = null, subjects = null) {
        try {
            let url = `/api/v1/posts/all?page=${page}&limit=${limit}${before ? `&before=${before.unix()}` : ''}`;
            if (subjects) url += `&subjects=${Array.from(subjects).join(',')}`;
            const response = await fetch(url);
            const postData = await response.json();
            return await Promise.all(postData.map(async post => await Post.fromJson(post)));
        } catch (error) {
            console.error(`Could not fetch posts with pagination`, error);
            return [];
        }
    }

    static async search(query, limit = 5) {
        try {
            const response = await fetch(`/api/v1/posts/search?query=${encodeURIComponent(query)}&limit=${limit}`);
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

    async resolve(reply) {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/resolve?reply_id=${reply.id}`, {method: 'POST'});
            const postData = await response.json();
            return Post.fromJson(postData);
        } catch (error) {
            console.error(`Could not resolve post: ${this.id}`)
        }
    }

    /**
     * Upvote the post.
     * @returns {Promise<void>} - A Promise that resolves when the post is upvoted.
     */
    async upvote() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/upvote`, {method: 'POST'});
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
            const response = await fetch(`/api/v1/posts/${this.id}/downvote`, {method: 'POST'});
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
            await fetch(`/api/v1/posts/${this.id}/delete`, {method: 'DELETE'});
        } catch (error) {
            console.error(`Could not delete post: ${this.id}`);
        }
    }
}

export default Post;
