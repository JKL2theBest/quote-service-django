document.addEventListener('DOMContentLoaded', () => {
    const likeBtn = document.getElementById('like-btn');
    const dislikeBtn = document.getElementById('dislike-btn');
    const likesCountSpan = document.getElementById('likes-count');
    const dislikesCountSpan = document.getElementById('dislikes-count');

    if (!likeBtn) return;

    let isRequestInProgress = false;

    async function handleVote(url) {
        if (isRequestInProgress) {
            return;
        }
        isRequestInProgress = true;
        likeBtn.disabled = true;
        dislikeBtn.disabled = true;

        const csrftoken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
            });

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }

            const data = await response.json();

            likesCountSpan.textContent = data.likes;
            dislikesCountSpan.textContent = data.dislikes;

        } catch (error) {
            console.error('There has been a problem with your fetch operation:', error);
            likeBtn.disabled = false;
            dislikeBtn.disabled = false;
        } finally {
            // isRequestInProgress = false; // Раскомментировать, если нужно разрешить повторные голоса
        }
    }

    likeBtn.addEventListener('click', () => {
        handleVote(likeBtn.dataset.url);
    });

    dislikeBtn.addEventListener('click', () => {
        handleVote(dislikeBtn.dataset.url);
    });
});