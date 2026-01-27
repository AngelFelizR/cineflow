// Dashboard JavaScript para CineFlow
$(document).ready(function() {
    // Inicializar selectores
    $('.selectpicker').selectpicker({
        style: 'btn-light',
        size: 10
    });
    
    // Variables para las gráficas ECharts
    let ingresosChart = null;
    let ocupacionChart = null;
    let boletosUsadosChart = null;
    let cancelacionesChart = null;
    
    // Inicializar gráficas
    function inicializarGraficas() {
        // Inicializar gráfica de ingresos
        ingresosChart = echarts.init(document.getElementById('ingresos-chart'), 'dark');
        
        // Inicializar gráfica de ocupación
        ocupacionChart = echarts.init(document.getElementById('ocupacion-chart'), 'dark');
        
        // Inicializar gráfica de boletos usados
        boletosUsadosChart = echarts.init(document.getElementById('boletos-usados-chart'), 'dark');
        
        // Inicializar gráfica de cancelaciones
        cancelacionesChart = echarts.init(document.getElementById('cancelaciones-chart'), 'dark');
        
        // Configurar opciones iniciales
        configurarGraficas();
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
                    const fecha = params[0].name;
                    const valor = params[0].value;
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
                    const fecha = params[0].name;
                    const valor = params[0].value;
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
                    const fecha = params[0].name;
                    const valor = params[0].value;
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
                    const fecha = params[0].name;
                    const valor = params[0].value;
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
        
        // Aplicar opciones
        ingresosChart.setOption(ingresosOptions);
        ocupacionChart.setOption(ocupacionOptions);
        boletosUsadosChart.setOption(boletosUsadosOptions);
        cancelacionesChart.setOption(cancelacionesOptions);
    }
    
    // Función para obtener datos del dashboard
    function obtenerDatosDashboard() {
        // Mostrar overlay de carga
        $('#loading-overlay').show();
        
        // Recolectar datos del formulario
        const formData = $('#filtros-form').serializeArray();
        const data = {};
        
        // Convertir form data a objeto
        formData.forEach(item => {
            if (item.name.endsWith('[]')) {
                const key = item.name.slice(0, -2);
                if (!data[key]) data[key] = [];
                data[key].push(item.value);
            } else {
                data[item.name] = item.value;
            }
        });
        
        // Enviar solicitud AJAX
        $.ajax({
            url: '/admin/dashboard/data',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                // Actualizar gráficas con los datos recibidos
                actualizarGraficas(response);
                actualizarResumenes(response);
                $('#loading-overlay').hide();
                
                // Mostrar notificación de éxito
                Swal.fire({
                    icon: 'success',
                    title: 'Datos actualizados',
                    text: 'Las gráficas se han actualizado con los filtros aplicados.',
                    timer: 2000,
                    showConfirmButton: false
                });
            },
            error: function(xhr) {
                $('#loading-overlay').hide();
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: xhr.responseJSON?.error || 'Error al cargar los datos del dashboard'
                });
            }
        });
    }
    
    // Actualizar gráficas con datos
    function actualizarGraficas(datos) {
        // Actualizar gráfica de ingresos
        if (datos.ingresos && datos.ingresos.length > 0) {
            const periodos = datos.ingresos.map(item => item.Periodo);
            const valores = datos.ingresos.map(item => item.Ingresos);
            
            ingresosChart.setOption({
                xAxis: { data: periodos },
                series: [{ data: valores }]
            });
        }
        
        // Actualizar gráfica de ocupación
        if (datos.ocupacion && datos.ocupacion.length > 0) {
            const periodos = datos.ocupacion.map(item => item.Periodo);
            const valores = datos.ocupacion.map(item => item.PorcentajeOcupacion);
            
            ocupacionChart.setOption({
                xAxis: { data: periodos },
                series: [{ data: valores }]
            });
        }
        
        // Actualizar gráfica de boletos usados
        if (datos.boletos_usados && datos.boletos_usados.length > 0) {
            const periodos = datos.boletos_usados.map(item => item.Periodo);
            const valores = datos.boletos_usados.map(item => item.PorcentajeUsados);
            
            boletosUsadosChart.setOption({
                xAxis: { data: periodos },
                series: [{ data: valores }]
            });
        }
        
        // Actualizar gráfica de cancelaciones
        if (datos.cancelaciones && datos.cancelaciones.length > 0) {
            const periodos = datos.cancelaciones.map(item => item.Periodo);
            const valores = datos.cancelaciones.map(item => item.PorcentajeCancelaciones);
            
            cancelacionesChart.setOption({
                xAxis: { data: periodos },
                series: [{ data: valores }]
            });
        }
    }
    
    // Actualizar resúmenes debajo de cada gráfica
    function actualizarResumenes(datos) {
        // Resumen de ingresos
        if (datos.ingresos && datos.ingresos.length > 0) {
            const totalIngresos = datos.ingresos.reduce((sum, item) => sum + (item.Ingresos || 0), 0);
            const totalBoletos = datos.ingresos.reduce((sum, item) => sum + (item.BoletosVendidos || 0), 0);
            const promedioIngresos = totalIngresos / datos.ingresos.length;
            
            $('#ingresos-summary').html(`
                <strong>Total:</strong> $${totalIngresos.toLocaleString('es-DO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} | 
                <strong>Boletos:</strong> ${totalBoletos} | 
                <strong>Promedio:</strong> $${promedioIngresos.toLocaleString('es-DO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            `);
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
    }
    
    // Descargar datos de una métrica específica (simulado - se puede implementar si se necesita)
    function descargarDatosMetrica(metrica) {
        // Por ahora, redirigir a la exportación completa de Excel
        // Esto se puede modificar para exportar solo una métrica específica
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
        if (ingresosChart) ingresosChart.resize();
        if (ocupacionChart) ocupacionChart.resize();
        if (boletosUsadosChart) boletosUsadosChart.resize();
        if (cancelacionesChart) cancelacionesChart.resize();
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
    inicializarGraficas();
    
    // Cargar datos iniciales
    obtenerDatosDashboard();
});