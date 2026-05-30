(() => {
    const form = document.getElementById('floatingContactForm');
    if (!form) {
        return;
    }

    const feedback = document.getElementById('floatingContactFeedback');

    const getCookie = (name) => {
        const cookie = document.cookie
            .split(';')
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    };

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (feedback) {
            feedback.className = 'small text-muted';
            feedback.textContent = 'Sending...';
        }

        try {
            const response = await fetch('/inquiries/submit/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: new FormData(form),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Message could not be submitted.');
            }

            form.reset();

            if (feedback) {
                feedback.className = 'small text-success';
                feedback.textContent = data.message || 'Thank you. Your message has been received.';
            }
        } catch (error) {
            if (feedback) {
                feedback.className = 'small text-danger';
                feedback.textContent = error.message || 'Message could not be submitted.';
            }
        }
    });
})();
