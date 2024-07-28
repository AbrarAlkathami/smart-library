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
    }
}

async function searchBooks() {
    const query = document.getElementById("searchInput").value;
    try {
        const response = await fetch(`http://127.0.0.1:8000/books/search/${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error("Failed to search books");
        }
        const results = await response.json();
        displayBooks(results);
    } catch (error) {
        console.error("Error searching books:", error);
    }
}

function displayBooks(books) {
    const bookGallery = document.getElementById("bookGallery");
    bookGallery.innerHTML = "";

    books.forEach(book => {
        const bookItem = document.createElement("div");
        bookItem.classList.add("book-item");

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
