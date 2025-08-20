// Portfolio Gallery JavaScript

class PortfolioGallery {
    constructor() {
        this.images = [];
        this.filteredImages = [];
        this.currentFilter = 'all';
        this.currentLightboxIndex = 0;
        
        this.init();
    }
    
    async init() {
        await this.loadImages();
        this.setupFilters();
        this.setupLightbox();
        this.renderGallery();
    }
    
    async loadImages() {
        try {
            const response = await fetch('/api/portfolio/images');
            const data = await response.json();
            
            if (data.success) {
                this.images = data.images;
                this.filteredImages = [...this.images];
                this.updateImageCount();
            } else {
                console.error('Failed to load images:', data.error);
                this.showError('Failed to load portfolio images');
            }
        } catch (error) {
            console.error('Error loading images:', error);
            this.showError('Network error loading portfolio');
        }
    }
    
    setupFilters() {
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Filter images
                const category = button.dataset.category;
                this.filterImages(category);
            });
        });
    }
    
    filterImages(category) {
        this.currentFilter = category;
        
        if (category === 'all') {
            this.filteredImages = [...this.images];
        } else {
            this.filteredImages = this.images.filter(image => 
                image.categories.some(cat => 
                    cat.name.toLowerCase() === category.toLowerCase()
                )
            );
        }
        
        this.updateImageCount();
        this.renderGallery();
    }
    
    updateImageCount() {
        const countElement = document.getElementById('image-count');
        if (countElement) {
            countElement.textContent = this.filteredImages.length;
        }
    }
    
    renderGallery() {
        const galleryGrid = document.getElementById('gallery-grid');
        
        if (this.filteredImages.length === 0) {
            galleryGrid.innerHTML = `
                <div class="loading-spinner">
                    <p>No images found for this category</p>
                </div>
            `;
            return;
        }
        
        const galleryHTML = this.filteredImages.map((image, index) => `
            <div class="gallery-item" data-index="${index}" onclick="portfolioGallery.openLightbox(${index})">
                <div class="gallery-image-container">
                    <img 
                        src="/static/assets/${image.filename}" 
                        alt="${image.title || 'Portfolio Image'}"
                        class="gallery-image portfolio-image"
                        loading="lazy"
                        oncontextmenu="return false"
                        ondragstart="return false"
                    >
                </div>
                <div class="gallery-overlay">
                    <h3 class="gallery-title">${image.title || 'Untitled'}</h3>
                    ${image.categories.length > 0 ? `
                        <div class="gallery-categories">
                            ${image.categories.map(cat => `
                                <span class="gallery-category-tag">${cat.name}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                    ${image.description ? `
                        <p class="gallery-description">${image.description}</p>
                    ` : ''}
                </div>
            </div>
        `).join('');
        
        galleryGrid.innerHTML = galleryHTML;
        
        // Add stagger animation
        const items = galleryGrid.querySelectorAll('.gallery-item');
        items.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.1}s`;
            item.classList.add('fade-in');
        });
    }
    
    setupLightbox() {
        const lightbox = document.getElementById('lightbox');
        const lightboxClose = document.getElementById('lightbox-close');
        const lightboxOverlay = document.getElementById('lightbox-overlay');
        const lightboxPrev = document.getElementById('lightbox-prev');
        const lightboxNext = document.getElementById('lightbox-next');
        
        // Close lightbox
        [lightboxClose, lightboxOverlay].forEach(element => {
            element.addEventListener('click', () => this.closeLightbox());
        });
        
        // Navigation
        lightboxPrev.addEventListener('click', () => this.previousImage());
        lightboxNext.addEventListener('click', () => this.nextImage());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('active')) return;
            
            switch(e.key) {
                case 'Escape':
                    this.closeLightbox();
                    break;
                case 'ArrowLeft':
                    this.previousImage();
                    break;
                case 'ArrowRight':
                    this.nextImage();
                    break;
            }
        });
    }
    
    openLightbox(index) {
        this.currentLightboxIndex = index;
        const lightbox = document.getElementById('lightbox');
        
        this.updateLightboxContent();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeLightbox() {
        const lightbox = document.getElementById('lightbox');
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    previousImage() {
        this.currentLightboxIndex = 
            (this.currentLightboxIndex - 1 + this.filteredImages.length) % this.filteredImages.length;
        this.updateLightboxContent();
    }
    
    nextImage() {
        this.currentLightboxIndex = 
            (this.currentLightboxIndex + 1) % this.filteredImages.length;
        this.updateLightboxContent();
    }
    
    updateLightboxContent() {
        const image = this.filteredImages[this.currentLightboxIndex];
        
        const lightboxImage = document.getElementById('lightbox-image');
        const lightboxTitle = document.getElementById('lightbox-title');
        const lightboxDescription = document.getElementById('lightbox-description');
        const lightboxCategories = document.getElementById('lightbox-categories');
        const lightboxExif = document.getElementById('lightbox-exif');
        
        // Update image
        lightboxImage.src = `/static/assets/${image.filename}`;
        lightboxImage.alt = image.title || 'Portfolio Image';
        
        // Update title
        lightboxTitle.textContent = image.title || 'Untitled';
        
        // Update description
        lightboxDescription.textContent = image.description || '';
        lightboxDescription.style.display = image.description ? 'block' : 'none';
        
        // Update categories
        if (image.categories.length > 0) {
            lightboxCategories.innerHTML = image.categories.map(cat => `
                <span class="lightbox-category-tag">${cat.name}</span>
            `).join('');
            lightboxCategories.style.display = 'flex';
        } else {
            lightboxCategories.style.display = 'none';
        }
        
        // Update EXIF data
        if (image.exif_data && Object.keys(image.exif_data).length > 0) {
            const exifHTML = Object.entries(image.exif_data).map(([key, value]) => `
                <div class="exif-item">
                    <span class="exif-label">${this.formatExifKey(key)}:</span>
                    <span class="exif-value">${value}</span>
                </div>
            `).join('');
            
            lightboxExif.innerHTML = exifHTML;
            lightboxExif.style.display = 'block';
        } else {
            lightboxExif.style.display = 'none';
        }
    }
    
    formatExifKey(key) {
        // Convert EXIF keys to readable format
        const keyMap = {
            'camera': 'Camera',
            'lens': 'Lens',
            'focal_length': 'Focal Length',
            'aperture': 'Aperture',
            'shutter_speed': 'Shutter Speed',
            'iso': 'ISO',
            'flash': 'Flash',
            'date_taken': 'Date Taken'
        };
        
        return keyMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    showError(message) {
        const galleryGrid = document.getElementById('gallery-grid');
        galleryGrid.innerHTML = `
            <div class="loading-spinner">
                <p style="color: var(--primary-color);">${message}</p>
                <button onclick="portfolioGallery.loadImages()" class="btn btn-primary" style="margin-top: 1rem;">
                    Try Again
                </button>
            </div>
        `;
    }
}

// Initialize portfolio gallery when DOM is loaded
let portfolioGallery;

document.addEventListener('DOMContentLoaded', () => {
    portfolioGallery = new PortfolioGallery();
});

// Export for global access
window.portfolioGallery = portfolioGallery;

