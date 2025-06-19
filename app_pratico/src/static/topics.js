// Funções para gerenciamento de tópicos
let topicsData = [];

// Carregar tópicos quando a página de tópicos for aberta
function loadTopicsData() {
    console.log('Carregando dados de tópicos...');
    
    // Mostrar indicador de carregamento
    const topicsList = document.querySelector('.topics-list');
    if (topicsList) {
        topicsList.innerHTML = '<div class="loading">Carregando tópicos...</div>';
    }
    
    fetch(`${BASE_URL}/api/topics/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro ao buscar tópicos: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados de tópicos recebidos:', data);
        topicsData = data.topics || [];
        renderTopicsList();
        
        // Atualizar seletores de tópicos em outras partes da aplicação
        updateTopicSelectors();
    })
    .catch(error => {
        console.error('Erro ao buscar tópicos:', error);
        if (topicsList) {
            topicsList.innerHTML = `<div class="error-message">Erro ao carregar tópicos: ${error.message}</div>`;
        }
    });
}

// Renderizar lista de tópicos
function renderTopicsList() {
    const topicsList = document.querySelector('.topics-list');
    if (!topicsList) return;
    
    const filterGroup = document.getElementById('filter-group').value;
    
    // Filtrar tópicos se necessário
    let filteredTopics = topicsData;
    if (filterGroup) {
        filteredTopics = topicsData.filter(topic => topic.group_id.toString() === filterGroup);
    }
    
    if (filteredTopics.length === 0) {
        topicsList.innerHTML = '<div class="empty-state">Nenhum tópico encontrado. Adicione seu primeiro tópico de estudo!</div>';
        return;
    }
    
    // Agrupar tópicos por grupo
    const groupedTopics = {};
    filteredTopics.forEach(topic => {
        const groupId = topic.group_id;
        if (!groupedTopics[groupId]) {
            groupedTopics[groupId] = {
                name: topic.group_name,
                topics: []
            };
        }
        groupedTopics[groupId].topics.push(topic);
    });
    
    // Construir HTML
    let html = '';
    Object.keys(groupedTopics).forEach(groupId => {
        const group = groupedTopics[groupId];
        
        html += `
            <div class="topic-group">
                <h3>${group.name}</h3>
                <div class="topic-group-items">
        `;
        
        group.topics.forEach(topic => {
            const confidenceClass = `confidence-${topic.confidence_level.toLowerCase()}`;
            const completedClass = topic.is_completed ? 'completed' : '';
            
            html += `
                <div class="topic-item ${completedClass}" data-id="${topic.id}">
                    <div class="topic-info">
                        <h4>${topic.name}</h4>
                        <p>${topic.description || 'Sem descrição'}</p>
                        <div class="topic-meta">
                            <span class="confidence-badge ${confidenceClass}">${topic.confidence_level}</span>
                            <span class="completion-status">${topic.is_completed ? 'Concluído' : 'Em andamento'}</span>
                        </div>
                    </div>
                    <div class="topic-actions">
                        <button class="edit-topic-btn" data-id="${topic.id}">Editar</button>
                        <button class="delete-topic-btn" data-id="${topic.id}">Excluir</button>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    topicsList.innerHTML = html;
    
    // Adicionar event listeners para botões de edição e exclusão
    document.querySelectorAll('.edit-topic-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const topicId = e.target.getAttribute('data-id');
            openTopicModal(topicId);
        });
    });
    
    document.querySelectorAll('.delete-topic-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const topicId = e.target.getAttribute('data-id');
            confirmDeleteTopic(topicId);
        });
    });
}

// Abrir modal de tópico (para adicionar ou editar)
function openTopicModal(topicId = null) {
    const modal = document.getElementById('topic-modal');
    const form = document.getElementById('topic-form');
    
    // Limpar formulário
    form.reset();
    
    if (topicId) {
        // Modo de edição
        const topic = topicsData.find(t => t.id.toString() === topicId.toString());
        if (topic) {
            form.querySelector('input[name="topic_id"]').value = topic.id;
            form.querySelector('select[name="group_id"]').value = topic.group_id;
            form.querySelector('input[name="name"]').value = topic.name;
            form.querySelector('textarea[name="description"]').value = topic.description || '';
            form.querySelector('select[name="confidence_level"]').value = topic.confidence_level;
            form.querySelector('input[name="is_completed"]').checked = topic.is_completed;
            
            document.querySelector('#topic-modal h3').textContent = 'Editar Tópico';
        }
    } else {
        // Modo de adição
        form.querySelector('input[name="topic_id"]').value = '';
        document.querySelector('#topic-modal h3').textContent = 'Adicionar Tópico';
    }
    
    // Mostrar modal
    modal.style.display = 'flex';
    
    // Configurar botão de fechar
    document.querySelector('#topic-modal .close-modal').addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Configurar envio do formulário
    form.onsubmit = function(e) {
        e.preventDefault();
        saveTopic();
    };
}

