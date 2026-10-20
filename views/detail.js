// La película, sus comentarios y el formulario (principio DRY). Se hace en tres pasos:
const queryString = window.location.search; // 1. Revisa la parte de la dirección que va desde el "?" para obtener el id de la película:
const params = new URLSearchParams(queryString); // 2. Convierte ese texto en un objeto al que se le puede 
// preguntar por cada parámetro.
const movieId = params.get("id"); // 3. Pregunta por el parámetro "id"

// Número de estrellas: el mismo máximo que MAX_RATING en controller.py.
const MAX_RATING = 5;

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
    list.innerHTML = ""; // propiedad para limpiar el contenido de un elemento
    if (comments.length === 0) {
        document.getElementById("comments-message").textContent = "Todavía no hay comentarios.";
        return;
    }
    comments.forEach(comment => {
        const item = document.createElement("li"); // crea un nuevo elemento li en el DOM
        item.className = "list-group-item"; // agrega la clase list-group-item al elemento li

        const author = document.createElement("strong"); // crea un nuevo elemento strong en el DOM
        author.textContent = `${comment.person} · ${comment.date}`; // agrega el texto al elemento strong.
        // textContent: lo que escribió otra persona se muestra como texto, y nunca se ejecuta como HTML.
        const text = document.createElement("p");
        text.className = "mb-0"; // agrega la clase mb-0 al elemento p
        text.textContent = comment.comment; // agrega el texto al elemento p

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

// Recibe el resumen de calificaciones de la API ({average, count}) y lo pinta: tantas estrellas
// llenas como el promedio redondeado, y debajo el promedio con un decimal y el número de votos.
function showRating(summary) {
    const stars = document.getElementById("rating-stars");
    const text = document.getElementById("rating-text");
    // average llega como null (el None de Python) cuando nadie ha votado todavía.
    if (summary.average === null) {
        stars.textContent = "☆".repeat(MAX_RATING);
        text.textContent = "Todavía no hay calificaciones.";
        return;
    }
    const filled = Math.round(summary.average);
    stars.textContent = "★".repeat(filled) + "☆".repeat(MAX_RATING - filled);
    text.textContent = `Promedio: ${summary.average.toFixed(1)} de ${MAX_RATING} · Votos: ${summary.count}`;
}

// Pide a la API el resumen de calificaciones de la película y lo muestra. Si algo falla, muestra el error.
async function loadRating() {
    const text = document.getElementById("rating-text");
    try {
        const response = await fetch(`/api/movies/${movieId}/rating`);
        const data = await response.json();
        if (!response.ok) {
            text.textContent = data.detail;
            return;
        }
        showRating(data);
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        text.textContent = "No se pudo cargar la calificación. Inténtalo de nuevo.";
    }
}

// Se ejecuta al enviar el formulario de calificación: manda la nota a la API y, si se guarda,
// vacía el formulario y vuelve a pedir el promedio. Si algo falla, muestra el error bajo el formulario.
async function sendRating(event) {
    // Sin esto, el navegador recargaría la página al enviar el formulario.
    event.preventDefault();
    const formError = document.getElementById("rating-error");
    formError.textContent = "";

    const newRating = {
        person: document.getElementById("rating-person").value,
        // El valor de un <select> siempre es texto ("4"); se convierte en número porque la API espera un entero.
        rating: Number(document.getElementById("rating-value").value),
    };
    try {
        const response = await fetch(`/api/movies/${movieId}/rating`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newRating),
        });
        const data = await response.json();
        if (!response.ok) {
            formError.textContent = data.detail;
            return;
        }
        document.getElementById("rating-form").reset();
        loadRating();
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        formError.textContent = "No se pudo enviar la calificación. Inténtalo de nuevo.";
    }
}

// Se ejecuta al enviar el formulario de comentarios: manda el comentario a la API y, si se guarda,
// vacía el formulario y vuelve a pedir la lista. Si algo falla, muestra el error bajo el formulario.
async function sendComment(event) {

    event.preventDefault();    // Sin esto, el navegador recargaría la página al enviar el formulario.
    const formError = document.getElementById("comment-error");
    formError.textContent = "";

    const newComment = {
        person: document.getElementById("person").value,
        comment: document.getElementById("comment").value,
    };
    try {
        const response = await fetch(`/api/movies/${movieId}/comments`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }, 
            body: JSON.stringify(newComment), // convierte el objeto en una cadena de texto en formato JSON.
        });
        const data = await response.json(); // convierte la respuesta en un objeto JavaScript.
        if (!response.ok) {
            formError.textContent = data.detail; // muestra el mensaje de error en el formulario.
            return;
        }
        document.getElementById("comment-form").reset(); // vacía el formulario.
        loadComments(); // vuelve a pedir la lista de comentarios.
    } catch (error) {
        // Solo llega aquí si el servidor no responde o responde algo que no es JSON.
        formError.textContent = "No se pudo enviar el comentario. Inténtalo de nuevo.";
    }
}

document.getElementById("rating-form").addEventListener("submit", sendRating);
document.getElementById("comment-form").addEventListener("submit", sendComment);

// Sin ?id= (o con ?id= vacío) no hay película que pedir: se avisa y no se hace ninguna petición.
// !movieId es verdadero tanto con null (no hay id) como con "" (id vacío).
if (!movieId) {
    document.getElementById("message").textContent = "No se indicó ninguna película. Vuelve al buscador y elige una.";
} else {
    loadMovie();
    loadRating();
    loadComments();
}
