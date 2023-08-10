import { Post, Reply, User, Essay } from "./models/index.js";
import { hideLoadingScreen } from "./index.js";
import { gradeColors } from "./essayHome.js";

const essayId = parseInt(window.location.pathname.split('/').pop());

$(document).ready(async function () {
    const essay = await Essay.getById(essayId);
    renderEssay(essay);

    hideLoadingScreen();
});

function renderEssay(essay) {
    document.getElementById('essay-title').value = essay.title;
    document.getElementById('essay-content').value = essay.content;
    document.getElementById('essay-comments').innerText = essay.comment;
    document.getElementById('essay-grade').innerText = essay.grade.replace('_', ' ');
    document.getElementById('essay-grade').style.color = gradeColors[essay.grade];

    $("#essay-content").height($("#essay-content")[0].scrollHeight);

    const suggestionsList = document.getElementById('essay-suggestions');
    essay.suggestions.forEach(suggestion => {
        const div = document.createElement('div');
        div.classList = 'list-group-item bg-transparent border-0 py-1';
        div.innerHTML =
            `<h4 class="fw-600 font-xs">${suggestion.area}</h4>
             <p class="font-xss">${suggestion.problem} ${suggestion.solution}</p>`;
        suggestionsList.appendChild(div);
    });
}