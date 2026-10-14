// El id viene en la dirección (detail.html?id=tt0133093). Lo usan la película y sus comentarios.
const movieId = new URLSearchParams(window.location.search).get("id");

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

// Pide la película a la API y la muestra. Si algo falla, muestra el error en el hueco de mensajes.
async function loadMovie() {
    const message = document.getElementById("message");
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

// Recibe la lista de comentarios de la API y pinta cada uno: quién, cuándo y qué dijo.
// Si la lista está vacía, lo avisa con un mensaje.
function showComments(comments) {
    const list = document.getElementById("comments");
    list.innerHTML = "";
    if (comments.length === 0) {
        document.getElementById("comments-message").textContent = "Todavía no hay comentarios.";
        return;
    }
    comments.forEach(comment => {
        const item = document.createElement("li");
        item.className = "list-group-item";

        const author = document.createElement("strong");
        author.textContent = `${comment.person} · ${comment.date}`;

        // textContent: lo que escribió otra persona se muestra como texto, nunca se ejecuta como HTML.
        const text = document.createElement("p");
        text.className = "mb-0";
        text.textContent = comment.comment;

        item.appendChild(author);
        item.appendChild(text);
        list.appendChild(item);
    });
}

// Pide a la API los comentarios de la película y los muestra. Si algo falla, muestra el error.
async function loadComments() {
    const message = document.getElementById("comments-message");
    message.textContent = "";
    try {
        const response = await fetch(`/api/movies/${movieId}/comments`);
        const data = await response.json();
        if (!response.ok) {
            message.textContent = data.detail;
            return;
        }
        showComments(data);
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        message.textContent = "No se pudieron cargar los comentarios. Inténtalo de nuevo.";
    }
}

loadMovie();
loadComments();
