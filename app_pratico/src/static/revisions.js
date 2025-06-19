// Funções para gerenciamento do sistema de revisões
document.addEventListener('DOMContentLoaded', function() {
    // Configurar event listeners específicos para a página de revisões
    setupRevisionsEventListeners();
});

// Configurar event listeners para a página de revisões
function setupRevisionsEventListeners() {
    // Botões de alternância entre visualizações de calendário e lista
    const calendarViewBtn = document.getElementById('calendar-view-btn');
    const listViewBtn = document.getElementById('list-view-btn');
    
    if (calendarViewBtn) {
        calendarViewBtn.addEventListener('click', function() {
            showCalendarView();
        });
    }
    
    if (listViewBtn) {
        listViewBtn.addEventListener('click', function() {
            showListView();
        });
    }
    
    // Botão de configuração de notificações
    const notificationSettingsBtn = document.getElementById('notification-settings-btn');
    if (notificationSettingsBtn) {
        notificationSettingsBtn.addEventListener('click', function() {
            showNotificationSettings();
        });
    }
    
    // Carregar revisões ao entrar na página
    if (document.getElementById('revisions-page')) {
        loadRevisionsData();
    }
}

// Carregar dados de revisões do backend
function loadRevisionsData() {
    showLoading('Carregando revisões...');
    
    fetch(`${BASE_URL}/api/topics/upcoming-revisions`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao carregar revisões');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        if (data.upcoming_revisions && data.upcoming_revisions.length > 0) {
            renderRevisions(data.upcoming_revisions);
        } else {
            showEmptyState('Nenhuma revisão programada', 'Adicione tópicos de estudo para gerar revisões automáticas.');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Erro ao carregar revisões', error.message);
    });
}

// Renderizar revisões no formato de calendário
function renderRevisionsCalendar(revisions) {
    const calendarContainer = document.getElementById('calendar-container');
    if (!calendarContainer) return;
    
    calendarContainer.innerHTML = '';
    
    // Agrupar revisões por data
    const revisionsByDate = {};
    revisions.forEach(revision => {
        const date = new Date(revision.scheduled_date);
        const dateKey = date.toISOString().split('T')[0];
        
        if (!revisionsByDate[dateKey]) {
            revisionsByDate[dateKey] = [];
        }
        revisionsByDate[dateKey].push(revision);
    });
    
    // Criar calendário
    const calendar = document.createElement('div');
    calendar.className = 'calendar';
    
    // Cabeçalho do calendário com mês atual
    const today = new Date();
    const currentMonth = today.toLocaleString('pt-BR', { month: 'long', year: 'numeric' });
    
    const calendarHeader = document.createElement('div');
    calendarHeader.className = 'calendar-header';
    calendarHeader.innerHTML = `
        <button class="btn btn-sm btn-outline-primary prev-month"><i class="fas fa-chevron-left"></i></button>
        <h3>${currentMonth}</h3>
        <button class="btn btn-sm btn-outline-primary next-month"><i class="fas fa-chevron-right"></i></button>
    `;
    calendar.appendChild(calendarHeader);
    
    // Dias da semana
    const weekdays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const weekdaysRow = document.createElement('div');
    weekdaysRow.className = 'weekdays';
    
    weekdays.forEach(day => {
        const dayElement = document.createElement('div');
        dayElement.className = 'weekday';
        dayElement.textContent = day;
        weekdaysRow.appendChild(dayElement);
    });
    
    calendar.appendChild(weekdaysRow);
    
    // Dias do mês
    const daysContainer = document.createElement('div');
    daysContainer.className = 'days';
    
    // Obter o primeiro dia do mês atual
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    // Adicionar dias vazios para alinhar com o dia da semana correto
    for (let i = 0; i < firstDay.getDay(); i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'day empty';
        daysContainer.appendChild(emptyDay);
    }
    
    // Adicionar dias do mês
    for (let i = 1; i <= lastDay.getDate(); i++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'day';
        
        const dateObj = new Date(today.getFullYear(), today.getMonth(), i);
        const dateKey = dateObj.toISOString().split('T')[0];
        
        // Verificar se é hoje
        if (i === today.getDate()) {
            dayElement.classList.add('today');
        }
        
        // Adicionar número do dia
        const dayNumber = document.createElement('div');
        dayNumber.className = 'day-number';
        dayNumber.textContent = i;
        dayElement.appendChild(dayNumber);
        
        // Adicionar revisões para este dia
        if (revisionsByDate[dateKey]) {
            const revisionsForDay = revisionsByDate[dateKey];
            
            revisionsForDay.forEach(revision => {
                const revisionElement = document.createElement('div');
                revisionElement.className = 'calendar-revision';
                revisionElement.style.backgroundColor = revision.color || '#4285f4';
                revisionElement.textContent = revision.topic_name;
                revisionElement.dataset.revisionId = revision.id;
                
                // Adicionar evento de clique para mostrar detalhes
                revisionElement.addEventListener('click', () => {
                    showRevisionDetails(revision);
                });
                
                dayElement.appendChild(revisionElement);
            });
        }
        
        daysContainer.appendChild(dayElement);
    }
    
    calendar.appendChild(daysContainer);
    calendarContainer.appendChild(calendar);
    
    // Adicionar eventos para navegação do calendário
    const prevMonthBtn = calendarContainer.querySelector('.prev-month');
    const nextMonthBtn = calendarContainer.querySelector('.next-month');
    
    prevMonthBtn.addEventListener('click', () => {
        // Implementar navegação para mês anterior
        alert('Navegação para mês anterior será implementada em breve!');
    });
    
    nextMonthBtn.addEventListener('click', () => {
        // Implementar navegação para próximo mês
        alert('Navegação para próximo mês será implementada em breve!');
    });
}

