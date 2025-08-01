document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element Selection ---
    const contentFileInput = document.getElementById('contentFile');
    const styleFileInput = document.getElementById('styleFile');
    const contentPreviewBox = document.getElementById('contentPreviewBox');
    const stylePreviewBox = document.getElementById('stylePreviewBox');
    
    const submitButton = document.getElementById('submitButton');
    const resultBox = document.getElementById('resultBox');
    const resultPlaceholder = document.getElementById('resultPlaceholder');
    const resultImage = document.getElementById('resultImage');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorToast = document.getElementById('error-toast');

    // --- Helper Functions ---
    const previewImage = (file, previewBox) => {
        if (!file) return;
        if (file.size > 10 * 1024 * 1024) {
            showError('File size exceeds 10MB.');
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            previewBox.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    };

    const showError = (message) => {
        errorToast.textContent = message;
        errorToast.classList.add('show');
        setTimeout(() => {
            errorToast.classList.remove('show');
        }, 4000);
    };

    // --- Event Listeners ---
    contentFileInput.addEventListener('change', () => previewImage(contentFileInput.files[0], contentPreviewBox));
    styleFileInput.addEventListener('change', () => previewImage(styleFileInput.files[0], stylePreviewBox));

    submitButton.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!contentFileInput.files[0] || !styleFileInput.files[0]) {
            showError('Please upload both a content and a style image.');
            return;
        }

        submitButton.disabled = true;
        loadingSpinner.classList.add('visible');
        resultImage.src = ''; // Clear previous result

        const formData = new FormData();
        formData.append('content_file', contentFileInput.files[0]);
        formData.append('style_file', styleFileInput.files[0]);

        try {
            const response = await fetch('/stylize/', { method: 'POST', body: formData });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An unknown server error occurred.');
            }

            const imageBlob = await response.blob();
            const imageUrl = URL.createObjectURL(imageBlob);
            
            resultImage.src = imageUrl;
            resultPlaceholder.style.display = 'none';

        } catch (error) {
            showError(`Processing failed: ${error.message}`);
        } finally {
            submitButton.disabled = false;
            loadingSpinner.classList.remove('visible');
        }
    });

    const setupDragAndDrop = (dropZone, fileInput) => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, e => {
                e.preventDefault();
                e.stopPropagation();
            });
        });
        ['dragenter', 'dragover'].forEach(eventName => dropZone.classList.add('dragover'));
        ['dragleave', 'drop'].forEach(eventName => dropZone.classList.remove('dragover'));
        
        dropZone.addEventListener('drop', e => {
            fileInput.files = e.dataTransfer.files;
            previewImage(fileInput.files[0], dropZone);
        });
    };

    setupDragAndDrop(contentPreviewBox, contentFileInput);
    setupDragAndDrop(stylePreviewBox, styleFileInput);
});
