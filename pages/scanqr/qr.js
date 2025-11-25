console.log("qr.js loaded ✅");

const params = new URLSearchParams(window.location.search);
const tableId = params.get("tableId");

console.log("tableId from URL =", tableId);

// If no tableId in URL → just stay on this page and show a message.
// DO NOT redirect to login here.
if (!tableId) {
  console.warn("No tableId in URL. Not setting any cookies.");
  // Optional: show something on the page
  // document.body.innerHTML = "<h2>Scan a valid table QR to continue.</h2>";
} else {
  // Clear any previous cookies (user or table)
  document.cookie = "id=;path=/;max-age=0";
  document.cookie = "name=;path=/;max-age=0";
  document.cookie = "mail=;path=/;max-age=0";

  // 10 minutes
  const maxAge = 60 * 10;

  document.cookie = `name=Table ${tableId};path=/;max-age=${maxAge}`;
  document.cookie = `id=${tableId};path=/;max-age=${maxAge}`;
  document.cookie = `mail=${tableId}@dinedelight.tech;path=/;max-age=${maxAge}`;

  console.log("Cookies set:", document.cookie);

  // Redirect to menu (be explicit)
  window.location.href = "../menu/index.html";
}
