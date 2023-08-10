import { Essay } from "./models/index.js";

const gradeColors = {
    'BAD': '#FF0000',          // Red for poor
    'FAIR': '#FFA500',         // Orange for fair
    'SATISFACTORY': '#F5BD1F', // Orange yellow for satisfactory
    'GOOD': '#90EE90',         // Light green for good
    'VERY_GOOD': '#228B22',    // Forest green for very good
    'EXCELLENT': '#008000'     // Dark green for excellent
};

$(document).ready(async function () {
    const essays = await Essay.getEssays();
    essays.sort((a, b) => b.timestamp - a.timestamp).forEach(essay => renderEssay(essay));

    document.getElementById('essay-form').onsubmit = () => {
        document.getElementById('grade-button').classList.add('d-none');
        document.getElementById('grade-button-loading').classList.remove('d-none');
    }
});

function renderEssay(essay) {
    const element = document.createElement('a');
    element.href = `/ai/essay/${essay.id}`;
    element.classList = 'card mb-1 bg-transparent border-0';

    element.innerHTML =
        `<div class="card-body p-2">
            <div class="d-flex align-items-center">
                <img src="/static/assets/document-check.png" class="w50 h55" style="margin-right: 1rem;" alt="">
                <div>
                    <h5 class="card-title fw-semibold font-xs w-75">${essay.title.length > 30 ? `${essay.title.slice(0, 30)}...` : essay.title}</h5>
                    <p class="card-text text-muted mt--1">${essay.timestamp.fromNow()}</p>
                </div>
                <div class="ms-auto">
                    <p class="card-text font-xs fw-bold mb-0"
                        style="color: ${gradeColors[essay.grade]}">${essay.grade.replace('_', ' ')}</p>
                </div>
            </div>
        </div>`;

    document.getElementById('recently-graded').appendChild(element);
}

export { gradeColors };