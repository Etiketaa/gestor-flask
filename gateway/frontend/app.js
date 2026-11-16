const API = ''; // misma origen: el gateway sirve el frontend y la API

let token = null;

async function api(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...opts.headers };
    const res = await fetch(`${API}/api${path}`, {
        ...opts,
        headers,
        credentials: 'include',
    });
    const ct = res.headers.get('content-type') || '';
    const data = ct.includes('application/json') ? await res.json() : await res.text();
    if (!res.ok) throw new Error(data.error || data.message || `Error ${res.status}`);
    return data;
}

// ---------- Vistas ----------
const viewAuth = document.getElementById('view-auth');
const viewApp = document.getElementById('view-app');
const panelLogin = document.getElementById('panel-login');
const panelRegister = document.getElementById('panel-register');

// ---------- Auth ----------
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        panelLogin.style.display = tab.dataset.tab === 'login' ? 'block' : 'none';
        panelRegister.style.display = tab.dataset.tab === 'register' ? 'block' : 'none';
    });
});

document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    try {
        await api('/auth/login', { method: 'POST', body: JSON.stringify(body) });
        loadApp();
    } catch (err) {
        document.getElementById('msg-login').textContent = err.message;
    }
});

document.getElementById('form-register').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    try {
        await api('/organizations/register', { method: 'POST', body: JSON.stringify(body) });
        alert('Organización creada. Ahora iniciá sesión.');
        document.querySelector('.tab[data-tab="login"]').click();
    } catch (err) {
        document.getElementById('msg-register').textContent = err.message;
    }
});

document.getElementById('btn-logout').addEventListener('click', async () => {
    try { await api('/auth/logout', { method: 'POST' }); } catch {}
    viewApp.style.display = 'none';
    viewAuth.style.display = 'block';
});

// ---------- App ----------
async function loadApp() {
    try {
        const me = await api('/auth/me');
        document.getElementById('org-name').textContent = me.user.organization;
        document.getElementById('user-info').textContent = `${me.user.username} (${me.user.role})`;
        viewAuth.style.display = 'none';
        viewApp.style.display = 'block';
        loadItems();
        loadSales();
    } catch {
        viewAuth.style.display = 'block';
        viewApp.style.display = 'none';
    }
}

// ---------- Ítems ----------
async function loadItems() {
    const tbody = document.getElementById('tbody-items');
    const empty = document.getElementById('empty-items');
    try {
        // Nota: auth-service no expone organization_id directo; usamos login para saber la org.
        // Para filtrar por organización, el front debería enviarla. Por ahora listamos todos y filtramos en cliente.
        const items = await api('/catalog/items');
        tbody.innerHTML = '';
        if (!items.length) { empty.style.display = 'block'; return; }
        empty.style.display = 'none';
        items.forEach(it => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${it.sku}</code></td>
                <td>${it.name}</td>
                <td>$${Number(it.price).toFixed(2)}</td>
                <td>${it.quantity} ${it.unit}</td>
                <td></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5">Error cargando ítems: ${err.message}</td></tr>`;
    }
}

document.getElementById('form-item').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.price = Number(body.price);
    body.quantity = Number(body.quantity);
    if (body.category_id) body.category_id = Number(body.category_id);
    // organization_id se lo envía para aislamiento (el front debería saberlo; por ahora lo pedimos implícito)
    try {
        await api('/catalog/items', { method: 'POST', body: JSON.stringify(body) });
        document.getElementById('modal-item').style.display = 'none';
        e.target.reset();
        loadItems();
    } catch (err) {
        document.getElementById('msg-item').textContent = err.message;
    }
});

document.getElementById('btn-new-item').addEventListener('click', () => {
    document.getElementById('modal-item').style.display = 'flex';
    document.getElementById('form-item').reset();
    document.getElementById('msg-item').textContent = '';
});

document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('modal-item').style.display = 'none';
});

document.getElementById('search-items').addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('#tbody-items tr').forEach(tr => {
        const text = tr.textContent.toLowerCase();
        tr.style.display = text.includes(q) ? '' : 'none';
    });
});

// ---------- Ventas ----------
document.getElementById('form-sale').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd);
    body.item_id = Number(body.item_id);
    body.quantity = Number(body.quantity);
    body.price = Number(body.price);
    body.total = body.quantity * body.price;
    try {
        await api('/sales/sales', { method: 'POST', body: JSON.stringify(body) });
        e.target.reset();
        loadSales();
        document.getElementById('msg-sale').textContent = 'Venta registrada';
        document.getElementById('msg-sale').className = 'msg';
        setTimeout(() => { document.getElementById('msg-sale').textContent = ''; }, 3000);
    } catch (err) {
        document.getElementById('msg-sale').textContent = err.message;
        document.getElementById('msg-sale').className = 'msg error';
    }
});

async function loadSales() {
    const tbody = document.getElementById('tbody-sales');
    try {
        const sales = await api('/sales/sales');
        tbody.innerHTML = '';
        sales.slice(0, 10).reverse().forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${s.id}</td>
                <td>${new Date(s.sale_date).toLocaleString()}</td>
                <td>$${Number(s.total_amount).toFixed(2)}</td>
                <td>Usuario ${s.user_id}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4">Error: ${err.message}</td></tr>`;
    }
}

// ---------- Inicio ----------
loadApp();
