import User from './user.js';

class Essay {
    static #cache = new Map();

    constructor(id, title, content, user, comment, grade, suggestions, timestamp) {
        if (Essay.#cache.has(id)) return Essay.#cache.get(id);

        this.id = id;
        this.title = title;
        this.content = content;
        this.user = user;
        this.comment = comment;
        this.grade = grade;
        this.suggestions = suggestions;
        this.timestamp = timestamp;
        Essay.#cache.set(id, this);
    }

    static async fromJson(json) {
        const { id, topic, essay, userId, comment, grade, suggestions, timestamp } = json;
        const user = await User.getById(userId);
        return new Essay(id, topic, essay, user, comment, grade, suggestions, moment.utc(timestamp));
    }

    // static async grade(title, content) {
    //     const formData = new FormData();
    //     formData.append('title', title);
    //     formData.append('essay', content);
    //
    //     const response = await fetch(`/api/v1/ai/essay/grade`, {
    //         method: 'POST',
    //         body: formData
    //     });
    //
    //     const jsonData = await response.json();
    //     return Essay.fromJson(jsonData);
    // }

    static async getById(essayId) {
        try {
            const response = await fetch(`/api/v1/ai/essay/${essayId}`);
            const essayData = await response.json();
            return await Essay.fromJson(essayData);
        } catch (error) {
            console.error(`Could not retrieve Essay by ID: ${essayId}`);
            return undefined;
        }
    }

    static async getEssays() {
        try {
            const response = await fetch(`/api/v1/ai/essay/all`);
            const essayData = await response.json();
            return await Promise.all(essayData.map(async essay => await Essay.fromJson(essay)));
        } catch (error) {
            console.error(`Could not fetch recent essays`);
            return [];
        }
    }
}

export default Essay;
