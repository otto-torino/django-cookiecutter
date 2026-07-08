/**
 * Shared PhotoSwipe initialization.
 *
 * Initializes a PhotoSwipeLightbox (with dynamic caption plugin) for every
 * element marked with the `js-pswp-gallery` class. Gallery items are anchors
 * with the `js-lightbox-item` class carrying data-pswp-* attributes (or href).
 *
 * Requires the PhotoSwipe UMD bundles (PhotoSwipe, PhotoSwipeLightbox,
 * PhotoSwipeDynamicCaption) to be loaded first.
 */
(function () {
    function initPhotoSwipeGalleries() {
        if (typeof PhotoSwipeLightbox === "undefined" || typeof PhotoSwipe === "undefined") {
            return;
        }
        document.querySelectorAll(".js-pswp-gallery").forEach(function (gallery) {
            if (gallery.dataset.pswpInit) {
                return;
            }
            gallery.dataset.pswpInit = "1";
            var lightbox = new PhotoSwipeLightbox({
                gallery: gallery,
                showHideAnimationType: "fade",
                children: "a.js-lightbox-item",
                pswpModule: PhotoSwipe,
            });
            if (typeof PhotoSwipeDynamicCaption !== "undefined") {
                new PhotoSwipeDynamicCaption(lightbox, {
                    type: "below",
                });
            }
            lightbox.init();
        });
    }

    window.initPhotoSwipeGalleries = initPhotoSwipeGalleries;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initPhotoSwipeGalleries);
    } else {
        initPhotoSwipeGalleries();
    }
})();
