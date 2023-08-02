console.log('Run')
const form = document.forms[0]

form.addEventListener('submit', async (e) => {
 e.preventDefault()
 const username = form.username.value
 const password = form.password.value

const myHeaders = new Headers()
myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')

const urlencoded = new URLSearchParams()
urlencoded.append('username', username) 
urlencoded.append('password', password)

const requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: urlencoded,
    redirect: 'follow',
}

 const responce = await fetch('https://legitimate-jaquenetta-greezli439.koyeb.app/api/users/login', requestOptions,)


if (responce.status == 200){
    result = await responce.json()
    localStorage.setItem('accessToken', result.access_token)
    localStorage.setItem('refreshToken', result.refresh_token)
    window.location = 'all_images.html'

}
})
