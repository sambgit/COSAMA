const input = document.getElementById('search-input');
const tbody = document.getElementById('results-body');
const fullTable = document.getElementById('full-table');
const filteredTable = document.getElementById('filtered-table');
const resultCount = document.getElementById('result-count');

let timer;

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

// 🔁 Fonction sécurisée pour afficher les résultats
function safeInnerHTML(container, rows) {
  if (rows.length === 0) {
    container.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; color:#666;">
          Aucun résultat trouvé
        </td>
      </tr>`;
    return;
  }

  container.innerHTML = rows.map(r => `
    <tr>
      <td>${escapeHTML(r.id.toString())}</td>
      <td>${escapeHTML(r.username)}</td>
      <td>
        <a href="/edit/${escapeHTML(r.id.toString())}" class="button">Modifier</a>
        <a href="/delete/${escapeHTML(r.id.toString())}" class="button danger"
           onclick="return confirm('Vous voulez vraiment supprimer ?')">
           Supprimer
        </a>
      </td>
    </tr>
  `).join('');
}

// 🔁 Fonction principale pour afficher le tableau
function renderTable(data) {
  resultCount.textContent = `Résultats trouvés : ${data.length}`;
  safeInnerHTML(tbody, data);
}

// 🔍 Recherche dynamique avec fallback
input.addEventListener('input', () => {
  clearTimeout(timer);

  timer = setTimeout(() => {
    const a = input.value.trim();

    if (a.length < 1) {
      fullTable.style.display = "table";
      filteredTable.style.display = "none";
      resultCount.textContent = "";
      renderTable(initialData);
      return;
    }

    fetch(`/super_admin/search?ajax=1&a=${encodeURIComponent(a)}`)
      .then(resp => resp.json())
      .then(data => {
        fullTable.style.display = "none";
        filteredTable.style.display = "table";
        renderTable(data);
      })
      .catch(err => {
        console.error("Erreur de recherche :", err);
        tbody.innerHTML = `
          <tr>
            <td colspan="7" style="text-align:center; color:red;">
              Une erreur est survenue lors de la recherche
            </td>
          </tr>`;
      });
  }, 300);
});

// 🟢 Affichage initial au chargement
renderTable(initialData);
