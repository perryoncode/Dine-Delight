let myProfile = document.querySelector(".myProfile")
let logoutButton = document.querySelector(".logoutButton")

let data = document.cookie
let name=""
const parts = data.split(";")
for  (let part of parts) {
    part = part.trim();
    if (part.startsWith("name=")) {
        name = part.split("=")[1];
        break;
        

    }
}
myProfile.innerHTML = `<i class="fa-solid fa-user"></i> ${name}`;



logoutButton.addEventListener("click", ()=>{
    document.cookie = "id=;path=/;max-age=0"
    document.cookie = "name=;path=/;max-age=0"
    document.cookie = "mail=;path=/;max-age=0"
})