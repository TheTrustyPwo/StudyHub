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
     */
    constructor(id, email, username, dateCreated) {
        if (User.#cache.has(id)) return User.#cache.get(id);

        this.id = id;
        this.email = email;
        this.username = username;
        this.dateCreated = dateCreated;
        User.#cache.set(id, this);
    }

    /**
     * Create a User object from JSON data
     * @param {object} json - The JSON data representing the user
     * @returns {User} - The created User object
     */
    static fromJson(json) {
        const { id, email, username, dateCreated } = json;
        return new User(id, email, username, moment.utc(dateCreated));
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
}

export default User;
