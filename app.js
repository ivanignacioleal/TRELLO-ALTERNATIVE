// Establecer conexión con SocketIO
const socket = io();

// Función para crear un tablero
function crearTablero() {
    const nombreTablero = document.getElementById('nombre-tablero').value;
    if (nombreTablero) {
        socket.emit('crear_tablero', { nombre: nombreTablero });
        document.getElementById('nombre-tablero').value = ''; // Limpiar el campo de texto
    }
}

// Función para eliminar un tablero
function eliminarTablero(button) {
    const tableroId = button.getAttribute('data-id');
    socket.emit('eliminar_tablero', { id: tableroId });
}

// Función para agregar un ítem a un tablero
function agregarItem(button) {
    const tableroId = button.closest('li').id.split('-')[1];  // Extraer el ID del tablero del `li` que contiene el botón
    const item = document.getElementById('input-item-' + tableroId).value;
    if (item) {
        socket.emit('agregar_item', { tableroId: tableroId, item: item });
        document.getElementById('input-item-' + tableroId).value = ''; // Limpiar el campo de texto
    }
}

// Función para eliminar un ítem de un tablero
function eliminarItem(tableroId, itemId) {
    socket.emit('eliminar_item', { tableroId: tableroId, itemId: itemId });
}

// Recibir actualizaciones de los tableros y los ítems
socket.on('actualizar_tableros', function(data) {
    actualizarTableros(data.tableros);
});

// Actualizar la lista de tableros
function actualizarTableros(tableros) {
    const tablerosLista = document.getElementById('tableros-lista');
    tablerosLista.innerHTML = ''; // Limpiar la lista actual

    tableros.forEach(tablero => {
        const liTablero = document.createElement('li');
        liTablero.id = 'tablero-' + tablero.id;

        // Nombre del tablero
        liTablero.innerHTML = `
            <strong>${tablero.nombre}</strong>
            <button class="eliminar-tablero" data-id="${tablero.id}" onclick="eliminarTablero(this)">Eliminar Tablero</button>
            <ul id="items-lista-${tablero.id}"></ul>
            <input type="text" id="input-item-${tablero.id}" placeholder="Nuevo ítem">
            <button onclick="agregarItem(this)">Agregar Ítem</button>
        `;

        // Añadir items al tablero
        const itemsLista = liTablero.querySelector(`#items-lista-${tablero.id}`);
        tablero.items.forEach(item => {
            const liItem = document.createElement('li');
            liItem.id = `item-${item.id}`;
            liItem.innerHTML = `${item.nombre} <button onclick="eliminarItem(${tablero.id}, ${item.id})">Eliminar Item</button>`;
            itemsLista.appendChild(liItem);
        });

        tablerosLista.appendChild(liTablero);
    });
}
