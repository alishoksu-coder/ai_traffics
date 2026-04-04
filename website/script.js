// ═══════════════════════════════════════
// Traffic AI — Landing Page JS
// ═══════════════════════════════════════

// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// Smooth reveal animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Add animation classes
document.querySelectorAll('.feature-card, .mm-step, .tech-item, .ai-card, .ai-features-list li').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// Make visible when intersecting
const style = document.createElement('style');
style.textContent = '.visible { opacity: 1 !important; transform: translateY(0) !important; }';
document.head.appendChild(style);

// Stagger animations for grid items
document.querySelectorAll('.features-grid, .tech-grid, .ai-features-list').forEach(grid => {
  const children = grid.children;
  Array.from(children).forEach((child, i) => {
    child.style.transitionDelay = `${i * 0.1}s`;
  });
});

// Counter animation for stats
function animateCounter(el, target, suffix = '') {
  let current = 0;
  const increment = target / 40;
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    el.textContent = Math.floor(current) + suffix;
  }, 30);
}

// Animate stats when visible
const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const nums = entry.target.querySelectorAll('.stat-num');
      nums.forEach(num => {
        const text = num.textContent;
        if (text.includes('+')) {
          animateCounter(num, parseInt(text), '+');
        }
      });
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) statsObserver.observe(heroStats);

// Chart bar hover effect
document.querySelectorAll('.chart-bar').forEach(bar => {
  bar.addEventListener('mouseenter', () => {
    bar.style.filter = 'brightness(1.2)';
    bar.style.transform = 'scaleY(1.05)';
  });
  bar.addEventListener('mouseleave', () => {
    bar.style.filter = '';
    bar.style.transform = '';
  });
});

console.log('🚀 Traffic AI Landing Page loaded');
