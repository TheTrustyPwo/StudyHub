class User {
    // Static cache map for storing User objects
    static #cache = new Map();
    // Reference to the current user
    static #currentUser = undefined;

    /**
     * User class constructor
     * @param {number} id - The ID of the user
     * @param {string} email - The email of the user
     * @param {string} username - The username of the user
     * @param {Date} dateCreated - The date the user was created
     * @param {string} pfp - The profile picture URL of the user
     */
    constructor(id, email, username, dateCreated, pfp) {
        if (User.#cache.has(id)) return User.#cache.get(id);

        this.id = id;
        this.email = email;
        this.username = username;
        this.dateCreated = dateCreated;
        this.pfp = pfp;
        User.#cache.set(id, this);
    }

    async updateProfilePicture(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/v1/users/pfp/upload', {
            method: 'POST',
            body: formData
        });

        const json = await response.json();
        this.pfp = json.url;
    }

    /**
     * Create a User object from JSON data
     * @param {object} json - The JSON data representing the user
     * @returns {User} - The created User object
     */
    static fromJson(json) {
        const { id, email, username, dateCreated, pfp } = json;
        return new User(id, email, username, moment.utc(dateCreated), pfp);
    }

    /**
     * Get the current user
     * @returns {User} - The current User object
     */
    static async getCurrent() {
        if (User.#currentUser !== undefined) return User.#currentUser;

        const response = await fetch(`/api/v1/users/current`);
        const userData = await response.json();

        return User.fromJson(userData);
    }

    /**
     * Get a user by ID
     * @param {number} userId - The ID of the user to retrieve
     * @returns {User} - The retrieved User object
     */
    static async getById(userId) {
        if (User.#cache.has(userId)) return User.#cache.get(userId);

        const response = await fetch(`/api/v1/users/${userId}`);
        const userData = await response.json();

        return User.fromJson(userData);
    }

    /**
     * Get a user by username
     * @param {string} username - The username of the user to retrieve
     * @returns {User} - The retrieved User object
     */
    static async getByUsername(username) {
        const response = await fetch(`/api/v1/users/${username}`);
        const userData = await response.json();

        return User.fromJson(userData);
    }

    static async getUserPosts(page, limit, userid) {
        try {
            let url = `/api/v1/posts/user?page=${page}&limit=${limit}&id=${userid}`;
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error(`Could not fetch posts from user`);
            return [];
        }
    }
}

export default User;
