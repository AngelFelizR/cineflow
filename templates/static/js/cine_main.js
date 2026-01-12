// Funciones JavaScript para la aplicación de cine

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
    
    // Efecto de carga para botones de acción
    const actionButtons = document.querySelectorAll('.btn-action');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
            this.disabled = true;
            
            // Restaurar el botón después de 2 segundos (simulación)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        });
    });
    
    // Manejo de selección de asientos (ejemplo)
    const seatElements = document.querySelectorAll('.seat-selectable');
    
    seatElements.forEach(seat => {
        seat.addEventListener('click', function() {
            this.classList.toggle('selected');
            updateTotalPrice();
        });
    });
    
    // Función para actualizar el precio total
    function updateTotalPrice() {
        const selectedSeats = document.querySelectorAll('.seat-selectable.selected');
        const pricePerSeat = 10; // Precio por asiento (ejemplo)
        const totalPrice = selectedSeats.length * pricePerSeat;
        
        const totalElement = document.getElementById('total-price');
        if (totalElement) {
            totalElement.textContent = `$${totalPrice.toFixed(2)}`;
        }
    }
    
    // Manejo de filtros de películas
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remover clase activa de todos los botones
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Agregar clase activa al botón clickeado
            this.classList.add('active');
            
            // Aquí iría la lógica para filtrar películas
            const filterValue = this.getAttribute('data-filter');
            filterMovies(filterValue);
        });
    });
    
    function filterMovies(filter) {
        // Esta función se implementaría según la lógica de filtrado
        console.log(`Filtrando películas por: ${filter}`);
    }
    
    // Cambio de tema (si se quisiera alternar entre claro/oscuro)
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            document.body.classList.toggle('light-theme');
            
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            // Cambiar ícono según el tema
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
});