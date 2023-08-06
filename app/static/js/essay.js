import { Post, Reply, User, Essay } from "./models/index.js";
import { hideLoadingScreen } from "./index.js";

const essayId = parseInt(window.location.pathname.split('/').pop());

$(document).ready(async function () {
    const essay = await Essay.getById(essayId);
    renderEssay(essay);

    hideLoadingScreen();
});

function renderEssay(essay) {
    document.getElementById('essay-title').value = essay.title;
    document.getElementById('essay-content').value = essay.content;

    const complimentsList = document.getElementById('essay-compliments');
    essay.suggestions.forEach(compliment => {
        complimentsList.innerHTML += `<li class="list-group-item bg-transparent border-0 py-1">${compliment.area} \n${compliment.problem} \n${compliment.solution}</li>`;
    });
}