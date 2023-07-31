

// Функція для взаємодії з сервером та отримання даних
async function getImages(username, userId) {
    try {
      // Запит до серверу з токеном
      const response = await fetch('http://127.0.0.1:8000/api/images/user/' + userId, {
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
      const imageCard = document.createElement('div');
      imageCard.classList.add('image-card');
  
      // Отримати URL зображення, опис та теги
      const imageUrl = item.url;
      const description = item.description;
      const tags = item.tags.map(tag => `<a href="http://127.0.0.1:5500/images_by_tag.html?tag_id=${tag.id}">${tag.name_tag}</a>`).join(', ');
      const username = item.username.username
      const id = item.username.id

  
      imageCard.innerHTML = `
      <p><a href="http://127.0.0.1:5500/user.html?username=${username}">${username}</a></p>
        <img src="${imageUrl}" alt="${description}">
        <p>${description}</p>
        <p>Tags: ${tags}</p>
      `;
  
      // Додати HTML-розмітку у контейнер
      contentDiv.appendChild(imageCard);
  
      // Отримати коментарі для поточного об'єкта
      const comments = item.comments;
  
      // Створити HTML-розмітку для коментарів
      const commentsContainer = document.createElement('div');
      commentsContainer.classList.add('comments-container');
  
      comments.forEach(comment => {
        const commentCard = document.createElement('div');
        commentCard.classList.add('comment-card');
  
        const commentText = comment.comment;
        const username = comment.username.username;
  
        commentCard.innerHTML = `
        <p><a href="http://127.0.0.1:5500/user.html?username=${username}&userId=${id}"> ${username}:</a> ${commentText}</p>`;

        commentsContainer.appendChild(commentCard);
      });
  
      // Додати коментарі до картки зображення
      imageCard.appendChild(commentsContainer);
    });
  }

  const userId = urlParams.get('userId');

  console.log(userId);

  
  

  // Викликати функцію для отримання та відображення даних при завантаженні сторінки
  getImages(username, userId);