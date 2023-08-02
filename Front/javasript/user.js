// Отримати доступ до локального токену з localStorage
const accessToken = localStorage.getItem('access_token');


// Функція для виконання запиту GET на сервер
async function getUserInfo(username) {
  try {
    // Запит до серверу з токеном
    const response = await fetch(`https://margatsni-greezli439.koyeb.app/api/users/` + username, {
      headers: {
        Authorization: `Bearer ${accessToken}`
      }
    });

    // Перевірка статусу відповіді
    if (!response.ok) {
      throw new Error('Failed to fetch data from the server');
    }

    // Отримання JSON даних про користувача
    const data = await response.json();

    // Відображення даних на сторінці
    displayUserInfo(data);
  } catch (error) {
    console.error(error.message);
    // Обробка помилки (наприклад, показати повідомлення про помилку)
  }
}

// Функція для відображення картки інформації про користувача
function displayUserInfo(response) {
  const userInfoDiv = document.getElementById('user-info');

  const userId = response.id;
  const username = response.username;
  const email = response.email;
  const createdAt = response.created_at;
  const role = response.role;
  const numberOfImages = response.number_of_images;
  const isBanned = response.banned;

  const userInfoHTML = `
    <h1>User Info</h1>
    <p><span class="info-label">User ID:</span> <span class="info-value">${userId}</span></p>
    <p><span class="info-label">Username:</span> <span class="info-value">${username}</span></p>
    <p><span class="info-label">Email:</span> <span class="info-value">${email}</span></p>
    <p><span class="info-label">Created At:</span> <span class="info-value">${createdAt}</span></p>
    <p><span class="info-label">Role:</span> <span class="info-value">${role}</span></p>
    <p><span class="info-label">Number of Images:</span> <span class="info-value">${numberOfImages}</span></p>
    <p><span class="info-label">Is Banned:</span> <span class="info-value">${isBanned}</span></p>
  `;

  userInfoDiv.innerHTML = userInfoHTML;
}



const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');


// Викликати функцію для отримання та відображення даних про користувача
getUserInfo(username);
