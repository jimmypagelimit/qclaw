// ==================== 全局状态 ====================
const API = '/api';
let currentPage = 'dashboard';
let currentYear = '';
let searchOffset = 0;
let currentAlbumId = null;
let currentAlbumData = null;

// ==================== API 封装 ====================
async function api(url, options = {}) {
  const res = await fetch(`${API}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || '请求失败');
  }
  return res.json();
}

// ==================== 页面导航 ====================
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    switchPage(link.dataset.page);
  });
});

function switchPage(page) {
  currentPage = page;
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`)?.classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${page}`)?.classList.add('active');

  if (page === 'dashboard') loadDashboard();
  if (page === 'albums') searchAlbums();
}

// ==================== 仪表盘（简化版）====================
async function loadDashboard() {
  try {
    const data = await api('/stats');
    const yearListens = data.yearListens || {};

    document.getElementById('stats-grid').innerHTML = `
      <div class="stat-card highlight">
        <div class="label">总库</div>
        <div class="value">${data.albums?.count || 0}</div>
        <div class="sub">${data.albums?.totalListens || 0} 次收听</div>
      </div>
      ${Object.entries(yearListens).sort().map(([y, c]) => `
      <div class="stat-card">
        <div class="label">${y} 年</div>
        <div class="value">${c}</div>
        <div class="sub">次收听</div>
      </div>`).join('')}
    `;

    loadAlbumLeaderboard();
    loadArtistLeaderboard();
  } catch (err) {
    showToast('加载仪表盘失败: ' + err.message, 'error');
  }
}

async function loadAlbumLeaderboard() {
  try {
    const data = await api('/albums?sort=listen&dir=desc&limit=10');
    renderAlbumLeaderboard(data.albums || []);
  } catch (err) {
    document.getElementById('album-leaderboard').innerHTML = '<div class="chart-empty">加载失败</div>';
  }
}

function renderAlbumLeaderboard(albums) {
  const container = document.getElementById('album-leaderboard');
  if (!albums.length) { container.innerHTML = '<div class="chart-empty">暂无数据</div>'; return; }
  container.innerHTML = albums.map((a, i) => {
    const url = a.cover_image_url ? '/' + a.cover_image_url.replace(/^\/+/, '') : null;
    const cover = url
      ? `<img class="lb-cover" src="${url}" loading="lazy">`
      : `<div class="lb-cover-placeholder">🎵</div>`;
    return `<div class="lb-item">
      <span class="lb-rank">${i + 1}</span>
      ${cover}
      <div class="lb-info">
        <div class="lb-title">${escapeHtml(a.album_name)}</div>
        <div class="lb-artist">${escapeHtml(a.artist)}</div>
      </div>
      <span class="lb-count">${a.total_listen_count || a.year_listen_count || 0} 次</span>
    </div>`;
  }).join('');
}

async function loadArtistLeaderboard() {
  try {
    const data = await api('/artists?sort=listen&dir=desc&limit=10');
    renderArtistLeaderboard(data.artists || []);
  } catch (err) {
    document.getElementById('artist-leaderboard').innerHTML = '<div class="chart-empty">加载失败</div>';
  }
}

function renderArtistLeaderboard(artists) {
  const container = document.getElementById('artist-leaderboard');
  if (!artists.length) { container.innerHTML = '<div class="chart-empty">暂无数据</div>'; return; }
  container.innerHTML = artists.map((ar, i) => {
    const url = ar.image_url ? '/' + ar.image_url.replace(/^\/+/, '') : null;
    const cover = url
      ? `<img class="lb-cover" src="${url}" loading="lazy">`
      : `<div class="lb-cover-placeholder">🎵</div>`;
    return `<div class="lb-item">
      <span class="lb-rank">${i + 1}</span>
      ${cover}
      <div class="lb-info">
        <div class="lb-artist-name">${escapeHtml(ar.artist || ar.name)}</div>
      </div>
      <span class="lb-count">${ar.total_listen_count || 0} 次</span>
    </div>`;
  }).join('');
}

// ==================== 专辑库 ====================
let albumViewMode = 'grid';

document.getElementById('search-btn')?.addEventListener('click', () => { searchOffset = 0; searchAlbums(); });
document.getElementById('search-input')?.addEventListener('keydown', (e) => { if (e.key === 'Enter') { searchOffset = 0; searchAlbums(); } });
document.getElementById('search-year')?.addEventListener('change', () => { searchOffset = 0; searchAlbums(); });
document.getElementById('sort-by')?.addEventListener('change', () => { searchOffset = 0; searchAlbums(); });
document.getElementById('sort-dir')?.addEventListener('change', () => { searchOffset = 0; searchAlbums(); });

document.getElementById('view-grid')?.addEventListener('click', () => {
  albumViewMode = 'grid';
  document.getElementById('view-grid').classList.add('active');
  document.getElementById('view-list').classList.remove('active');
  document.getElementById('albums-grid').style.display = '';
  document.getElementById('albums-list').style.display = 'none';
  searchAlbums();
});
document.getElementById('view-list')?.addEventListener('click', () => {
  albumViewMode = 'list';
  document.getElementById('view-list').classList.add('active');
  document.getElementById('view-grid').classList.remove('active');
  document.getElementById('albums-list').style.display = '';
  document.getElementById('albums-grid').style.display = 'none';
  searchAlbums();
});

async function searchAlbums() {
  const q = document.getElementById('search-input')?.value || '';
  const year = document.getElementById('search-year')?.value || '';
  const sortBy = document.getElementById('sort-by')?.value || 'listen';
  const sortDir = document.getElementById('sort-dir')?.value || 'desc';
  currentYear = year;

  try {
    const yearParam = year ? `&year=${year}` : '';
    const url = `/albums?search=${encodeURIComponent(q)}${yearParam}&limit=40&offset=${searchOffset}&sort=${sortBy}&dir=${sortDir}`;
    const data = await api(url);
    if (albumViewMode === 'grid') renderAlbumsGrid(data.albums || [], data.total, data.limit);
    else renderAlbumsTable(data.albums || [], data.total, data.limit);
  } catch (err) {
    showToast('搜索失败: ' + err.message, 'error');
  }
}

function coverUrl(album) {
  return album.cover_image_url ? '/' + album.cover_image_url.replace(/^\/+/, '') : null;
}

function renderAlbumsGrid(albums, total, limit) {
  const grid = document.getElementById('albums-grid');
  if (!albums.length) {
    grid.innerHTML = '<div class="albums-empty">未找到匹配的专辑</div>';
    document.getElementById('pagination').innerHTML = '';
    return;
  }
  grid.innerHTML = albums.map((a, i) => {
    const url = coverUrl(a);
    const coverHtml = url
      ? `<img src="${url}" alt="${escapeHtml(a.album_name)}" loading="lazy">`
      : `<div class="album-card-placeholder"><div class="placeholder-icon">🎵</div><div class="placeholder-artist">${escapeHtml(a.artist)}</div></div>`;
    const meta = [a.release_year && String(a.release_year).slice(0, 4), a.country, a.genre?.split(',')[0].trim()].filter(Boolean);
    return `<div class="album-card" onclick="showAlbumDetail(${a.album_id})" style="animation-delay:${i * 0.03}s">
      <div class="album-card-cover">${coverHtml}<div class="album-card-listen-badge">${a.year_listen_count || a.total_listen_count}</div></div>
      <div class="album-card-info">
        <div class="album-card-title" title="${escapeHtml(a.album_name)}">${escapeHtml(a.album_name)}</div>
        <div class="album-card-artist" title="${escapeHtml(a.artist)}">${escapeHtml(a.artist)}</div>
        ${meta.length ? `<div class="album-card-meta">${meta.map((p, idx) => idx < meta.length - 1 ? `<span>${escapeHtml(p)}</span><div class="divider"></div>` : `<span>${escapeHtml(p)}</span>`).join('')}</div>` : ''}
      </div>
    </div>`;
  }).join('');
  renderPagination(total, limit);
}

function renderAlbumsTable(albums, total, limit) {
  const tbody = document.getElementById('albums-tbody');
  if (!albums.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="table-empty">未找到匹配的专辑</td></tr>';
    document.getElementById('pagination').innerHTML = '';
    return;
  }
  tbody.innerHTML = albums.map(a => {
    const url = coverUrl(a);
    const coverHtml = url
      ? `<img src="${url}" alt="" class="table-cover">`
      : `<div class="table-cover-placeholder">🎵</div>`;
    return `<tr onclick="showAlbumDetail(${a.album_id})">
      <td>${coverHtml}</td>
      <td class="cell-title" title="${escapeHtml(a.album_name)}">${escapeHtml(a.album_name)}</td>
      <td title="${escapeHtml(a.artist)}">${escapeHtml(a.artist)}</td>
      <td>${a.genre ? escapeHtml(a.genre) : '-'}</td>
      <td>${a.country || '-'}</td>
      <td>${a.release_year || '-'}</td>
      <td class="listen-count">${a.year_listen_count || a.total_listen_count}</td>
    </tr>`;
  }).join('');
  renderPagination(total, limit);
}

function renderPagination(total, limit) {
  const totalPages = Math.ceil(total / limit);
  const pageNum = Math.floor(searchOffset / limit) + 1;
  if (totalPages <= 1) { document.getElementById('pagination').innerHTML = ''; return; }
  const prev = pageNum > 1 ? `<button class="page-btn" onclick="goPage(${searchOffset - limit})">← 上一页</button>` : '';
  const next = pageNum < totalPages ? `<button class="page-btn" onclick="goPage(${searchOffset + limit})">下一页 →</button>` : '';
  document.getElementById('pagination').innerHTML = `${prev}<span class="page-info">${pageNum} / ${totalPages}（共 ${total} 条）</span>${next}`;
}

function goPage(offset) {
  searchOffset = offset;
  searchAlbums();
}

// ==================== 专辑详情（只读）====================
function showAlbumDetail(id) {
  currentAlbumId = id;
  api(`/albums/${id}`).then(album => {
    currentAlbumData = album;
    document.getElementById('modal-title').textContent = album.album_name;
    const url = coverUrl(album);
    const coverHtml = url
      ? `<div class="detail-cover"><img src="${url}" alt="${escapeHtml(album.album_name)}"></div>`
      : '';

    const scoreFields = [
      { key: 'composition_score', label: '作曲' },
      { key: 'lyrics_meaning_score', label: '歌词意境' },
      { key: 'creativity_score', label: '创意' },
      { key: 'arrangement_score', label: '编曲' },
      { key: 'vocal_performance_score', label: '情感表达' },
      { key: 'instrumental_performance_score', label: '节奏律动' },
      { key: 'sincerity_score', label: '制作质量' },
      { key: 'subjective_score', label: '耐听度' },
    ];
    const hasScores = scoreFields.some(f => album[f.key] && album[f.key] > 0);
    const scoresHtml = hasScores ? `<div class="detail-scores">
      <div class="detail-section-title">📐 八维度评分</div>
      ${scoreFields.map(f => album[f.key] && album[f.key] > 0
        ? `<div class="score-item"><span class="score-label">${f.label}</span><div class="score-bar"><div class="score-fill" style="width:${album[f.key] * 10}%"></div></div><span class="score-value">${album[f.key]}</span></div>`
        : '').join('')}
      <div class="score-total">综合：<strong>${album.overall_score || '-'}</strong></div>
    </div>` : '';

    document.getElementById('modal-body').innerHTML = `
      ${coverHtml}
      <div class="detail-grid">
        <div class="detail-row"><span class="detail-label">艺术家</span><span class="detail-value">${escapeHtml(album.artist)}</span></div>
        <div class="detail-row"><span class="detail-label">风格</span><span class="detail-value">${album.genre || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">大类</span><span class="detail-value">${album.style || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">国家</span><span class="detail-value">${album.country || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">地区</span><span class="detail-value">${album.region || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">发行年份</span><span class="detail-value">${album.release_year || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">发行公司</span><span class="detail-value">${album.release_company || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">制作人</span><span class="detail-value">${album.producer || '-'}</span></div>
        <div class="detail-row"><span class="detail-label">时长</span><span class="detail-value">${album.duration || '-'}</span></div>
        <div class="detail-row highlight-row"><span class="detail-label">收听次数</span><span class="detail-value listen-value">${album.total_listen_count}</span></div>
        <div class="detail-row"><span class="detail-label">首次收听</span><span class="detail-value">${album.first_listen_date || '-'}</span></div>
      </div>
      ${scoresHtml}
      <div class="detail-desc"><div class="detail-section-title">📝 描述</div><div class="desc-text">${escapeHtml(album.description || '无描述')}</div></div>
      <div class="detail-cli-hint">💡 编辑 / 删除 / 收听请使用 CLI 工具</div>
    `;
    document.getElementById('album-modal').classList.add('show');
  }).catch(err => showToast(err.message, 'error'));
}

document.getElementById('modal-close').addEventListener('click', () => {
  document.getElementById('album-modal').classList.remove('show');
});
document.getElementById('album-modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) e.currentTarget.classList.remove('show');
});

// ==================== 提示消息 ====================
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = `toast ${type} show`;
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// ==================== 工具函数 ====================
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ==================== 初始化 ====================
loadDashboard();
