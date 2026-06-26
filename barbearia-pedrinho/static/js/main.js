// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(f => {
        setTimeout(() => {
            f.style.transition = 'opacity 400ms ease';
            f.style.opacity = '0';
            setTimeout(() => f.remove(), 400);
        }, 4000);
    });
});
