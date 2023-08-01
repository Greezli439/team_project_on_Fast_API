// Функція для отримання респонсу з бекенду
const accessToken = localStorage.getItem('accessToken');

async function getImageFromBackend(Id) {
  const response = await fetch('http://127.0.0.1:8000/api/images/qrcode/' + Id, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  return data;
}

// Функція для відображення зображення на сторінці
async function displayImage(Id) {
  const imageContainer = document.getElementById('image-container');
  
  // Отримуємо респонс з бекенду
  const imageResponse = await getImageFromBackend(Id);

  // Розкодовуємо base64-кодоване зображення в бінарний формат
  const binaryImg = atob(imageResponse.base64_encoded_img);

  // Створюємо URL-об'єкт з бінарним зображенням
  const blob = new Blob([new Uint8Array([...binaryImg].map(char => char.charCodeAt(0)))], { type: 'image/png' });
  const imageUrl = URL.createObjectURL(blob);

  // Створюємо тег <img> і встановлюємо йому створений URL
  const imageTag = document.createElement('img');
  imageTag.src = imageUrl;

  // Додаємо зображення до контейнера
  imageContainer.appendChild(imageTag);
}
const urlParams = new URLSearchParams(window.location.search);
const Id = urlParams.get('Id');

// Виклик функції для відображення зображення
displayImage(Id);
