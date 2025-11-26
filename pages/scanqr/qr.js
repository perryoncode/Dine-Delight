console.log("qr.js loaded ✅");

const params = new URLSearchParams(window.location.search);
const tableId = params.get("tableId");

console.log("tableId from URL =", tableId);

if (!tableId) {
  console.warn("No tableId in URL. Not setting any cookies.");
} else {
  // Clear any previous cookies (user or table)
  document.cookie = "id=;path=/;max-age=0";
  document.cookie = "name=;path=/;max-age=0";
  document.cookie = "mail=;path=/;max-age=0";
  document.cookie = "role=;path=/;max-age=0";

  // 10 minutes
  const maxAge = 60 * 10;

  // Sanitize tableId: remove all non-digit characters (handles trailing slashes)
  const cleanTableId = (tableId + '').replace(/\D/g, "");
  const tableLabel = `Table ${cleanTableId}`;
  const tableMail = `table${cleanTableId}@dinedelight.tech`;

  document.cookie = `name=${encodeURIComponent(tableLabel)};path=/;max-age=${maxAge}`;
  document.cookie = `id=${encodeURIComponent(cleanTableId)};path=/;max-age=${maxAge}`;
  document.cookie = `mail=${encodeURIComponent(tableMail)};path=/;max-age=${maxAge}`;
  document.cookie = `role=table;path=/;max-age=${maxAge}`;

  console.log("Cookies set:", document.cookie);

  // Redirect to menu (be explicit)
  window.location.href = "../menu/index.html";
}
