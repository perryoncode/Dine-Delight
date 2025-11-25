// ==== COOKIE LOGIN CHECK ====
setTimeout(() => {
  if (!document.cookie.includes("name=")) {
    console.warn("No cookie found. Probably arriving from QR redirect, waiting...");
  }
}, 2000);



// === CONFIG ===
const API_BASE = "http://127.0.0.1:8000"; // change to your VPS IP when needed

// === ELEMENTS ===
const menuContainer = document.querySelector(".menu");
const input = document.getElementById("searchInput");

// for profile name from cookie (optional, matches your earlier pattern)
const myProfile = document.querySelector(".myProfile");
const logoutButton = document.querySelector(".logoutButton");

// === SIMPLE COOKIE HELPER ===
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

// Show profile name (works for both real user & table guest)
(function initProfile() {
  const name = getCookie("name");
  if (name && myProfile) {
    myProfile.innerHTML = `<i class="fa-solid fa-user"></i> ${name}`;
  }
})();

// Logout clears cookies and goes to login
if (logoutButton) {
  logoutButton.addEventListener("click", (e) => {
    e.preventDefault();
    document.cookie = "id=;path=/;max-age=0";
    document.cookie = "name=;path=/;max-age=0";
    document.cookie = "mail=;path=/;max-age=0";
    window.location.href = "../login/index.html";
  });
}

// === LOAD DISHES FROM BACKEND ===
let dishNamesForTypewriter = [
  // fallback values if API fails
  "Brownie",
  "Chole Bhature",
  "Fries",
  "Maggie",
  "Momos",
  "Panipuri",
  "Paneer Tikka",
  "Soya Chaap",
];

async function loadDishes() {
  try {
    const res = await fetch(`${API_BASE}/dishes`);
    const data = await res.json();

    if (data.response !== "success") {
      console.error("Failed to load dishes:", data);
      menuContainer.innerHTML = "<p>Unable to load menu right now.</p>";
      return;
    }

    const dishes = data.dishes;
    if (!dishes.length) {
      menuContainer.innerHTML = "<p>No dishes available at the moment.</p>";
      return;
    }

    // Use dish names from API for the typewriter
    dishNamesForTypewriter = dishes.map((d) => d.name);

    // Clear any static cards
    menuContainer.innerHTML = "";

    dishes.forEach((dish) => {
      const card = document.createElement("div");
      card.className = "card";

      // images are in /pages/menu/dishes/<filename>
      const imgSrc = `./dishes/${dish.image}`;

      card.innerHTML = `
        <img src="${imgSrc}" alt="${dish.name}">
        <div class="info">
          <p class="title">${dish.name}</p>
          <div class="info-actions">
            <p class="price">
              <i class="fa-solid fa-indian-rupee-sign"></i> ${dish.price}
            </p>
            <p class="add-to-cart"
               data-name="${dish.name}"
               data-price="${dish.price}">
               <i class="fa-solid fa-burger"></i> Add to Table
            </p>
          </div>
        </div>
      `;

      menuContainer.appendChild(card);
    });

    // hook up Add to Table buttons later for cart system
    document.querySelectorAll(".add-to-cart").forEach((btn) => {
      btn.addEventListener("click", () => {
        const name = btn.dataset.name;
        const price = Number(btn.dataset.price);
        console.log("Add to Table clicked:", name, price);
        // TODO: add to cart / table order
      });
    });
  } catch (err) {
    console.error("Error loading dishes:", err);
    menuContainer.innerHTML = "<p>Network error while loading menu.</p>";
  }
}

// === TYPEWRITER PLACEHOLDER (USING dishNamesForTypewriter) ===
let dishIndex = 0;
let charIndex = 0;
let typing = true;

function typeWriter() {
  if (!input) return;
  const currentDish = dishNamesForTypewriter[dishIndex] || "";
  if (typing) {
    if (charIndex <= currentDish.length) {
      input.placeholder = currentDish.slice(0, charIndex);
      charIndex++;
      setTimeout(typeWriter, 100);
    } else {
      typing = false;
      setTimeout(typeWriter, 1000);
    }
  } else {
    if (charIndex > 0) {
      input.placeholder = currentDish.slice(0, charIndex);
      charIndex--;
      setTimeout(typeWriter, 40);
    } else {
      typing = true;
      dishIndex = (dishIndex + 1) % dishNamesForTypewriter.length;
      setTimeout(typeWriter, 400);
    }
  }
}

// === INIT ===
loadDishes();
typeWriter();