// Renderizar revisões no formato de lista
function renderRevisionsList(revisions) {
    const listContainer = document.getElementById('list-container');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';
    
    // Agrupar revisões por data
    const revisionsByDate = {};
    revisions.forEach(revision => {
        const date = new Date(revision.scheduled_date);
        const dateKey = date.toISOString().split('T')[0];
        
        if (!revisionsByDate[dateKey]) {
            revisionsByDate[dateKey] = [];
        }
        revisionsByDate[dateKey].push(revision);
    });
    
    // Ordenar datas
    const sortedDates = Object.keys(revisionsByDate).sort();
    
    // Criar lista de revisões agrupadas por data
    sortedDates.forEach(dateKey => {
        const dateObj = new Date(dateKey);
        const formattedDate = dateObj.toLocaleDateString('pt-BR', { 
            weekday: 'long', 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
        });
        
        const dateHeader = document.createElement('div');
        dateHeader.className = 'date-header';
        dateHeader.innerHTML = `<h5>${formattedDate}</h5>`;
        listContainer.appendChild(dateHeader);
        
        const revisionsForDate = revisionsByDate[dateKey];
        
        revisionsForDate.forEach(revision => {
            const revisionElement = document.createElement('div');
            revisionElement.className = 'revision-item';
            revisionElement.dataset.revisionId = revision.id;
            
            // Adicionar borda colorida baseada na cor da revisão
            revisionElement.style.borderLeft = `4px solid ${revision.color || '#4285f4'}`;
            
            revisionElement.innerHTML = `
                <div class="revision-content">
                    <h6>${revision.topic_name}</h6>
                    <p class="revision-info">
                        <span class="badge ${revision.is_completed ? 'bg-success' : 'bg-warning'}">
                            ${revision.is_completed ? 'Concluída' : 'Pendente'}
                        </span>
                        <span class="revision-number">Revisão #${revision.revision_number}</span>
                    </p>
                    <p class="revision-description">${revision.topic_description || 'Sem descrição'}</p>
                </div>
                <div class="revision-actions">
                    <button class="btn btn-sm ${revision.is_completed ? 'btn-outline-success' : 'btn-success'} complete-btn">
                        <i class="fas ${revision.is_completed ? 'fa-check-circle' : 'fa-check'}"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary details-btn">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
            `;
            
            listContainer.appendChild(revisionElement);
            
            // Adicionar eventos aos botões
            const completeBtn = revisionElement.querySelector('.complete-btn');
            const detailsBtn = revisionElement.querySelector('.details-btn');
            
            completeBtn.addEventListener('click', () => {
                toggleRevisionCompletion(revision);
            });
            
            detailsBtn.addEventListener('click', () => {
                showRevisionDetails(revision);
            });
        });
    });
}

