// Admin Dashboard JS

document.addEventListener('DOMContentLoaded', () => {
  const userCountEl = document.getElementById('userCount');
  const tableCountEl = document.getElementById('tableCount');
  const orderCountEl = document.getElementById('orderCount');

  userCountEl.textContent = '...';
  tableCountEl.textContent = '...';
  orderCountEl.textContent = '...';

  // Fetch real counts from backend
  fetch('http://127.0.0.1:8000/stats')
    .then(res => res.json())
    .then(data => {
      if (data && data.response === 'success') {
        userCountEl.textContent = data.users ?? 0;
        tableCountEl.textContent = data.tables ?? 0;
        orderCountEl.textContent = data.orders ?? 0;
      } else {
        userCountEl.textContent = '0';
        tableCountEl.textContent = '0';
        orderCountEl.textContent = '0';
      }
    })
    .catch(() => {
      userCountEl.textContent = '0';
      tableCountEl.textContent = '0';
      orderCountEl.textContent = '0';
    });

  // Logout button
  const logoutButton = document.querySelector('.logoutButton');
  if (logoutButton) {
    logoutButton.addEventListener('click', (e) => {
      e.preventDefault();
      document.cookie = "id=;path=/;max-age=0";
      document.cookie = "name=;path=/;max-age=0";
      document.cookie = "mail=;path=/;max-age=0";
      document.cookie = "role=;path=/;max-age=0";
      window.location.href = "/index.html";
    });
  }
});
