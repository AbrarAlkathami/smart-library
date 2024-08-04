document.addEventListener("DOMContentLoaded", fetchBooks);

async function fetchBooks() {
    try {
        const response = await fetch("http://127.0.0.1:8000/books");
        if (!response.ok) {
            throw new Error("Failed to fetch books");
        }
        const books = await response.json();
        displayBooks(books);
    } catch (error) {
        console.error("Error fetching books:", error);
        window.alert("Error fetching books: " + error.message);
    }
}

async function searchBooks() {
    const query = document.getElementById("searchInput").value;
    const searchInput = document.getElementById("searchInput");
    const searchMessage = document.getElementById("searchMessage");

    try {
        const response = await fetch(`http://127.0.0.1:8000/books/search/${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error("Failed to search books");
        }
        const results = await response.json();
        if (results.length === 0) {
            searchInput.style.borderColor = "red";
            searchMessage.textContent = "No books found";
        } else {
            searchInput.style.borderColor = "";
            searchMessage.textContent = "";
        }
        displayBooks(results);
    } catch (error) {
        console.error("Error searching books:", error);
        searchInput.style.borderColor = "red";
        searchMessage.textContent = "Error searching books";
    }
}

function displayBooks(books) {
    const bookGallery = document.getElementById("bookGallery");
    bookGallery.innerHTML = "";

    const colors = ["#000000", "#221b27", "#32243c"];
    let colorIndex = 0;

    books.forEach(book => {
        const bookItem = document.createElement("div");
        bookItem.classList.add("book-item");

        // Assign a background color from the colors array
        bookItem.style.backgroundColor = colors[colorIndex];
        colorIndex = (colorIndex + 1) % colors.length;

        const coverPhoto = document.createElement("div");
        coverPhoto.classList.add("cover-photo");
        const img = document.createElement("img");
        const thumbnailUrl = book.thumbnail && book.thumbnail.trim() !== '' ? book.thumbnail : 'https://via.placeholder.com/150';
        console.log(`Book title: ${book.title}, Thumbnail URL: ${thumbnailUrl}`);
        img.src = thumbnailUrl;
        coverPhoto.appendChild(img);

        const bookTitle = document.createElement("div");
        bookTitle.classList.add("book-title");
        bookTitle.textContent = book.title;

        bookItem.appendChild(coverPhoto);
        bookItem.appendChild(bookTitle);

        bookGallery.appendChild(bookItem);
    });
}
