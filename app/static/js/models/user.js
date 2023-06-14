class User {
    static #cache = new Map();
    static #currentUser = undefined;

    constructor(id, email, username, dateCreated) {
        if (User.#cache.has(id)) return User.#cache.get(id);

        this.id = id;
        this.email = email;
        this.username = username;
        this.dateCreated = dateCreated;
        User.#cache.set(id, this);
    }

    static async fromJson(json) {
        const { id, email, username, dateCreated } = json;
        return new User(id, email, username, moment.utc(dateCreated));
    }

    static async getCurrent() {
        if (User.#currentUser !== undefined) return User.#currentUser;

        const response = await fetch(`/api/v1/users/current`);
        const userData = await response.json();

        return await User.fromJson(userData);
    }


    static async getById(userId) {
        if (User.#cache.has(userId)) return User.#cache.get(userId);

        const response = await fetch(`/api/v1/users/${userId}`);
        const userData = await response.json();

        return await User.fromJson(userData);
    }
}

export default User;