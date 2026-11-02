// AI Resume Screening - Shared Client Logic

document.addEventListener('DOMContentLoaded', () => {
    // Auto dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Mobile Navigation Drawer Toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    const navBackdrop = document.getElementById('navBackdrop');

    function closeNav() {
        if (navLinks && navLinks.classList.contains('open')) {
            navLinks.classList.remove('open');
            navToggle && navToggle.classList.remove('open');
            navToggle && navToggle.setAttribute('aria-expanded', 'false');
            navBackdrop && navBackdrop.classList.remove('active');
            document.body.classList.remove('nav-open');
        }
    }

    function toggleNav() {
        if (!navLinks) return;
        const isOpen = navLinks.classList.toggle('open');
        navToggle && navToggle.classList.toggle('open', isOpen);
        navToggle && navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        navBackdrop && navBackdrop.classList.toggle('active', isOpen);
        document.body.classList.toggle('nav-open', isOpen);
    }

    if (navToggle) {
        navToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleNav();
        });
    }

    if (navBackdrop) {
        navBackdrop.addEventListener('click', closeNav);
    }

    // Close mobile nav when clicking any nav link
    if (navLinks) {
        navLinks.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', closeNav);
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeNav();
    });
});
