import { Post } from "./models/index.js";

$(document).ready(async function () {
    const themeButton = document.getElementById('theme-button');
    const searchInput = document.getElementById('search-input')

    localStorage.theme = localStorage.theme || 'light';
    if (localStorage.theme === 'dark') toggleDark();

    themeButton.addEventListener('click', () => {
        localStorage.theme = localStorage.theme === 'light' ? 'dark' : 'light';
        if (localStorage.theme === 'dark') toggleDark();
        else toggleLight();
    })

    searchInput.addEventListener('input', async function () {
        const searchResults = document.getElementById('searchResults');
        const query = searchInput.value.trim();
        if (query === '') {
            searchResults.innerHTML = '';
            return;
        }

        const posts = await Post.search(query, 5);
        if (posts.length === 0) searchResults.innerHTML = '<p>No results found</p>';

        let newInnerHTML = '';
        posts.forEach((post, index) => {
            newInnerHTML +=
                `<a href="/post/${post.id}" class="list-group-item list-group-item-action card w-100 shadow-xss border-0 rounded-0 px-4 py-0">
                    <div class="pt-3 pb-0">
                        <h4 class="fw-bold font-xs">${post.title}</h4>
                        <div class="card-body p-0 d-flex">
                          <figure class="avatar me-3"><img src=${post.author.pfp} alt="avater" class="shadow-sm rounded-circle w25"></figure>
                          <h3 class="fw-600 text-grey-900 font-xsss lh-28">${post.author.username}</h3>
                          <span class="fw-900 font-x mx-2">&#183;</span>
                          <span class="font-xsss fw-500 text-grey-500">${post.timestamp.fromNow()}</span>
                        </div>
                    </div>
                    ${index === posts.length - 1 ? '' : '<hr class="p-0 my-0 mx-3">'}
                </a>`;
        });

        searchResults.innerHTML = newInnerHTML;
    });
});

function toggleDark() {
    const themeButton = document.getElementById('theme-button');
    themeButton.querySelector('i').classList.add('feather-moon');
    themeButton.querySelector('i').classList.remove('feather-sun');
    document.querySelector('html').setAttribute('data-bs-theme', 'dark');
    document.querySelector('body').classList.add('theme-dark')
}

function toggleLight() {
    const themeButton = document.getElementById('theme-button');
    themeButton.querySelector('i').classList.add('feather-sun');
    themeButton.querySelector('i').classList.remove('feather-moon');
    document.querySelector('html').removeAttribute('data-bs-theme');
    document.querySelector('body').classList.remove('theme-dark')
}

function showLoadingScreen() {
    document.getElementById('loading-screen').style.display = 'flex';
}

function hideLoadingScreen() {
    document.getElementById('loading-screen').style.display = 'none';
}

export { toggleDark, toggleLight, showLoadingScreen, hideLoadingScreen };
