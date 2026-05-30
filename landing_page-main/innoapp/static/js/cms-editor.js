(() => {
    const isStaff = document.body.dataset.isStaff === 'true';
    if (!isStaff) {
        return;
    }

    const contextMenu = document.getElementById('cms-context-menu');
    const imageInput = document.getElementById('imageFileInput');
    const videoFileInput = document.getElementById('videoFileInput');
    const heroVideoFilesInput = document.getElementById('heroVideoFilesInput');
    const textEditorInput = document.getElementById('textEditorInput');
    const socialNameInput = document.getElementById('socialNameInput');
    const socialUrlInput = document.getElementById('socialUrlInput');
    const socialIconInput = document.getElementById('socialIconInput');
    const toastEl = document.getElementById('cmsToast');
    const toast = toastEl ? new bootstrap.Toast(toastEl) : null;
    const textEditorModal = new bootstrap.Modal(document.getElementById('textEditorModal'));
    const videoEditorModal = new bootstrap.Modal(document.getElementById('videoEditorModal'));
    const linkEditorModal = new bootstrap.Modal(document.getElementById('linkEditorModal'));
    const editableSelector = '.editable, .editable-image, .editable-video, .editable-video-gallery, .editable-link';

    let currentTarget = null;
    let linkClickTimer = null;

    const getCookie = (name) => {
        const cookie = document.cookie
            .split(';')
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
    };

    const showToast = (message, mode = 'success') => {
        if (!toastEl) {
            if (mode === 'error') {
                console.error(message);
            }
            return;
        }
        toastEl.classList.remove('text-bg-success', 'text-bg-danger');
        toastEl.classList.add(mode === 'error' ? 'text-bg-danger' : 'text-bg-success');
        toastEl.querySelector('.toast-body').textContent = message;
        toast.show();
    };

    const handleError = (error, fallbackMessage = 'Something went wrong. Please try again.') => {
        const message = error?.message || fallbackMessage;
        console.error('[CMS editor]', error);
        showToast(message, 'error');
    };

    const request = async (url, options = {}) => {
        const headers = { ...(options.headers || {}) };
        headers['X-CSRFToken'] = getCookie('csrftoken');
        const response = await fetch(url, { ...options, headers });
        let data = {};
        try {
            data = await response.json();
        } catch (error) {
            throw new Error('The server returned an unreadable response.');
        }
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        return data;
    };

    const hideMenu = () => contextMenu.classList.remove('show');
    const escapeSelector = (value) => window.CSS?.escape ? CSS.escape(value) : value.replace(/"/g, '\\"');
    const modelSelector = (target) => {
        if (!target?.dataset.model || !target.dataset.id || !target.dataset.field) {
            return '';
        }
        return `[data-model="${escapeSelector(target.dataset.model)}"][data-id="${escapeSelector(target.dataset.id)}"][data-field="${escapeSelector(target.dataset.field)}"]`;
    };

    const getTargetType = (target) => {
        if (!target) {
            return '';
        }
        if (target.dataset.socialId || target.classList.contains('editable-link')) {
            return 'link';
        }
        if (target.classList.contains('editable-image')) {
            return 'image';
        }
        if (target.classList.contains('editable-video')) {
            return 'video';
        }
        if (target.classList.contains('editable-video-gallery')) {
            return 'video-gallery';
        }
        if (target.classList.contains('editable')) {
            return 'text';
        }
        return '';
    };

    const openTextEditor = (target) => {
        currentTarget = target;
        textEditorInput.value = target.dataset.display === 'pipe-list'
            ? Array.from(target.querySelectorAll('b')).map((item) => item.textContent.trim()).join('|')
            : target.textContent.trim();
        textEditorModal.show();
    };

    const openImageEditor = (target) => {
        currentTarget = target;
        imageInput.value = '';
        imageInput.click();
    };

    const openVideoEditor = (target) => {
        currentTarget = target;
        videoFileInput.value = '';
        videoEditorModal.show();
    };

    const openVideoGalleryUploader = (target) => {
        currentTarget = target || document.querySelector('.editable-video-gallery');
        heroVideoFilesInput.value = '';
        heroVideoFilesInput.click();
    };

    const openSocialLinkEditor = (target) => {
        currentTarget = target;
        socialNameInput.value = target.dataset.name || '';
        socialUrlInput.value = target.dataset.url || '';
        socialIconInput.value = target.dataset.icon || '';
        linkEditorModal.show();
    };

    const runEditorAction = (action, target) => {
        if (!target) {
            showToast('Choose editable content first.', 'error');
            return;
        }

        const actions = {
            'edit-text': openTextEditor,
            'change-image': openImageEditor,
            'change-video': openVideoEditor,
            'add-videos': openVideoGalleryUploader,
            'edit-link': openSocialLinkEditor,
        };
        const handler = actions[action];
        if (!handler) {
            showToast('That editor action is not available.', 'error');
            return;
        }
        handler(target);
    };

    const openMenu = (event, target) => {
        currentTarget = target;
        const targetType = getTargetType(target);

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
        if (targetType === 'video-gallery') {
            contextMenu.querySelector('[data-action="add-videos"]').style.display = 'block';
        }
        if (targetType === 'link') {
            contextMenu.querySelector('[data-action="edit-link"]').style.display = 'block';
        }

        contextMenu.style.left = `${event.pageX}px`;
        contextMenu.style.top = `${event.pageY}px`;
        contextMenu.classList.add('show');
    };

    document.addEventListener('contextmenu', (event) => {
        const target = event.target.closest(editableSelector);
        if (!target) {
            hideMenu();
            return;
        }
        event.preventDefault();
        openMenu(event, target);
    });

    document.addEventListener('dblclick', (event) => {
        const target = event.target.closest(editableSelector);
        if (!target) {
            return;
        }
        clearTimeout(linkClickTimer);
        event.preventDefault();
        event.stopPropagation();

        const targetType = getTargetType(target);
        const actionByType = {
            text: 'edit-text',
            image: 'change-image',
            video: 'change-video',
            'video-gallery': 'add-videos',
            link: 'edit-link',
        };
        hideMenu();
        runEditorAction(actionByType[targetType], target);
    });

    document.addEventListener('click', (event) => {
        const editableTarget = event.target.closest(editableSelector);
        const editableLink = editableTarget?.closest('a');
        if (!editableLink || editableLink.dataset.bsToggle) {
            return;
        }

        if (event.detail > 1) {
            clearTimeout(linkClickTimer);
            event.preventDefault();
            event.stopPropagation();
            return;
        }

        event.preventDefault();
        event.stopPropagation();
        clearTimeout(linkClickTimer);
        linkClickTimer = window.setTimeout(() => {
            const href = editableLink.getAttribute('href');
            if (href && href !== '#') {
                window.location.href = href;
            }
        }, 250);
    }, true);

    document.addEventListener('click', hideMenu);

    contextMenu.addEventListener('click', (event) => {
        const action = event.target.closest('[data-action]')?.dataset.action;
        if (!action || !currentTarget) {
            return;
        }
        hideMenu();
        runEditorAction(action, currentTarget);
    });

    document.getElementById('saveTextButton').addEventListener('click', async () => {
        try {
            const key = currentTarget?.dataset.key;
            const model = currentTarget?.dataset.model;
            const id = currentTarget?.dataset.id;
            const field = currentTarget?.dataset.field;
            if (!key && (!model || !id || !field)) {
                return;
            }
            const data = await request('/save-text/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, model, id, field, content: textEditorInput.value }),
            });
            const targets = data.model
                ? document.querySelectorAll(`.editable${modelSelector(currentTarget)}`)
                : document.querySelectorAll(`.editable[data-key="${escapeSelector(key)}"]`);
            targets.forEach((element) => {
                if (element.dataset.display === 'pipe-list') {
                    const words = data.content.split('|').map((item) => item.trim()).filter(Boolean);
                    element.innerHTML = words.map((word, index) => `<b class="${index === 0 ? 'is-visible' : ''}">${word}</b>`).join('');
                } else {
                    element.textContent = data.content;
                }
            });
            if (key) {
                document.querySelectorAll(`[data-placeholder-key="${escapeSelector(key)}"]`).forEach((field) => {
                    field.placeholder = data.content;
                });
                document.querySelectorAll(`[data-url-key="${escapeSelector(key)}"]`).forEach((link) => {
                    if (/^https?:\/\//i.test(data.content.trim())) {
                        link.href = data.content.trim();
                    }
                });
            }
            if (data.model === 'testimonial' && data.field === 'whatsapp_url' && /^https?:\/\//i.test(data.content.trim())) {
                currentTarget.closest('.testimony-card')?.querySelector('.testimony-whatsapp-link')?.setAttribute('href', data.content.trim());
            }
            textEditorModal.hide();
            showToast('Saved successfully');
        } catch (error) {
            handleError(error, 'Text could not be saved.');
        }
    });

    imageInput.addEventListener('change', async () => {
        try {
            if (!currentTarget || !imageInput.files.length) {
                return;
            }
            const formData = new FormData();
            if (currentTarget.dataset.model) {
                formData.append('model', currentTarget.dataset.model);
                formData.append('id', currentTarget.dataset.id);
                formData.append('field', currentTarget.dataset.field);
            } else {
                formData.append('key', currentTarget.dataset.key);
            }
            formData.append('file', imageInput.files[0]);
            const data = await request('/upload-image/', { method: 'POST', body: formData });
            const targets = data.model
                ? document.querySelectorAll(`.editable-image[data-model="${escapeSelector(data.model)}"][data-id="${escapeSelector(data.id)}"][data-field="${escapeSelector(data.field)}"]`)
                : document.querySelectorAll(`.editable-image[data-key="${data.key}"]`);
            targets.forEach((img) => {
                img.src = data.image_url;
            });
            showToast('Saved successfully');
        } catch (error) {
            handleError(error, 'Image could not be saved.');
        }
    });

    document.getElementById('addHeroVideoButton')?.addEventListener('click', () => {
        openVideoGalleryUploader(document.querySelector('.editable-video-gallery'));
    });

    document.getElementById('addGalleryItemButton')?.addEventListener('click', async () => {
        try {
            await request('/gallery/create/', { method: 'POST' });
            showToast('Gallery item added successfully');
            window.setTimeout(() => window.location.reload(), 500);
        } catch (error) {
            handleError(error, 'Gallery item could not be added.');
        }
    });

    heroVideoFilesInput?.addEventListener('change', async () => {
        try {
            if (!heroVideoFilesInput.files.length) {
                return;
            }
            const formData = new FormData();
            formData.append('gallery_key', 'hero_video_gallery');
            Array.from(heroVideoFilesInput.files).forEach((file) => {
                formData.append('files', file);
            });
            const data = await request('/upload-video/', { method: 'POST', body: formData });
            showToast(`${data.videos.length} video${data.videos.length === 1 ? '' : 's'} added successfully`);
            window.setTimeout(() => window.location.reload(), 650);
        } catch (error) {
            handleError(error, 'Videos could not be added.');
        }
    });

    document.getElementById('saveVideoButton').addEventListener('click', async () => {
        try {
            if (!currentTarget) {
                return;
            }
            if (videoFileInput.files.length) {
                const formData = new FormData();
                if (currentTarget.dataset.model) {
                    formData.append('model', currentTarget.dataset.model);
                    formData.append('id', currentTarget.dataset.id);
                    formData.append('field', currentTarget.dataset.field);
                } else {
                    formData.append('key', currentTarget.dataset.key);
                }
                formData.append('file', videoFileInput.files[0]);
                const data = await request('/upload-video/', { method: 'POST', body: formData });
                if (currentTarget.classList.contains('hero-video-slide')) {
                    currentTarget.querySelector('.hero-video-player, .hero-video-empty')?.remove();
                    currentTarget.insertAdjacentHTML('afterbegin', `<video class="hero-video-player" controls preload="metadata" playsinline><source src="${data.video_url}">Your browser does not support the video tag.</video>`);
                } else {
                    currentTarget.innerHTML = `<video controls class="w-100 h-100 object-fit-cover"><source src="${data.video_url}"></video>`;
                }
            } else {
                throw new Error('Choose a video file.');
            }
            videoEditorModal.hide();
            showToast('Saved successfully');
        } catch (error) {
            handleError(error, 'Video could not be saved.');
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
            handleError(error, 'Social link could not be saved.');
        }
    });
})();
