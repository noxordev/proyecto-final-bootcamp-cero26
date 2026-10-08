// Muestra un texto en el hueco de mensajes. Con "" lo deja vacío.
function showMessage(text) {
    document.getElementById("message").textContent = text;
}

// Recibe la lista de películas de la API y pinta cada una como un enlace a su detalle.
// Si la lista está vacía, lo avisa con un mensaje.
function showMovies(movies) {
    if (movies.length === 0) {
        showMessage("No se encontraron películas.");
        return;
    }
    const results = document.getElementById("results");
    movies.forEach(movie => {
        const link = document.createElement("a"); // Mejor que innerHTML que vimos en clase porque es más seguro. Crea el elemento <a> en el DOM.
        link.href = `detail.html?id=${movie.imdbID}`; // URL de la película.
        link.className = "list-group-item list-group-item-action"; // Clase para que se vea como un enlace.
        link.textContent = `${movie.Title} (${movie.Year})`; // Texto del enlace en la lista de resultados.
        results.appendChild(link); // Añade el enlace al contenedor de resultados.
    });
}

// Se ejecuta al enviar el formulario: pide las películas a /api/search y las muestra, o muestra el error.
async function searchMovies(event) {
    event.preventDefault();     // Evita que el formulario se envíe y se recargue la página. Pasaba en clases.
    showMessage("");
    document.getElementById("results").innerHTML = ""; // Limpia el contenedor de resultados de búsquedas anteriores.

    const params = new URLSearchParams({ // Crea un objeto con los parámetros de la búsqueda. 
        title: document.getElementById("title").value,
        year: document.getElementById("year").value,
    });

    try {
        const response = await fetch(`/api/search?${params}`); // Hace la petición a la API.
        const data = await response.json(); // Convierte la respuesta a JSON.
        // Si la API responde con error, el motivo viene dentro del JSON, en "detail".
        if (!response.ok) {
            showMessage(`No se pudo completar la búsqueda: ${data.detail}`);
            return;
        }
        showMovies(data);
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        showMessage("No se pudo completar la búsqueda. Inténtalo de nuevo.");
    }
}

document.getElementById("search-form").addEventListener("submit", searchMovies);
