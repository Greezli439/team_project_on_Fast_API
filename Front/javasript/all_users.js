// Отримати доступ до локального токену з localStorage
const accessToken = localStorage.getItem('accessToken');
// const accessToken = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaWtlQGdtYWlsLmNvbSIsImlhdCI6MTY5MDQwMTU5OSwiZXhwIjoxNjkwNDAzMzk5LCJzY29wZSI6ImFjY2Vzc190b2tlbiJ9.lO2PUWv59lKuYCULv5V4C5gNJFrfzooIK5Kkz_xGNr0;
// URL вашого серверу
const serverURL = 'http://127.0.0.1:8000/api/users/all_users'; // Замініть на свій URL

// Функція для взаємодії з сервером та отримання даних
async function getData() {
    try {
      // Запит до серверу з токеном
      const response = await fetch(serverURL, {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      });
  
      // Перевірка статусу відповіді
      if (!response.ok) {
        throw new Error('Failed to fetch data from the server');
      }
  
      // Отримання JSON даних
      const data = await response.json();
  
      // Відображення даних на сторінці
      displayData(data);
    } catch (error) {
      console.error(error.message);
      // Обробка помилки (наприклад, показати повідомлення про помилку)
    }
  }
  
  // Функція для відображення даних на сторінці
  function displayData(data) {
    // Отримати DOM-елемент, в який будуть вставлятися дані
    const contentDiv = document.getElementById('content');
  
    // Очистити вміст контейнера перед вставкою нових даних
    contentDiv.innerHTML = '';
  
    // Створити HTML-розмітку для кожного об'єкта в масиві даних
    data.forEach(item => {
      const userCard = document.createElement('div');
      userCard.classList.add('user-card');
  
      userCard.innerHTML = `
        <h1>${item.username}</h1>
        <p>Email: ${item.email}</p>
        <p>ID: ${item.id}</p>
        <p>Created At: ${item.created_at}</p>
      `;
  
      // Додати HTML-розмітку у контейнер
      contentDiv.appendChild(userCard);
    });
  }
  
  // Викликати функцію для отримання та відображення даних при завантаженні сторінки
  getData();