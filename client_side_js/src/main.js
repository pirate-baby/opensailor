import { Crepe } from "@milkdown/crepe";
import "@milkdown/crepe/theme/common/style.css";
import "@milkdown/crepe/theme/frame.css";

// Get CSRF token for API calls
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Upload handler for images
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload-image', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrfToken(),
            },
        });
        
        const result = await response.json();
        
        if (result.success) {
            return result.url;
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Image upload failed:', error);
        throw error;
    }
}

window.initMilkdownCrepe = async function(domId, defaultValue = "") {
    const crepe = new Crepe({
        root: document.getElementById(domId),
        defaultValue: defaultValue,
        upload: uploadImage,
    });
    await crepe.create();
    return crepe;
};

// If headings still appear in the UI, add this CSS to hide them:
// .milkdown .slash-menu [data-type="heading"] { display: none !important; }