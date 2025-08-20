// Portfolio JavaScript - Category Filtering and Lightbox

class PortfolioManager {
    constructor() {
        this.currentImages = [];
        this.currentImageIndex = 0;
        this.isLightboxOpen = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadPortfolioData();
        this.setupImageLoading();
    }
    
    setupEventListeners() {
        // Category filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleCategoryFilter(e.target.dataset.category);
            });
        });
        
        // Category tags in gallery items
        document.querySelectorAll('.category-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleCategoryFilter(e.target.dataset.category);
            });
        });
        
        // Gallery view buttons
        document.querySelectorAll('.gallery-view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const imageId = e.target.dataset.imageId;
                this.openLightbox(imageId);
            });
        });
        
        // Gallery items click
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const imageId = item.querySelector('.gallery-view-btn').dataset.imageId;
                this.openLightbox(imageId);
            });
        });
        
        // Lightbox controls
        this.setupLightboxControls();
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (this.isLightboxOpen) {
                this.handleKeyboardNavigation(e);
            }
        });
    }
    
    setupLightboxControls() {
        const lightboxModal = document.getElementById('lightbox-modal');
        const lightboxOverlay = document.getElementById('lightbox-overlay');
        const lightboxClose = document.getElementById('lightbox-close');
        const lightboxPrev = document.getElementById('lightbox-prev');
        const lightboxNext = document.getElementById('lightbox-next');
        
        if (lightboxOverlay) {
            lightboxOverlay.addEventListener('click', () => this.closeLightbox());
        }
        
        if (lightboxClose) {
            lightboxClose.addEventListener('click', () => this.closeLightbox());
        }
        
        if (lightboxPrev) {
            lightboxPrev.addEventListener('click', () => this.previousImage());
        }
        
        if (lightboxNext) {
            lightboxNext.addEventListener('click', () => this.nextImage());
        }
    }
    
    async loadPortfolioData() {
        try {
            const response = await fetch('/api/portfolio');
            this.currentImages = await response.json();
            this.updateImageCount();
        } catch (error) {
            console.error('Error loading portfolio data:', error);
        }
    }
    
    handleCategoryFilter(category) {
        // Update active filter button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-category="${category}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        // Filter gallery items
        this.filterGalleryItems(category);
        
        // Update URL without page reload
        const url = new URL(window.location);
        if (category === 'all') {
            url.searchParams.delete('category');
        } else {
            url.searchParams.set('category', category);
        }
        window.history.pushState({}, '', url);
        
        // Update image count
        this.updateImageCount(category);
    }
    
    filterGalleryItems(category) {
        const galleryItems = document.querySelectorAll('.gallery-item');
        let visibleCount = 0;
        
        galleryItems.forEach((item, index) => {
            const itemCategories = item.dataset.categories.split(',');
            const shouldShow = category === 'all' || itemCategories.includes(category);
            
            if (shouldShow) {
                item.style.display = 'block';
                item.classList.remove('filtered-out');
                
                // Stagger animation
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, index * 50);
                
                visibleCount++;
            } else {
                item.style.opacity = '0';
                item.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    item.style.display = 'none';
                    item.classList.add('filtered-out');
                }, 300);
            }
        });
        
        // Update stats
        const imageCountElement = document.getElementById('image-count');
        if (imageCountElement) {
            imageCountElement.textContent = visibleCount;
        }
    }
    
    updateImageCount(category = null) {
        let count = this.currentImages.length;
        
        if (category && category !== 'all') {
            count = this.currentImages.filter(img => 
                img.categories.includes(category)
            ).length;
        }
        
        const imageCountElement = document.getElementById('image-count');
        if (imageCountElement) {
            imageCountElement.textContent = count;
        }
    }
    
    async openLightbox(imageId) {
        const image = this.currentImages.find(img => img.id == imageId);
        if (!image) return;
        
        this.currentImageIndex = this.currentImages.findIndex(img => img.id == imageId);
        this.isLightboxOpen = true;
        
        // Populate lightbox content
        this.populateLightboxContent(image);
        
        // Show lightbox
        const lightboxModal = document.getElementById('lightbox-modal');
        if (lightboxModal) {
            lightboxModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        // Load EXIF data if available
        this.loadImageMetadata(image);
    }
    
    populateLightboxContent(image) {
        const lightboxImage = document.getElementById('lightbox-image');
        const lightboxTitle = document.getElementById('lightbox-title');
        const lightboxDescription = document.getElementById('lightbox-description');
        const lightboxCategories = document.getElementById('lightbox-categories');
        
        if (lightboxImage) {
            lightboxImage.src = image.url;
            lightboxImage.alt = image.title;
        }
        
        if (lightboxTitle) {
            lightboxTitle.textContent = image.title;
        }
        
        if (lightboxDescription) {
            lightboxDescription.textContent = image.description || '';
            lightboxDescription.style.display = image.description ? 'block' : 'none';
        }
        
        if (lightboxCategories) {
            lightboxCategories.innerHTML = image.categories.map(cat => 
                `<span class="category-tag" data-category="${cat}">${cat}</span>`
            ).join('');
            
            // Add click handlers to category tags
            lightboxCategories.querySelectorAll('.category-tag').forEach(tag => {
                tag.addEventListener('click', (e) => {
                    this.closeLightbox();
                    setTimeout(() => {
                        this.handleCategoryFilter(e.target.dataset.category);
                    }, 300);
                });
            });
        }
    }
    
    async loadImageMetadata(image) {
        const lightboxMeta = document.getElementById('lightbox-meta');
        if (!lightboxMeta) return;
        
        try {
            // Try to load EXIF data from API
            const response = await fetch(`/api/portfolio/image/${image.id}/metadata`);
            
            if (response.ok) {
                const metadata = await response.json();
                this.displayMetadata(metadata);
            } else {
                // No EXIF data available
                lightboxMeta.innerHTML = `
                    <div class="meta-title">Image Information</div>
                    <div class="meta-item">
                        <span class="meta-label">Filename:</span>
                        <span class="meta-value">${image.filename}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Upload Date:</span>
                        <span class="meta-value">${new Date(image.created_at).toLocaleDateString()}</span>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading image metadata:', error);
            lightboxMeta.innerHTML = `
                <div class="meta-title">Image Information</div>
                <div class="meta-item">
                    <span class="meta-label">Filename:</span>
                    <span class="meta-value">${image.filename}</span>
                </div>
            `;
        }
    }
    
    displayMetadata(metadata) {
        const lightboxMeta = document.getElementById('lightbox-meta');
        if (!lightboxMeta) return;
        
        let metaHTML = '<div class="meta-title">Technical Details</div>';
        
        if (metadata.camera) {
            metaHTML += `
                <div class="meta-item">
                    <span class="meta-label">Camera:</span>
                    <span class="meta-value">${metadata.camera}</span>
                </div>
            `;
        }
        
        if (metadata.lens) {
            metaHTML += `
                <div class="meta-item">
                    <span class="meta-label">Lens:</span>
                    <span class="meta-value">${metadata.lens}</span>
                </div>
            `;
        }
        
        if (metadata.settings) {
            metaHTML += `
                <div class="meta-item">
                    <span class="meta-label">Settings:</span>
                    <span class="meta-value">${metadata.settings}</span>
                </div>
            `;
        }
        
        if (metadata.iso) {
            metaHTML += `
                <div class="meta-item">
                    <span class="meta-label">ISO:</span>
                    <span class="meta-value">${metadata.iso}</span>
                </div>
            `;
        }
        
        if (metadata.focal_length) {
            metaHTML += `
                <div class="meta-item">
                    <span class="meta-label">Focal Length:</span>
                    <span class="meta-value">${metadata.focal_length}</span>
                </div>
            `;
        }
        
        lightboxMeta.innerHTML = metaHTML;
    }
    
    closeLightbox() {
        const lightboxModal = document.getElementById('lightbox-modal');
        if (lightboxModal) {
            lightboxModal.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        this.isLightboxOpen = false;
    }
    
    previousImage() {
        if (this.currentImageIndex > 0) {
            this.currentImageIndex--;
            const image = this.currentImages[this.currentImageIndex];
            this.populateLightboxContent(image);
            this.loadImageMetadata(image);
        }
    }
    
    nextImage() {
        if (this.currentImageIndex < this.currentImages.length - 1) {
            this.currentImageIndex++;
            const image = this.currentImages[this.currentImageIndex];
            this.populateLightboxContent(image);
            this.loadImageMetadata(image);
        }
    }
    
    handleKeyboardNavigation(e) {
        switch (e.key) {
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
    }
    
    setupImageLoading() {
        // Lazy loading for gallery images
        const galleryImages = document.querySelectorAll('.gallery-image');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('loading');
                    
                    img.onload = () => {
                        img.classList.remove('loading');
                        img.classList.add('loaded');
                    };
                    
                    observer.unobserve(img);
                }
            });
        });
        
        galleryImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialize portfolio manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PortfolioManager();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const category = urlParams.get('category') || 'all';
    
    // Update filter without triggering history change
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-category="${category}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
    
    // Filter items
    const portfolioManager = new PortfolioManager();
    portfolioManager.filterGalleryItems(category);
});

