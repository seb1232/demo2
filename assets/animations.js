// Custom animation functions for the Agile Project Management Suite

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Apply parallax effect to header
    const headerElement = document.querySelector('.animated-header');
    if (headerElement) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            headerElement.style.transform = `translateY(${scrollPosition * 0.3}px)`;
            headerElement.style.opacity = 1 - (scrollPosition * 0.003);
        });
    }

    // Add hover effects to cards
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.3)';
            this.style.transition = 'all 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
            this.style.transition = 'all 0.3s ease';
        });
    });

    // Add staggered fade-in effect to list items
    const listItems = document.querySelectorAll('.staggered-fade li');
    listItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
    });

    // Add typing effect to title
    const titleElement = document.querySelector('.typing-effect');
    if (titleElement) {
        const text = titleElement.textContent;
        titleElement.textContent = '';
        let i = 0;
        
        function typeWriter() {
            if (i < text.length) {
                titleElement.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        }
        
        typeWriter();
    }
});

// Function to create floating elements (like Apple's floating UI elements)
function createFloatingElements() {
    const container = document.querySelector('.floating-container');
    if (!container) return;
    
    // Create floating elements
    for (let i = 0; i < 5; i++) {
        const floater = document.createElement('div');
        floater.className = 'floating-element';
        
        // Random position, size and color
        const size = Math.random() * 60 + 20;
        floater.style.width = `${size}px`;
        floater.style.height = `${size}px`;
        floater.style.left = `${Math.random() * 80 + 10}%`;
        floater.style.top = `${Math.random() * 80 + 10}%`;
        
        // Random background with transparency
        const r = Math.floor(Math.random() * 255);
        const g = Math.floor(Math.random() * 255);
        const b = Math.floor(Math.random() * 255);
        floater.style.backgroundColor = `rgba(${r}, ${g}, ${b}, 0.2)`;
        
        // Random blur
        floater.style.filter = `blur(${Math.random() * 10 + 5}px)`;
        
        // Add animation
        floater.style.animation = `float ${Math.random() * 10 + 10}s linear infinite`;
        
        container.appendChild(floater);
    }
}

// Function to add magnetic effect to buttons (similar to Apple's buttons)
function createMagneticButtons() {
    const buttons = document.querySelectorAll('.magnetic-button');
    
    buttons.forEach(button => {
        button.addEventListener('mousemove', function(e) {
            const position = button.getBoundingClientRect();
            const x = e.clientX - position.left - position.width / 2;
            const y = e.clientY - position.top - position.height / 2;
            
            button.style.transform = `translate(${x * 0.3}px, ${y * 0.5}px)`;
        });
        
        button.addEventListener('mouseout', function() {
            button.style.transform = 'translate(0, 0)';
        });
    });
}

// Initialize all animations
window.addEventListener('load', function() {
    createFloatingElements();
    createMagneticButtons();
});