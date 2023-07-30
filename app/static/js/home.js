let post_count
const currentUrl = window.location.href;
$(document).ready(async function () {
    post_count = await fetch(`/api/v1/post/count`)}
);

async function fetchPosts(from, to) {
    return await fetch(`/api/v1/post/${from}/${to}`)
}

function addPosts(posts) {
    posts.forEach(function (post) {
        document.getElementById("posts").innerHTML += `<div class="col-12 col-md-6">
                <div class="position-relative rounded-4 shadow-4-hover bg-surface-secondary">
                    <div class="p-5 p-md-5 p-xl-10">
                        <section>
                            <header>
                                <h1 class="h3 ls-tight mb-4">
                                    ${post.ptitle}
                                </h1>
                            </header>
                            <p class="text-muted mb-5">
                                ${post.post}
                            </p>
                            <footer>
                                <a href=${currentUrl + "post/" + post.id}  class="font-semibold link-primary stretched-link">See Post -></a>
                            </footer>
                        </section>
                    </div>
                </div>
            </div>`
    });
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
            addPosts(newPosts);
            startPostIndex = endPostIndex;
        }
    }
}

window.addEventListener('scroll', handleScroll);
window.addEventListener('load', async () => {
    const initialPosts = await (await fetchPosts(startPostIndex, startPostIndex + postsPerPage)).json();
    console.log(initialPosts)
    addPosts(initialPosts);
    startPostIndex += postsPerPage;
});
