import User from "./user.js";
import Post from "./post.js";

class Reply {
    static #cache = new Map();

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

    static async fromJson(json) {
        const { id, authorId, postId, reply, votes, timestamp } = json;
        const author = await User.getById(authorId);
        const post = await Post.getById(postId);
        return new Reply(id, author, post, reply, votes, moment.utc(timestamp));
    }

    static async create(reply, post) {
        return fetch(`/api/v1/replies/create`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({'post_id': post.id, 'reply': reply})
        })
            .then(response => response.json()).then(json => Reply.fromJson(json))
            .catch(err => console.error(`Could not create reply! ${err.message}`));
    }

    static async getById(replyId) {
        if (Reply.#cache.has(replyId)) return Reply.#cache.get(replyId);

        const response = await fetch(`/api/v1/replies/${replyId}`);
        const replyData = await response.json();

        return Reply.fromJson(replyData);
    }

    getVoteCount() {
        return this.votes.map(vote => vote.vote).reduce((accumulator, currentValue) => {
            return accumulator + currentValue
        }, 0);
    }

    async upvote() {
        try {
            const response = await fetch(`/api/v1/replies/${this.id}/upvote`, { method: 'POST' });
            const replyData = await response.json();
            this.votes = replyData.votes;
        } catch (error) {
            console.error(`Could not upvote reply: ${this.id}`);
            return undefined;
        }
    }

    async downvote() {
        try {
            const response = await fetch(`/api/v1/replies/${this.id}/downvote`, { method: 'POST' });
            const replyData = await response.json();
            this.votes = replyData.votes;
        } catch (error) {
            console.error(`Could not downvote reply: ${this.id}`);
            return undefined;
        }
    }
}

export default Reply;
