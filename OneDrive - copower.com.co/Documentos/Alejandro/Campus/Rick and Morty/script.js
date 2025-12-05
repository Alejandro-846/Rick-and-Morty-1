const API_BASE_URL = 'https://rickandmortyapi.com/api';
let currentPage = 1;
let currentQuery = '';
let totalPages = 0;

const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const charactersContainer = document.getElementById('characters');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const resultsInfoDiv = document.getElementById('resultsInfo');
const resultCountDiv = document.getElementById('resultCount');
const paginationDiv = document.getElementById('pagination');
const paginationBottomDiv = document.getElementById('pagination-bottom');
const characterModal = document.getElementById('characterModal');
const closeModalBtn = document.getElementById('closeModal');

// Event listeners
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

// Cerrar modal
closeModalBtn.addEventListener('click', closeCharacterModal);
characterModal.addEventListener('click', (e) => {
    if (e.target === characterModal) {
        closeCharacterModal();
    }
});

// Cerrar modal con tecla ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !characterModal.classList.contains('hidden')) {
        closeCharacterModal();
    }
});

// Búsqueda en tiempo real mientras escribe
let debounceTimer;
searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();
    
    if (query.length > 0) {
        // Agregar pequeño delay para no hacer demasiadas peticiones
        debounceTimer = setTimeout(() => {
            currentQuery = query;
            currentPage = 1;
            searchCharacters(query, 1);
        }, 300);
    } else {
        // Si el input está vacío, limpiar resultados
        charactersContainer.innerHTML = '';
        resultsInfoDiv.classList.add('hidden');
        paginationDiv.classList.add('hidden');
        paginationBottomDiv.classList.add('hidden');
        hideError();
    }
});

async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showError('Por favor ingresa un nombre para buscar');
        return;
    }

    currentQuery = query;
    currentPage = 1;
    await searchCharacters(query, 1);
}