// Renderizar revisões (decide entre calendário ou lista)
function renderRevisions(revisions) {
    // Verificar qual visualização está ativa
    const calendarContainer = document.getElementById('calendar-container');
    const listContainer = document.getElementById('list-container');
    
    if (calendarContainer && calendarContainer.style.display !== 'none') {
        renderRevisionsCalendar(revisions);
    } else if (listContainer) {
        renderRevisionsList(revisions);
    }
}

// Alternar entre visualizações de calendário e lista
function showCalendarView() {
    const calendarContainer = document.getElementById('calendar-container');
    const listContainer = document.getElementById('list-container');
    const calendarViewBtn = document.getElementById('calendar-view-btn');
    const listViewBtn = document.getElementById('list-view-btn');
    
    if (calendarContainer && listContainer) {
        calendarContainer.style.display = 'block';
        listContainer.style.display = 'none';
        
        calendarViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        
        // Recarregar dados para o calendário
        loadRevisionsData();
    }
}

function showListView() {
    const calendarContainer = document.getElementById('calendar-container');
    const listContainer = document.getElementById('list-container');
    const calendarViewBtn = document.getElementById('calendar-view-btn');
    const listViewBtn = document.getElementById('list-view-btn');
    
    if (calendarContainer && listContainer) {
        calendarContainer.style.display = 'none';
        listContainer.style.display = 'block';
        
        calendarViewBtn.classList.remove('active');
        listViewBtn.classList.add('active');
        
        // Recarregar dados para a lista
        loadRevisionsData();
    }
}

// Mostrar detalhes de uma revisão
function showRevisionDetails(revision) {
    // Criar modal de detalhes
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'revisionDetailsModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'revisionDetailsModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    const formattedDate = new Date(revision.scheduled_date).toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header" style="border-bottom: 4px solid ${revision.color || '#4285f4'}">
                    <h5 class="modal-title" id="revisionDetailsModalLabel">Detalhes da Revisão</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <h4>${revision.topic_name}</h4>
                    <p class="text-muted">${revision.topic_group}</p>
                    
                    <div class="revision-detail">
                        <strong>Data programada:</strong> ${formattedDate}
                    </div>
                    
                    <div class="revision-detail">
                        <strong>Número da revisão:</strong> ${revision.revision_number}
                    </div>
                    
                    <div class="revision-detail">
                        <strong>Status:</strong> 
                        <span class="badge ${revision.is_completed ? 'bg-success' : 'bg-warning'}">
                            ${revision.is_completed ? 'Concluída' : 'Pendente'}
                        </span>
                    </div>
                    
                    <div class="revision-detail">
                        <strong>Descrição:</strong>
                        <p>${revision.topic_description || 'Sem descrição'}</p>
                    </div>
                    
                    <div class="revision-detail">
                        <strong>Notas:</strong>
                        <textarea id="revision-notes" class="form-control" rows="3">${revision.notes || ''}</textarea>
                    </div>
                    
                    <div class="form-check mt-3">
                        <input class="form-check-input" type="checkbox" id="revision-notify" ${revision.notify ? 'checked' : ''}>
                        <label class="form-check-label" for="revision-notify">
                            Receber notificação para esta revisão
                        </label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    <button type="button" class="btn ${revision.is_completed ? 'btn-outline-success' : 'btn-success'}" id="toggle-completion-btn">
                        ${revision.is_completed ? 'Marcar como Pendente' : 'Marcar como Concluída'}
                    </button>
                    <button type="button" class="btn btn-primary" id="save-revision-btn">Salvar Alterações</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Inicializar o modal Bootstrap
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Adicionar eventos aos botões
    const toggleCompletionBtn = document.getElementById('toggle-completion-btn');
    const saveRevisionBtn = document.getElementById('save-revision-btn');
    
    toggleCompletionBtn.addEventListener('click', () => {
        toggleRevisionCompletion(revision);
        modalInstance.hide();
    });
    
    saveRevisionBtn.addEventListener('click', () => {
        const notes = document.getElementById('revision-notes').value;
        const notify = document.getElementById('revision-notify').checked;
        
        updateRevision(revision.id, {
            notes: notes,
            notify: notify
        });
        
        modalInstance.hide();
    });
    
    // Remover o modal do DOM quando for fechado
    modal.addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modal);
    });
}

