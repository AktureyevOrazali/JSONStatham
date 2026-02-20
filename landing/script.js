/* ============================================================
   OpenClaw Landing Page — Interactions & Animations
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    initStickyHeader();
    initFAQAccordion();
    initSmoothScroll();
    initMobileMenu();
});

/* ─── Scroll Reveal (Intersection Observer) ─── */
function initScrollReveal() {
    const reveals = document.querySelectorAll('.reveal');

    if (!reveals.length) return;

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -40px 0px',
        }
    );

    reveals.forEach((el) => observer.observe(el));
}

/* ─── Sticky Header with Blur ─── */
function initStickyHeader() {
    const header = document.querySelector('.header');
    if (!header) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;

        if (currentScroll > 60) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    }, { passive: true });
}

/* ─── FAQ Accordion ─── */
function initFAQAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach((item) => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all
            faqItems.forEach((i) => i.classList.remove('active'));

            // Open clicked (if was closed)
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}

/* ─── Smooth Scroll for Anchor Links ─── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (!target) return;

            // Close mobile menu if open
            const mobileNav = document.querySelector('.nav-links');
            const toggle = document.querySelector('.mobile-toggle');
            if (mobileNav && mobileNav.classList.contains('open')) {
                mobileNav.classList.remove('open');
                toggle?.classList.remove('active');
                document.body.style.overflow = '';
            }

            const headerHeight = document.querySelector('.header')?.offsetHeight || 80;
            const targetPosition = target.getBoundingClientRect().top + window.scrollY - headerHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth',
            });
        });
    });
}

/* ─── Mobile Burger Menu ─── */
function initMobileMenu() {
    const toggle = document.querySelector('.mobile-toggle');
    const nav = document.querySelector('.nav-links');

    if (!toggle || !nav) return;

    toggle.addEventListener('click', () => {
        toggle.classList.toggle('active');
        nav.classList.toggle('open');
        document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
    });
}
