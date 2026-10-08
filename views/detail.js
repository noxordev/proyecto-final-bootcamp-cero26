// Recibe los datos de una película (tal como los da la API) y los pinta en la página.
function showMovie(movie) {
    document.title = movie.Title;
    document.getElementById("title").textContent = `${movie.Title} (${movie.Year})`;
    document.getElementById("plot").textContent = movie.Plot;
    document.getElementById("director").textContent = movie.Director;
    document.getElementById("actors").textContent = movie.Actors;
    document.getElementById("genre").textContent = movie.Genre;
    document.getElementById("runtime").textContent = movie.Runtime;

    // OMDb pone el texto "N/A" cuando no tiene póster: en ese caso la imagen sigue oculta.
    if (movie.Poster !== "N/A") {
        const poster = document.getElementById("poster");
        poster.src = movie.Poster; // Asigna la URL del póster a la imagen.
        poster.alt = `Póster de ${movie.Title}`; // Asigna el texto alternativo a la imagen.
        poster.hidden = false; // Muestra la imagen.
    }
    document.getElementById("movie").hidden = false; // Muestra el contenedor de la película.
}

// Lee el id de la dirección (detail.html?id=tt0133093), pide la película a la API y la muestra.
// Si algo falla, muestra el error en el hueco de mensajes.
async function loadMovie() {
    const message = document.getElementById("message");
    const movieId = new URLSearchParams(window.location.search).get("id");
    try {
        const response = await fetch(`/api/movies/${movieId}`);
        const data = await response.json();
        if (!response.ok) {
            message.textContent = `No se pudo cargar la película: ${data.detail}`;
            return;
        }
        showMovie(data);
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        message.textContent = "No se pudo cargar la película. Inténtalo de nuevo.";
    }
}

loadMovie();
