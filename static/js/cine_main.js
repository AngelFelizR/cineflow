// static/js/cine_main.js (versión simplificada sin modal)
document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Manejar cierre automático de alertas
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            setTimeout(function() {
                bsAlert.close();
            }, 5000);
        });
    }, 3000);
    
    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // ===== Carrusel de Banner Principal =====
    function initBannerCarousel() {
        console.log('Inicializando carrusel...');
        
        const bannerSlides = document.querySelectorAll('.banner-slide');
        const bannerIndicators = document.querySelectorAll('.banner-indicator');
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        
        console.log('Elementos encontrados:', {
            slides: bannerSlides.length,
            indicators: bannerIndicators.length,
            prevBtn: !!prevBtn,
            nextBtn: !!nextBtn
        });
        
        if (bannerSlides.length === 0) {
            console.log('No hay slides para el carrusel');
            return;
        }
        
        let currentBannerIndex = 0;
        let bannerInterval;
        
        function showBannerSlide(index) {
            // Validar índice
            if (index < 0) index = bannerSlides.length - 1;
            if (index >= bannerSlides.length) index = 0;
            
            console.log('Mostrando slide:', index);
            
            // Ocultar todos los slides
            bannerSlides.forEach(slide => {
                slide.style.opacity = '0';
                slide.classList.remove('active');
            });
            
            // Ocultar todos los indicadores
            bannerIndicators.forEach(indicator => {
                indicator.classList.remove('active');
            });
            
            // Mostrar slide actual
            bannerSlides[index].style.opacity = '1';
            bannerSlides[index].classList.add('active');
            
            // Activar indicador actual
            if (bannerIndicators[index]) {
                bannerIndicators[index].classList.add('active');
            }
            
            currentBannerIndex = index;
        }
        
        function nextBannerSlide() {
            showBannerSlide(currentBannerIndex + 1);
        }
        
        function prevBannerSlide() {
            showBannerSlide(currentBannerIndex - 1);
        }
        
        function startBannerAutoSlide() {
            stopBannerAutoSlide();
            bannerInterval = setInterval(nextBannerSlide, 5000);
            console.log('Auto-slide iniciado');
        }
        
        function stopBannerAutoSlide() {
            if (bannerInterval) {
                clearInterval(bannerInterval);
                console.log('Auto-slide detenido');
            }
        }
        
        // Event listeners para botones de navegación
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                console.log('Botón anterior clickeado');
                prevBannerSlide();
                startBannerAutoSlide();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                console.log('Botón siguiente clickeado');
                nextBannerSlide();
                startBannerAutoSlide();
            });
        }
        
        // Event listeners para indicadores
        bannerIndicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                console.log('Indicador clickeado:', index);
                showBannerSlide(index);
                startBannerAutoSlide();
            });
        });
        
        // Navegación con teclado
        document.addEventListener('keydown', (e) => {
            const bannerSection = document.querySelector('.hero-banner');
            if (bannerSection && bannerSection.offsetTop <= window.scrollY + 100) {
                if (e.key === 'ArrowLeft') {
                    console.log('Tecla izquierda presionada');
                    prevBannerSlide();
                    startBannerAutoSlide();
                }
                if (e.key === 'ArrowRight') {
                    console.log('Tecla derecha presionada');
                    nextBannerSlide();
                    startBannerAutoSlide();
                }
            }
        });
        
        // Pausar auto-slide al pasar el mouse
        const heroBanner = document.querySelector('.hero-banner');
        if (heroBanner) {
            heroBanner.addEventListener('mouseenter', () => {
                console.log('Mouse sobre el banner');
                stopBannerAutoSlide();
            });
            
            heroBanner.addEventListener('mouseleave', () => {
                console.log('Mouse fuera del banner');
                startBannerAutoSlide();
            });
        }
        
        // Iniciar auto-slide
        startBannerAutoSlide();
        
        // Asegurar que el primer slide esté visible
        showBannerSlide(0);
        
        console.log('Carrusel inicializado correctamente');
    }
    
    // ===== Efectos hover para tarjetas de películas =====
    function initMovieCardEffects() {
        const movieCards = document.querySelectorAll('.movie-card');
        
        movieCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px)';
                this.style.boxShadow = '0 15px 30px rgba(255, 193, 7, 0.15)';
                this.style.borderColor = 'var(--accent-color)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = 'none';
                this.style.borderColor = 'var(--dark-border)';
            });
        });
    }
    
    // ===== Botones de tráiler (redirigir a YouTube) =====
    function initTrailerButtons() {
        const trailerButtons = document.querySelectorAll('.trailer-btn');
        
        trailerButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const trailerUrl = this.getAttribute('data-trailer');
                if (trailerUrl) {
                    console.log('Abriendo tráiler:', trailerUrl);
                    window.open(trailerUrl, '_blank');
                }
            });
        });
    }
    
    // ===== Efectos de scroll suave =====
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                
                if (targetId === '#' || targetId === '#!') return;
                
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    const offset = 80;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    history.pushState(null, null, targetId);
                }
            });
        });
    }
    
    // ===== Cambio de tema =====
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            document.body.classList.toggle('light-theme');
            
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            const icon = this.querySelector('i');
            if (isDark) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
            } else {
                icon.classList.remove('bi-sun');
                icon.classList.add('bi-moon');
            }
        });
    }
    
    // Verificar tema guardado en localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
    }
    
    // Inicializar todas las funciones
    initBannerCarousel();
    initMovieCardEffects();
    initTrailerButtons();
    initSmoothScroll();
    
    console.log('CineFlow JavaScript inicializado correctamente');
});