async function searchCharacters(name, page = 1) {
    try {
        showLoading(true);
        hideError();
        
        const url = `${API_BASE_URL}/character/?name=${encodeURIComponent(name)}&page=${page}`;
        const response = await fetch(url);

        if (!response.ok) {
            if (response.status === 404) {
                showError('No se encontraron personajes con ese nombre');
                charactersContainer.innerHTML = '';
                resultsInfoDiv.classList.add('hidden');
                paginationDiv.classList.add('hidden');
                paginationBottomDiv.classList.add('hidden');
                showLoading(false);
                return;
            }
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        
        totalPages = data.info.pages;
        currentPage = page;

        displayCharacters(data.results);
        displayResultsInfo(data.info);
        displayPagination(data.info);
        
        showLoading(false);
    } catch (error) {
        showError('Error al buscar personajes: ' + error.message);
        showLoading(false);
    }
}

function displayCharacters(characters) {
    charactersContainer.innerHTML = '';

    if (!characters || characters.length === 0) {
        charactersContainer.innerHTML = '<p>No hay personajes para mostrar</p>';
        return;
    }

    characters.forEach((character, index) => {
        const card = createCharacterCard(character);
        charactersContainer.appendChild(card);
        
        // Agregar animación escalonada
        setTimeout(() => {
            card.style.animation = `fadeIn 0.5s ease-out`;
        }, index * 50);
    });
}

function createCharacterCard(character) {
    const card = document.createElement('div');
    card.className = 'character-card';

    const statusClass = `status-${character.status.toLowerCase()}`;
    
    card.innerHTML = `
        <img 
            src="${character.image}" 
            alt="${character.name}" 
            class="character-image"
            onerror="this.src='https://via.placeholder.com/300x300?text=No+Image'"
        >
        <div class="character-info">
            <div class="character-name">${escapeHtml(character.name)}</div>
            
            <div class="character-detail">
                <span class="detail-label">Estado:</span>
                <span class="detail-value">${character.status}</span>
            </div>

            <div class="character-detail">
                <span class="detail-label">Especie:</span>
                <span class="detail-value">${escapeHtml(character.species)}</span>
            </div>

            <div class="character-detail">
                <span class="detail-label">Género:</span>
                <span class="detail-value">${character.gender}</span>
            </div>

            <div class="character-detail">
                <span class="detail-label">Origen:</span>
                <span class="detail-value">${escapeHtml(character.origin.name)}</span>
            </div>

            <div class="character-detail">
                <span class="detail-label">Ubicación:</span>
                <span class="detail-value">${escapeHtml(character.location.name)}</span>
            </div>

            <span class="status-badge ${statusClass}">${character.status}</span>
        </div>
    `;

    card.addEventListener('click', () => openCharacterModal(character));

    return card;
}

function displayResultsInfo(info) {
    resultCountDiv.textContent = `Se encontraron ${info.count} personaje(s) en ${info.pages} página(s)`;
    resultsInfoDiv.classList.remove('hidden');
}

function displayPagination(info) {
    paginationDiv.innerHTML = '';
    paginationBottomDiv.innerHTML = '';

    const totalPages = info.pages;

    if (totalPages <= 1) {
        paginationDiv.classList.add('hidden');
        paginationBottomDiv.classList.add('hidden');
        return;
    }

    // Crear botones de paginación
    const createPaginationButtons = () => {
        const buttons = [];

        // Botón "Anterior"
        if (info.prev) {
            const prevBtn = document.createElement('button');
            prevBtn.textContent = 'Anterior';
            prevBtn.addEventListener('click', () => searchCharacters(currentQuery, currentPage - 1));
            buttons.push(prevBtn);
        }

        // Números de páginas
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        if (startPage > 1) {
            const firstBtn = document.createElement('button');
            firstBtn.textContent = '1';
            firstBtn.addEventListener('click', () => searchCharacters(currentQuery, 1));
            buttons.push(firstBtn);

            if (startPage > 2) {
                const dotsBtn = document.createElement('button');
                dotsBtn.textContent = '...';
                dotsBtn.disabled = true;
                buttons.push(dotsBtn);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            if (i === currentPage) {
                pageBtn.classList.add('active');
            }
            pageBtn.addEventListener('click', () => searchCharacters(currentQuery, i));
            buttons.push(pageBtn);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const dotsBtn = document.createElement('button');
                dotsBtn.textContent = '...';
                dotsBtn.disabled = true;
                buttons.push(dotsBtn);
            }

            const lastBtn = document.createElement('button');
            lastBtn.textContent = totalPages;
            lastBtn.addEventListener('click', () => searchCharacters(currentQuery, totalPages));
            buttons.push(lastBtn);
        }

        // Botón "Siguiente"
        if (info.next) {
            const nextBtn = document.createElement('button');
            nextBtn.textContent = 'Siguiente';
            nextBtn.addEventListener('click', () => searchCharacters(currentQuery, currentPage + 1));
            buttons.push(nextBtn);
        }

        return buttons;
    };

    const buttons = createPaginationButtons();
    buttons.forEach(btn => {
        paginationDiv.appendChild(btn);
        paginationBottomDiv.appendChild(btn.cloneNode(true));
    });

    // Agregar event listeners a los botones clonados
    document.querySelectorAll('#pagination-bottom button').forEach((btn, index) => {
        btn.onclick = buttons[index].onclick;
    });

    paginationDiv.classList.remove('hidden');
    paginationBottomDiv.classList.remove('hidden');
}

function showLoading(show) {
    if (show) {
        loadingDiv.classList.remove('hidden');
    } else {
        loadingDiv.classList.add('hidden');
    }
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    errorDiv.classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Modal functions
function openCharacterModal(character) {
    document.getElementById('modalName').textContent = character.name;
    document.getElementById('modalImage').src = character.image;
    document.getElementById('modalImage').alt = character.name;
    document.getElementById('modalStatus').textContent = character.status;
    document.getElementById('modalSpecies').textContent = character.species;
    document.getElementById('modalGender').textContent = character.gender;
    document.getElementById('modalType').textContent = character.type || 'N/A';
    document.getElementById('modalOrigin').textContent = character.origin.name;
    document.getElementById('modalLocation').textContent = character.location.name;
    document.getElementById('modalEpisodes').textContent = `${character.episode.length} episodios`;
    
    const statusBadge = document.getElementById('modalStatusBadge');
    const statusClass = `status-${character.status.toLowerCase()}`;
    statusBadge.className = `status-badge ${statusClass}`;
    statusBadge.textContent = character.status;
    
    characterModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeCharacterModal() {
    characterModal.classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Focus en el input al cargar
window.addEventListener('load', () => {
    searchInput.focus();
});
