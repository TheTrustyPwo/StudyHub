import { User } from "./models/index.js";

let post_count
const currentUrl = window.location.href;
$(document).ready(async function () {
    post_count = parseInt(await (await fetch(`/api/v1/posts/count`)).json());
});

async function fetchPosts(from, to) {
    return await fetch(`/api/v1/posts/${from}/${to}`)
}

async function addPosts(posts) {
    for (const post of posts) {
        document.getElementById("posts").innerHTML += `<div class="col-12 col-md-6">
                <div class="position-relative rounded-4 shadow-4-hover bg-surface-secondary">
                    <div class="p-5 p-md-5 p-xl-10">
                        <section>
                            <header>
                                <h1 class="h3 ls-tight mb-8">
                                    ${post.ptitle}
                                </h1>
                            </header>
                            <p class="text-muted mb-7">
                                ${post.post}
                            </p>
                            <p class="text-muted mb-3">
                                By ${(await User.getById(post.user)).username}
                            </p>
                            <footer>
                                <a href=post/${post.id} class="font-semibold link-primary stretched-link">See Post -></a>
                            </footer>
                        </section>
                    </div>
                </div>
            </div>`
    }
}
let startPostIndex = 0;
const postsPerPage = 10;

function isScrollAtBottom() {
    const scrollOffset = window.innerHeight + window.scrollY;
    const pageHeight = document.documentElement.scrollHeight;
    return scrollOffset >= pageHeight;
}

async function handleScroll() {
    if (isScrollAtBottom() && post_count > startPostIndex) {
        const endPostIndex = startPostIndex + postsPerPage;
        const newPosts = await(await fetchPosts(startPostIndex, endPostIndex)).json();

        if (newPosts.length > 0) {
            await addPosts(newPosts);
            startPostIndex = endPostIndex;
        }
    }
}

window.addEventListener('scroll', handleScroll);
window.addEventListener('load', async () => {
    const initialPosts = await (await fetchPosts(startPostIndex, startPostIndex + postsPerPage)).json();
    await addPosts(initialPosts);
    startPostIndex += postsPerPage;
});
