// Dashboard JavaScript para CineFlow
$(document).ready(function() {
    console.log('Inicializando dashboard...');
    
    // Inicializar selectores
    $('.selectpicker').selectpicker({
        style: 'btn-light',
        size: 10,
        noneSelectedText: 'Ninguno seleccionado',
        selectAllText: 'Seleccionar todos',
        deselectAllText: 'Deseleccionar todos'
    });
    
    // Variables para las gráficas ECharts
    let ingresosChart = null;
    let ocupacionChart = null;
    let boletosUsadosChart = null;
    let cancelacionesChart = null;
    
    // Inicializar gráficas
    function inicializarGraficas() {
        // Verificar si ECharts está disponible
        if (typeof echarts === 'undefined') {
            console.error('ECharts no está cargado. Recargando página...');
            setTimeout(function() {
                location.reload();
            }, 1000);
            return;
        }
        
        try {
            console.log('Inicializando gráficas ECharts...');
            
            // Inicializar gráfica de ingresos
            const ingresosContainer = document.getElementById('ingresos-chart');
            if (ingresosContainer) {
                ingresosChart = echarts.init(ingresosContainer, 'dark');
            }
            
            // Inicializar gráfica de ocupación
            const ocupacionContainer = document.getElementById('ocupacion-chart');
            if (ocupacionContainer) {
                ocupacionChart = echarts.init(ocupacionContainer, 'dark');
            }
            
            // Inicializar gráfica de boletos usados
            const boletosUsadosContainer = document.getElementById('boletos-usados-chart');
            if (boletosUsadosContainer) {
                boletosUsadosChart = echarts.init(boletosUsadosContainer, 'dark');
            }
            
            // Inicializar gráfica de cancelaciones
            const cancelacionesContainer = document.getElementById('cancelaciones-chart');
            if (cancelacionesContainer) {
                cancelacionesChart = echarts.init(cancelacionesContainer, 'dark');
            }
            
            // Configurar opciones iniciales
            configurarGraficas();
            
            console.log('Gráficas inicializadas correctamente');
        } catch (error) {
            console.error('Error al inicializar gráficas:', error);
            mostrarMensajeError('Error al inicializar las gráficas. Por favor, recarga la página.');
        }
    }
    
    // Configurar opciones de las gráficas
    function configurarGraficas() {
        // Opciones para gráfica de ingresos
        const ingresosOptions = {
            title: {
                text: 'Ingresos por Período',
                left: 'center',
                textStyle: {
                    color: '#e2e8f0',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    if (!params || params.length === 0) return '';
                    const fecha = params[0].name;
                    const valor = params[0].value || 0;
                    return `<strong>${fecha}</strong><br/>Ingresos: <span style="color: #28a745; font-weight: bold;">$${valor.toLocaleString('es-DO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>`;
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#28a745',
                textStyle: {
                    color: '#fff'
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLabel: {
                    color: '#a0aec0',
                    rotate: 45
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: 'Dólares ($)',
                nameTextStyle: {
                    color: '#a0aec0'
                },
                axisLabel: {
                    formatter: '${value}',
                    color: '#a0aec0'
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#4a5568',
                        type: 'dashed'
                    }
                }
            },
            series: [{
                name: 'Ingresos',
                type: 'line',
                data: [],
                smooth: true,
                itemStyle: {
                    color: '#28a745'
                },
                lineStyle: {
                    color: '#28a745',
                    width: 3
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(40, 167, 69, 0.6)' },
                        { offset: 1, color: 'rgba(40, 167, 69, 0.1)' }
                    ])
                },
                symbol: 'circle',
                symbolSize: 8
            }],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                top: '15%',
                containLabel: true
            },
            backgroundColor: 'transparent'
        };
        
        // Opciones para gráfica de ocupación
        const ocupacionOptions = {
            title: {
                text: 'Ocupación de Salas',
                left: 'center',
                textStyle: {
                    color: '#e2e8f0',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    if (!params || params.length === 0) return '';
                    const fecha = params[0].name;
                    const valor = params[0].value || 0;
                    return `<strong>${fecha}</strong><br/>Ocupación: <span style="color: #17a2b8; font-weight: bold;">${valor.toFixed(2)}%</span>`;
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#17a2b8',
                textStyle: {
                    color: '#fff'
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLabel: {
                    color: '#a0aec0',
                    rotate: 45
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: 'Porcentaje (%)',
                nameTextStyle: {
                    color: '#a0aec0'
                },
                axisLabel: {
                    formatter: '{value}%',
                    color: '#a0aec0'
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#4a5568',
                        type: 'dashed'
                    }
                },
                max: 100
            },
            series: [{
                name: 'Ocupación',
                type: 'line',
                data: [],
                smooth: true,
                itemStyle: {
                    color: '#17a2b8'
                },
                lineStyle: {
                    color: '#17a2b8',
                    width: 3
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(23, 162, 184, 0.6)' },
                        { offset: 1, color: 'rgba(23, 162, 184, 0.1)' }
                    ])
                },
                symbol: 'circle',
                symbolSize: 8
            }],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                top: '15%',
                containLabel: true
            },
            backgroundColor: 'transparent'
        };
        
        // Opciones para gráfica de boletos usados
        const boletosUsadosOptions = {
            title: {
                text: 'Boletos Usados',
                left: 'center',
                textStyle: {
                    color: '#e2e8f0',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    if (!params || params.length === 0) return '';
                    const fecha = params[0].name;
                    const valor = params[0].value || 0;
                    return `<strong>${fecha}</strong><br/>Usados: <span style="color: #ffc107; font-weight: bold;">${valor.toFixed(2)}%</span>`;
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#ffc107',
                textStyle: {
                    color: '#fff'
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLabel: {
                    color: '#a0aec0',
                    rotate: 45
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: 'Porcentaje (%)',
                nameTextStyle: {
                    color: '#a0aec0'
                },
                axisLabel: {
                    formatter: '{value}%',
                    color: '#a0aec0'
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#4a5568',
                        type: 'dashed'
                    }
                },
                max: 100
            },
            series: [{
                name: 'Boletos Usados',
                type: 'line',
                data: [],
                smooth: true,
                itemStyle: {
                    color: '#ffc107'
                },
                lineStyle: {
                    color: '#ffc107',
                    width: 3
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(255, 193, 7, 0.6)' },
                        { offset: 1, color: 'rgba(255, 193, 7, 0.1)' }
                    ])
                },
                symbol: 'circle',
                symbolSize: 8
            }],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                top: '15%',
                containLabel: true
            },
            backgroundColor: 'transparent'
        };
        
        // Opciones para gráfica de cancelaciones
        const cancelacionesOptions = {
            title: {
                text: 'Cancelaciones',
                left: 'center',
                textStyle: {
                    color: '#e2e8f0',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                formatter: function(params) {
                    if (!params || params.length === 0) return '';
                    const fecha = params[0].name;
                    const valor = params[0].value || 0;
                    return `<strong>${fecha}</strong><br/>Cancelaciones: <span style="color: #dc3545; font-weight: bold;">${valor.toFixed(2)}%</span>`;
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#dc3545',
                textStyle: {
                    color: '#fff'
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLabel: {
                    color: '#a0aec0',
                    rotate: 45
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                }
            },
            yAxis: {
                type: 'value',
                name: 'Porcentaje (%)',
                nameTextStyle: {
                    color: '#a0aec0'
                },
                axisLabel: {
                    formatter: '{value}%',
                    color: '#a0aec0'
                },
                axisLine: {
                    lineStyle: {
                        color: '#4a5568'
                    }
                },
                splitLine: {
                    lineStyle: {
                        color: '#4a5568',
                        type: 'dashed'
                    }
                },
                max: 100
            },
            series: [{
                name: 'Cancelaciones',
                type: 'line',
                data: [],
                smooth: true,
                itemStyle: {
                    color: '#dc3545'
                },
                lineStyle: {
                    color: '#dc3545',
                    width: 3
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(220, 53, 69, 0.6)' },
                        { offset: 1, color: 'rgba(220, 53, 69, 0.1)' }
                    ])
                },
                symbol: 'circle',
                symbolSize: 8
            }],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                top: '15%',
                containLabel: true
            },
            backgroundColor: 'transparent'
        };
        
        // Aplicar opciones iniciales
        if (ingresosChart) ingresosChart.setOption(ingresosOptions);
        if (ocupacionChart) ocupacionChart.setOption(ocupacionOptions);
        if (boletosUsadosChart) boletosUsadosChart.setOption(boletosUsadosOptions);
        if (cancelacionesChart) cancelacionesChart.setOption(cancelacionesOptions);
    }
    
    // Obtener datos del dashboard
    function obtenerDatosDashboard() {
        console.log('Obteniendo datos del dashboard...');
        
        // Mostrar overlay de carga
        $('#loading-overlay').fadeIn();
        
        // Obtener valores del formulario
        const filtros = {
            fecha_inicio: $('#fecha-inicio').val(),
            fecha_fin: $('#fecha-fin').val(),
            agrupacion: $('#agrupacion-select').val(),
            cine_ids: $('#cine-select').val() || [],
            genero_ids: $('#genero-select').val() || [],
            pelicula_ids: $('#pelicula-select').val() || [],
            funcion_ids: $('#funcion-select').val() || [],
            dias_semana: $('#dia-semana-select').val() || []
        };
        
        console.log('Filtros aplicados:', filtros);
        
        // Validar fechas
        if (!filtros.fecha_inicio || !filtros.fecha_fin) {
            mostrarMensajeError('Por favor, selecciona las fechas de inicio y fin.');
            return;
        }
        
        // Realizar solicitud AJAX
        $.ajax({
            url: '/admin/dashboard/data',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(filtros),
            success: function(datos) {
                console.log('Datos recibidos:', datos);
                
                if (datos.error) {
                    mostrarMensajeError(datos.error);
                    return;
                }
                
                // Actualizar gráficas con los datos
                actualizarGraficas(datos);
                
                // Actualizar resúmenes
                actualizarResumenes(datos);
                
                // Ocultar overlay
                $('#loading-overlay').fadeOut();
                
                console.log('Dashboard actualizado correctamente');
            },
            error: function(xhr, status, error) {
                console.error('Error al obtener datos:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
                
                let mensaje = 'Error al cargar los datos del dashboard.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    mensaje += ' ' + xhr.responseJSON.error;
                }
                
                mostrarMensajeError(mensaje);
            }
        });
    }
    
    // Actualizar gráficas con nuevos datos
    function actualizarGraficas(datos) {
        try {
            console.log('Actualizando gráficas...');
            
            // Actualizar gráfica de ingresos
            if (ingresosChart && datos.ingresos) {
                const periodos = datos.ingresos.map(item => item.Periodo);
                const valores = datos.ingresos.map(item => item.Ingresos || 0);
                
                ingresosChart.setOption({
                    xAxis: { data: periodos },
                    series: [{ data: valores }]
                });
                
                console.log('Gráfica de ingresos actualizada:', periodos.length, 'puntos');
            }
            
            // Actualizar gráfica de ocupación
            if (ocupacionChart && datos.ocupacion) {
                const periodos = datos.ocupacion.map(item => item.Periodo);
                const valores = datos.ocupacion.map(item => item.PorcentajeOcupacion || 0);
                
                ocupacionChart.setOption({
                    xAxis: { data: periodos },
                    series: [{ data: valores }]
                });
                
                console.log('Gráfica de ocupación actualizada:', periodos.length, 'puntos');
            }
            
            // Actualizar gráfica de boletos usados
            if (boletosUsadosChart && datos.boletos_usados) {
                const periodos = datos.boletos_usados.map(item => item.Periodo);
                const valores = datos.boletos_usados.map(item => item.PorcentajeUsados || 0);
                
                boletosUsadosChart.setOption({
                    xAxis: { data: periodos },
                    series: [{ data: valores }]
                });
                
                console.log('Gráfica de boletos usados actualizada:', periodos.length, 'puntos');
            }
            
            // Actualizar gráfica de cancelaciones
            if (cancelacionesChart && datos.cancelaciones) {
                const periodos = datos.cancelaciones.map(item => item.Periodo);
                const valores = datos.cancelaciones.map(item => item.PorcentajeCancelaciones || 0);
                
                cancelacionesChart.setOption({
                    xAxis: { data: periodos },
                    series: [{ data: valores }]
                });
                
                console.log('Gráfica de cancelaciones actualizada:', periodos.length, 'puntos');
            }
            
        } catch (error) {
            console.error('Error al actualizar gráficas:', error);
            mostrarMensajeError('Error al renderizar las gráficas.');
        }
    }
    
    // Mostrar mensaje de error
    function mostrarMensajeError(mensaje) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje || 'Error desconocido'
        });
        $('#loading-overlay').fadeOut();
    }
    
    // Actualizar resúmenes debajo de cada gráfica
    function actualizarResumenes(datos) {
        try {
            // Resumen de ingresos
            if (datos.ingresos && datos.ingresos.length > 0) {
                const totalIngresos = datos.ingresos.reduce((sum, item) => sum + (item.Ingresos || 0), 0);
                const totalBoletos = datos.ingresos.reduce((sum, item) => sum + (item.BoletosVendidos || 0), 0);
                const promedioIngresos = datos.ingresos.length > 0 ? totalIngresos / datos.ingresos.length : 0;
                
                $('#ingresos-summary').html(`
                    <strong>Total:</strong> $${totalIngresos.toLocaleString('es-DO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} | 
                    <strong>Boletos:</strong> ${totalBoletos} | 
                    <strong>Promedio:</strong> $${promedioIngresos.toLocaleString('es-DO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                `);
            } else {
                $('#ingresos-summary').html('<span class="text-warning">No hay datos disponibles</span>');
            }
            
            // Resumen de ocupación
            if (datos.ocupacion && datos.ocupacion.length > 0) {
                const ocupacionPromedio = datos.ocupacion.reduce((sum, item) => sum + (item.PorcentajeOcupacion || 0), 0) / datos.ocupacion.length;
                const capacidadTotal = datos.ocupacion.reduce((sum, item) => sum + (item.CapacidadTotal || 0), 0);
                const boletosVendidos = datos.ocupacion.reduce((sum, item) => sum + (item.BoletosVendidos || 0), 0);
                
                $('#ocupacion-summary').html(`
                    <strong>Ocupación promedio:</strong> ${ocupacionPromedio.toFixed(2)}% | 
                    <strong>Capacidad total:</strong> ${capacidadTotal} asientos | 
                    <strong>Boletos vendidos:</strong> ${boletosVendidos}
                `);
            } else {
                $('#ocupacion-summary').html('<span class="text-warning">No hay datos disponibles</span>');
            }
            
            // Resumen de boletos usados
            if (datos.boletos_usados && datos.boletos_usados.length > 0) {
                const promedioUsados = datos.boletos_usados.reduce((sum, item) => sum + (item.PorcentajeUsados || 0), 0) / datos.boletos_usados.length;
                const totalBoletos = datos.boletos_usados.reduce((sum, item) => sum + (item.BoletosTotales || 0), 0);
                const totalUsados = datos.boletos_usados.reduce((sum, item) => sum + (item.BoletosUsados || 0), 0);
                
                $('#boletos-usados-summary').html(`
                    <strong>Promedio usado:</strong> ${promedioUsados.toFixed(2)}% | 
                    <strong>Total boletos:</strong> ${totalBoletos} | 
                    <strong>Total usados:</strong> ${totalUsados}
                `);
            } else {
                $('#boletos-usados-summary').html('<span class="text-warning">No hay datos disponibles</span>');
            }
            
            // Resumen de cancelaciones
            if (datos.cancelaciones && datos.cancelaciones.length > 0) {
                const promedioCancel = datos.cancelaciones.reduce((sum, item) => sum + (item.PorcentajeCancelaciones || 0), 0) / datos.cancelaciones.length;
                const totalVendidos = datos.cancelaciones.reduce((sum, item) => sum + (item.BoletosVendidos || 0), 0);
                const totalCancelados = datos.cancelaciones.reduce((sum, item) => sum + (item.BoletosCancelados || 0), 0);
                
                $('#cancelaciones-summary').html(`
                    <strong>Cancelación promedio:</strong> ${promedioCancel.toFixed(2)}% | 
                    <strong>Total vendidos:</strong> ${totalVendidos} | 
                    <strong>Total cancelados:</strong> ${totalCancelados}
                `);
            } else {
                $('#cancelaciones-summary').html('<span class="text-warning">No hay datos disponibles</span>');
            }
        } catch (error) {
            console.error('Error al actualizar resúmenes:', error);
        }
    }
    
    // Descargar gráfica como PNG
    function descargarGrafica(chartElementId) {
        let chart;
        switch(chartElementId) {
            case 'ingresos-chart':
                chart = ingresosChart;
                break;
            case 'ocupacion-chart':
                chart = ocupacionChart;
                break;
            case 'boletos-usados-chart':
                chart = boletosUsadosChart;
                break;
            case 'cancelaciones-chart':
                chart = cancelacionesChart;
                break;
            default:
                return;
        }
        
        if (!chart) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'La gráfica no está disponible para descargar'
            });
            return;
        }
        
        try {
            const url = chart.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#1a202c'
            });
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `cineflow_${chartElementId}_${new Date().toISOString().slice(0,10)}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Error al descargar gráfica:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo descargar la gráfica'
            });
        }
    }
    
    // Descargar datos de una métrica específica
    function descargarDatosMetrica(metrica) {
        const formData = $('#filtros-form').serialize();
        window.location.href = `/admin/dashboard/export/excel?${formData}`;
    }
    
    // Exportar a Excel
    function exportarExcel() {
        const formData = $('#filtros-form').serialize();
        window.location.href = `/admin/dashboard/export/excel?${formData}`;
    }
    
    // Exportar a PDF
    function exportarPDF() {
        const formData = $('#filtros-form').serialize();
        window.location.href = `/admin/dashboard/export/pdf?${formData}`;
    }
    
    // Limpiar todos los filtros
    function limpiarFiltros() {
        // Limpiar selects
        $('.selectpicker').selectpicker('deselectAll');
        
        // Restablecer fechas a los últimos 30 días
        const fechaFin = new Date();
        const fechaInicio = new Date();
        fechaInicio.setDate(fechaInicio.getDate() - 30);
        
        $('#fecha-inicio').val(fechaInicio.toISOString().slice(0, 10));
        $('#fecha-fin').val(fechaFin.toISOString().slice(0, 10));
        
        // Restablecer agrupación a día
        $('#agrupacion-select').val('dia');
        $('.selectpicker').selectpicker('refresh');
        
        // Actualizar gráficas con filtros limpios
        obtenerDatosDashboard();
    }
    
    // Redimensionar gráficas al cambiar tamaño de ventana
    function redimensionarGraficas() {
        try {
            if (ingresosChart) ingresosChart.resize();
            if (ocupacionChart) ocupacionChart.resize();
            if (boletosUsadosChart) boletosUsadosChart.resize();
            if (cancelacionesChart) cancelacionesChart.resize();
        } catch (error) {
            console.error('Error al redimensionar gráficas:', error);
        }
    }
    
    // Event Listeners
    $('#filtros-form').on('submit', function(e) {
        e.preventDefault();
        obtenerDatosDashboard();
    });
    
    $('#limpiar-filtros').on('click', limpiarFiltros);
    
    $('.download-chart').on('click', function() {
        const chartId = $(this).data('chart');
        descargarGrafica(chartId);
    });
    
    $('.download-data').on('click', function() {
        const metrica = $(this).data('metric');
        descargarDatosMetrica(metrica);
    });
    
    $('#export-excel-btn').on('click', exportarExcel);
    $('#export-pdf-btn').on('click', exportarPDF);
    
    $(window).on('resize', redimensionarGraficas);
    
    // Inicializar
    console.log('Esperando inicialización...');
    setTimeout(function() {
        inicializarGraficas();
        
        // Cargar datos iniciales después de un breve delay para asegurar que las gráficas estén listas
        setTimeout(function() {
            obtenerDatosDashboard();
        }, 500);
    }, 100);
});