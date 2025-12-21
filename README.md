# Cine Flow

Este repositorio contiene todo el código para adminitrar salas de cine de manera digital.

## Definiendo User Flows

La aplicación esta dirigida a dos tipos de usurios:

- Los que comprar tickets para asistir la funciones (Cliente)
- Los que administran las funciones a ser presentadas (Administrador)

Como hay algunas tareas son comunes para **clientes** y **administradores** las vamos a definir bajo la etiqueta de **usuarios**.

### Usurios

#### Crear Usurio

#### Cambiar contraseña


### Administrador

#### Agregar Películas

#### Vincular películas con salas por día y hora


### Cliente

#### Consultar horarios de una película

#### Consultar todos disponibles de un día

#### Cambiar contraseña

#### Crear usuario

#### Comprar tickets para película

# Ejemplo de diagrama

```mermaid
flowchart TD
    Start([Inicio]) --> Step1[Usuario abre la aplicación]
    Step1 --> Step2[Usuario ingresa credenciales]
    Step2 --> Step3[Sistema valida credenciales]
    Step3 --> Step4[Usuario navega al dashboard]
    Step4 --> Step5[Usuario selecciona 'Crear nuevo proyecto']
    Step5 --> Step6[Sistema muestra formulario]
    Step6 --> Step7[Usuario completa información del proyecto]
    Step7 --> Step8[Usuario hace clic en 'Guardar']
    Step8 --> Step9[Sistema procesa y guarda datos]
    Step9 --> Step10[Sistema muestra confirmación]
    Step10 --> Step11[Usuario ve proyecto en lista]
    Step11 --> End([Fin])
    
    %% Estilos por tipo de acción
    style Start fill:#4CAF50,stroke:#2E7D32,color:#fff
    style End fill:#4CAF50,stroke:#2E7D32,color:#fff
    style Step1 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step2 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step4 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step5 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step7 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step8 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step11 fill:#2196F3,stroke:#1565C0,color:#fff
    style Step3 fill:#FF9800,stroke:#E65100,color:#fff
    style Step6 fill:#FF9800,stroke:#E65100,color:#fff
    style Step9 fill:#FF9800,stroke:#E65100,color:#fff
    style Step10 fill:#FF9800,stroke:#E65100,color:#fff
    
    %% Leyenda
    subgraph Legend[" LEYENDA "]
        L1[Acción del Usuario]
        L2[Acción del Sistema]
        L3[Inicio/Fin]
        
        style L1 fill:#2196F3,stroke:#1565C0,color:#fff
        style L2 fill:#FF9800,stroke:#E65100,color:#fff
        style L3 fill:#4CAF50,stroke:#2E7D32,color:#fff
    end
    
    style Legend fill:#f9f9f9,stroke:#333,stroke-width:2px
```



https://templatemo.com/tm-559-zay-shop

