// 🔐 Fonction pour échapper les caractères HTML
function escapeHTML(str) {
  return str.replace(/[&<>"']/g, function (char) {
    const escapeMap = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return escapeMap[char];
  });
}

// 🧪 Données de test
let users = [
  { id: 1, prenom: "John", nom: "Doe", tel: "771234567", nin: "123456789" },
  { id: 2, prenom: "Jane", nom: "Smith", tel: "781234567", nin: "987654321" },
];

// 🔧 Éléments DOM
const userTable = document.getElementById("filtered-table").getElementsByTagName("tbody")[0];
const addUserBtn = document.getElementById("add-user-btn");
const addUserModal = document.getElementById("add-user-modal");
const closeModal = document.querySelector(".close");
const userForm = document.getElementById("user-form");

// 🔁 Affichage du tableau des utilisateurs
function renderUsers() {
  userTable.innerHTML = "";
  users.forEach((user) => {
    const row = userTable.insertRow();
    row.innerHTML = `
      <td>${escapeHTML(user.id.toString())}</td>
      <td>${escapeHTML(user.prenom)}</td>
      <td>${escapeHTML(user.nom)}</td>
      <td>${escapeHTML(user.tel)}</td>
      <td>${escapeHTML(user.nin)}</td>
      <td>
        <button onclick="editUser(${user.id})">Modifier</button>
        <button onclick="deleteUser(${user.id})">Supprimer</button>
      </td>
    `;
  });
}

// ➕ Ajouter un utilisateur
addUserBtn.addEventListener("click", () => {
  addUserModal.style.display = "flex";
});

closeModal.addEventListener("click", () => {
  addUserModal.style.display = "none";
});

userForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const prenom = document.getElementById("prenom").value;
  const nom = document.getElementById("nom").value;
  const tel = document.getElementById("tel").value;
  const nin = document.getElementById("nin").value;

  const newUser = {
    id: users.length + 1,
    prenom,
    nom,
    tel,
    nin,
  };

  users.push(newUser);
  renderUsers();
  addUserModal.style.display = "none";
  userForm.reset();
});

// ✏️ Modifier un utilisateur
function editUser(id) {
  const user = users.find((user) => user.id === id);
  if (user) {
    document.getElementById("prenom").value = user.prenom;
    document.getElementById("nom").value = user.nom;
    document.getElementById("tel").value = user.tel;
    document.getElementById("nin").value = user.nin;
    addUserModal.style.display = "flex";

    userForm.onsubmit = (e) => {
      e.preventDefault();
      user.prenom = document.getElementById("prenom").value;
      user.nom = document.getElementById("nom").value;
      user.tel = document.getElementById("tel").value;
      user.nin = document.getElementById("nin").value;
      renderUsers();
      addUserModal.style.display = "none";
      userForm.reset();
    };
  }
}

// ❌ Supprimer un utilisateur
function deleteUser(id) {
  if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
    users = users.filter((user) => user.id !== id);
    renderUsers();
  }
}

// 🟢 Rendu initial
renderUsers();