// Alternar o status de conclusão de uma revisão
function toggleRevisionCompletion(revision) {
    const newStatus = !revision.is_completed;
    
    showLoading('Atualizando revisão...');
    
    fetch(`${BASE_URL}/api/topics/revisions/${revision.id}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            is_completed: newStatus
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao atualizar revisão');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        showSuccess(`Revisão ${newStatus ? 'concluída' : 'marcada como pendente'} com sucesso!`);
        
        // Recarregar dados
        loadRevisionsData();
    })
    .catch(error => {
        hideLoading();
        showError('Erro ao atualizar revisão', error.message);
    });
}

// Atualizar dados de uma revisão
function updateRevision(revisionId, data) {
    showLoading('Atualizando revisão...');
    
    fetch(`${BASE_URL}/api/topics/revisions/${revisionId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao atualizar revisão');
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        showSuccess('Revisão atualizada com sucesso!');
        
        // Recarregar dados
        loadRevisionsData();
    })
    .catch(error => {
        hideLoading();
        showError('Erro ao atualizar revisão', error.message);
    });
}

// Mostrar configurações de notificação
function showNotificationSettings() {
    // Criar modal de configurações
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'notificationSettingsModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'notificationSettingsModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="notificationSettingsModalLabel">Configurações de Notificação</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="enable-notifications" checked>
                        <label class="form-check-label" for="enable-notifications">
                            Ativar notificações para revisões
                        </label>
                    </div>
                    
                    <div class="mb-3">
                        <label for="notification-time" class="form-label">Horário para receber notificações:</label>
                        <input type="time" class="form-control" id="notification-time" value="08:00">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Notificar com antecedência:</label>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="notify-same-day" checked>
                            <label class="form-check-label" for="notify-same-day">
                                No mesmo dia
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="notify-day-before">
                            <label class="form-check-label" for="notify-day-before">
                                Um dia antes
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="save-notification-settings">Salvar Configurações</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Inicializar o modal Bootstrap
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Adicionar evento ao botão de salvar
    const saveSettingsBtn = document.getElementById('save-notification-settings');
    
    saveSettingsBtn.addEventListener('click', () => {
        const enableNotifications = document.getElementById('enable-notifications').checked;
        const notificationTime = document.getElementById('notification-time').value;
        const notifySameDay = document.getElementById('notify-same-day').checked;
        const notifyDayBefore = document.getElementById('notify-day-before').checked;
        
        // Aqui você implementaria a lógica para salvar as configurações
        // Por enquanto, apenas mostrar uma mensagem de sucesso
        showSuccess('Configurações de notificação salvas com sucesso!');
        
        modalInstance.hide();
    });
    
    // Remover o modal do DOM quando for fechado
    modal.addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modal);
    });
}
