(() => {
    const isStaff = document.body.dataset.isStaff === 'true';
    if (!isStaff) {
        return;
    }

    const contextMenu = document.getElementById('cms-context-menu');
    const imageInput = document.getElementById('imageFileInput');
    const videoFileInput = document.getElementById('videoFileInput');
    const youtubeUrlInput = document.getElementById('youtubeUrlInput');
    const textEditorInput = document.getElementById('textEditorInput');
    const socialNameInput = document.getElementById('socialNameInput');
    const socialUrlInput = document.getElementById('socialUrlInput');
    const socialIconInput = document.getElementById('socialIconInput');
    const toastEl = document.getElementById('cmsToast');
    const toast = toastEl ? new bootstrap.Toast(toastEl) : null;
    const textEditorModal = new bootstrap.Modal(document.getElementById('textEditorModal'));
    const videoEditorModal = new bootstrap.Modal(document.getElementById('videoEditorModal'));
    const linkEditorModal = new bootstrap.Modal(document.getElementById('linkEditorModal'));

    let currentTarget = null;

    const getCookie = (name) => {
        const cookie = document.cookie
            .split(';')
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    };

    const showToast = (message, mode = 'success') => {
        if (!toastEl) {
            return;
        }
        toastEl.classList.remove('text-bg-success', 'text-bg-danger');
        toastEl.classList.add(mode === 'error' ? 'text-bg-danger' : 'text-bg-success');
        toastEl.querySelector('.toast-body').textContent = message;
        toast.show();
    };

    const request = async (url, options = {}) => {
        const headers = options.headers || {};
        headers['X-CSRFToken'] = getCookie('csrftoken');
        options.headers = headers;
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        return data;
    };

    const hideMenu = () => contextMenu.classList.remove('show');

    const openMenu = (event, target) => {
        currentTarget = target;
        const targetType = target.dataset.socialId
            ? 'link'
            : target.classList.contains('editable-image')
              ? 'image'
              : target.classList.contains('editable-video')
                ? 'video'
                : 'text';

        contextMenu.querySelectorAll('[data-action]').forEach((button) => {
            button.style.display = 'none';
        });

        if (targetType === 'text') {
            contextMenu.querySelector('[data-action="edit-text"]').style.display = 'block';
        }
        if (targetType === 'image') {
            contextMenu.querySelector('[data-action="change-image"]').style.display = 'block';
        }
        if (targetType === 'video') {
            contextMenu.querySelector('[data-action="change-video"]').style.display = 'block';
        }
        if (targetType === 'link') {
            contextMenu.querySelector('[data-action="edit-link"]').style.display = 'block';
        }

        contextMenu.style.left = `${event.pageX}px`;
        contextMenu.style.top = `${event.pageY}px`;
        contextMenu.classList.add('show');
    };

    document.addEventListener('contextmenu', (event) => {
        const target = event.target.closest('.editable, .editable-image, .editable-video, .editable-link');
        if (!target) {
            hideMenu();
            return;
        }
        event.preventDefault();
        openMenu(event, target);
    });

    document.addEventListener('click', hideMenu);

    contextMenu.addEventListener('click', (event) => {
        const action = event.target.dataset.action;
        if (!action || !currentTarget) {
            return;
        }

        if (action === 'edit-text') {
            textEditorInput.value = currentTarget.dataset.display === 'pipe-list'
                ? Array.from(currentTarget.querySelectorAll('b')).map((item) => item.textContent.trim()).join('|')
                : currentTarget.textContent.trim();
            textEditorModal.show();
        }

        if (action === 'change-image') {
            imageInput.click();
        }

        if (action === 'change-video') {
            videoFileInput.value = '';
            youtubeUrlInput.value = '';
            videoEditorModal.show();
        }

        if (action === 'edit-link') {
            socialNameInput.value = currentTarget.dataset.name || '';
            socialUrlInput.value = currentTarget.dataset.url || '';
            socialIconInput.value = currentTarget.dataset.icon || '';
            linkEditorModal.show();
        }
    });

    document.getElementById('saveTextButton').addEventListener('click', async () => {
        try {
            const key = currentTarget?.dataset.key;
            if (!key) {
                return;
            }
            const data = await request('/save-text/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, content: textEditorInput.value }),
            });
            if (currentTarget.dataset.display === 'pipe-list') {
                const words = data.content.split('|').map((item) => item.trim()).filter(Boolean);
                currentTarget.innerHTML = words.map((word, index) => `<b class="${index === 0 ? 'is-visible' : ''}">${word}</b>`).join('');
            } else {
                currentTarget.textContent = data.content;
            }
            textEditorModal.hide();
            showToast('Saved successfully');
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    imageInput.addEventListener('change', async () => {
        try {
            if (!currentTarget || !imageInput.files.length) {
                return;
            }
            const formData = new FormData();
            formData.append('key', currentTarget.dataset.key);
            formData.append('file', imageInput.files[0]);
            const data = await request('/upload-image/', { method: 'POST', body: formData });
            document.querySelectorAll(`.editable-image[data-key="${data.key}"]`).forEach((img) => {
                img.src = data.image_url;
            });
            showToast('Saved successfully');
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    document.getElementById('saveVideoButton').addEventListener('click', async () => {
        try {
            if (!currentTarget) {
                return;
            }
            const key = currentTarget.dataset.key;
            if (videoFileInput.files.length) {
                const formData = new FormData();
                formData.append('key', key);
                formData.append('file', videoFileInput.files[0]);
                const data = await request('/upload-video/', { method: 'POST', body: formData });
                currentTarget.innerHTML = `<video controls class="w-100 h-100 object-fit-cover"><source src="${data.video_url}"></video>`;
            } else if (youtubeUrlInput.value.trim()) {
                const data = await request('/update-youtube/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, youtube_url: youtubeUrlInput.value.trim() }),
                });
                currentTarget.innerHTML = `<iframe src="${data.youtube_embed_url}" title="Hero video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`;
            } else {
                throw new Error('Choose a video file or provide a YouTube URL.');
            }
            videoEditorModal.hide();
            showToast('Saved successfully');
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    document.getElementById('saveSocialButton').addEventListener('click', async () => {
        try {
            if (!currentTarget) {
                return;
            }
            const data = await request('/update-social/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: currentTarget.dataset.socialId,
                    name: socialNameInput.value.trim(),
                    url: socialUrlInput.value.trim(),
                    icon_class: socialIconInput.value.trim(),
                }),
            });
            currentTarget.href = data.url;
            currentTarget.title = data.name;
            currentTarget.className = `social-icon-link editable-link ${data.icon_class}`;
            currentTarget.dataset.name = data.name;
            currentTarget.dataset.url = data.url;
            currentTarget.dataset.icon = data.icon_class;
            linkEditorModal.hide();
            showToast('Saved successfully');
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
})();