// Salvar tópico (adicionar ou atualizar)
function saveTopic() {
    const form = document.getElementById('topic-form');
    const topicId = form.querySelector('input[name="topic_id"]').value;
    
    // Obter dados do formulário
    const groupId = form.querySelector('select[name="group_id"]').value;
    const groupName = form.querySelector('select[name="group_id"] option:checked').textContent;
    const name = form.querySelector('input[name="name"]').value;
    const description = form.querySelector('textarea[name="description"]').value;
    const confidenceLevel = form.querySelector('select[name="confidence_level"]').value;
    const isCompleted = form.querySelector('input[name="is_completed"]').checked;
    
    // Validar dados
    if (!name || !groupId) {
        alert('Por favor, preencha os campos obrigatórios.');
        return;
    }
    
    // Preparar dados para envio
    const topicData = {
        name,
        group_id: parseInt(groupId),
        group_name: groupName,
        description,
        confidence_level: confidenceLevel,
        is_completed: isCompleted,
        create_revisions: true // Sempre criar revisões para novos tópicos
    };
    
    console.log('Salvando tópico:', topicData);
    
    // Determinar método e URL com base em adição ou edição
    const method = topicId ? 'PUT' : 'POST';
    const url = topicId ? `${BASE_URL}/api/topics/${topicId}` : `${BASE_URL}/api/topics/`;
    
    // Enviar requisição
    fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(topicData),
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro ao salvar tópico: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Tópico salvo com sucesso:', data);
        
        // Fechar modal
        document.getElementById('topic-modal').style.display = 'none';
        
        // Atualizar lista de tópicos
        loadTopicsData();
        
        // Mostrar notificação de sucesso
        showNotification(topicId ? 'Tópico atualizado com sucesso!' : 'Tópico adicionado com sucesso!', 'success');
    })
    .catch(error => {
        console.error('Erro ao salvar tópico:', error);
        showNotification(`Erro ao salvar tópico: ${error.message}`, 'error');
    });
}

// Confirmar exclusão de tópico
function confirmDeleteTopic(topicId) {
    if (confirm('Tem certeza que deseja excluir este tópico? Esta ação não pode ser desfeita.')) {
        deleteTopic(topicId);
    }
}

// Excluir tópico
function deleteTopic(topicId) {
    fetch(`${BASE_URL}/api/topics/${topicId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro ao excluir tópico: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Tópico excluído com sucesso:', data);
        
        // Atualizar lista de tópicos
        loadTopicsData();
        
        // Mostrar notificação de sucesso
        showNotification('Tópico excluído com sucesso!', 'success');
    })
    .catch(error => {
        console.error('Erro ao excluir tópico:', error);
        showNotification(`Erro ao excluir tópico: ${error.message}`, 'error');
    });
}

// Atualizar seletores de tópicos em outras partes da aplicação
function updateTopicSelectors() {
    // Atualizar seletor de tópicos no cronômetro
    const timerTopicSelect = document.getElementById('timer-topic');
    if (timerTopicSelect) {
        // Manter a opção vazia
        let html = '<option value="">Selecione um tópico</option>';
        
        // Adicionar tópicos agrupados
        const groupedTopics = {};
        topicsData.forEach(topic => {
            const groupId = topic.group_id;
            if (!groupedTopics[groupId]) {
                groupedTopics[groupId] = {
                    name: topic.group_name,
                    topics: []
                };
            }
            groupedTopics[groupId].topics.push(topic);
        });
        
        Object.keys(groupedTopics).forEach(groupId => {
            const group = groupedTopics[groupId];
            html += `<optgroup label="${group.name}">`;
            
            group.topics.forEach(topic => {
                html += `<option value="${topic.id}">${topic.name}</option>`;
            });
            
            html += '</optgroup>';
        });
        
        timerTopicSelect.innerHTML = html;
    }
    
    // Atualizar seletor de tópicos no registro de questões
    const questionTopicSelect = document.querySelector('#question-record-form select[name="topic_id"]');
    if (questionTopicSelect) {
        // Manter a opção vazia
        let html = '<option value="">Selecione um tópico</option>';
        
        // Adicionar tópicos agrupados
        const groupedTopics = {};
        topicsData.forEach(topic => {
            const groupId = topic.group_id;
            if (!groupedTopics[groupId]) {
                groupedTopics[groupId] = {
                    name: topic.group_name,
                    topics: []
                };
            }
            groupedTopics[groupId].topics.push(topic);
        });
        
        Object.keys(groupedTopics).forEach(groupId => {
            const group = groupedTopics[groupId];
            html += `<optgroup label="${group.name}">`;
            
            group.topics.forEach(topic => {
                html += `<option value="${topic.id}">${topic.name}</option>`;
            });
            
            html += '</optgroup>';
        });
        
        questionTopicSelect.innerHTML = html;
    }
    
    // Atualizar filtro de tópicos na página de revisões
    const filterTopicSelect = document.getElementById('filter-topic');
    if (filterTopicSelect) {
        // Manter a opção vazia
        let html = '<option value="">Todos os Tópicos</option>';
        
        // Adicionar tópicos agrupados
        const groupedTopics = {};
        topicsData.forEach(topic => {
            const groupId = topic.group_id;
            if (!groupedTopics[groupId]) {
                groupedTopics[groupId] = {
                    name: topic.group_name,
                    topics: []
                };
            }
            groupedTopics[groupId].topics.push(topic);
        });
        
        Object.keys(groupedTopics).forEach(groupId => {
            const group = groupedTopics[groupId];
            html += `<optgroup label="${group.name}">`;
            
            group.topics.forEach(topic => {
                html += `<option value="${topic.id}">${topic.name}</option>`;
            });
            
            html += '</optgroup>';
        });
        
        filterTopicSelect.innerHTML = html;
    }
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    // Verificar se a biblioteca Notyf está disponível
    if (typeof Notyf !== 'undefined') {
        const notyf = new Notyf({
            duration: 3000,
            position: {
                x: 'right',
                y: 'top'
            },
            types: [
                {
                    type: 'success',
                    background: '#2ecc71'
                },
                {
                    type: 'error',
                    background: '#e74c3c'
                },
                {
                    type: 'info',
                    background: '#3498db'
                }
            ]
        });
        
        notyf.open({
            type: type,
            message: message
        });
    } else {
        // Fallback para alert se Notyf não estiver disponível
        alert(message);
    }
}
