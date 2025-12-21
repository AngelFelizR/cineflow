# Cine Flow

Sistema digital para administración de cines y venta de tickets.

## 👥 Roles de Usuario

### **Cliente**
- Usuario final que compra tickets para funciones
- Necesita consultar información y realizar compras

### **Administrador**
- Personal del cine que gestiona operaciones
- Requiere herramientas de gestión y reportes

## 🔄 User Flows

### **Usuarios (Flujos Comunes)**
1. **Registrar cuenta** - Crear nuevo usuario
2. **Iniciar sesión** - Autenticación en el sistema
3. **Recuperar contraseña** - Restablecer credenciales
4. **Cerrar sesión** - Finalizar sesión activa
5. **Actualizar perfil** - Modificar información personal

### **Administrador**
1. **Gestionar películas**
   - Agregar nuevas películas
   - Actualizar información existente
   - Eliminar películas del catálogo
   
2. **Gestionar salas**
   - Crear/configurar nuevas salas
   - Definir capacidad y distribución
   - Mantenimiento de salas

3. **Programar funciones**
   - Vincular películas con salas
   - Establecer horarios y fechas
   - Modificar/cancelar funciones

4. **Reportes y métricas**
   - Ventas por período
   - Ocupación de salas
   - Popularidad de películas
   - Ingresos por combos

### **Cliente**
1. **Búsqueda y consulta**
   - Consultar horarios por película
   - Ver funciones por día
   - Explorar cartelera completa
   - Ver detalles de películas

2. **Proceso de compra**
   - Seleccionar función y horario
   - Elegir asientos disponibles
   - Agregar combos de comida
   - Completar pago seguro
   - Recibir confirmación

3. **Gestionar reservas**
   - Ver historial de compras
   - Modificar reservas existentes
   - Cancelar reservas (con políticas)
   - Recibir recordatorios

4. **Experiencia post-compra**
   - Recibir QR de acceso (24h antes)
   - Valorar experiencia
   - Obtener recomendaciones

## 📊 Diagrama de Flujo Ejemplo (Proceso de Compra Cliente)

```mermaid
flowchart TD
    Start([Cliente busca película]) --> Step1[Explora cartelera]
    Step1 --> Step2[Selecciona función]
    Step2 --> Step3[Elige cantidad de tickets]
    Step3 --> Step4[Selecciona asientos en mapa]
    Step4 --> Step5[Añade combos opcionales]
    Step5 --> Step6[Revisa resumen]
    Step6 --> Step7[Proceso de pago]
    Step7 --> Step8[Pago exitoso]
    Step8 --> Step9[Recibe confirmación por email]
    Step9 --> Step10[QR generado 24h antes]
    Step10 --> End([Asiste a función])
    
    %% Flujos alternativos
    Step6 -->|Modificar| Step3
    Step7 -->|Pago fallido| Step7
    Step10 -->|Perdió QR| Step11[Solicitar nuevo QR]
    Step11 --> Step10
    
    %% Estilos
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style End fill:#4CAF50,stroke:#2E7D32,color:#fff
```



https://templatemo.com/tm-559-zay-shop

