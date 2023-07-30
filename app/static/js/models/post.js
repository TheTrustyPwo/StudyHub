import User from './user.js';
import Reply from "./reply.js";

class Post {
    // Static cache map for storing Post objects
    static #cache = new Map();

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

    static async fromJson(json) {
        const {id, title, body, authorId, votes, timestamp} = json;
        const user = await User.getById(authorId);
        return new Post(id, title, body, user, votes, moment.utc(timestamp));
    }

    static async create(title, body) {
        return fetch(`/api/v1/posts/create`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({'title': title, 'body': body})
        })
            .then(response => response.json()).then(json => Post.fromJson(json))
            .catch(err => console.error(`Could not create post! ${err.message}`));
    }

    static async getById(postId) {
        if (Post.#cache.has(postId)) return Post.#cache.get(postId);

        try {
            const response = await fetch(`/api/v1/posts/${postId}`);
            const postData = await response.json();
            return await Post.fromJson(postData);
        } catch (error) {
            console.error(`Could not retrieve Post by ID: ${postId}`);
            return undefined;
        }
    }

    async loadReplies() {
        const response = await fetch(`/api/v1/posts/${this.id}/replies`);
        const replies = await response.json();
        this.replies = await Promise.all(replies.map(async reply => await Reply.fromJson(reply)));
    }

    getVoteCount() {
        return this.votes.map(vote => vote.vote).reduce((accumulator, currentValue) => {
            return accumulator + currentValue
        }, 0);
    }

    async upvote() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/upvote`, { method: 'POST' });
            const postData = await response.json();
            this.votes = postData.votes;
        } catch (error) {
            console.error(`Could not upvote post: ${this.id}`);
            return undefined;
        }
    }

    async downvote() {
        try {
            const response = await fetch(`/api/v1/posts/${this.id}/downvote`, { method: 'POST' });
            const postData = await response.json();
            this.votes = postData.votes;
        } catch (error) {
            console.error(`Could not downvote post: ${this.id}`);
            return undefined;
        }
    }

    async delete() {
        try {
            await fetch(`/api/v1/posts/${this.id}/delete`, { method: 'DELETE' });
        } catch (error) {
            console.error(`Could not delete post: ${this.id}`);
            return undefined;
        }
    }
}

export default Post;
