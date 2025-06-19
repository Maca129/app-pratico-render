// Variáveis globais
let currentUser = null;
let currentView = 'login';
const BASE_URL = window.location.origin; // Usar URL absoluta baseada na origem atual

// Função para inicializar a aplicação
document.addEventListener('DOMContentLoaded', () => {
    console.log('Inicializando aplicação...');
    console.log('URL base:', BASE_URL);
    setupEventListeners();
    checkAuthentication();
});

// Configurar listeners de eventos
function setupEventListeners() {
    console.log('Configurando event listeners...');
    
    // Formulário de login (usando o evento submit do formulário)
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        handleLogin();
    });
    
    // Formulário de registro (usando o evento submit do formulário)
    document.getElementById('register-form').addEventListener('submit', (e) => {
        e.preventDefault();
        handleRegister();
    });
}

// Verificar se o usuário está autenticado
function checkAuthentication() {
    console.log('Verificando autenticação...');
    fetch(`${BASE_URL}/api/auth/check-auth`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
    .then(response => {
        console.log('Resposta de autenticação status:', response.status);
        if (!response.ok) {
            throw new Error(`Erro de autenticação: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Resposta de autenticação:', data);
        if (data.authenticated && data.user) {
            currentUser = data.user;
            showDashboard();
        } else {
            // Garantir que a tela de login seja exibida
            document.getElementById('auth-container').style.display = 'block';
            document.getElementById('app-container').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Erro ao verificar autenticação:', error);
        // Garantir que a tela de login seja exibida em caso de erro
        document.getElementById('auth-container').style.display = 'block';
        document.getElementById('app-container').style.display = 'none';
    });
}

// Função para lidar com o login
function handleLogin() {
    console.log('Processando login...');
    const username = document.querySelector('#login-form input[name="username"]').value;
    const password = document.querySelector('#login-form input[name="password"]').value;
    
    if (!username || !password) {
        alert('Por favor, preencha todos os campos.');
        return;
    }
    
    const data = { username, password };
    console.log('Enviando dados de login:', data);
    
    fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
    })
    .then(response => {
        console.log('Resposta do servidor (login):', response.status);
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Credenciais inválidas');
            } else {
                throw new Error(`Erro no servidor: ${response.status}`);
            }
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados da resposta (login):', data);
        if (data.error) {
            alert(data.error);
        } else if (data.user) {
            currentUser = data.user;
            showDashboard();
        } else {
            throw new Error('Resposta do servidor não contém dados do usuário');
        }
    })
    .catch(error => {
        console.error('Erro no login:', error);
        alert(`Erro ao fazer login: ${error.message || 'Tente novamente mais tarde.'}`);
    });
}

// Função para lidar com o registro
function handleRegister() {
    console.log('Processando registro...');
    const username = document.querySelector('#register-form input[name="username"]').value;
    const email = document.querySelector('#register-form input[name="email"]').value;
    const password = document.querySelector('#register-form input[name="password"]').value;
    
    if (!username || !email || !password) {
        alert('Por favor, preencha todos os campos.');
        return;
    }
    
    const data = { username, email, password };
    console.log('Enviando dados de registro:', data);
    
    // Mostrar status de registro em andamento
    const statusDiv = document.getElementById('register-status');
    statusDiv.className = 'status-message';
    statusDiv.textContent = 'Processando registro...';
    statusDiv.style.display = 'block';
    
    fetch(`${BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'include'
    })
    .then(response => {
        console.log('Resposta do servidor (registro):', response.status);
        // Verificar se a resposta é bem-sucedida
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || `Erro no servidor: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados da resposta (registro):', data);
        if (data.error) {
            statusDiv.className = 'status-message error';
            statusDiv.textContent = `Erro: ${data.error}`;
        } else {
            statusDiv.className = 'status-message success';
            statusDiv.textContent = 'Registro realizado com sucesso!';
            
            // Verificar se a resposta contém dados do usuário
            if (data.user) {
                currentUser = data.user;
                setTimeout(() => {
                    showDashboard();
                }, 1500);
            } else {
                console.error('Resposta de registro não contém dados do usuário:', data);
                setTimeout(() => {
                    // Redirecionar para login se não houver dados do usuário
                    alert('Registro realizado! Por favor, faça login.');
                    // Limpar campos
                    document.querySelectorAll('#register-form input').forEach(input => input.value = '');
                }, 1500);
            }
        }
    })
    .catch(error => {
        console.error('Erro no registro:', error);
        statusDiv.className = 'status-message error';
        statusDiv.textContent = `Erro: ${error.message || 'Falha na conexão com o servidor.'}`;
    });
}

// Função para mostrar o dashboard
function showDashboard() {
    console.log('Mostrando dashboard para:', currentUser);
    if (!currentUser) {
        console.error('Tentativa de mostrar dashboard sem usuário autenticado');
        alert('Erro de autenticação. Por favor, faça login novamente.');
        document.getElementById('auth-container').style.display = 'block';
        document.getElementById('app-container').style.display = 'none';
        return;
    }
    
    currentView = 'dashboard';
    
    document.getElementById('auth-container').style.display = 'none';
    const appContainer = document.getElementById('app-container');
    appContainer.style.display = 'block';
    
    // Atualizar nome do usuário na navegação
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        userNameElement.textContent = currentUser.username;
    }
    
    // Carregar o dashboard inicial
    loadDashboardContent();
    
    // Configurar navegação
    setupNavigation();
    
    // Configurar event listeners específicos das páginas
    setupTopicsEventListeners();
}

// Carregar conteúdo do dashboard
function loadDashboardContent() {
    const contentArea = document.getElementById('content-area');
    if (!contentArea) {
        console.error('Elemento content-area não encontrado');
        return;
    }
    
    // Mostrar a página do dashboard
    document.querySelectorAll('.page-content').forEach(page => {
        page.style.display = 'none';
    });
    
    const dashboardPage = document.getElementById('dashboard-page');
    if (dashboardPage) {
        dashboardPage.style.display = 'block';
        
        // Carregar dados do dashboard
        fetchDashboardData();
    } else {
        console.error('Elemento dashboard-page não encontrado');
    }
}

// Configurar navegação
function setupNavigation() {
    document.querySelectorAll('.main-nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = e.target.getAttribute('data-page');
            
            // Atualizar classe ativa
            document.querySelectorAll('.main-nav a').forEach(a => {
                a.classList.remove('active');
            });
            e.target.classList.add('active');
            
            // Mostrar página correspondente
            document.querySelectorAll('.page-content').forEach(content => {
                content.style.display = 'none';
            });
            
            const pageElement = document.getElementById(`${page}-page`);
            if (pageElement) {
                pageElement.style.display = 'block';
                
                // Carregar dados específicos da página
                if (page === 'dashboard') {
                    fetchDashboardData();
                } else if (page === 'topics') {
                    loadTopicsData();
                    setupTopicsEventListeners();
                } else if (page === 'revisions') {
                    loadRevisionsCalendar();
                } else if (page === 'questions') {
                    loadQuestionsData();
                } else if (page === 'edital') {
                    loadEditalContent();
                } else if (page === 'study-timer') {
                    loadTimerData();
                }
            }
        });
    });
    
    // Configurar botão de logout
    document.getElementById('logout-btn').addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
    });
}

// Buscar dados do dashboard
function fetchDashboardData() {
    console.log('Buscando dados do dashboard...');
    fetch(`${BASE_URL}/api/study/dashboard`, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro ao buscar dados do dashboard: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados do dashboard:', data);
        updateDashboardUI(data);
    })
    .catch(error => {
        console.error('Erro ao buscar dados do dashboard:', error);
    });
}

// Atualizar UI do dashboard com os dados
function updateDashboardUI(data) {
    // Implementar atualização dos gráficos e tabelas com os dados recebidos
    // Esta função será expandida conforme necessário
    console.log('Atualizando UI do dashboard com dados:', data);
}

// Carregar calendário de revisões
function loadRevisionsCalendar() {
    console.log('Carregando calendário de revisões...');
    // Implementar carregamento do calendário
}

// Carregar dados de questões
function loadQuestionsData() {
    console.log('Carregando dados de questões...');
    
    // Configurar event listeners para questões
    setupQuestionsEventListeners();
    
    // Carregar tópicos para o filtro
    loadTopicsForQuestions();
    
    // Carregar registros de questões
    loadQuestionRecords();
}

function setupQuestionsEventListeners() {
    // Botão adicionar registro
    const addBtn = document.getElementById('add-question-record-btn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            showQuestionRecordModal();
        });
    }
    
    // Filtros
    const topicFilter = document.getElementById('filter-question-topic');
    const difficultyFilter = document.getElementById('filter-question-difficulty');
    const groupBySelect = document.getElementById('group-by-select');
    
    if (topicFilter) {
        topicFilter.addEventListener('change', loadQuestionRecords);
    }
    if (difficultyFilter) {
        difficultyFilter.addEventListener('change', loadQuestionRecords);
    }
    if (groupBySelect) {
        groupBySelect.addEventListener('change', loadQuestionRecords);
    }
    
    // Modal close button
    const closeBtn = document.querySelector('#question-record-modal .close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeQuestionModal);
    }
}

function showQuestionRecordModal() {
    const modal = document.getElementById('question-record-modal');
    if (modal) {
        modal.style.display = 'block';
        
        // Carregar tópicos no select do modal
        loadTopicsForModal();
        
        // Configurar submit do formulário se ainda não foi configurado
        const form = document.getElementById('question-record-form');
        if (form && !form.hasAttribute('data-listener-added')) {
            form.addEventListener('submit', handleQuestionSubmit);
            form.setAttribute('data-listener-added', 'true');
        }
    }
}

function closeQuestionModal() {
    const modal = document.getElementById('question-record-modal');
    if (modal) {
        modal.style.display = 'none';
        
        // Limpar formulário
        const form = document.getElementById('question-record-form');
        if (form) {
            form.reset();
        }
    }
}

function loadTopicsForModal() {
    fetch(`${BASE_URL}/api/topics`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        // Carregar no modal
        const modalSelect = document.querySelector('#question-record-modal select[name="topic_id"]');
        if (modalSelect && data.topics) {
            // Limpar opções existentes exceto a primeira
            while (modalSelect.children.length > 1) {
                modalSelect.removeChild(modalSelect.lastChild);
            }
            
            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                modalSelect.appendChild(option);
            });
        }
        
        // Carregar no filtro
        const filterSelect = document.getElementById('filter-question-topic');
        if (filterSelect && data.topics) {
            // Limpar opções existentes exceto a primeira
            while (filterSelect.children.length > 1) {
                filterSelect.removeChild(filterSelect.lastChild);
            }
            
            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                filterSelect.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Erro ao carregar tópicos:', error);
    });
}

function handleQuestionSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        topic_id: formData.get('topic_id'),
        source: formData.get('source'),
        specific_topic: formData.get('specific_topic'),
        difficulty_level: formData.get('difficulty_level'),
        total_questions: parseInt(formData.get('total_questions')),
        correct_answers: parseInt(formData.get('correct_answers')),
        notes: formData.get('notes')
    };
    
    // Validar dados
    if (data.correct_answers > data.total_questions) {
        alert('O número de questões corretas não pode ser maior que o total de questões.');
        return;
    }
    
    fetch(`${BASE_URL}/api/study/questions`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erro: ' + data.error);
        } else {
            alert('Registro de questões adicionado com sucesso!');
            closeQuestionModal();
            loadQuestionRecords();
        }
    })
    .catch(error => {
        console.error('Erro ao salvar registro:', error);
        alert('Erro ao salvar registro de questões.');
    });
}

function loadTopicsForQuestions() {
    fetch(`${BASE_URL}/api/topics`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const select = document.querySelector('#questions-page select[id*="topic"]');
        if (select && data.topics) {
            // Limpar opções existentes exceto a primeira
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                select.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Erro ao carregar tópicos:', error);
    });
}

function loadQuestionRecords() {
    console.log('Carregando registros de questões...');
    
    fetch(`${BASE_URL}/api/study/questions`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.records) {
            displayQuestionRecords(data.records);
            updateQuestionCharts(data.records);
        }
    })
    .catch(error => {
        console.error('Erro ao carregar registros:', error);
    });
}

function displayQuestionRecords(records) {
    const container = document.querySelector('.question-records-list');
    if (!container) return;
    
    if (records.length === 0) {
        container.innerHTML = '<p>Nenhum registro encontrado. Adicione seu primeiro registro de questões!</p>';
        return;
    }
    
    let html = '<div class="records-list">';
    records.forEach(record => {
        const accuracy = ((record.correct_answers / record.total_questions) * 100).toFixed(1);
        html += `
            <div class="record-item">
                <div class="record-header">
                    <h4>${record.topic_name || 'Tópico não especificado'}</h4>
                    <span class="record-date">${new Date(record.date).toLocaleDateString('pt-BR')}</span>
                </div>
                <div class="record-details">
                    <p><strong>Fonte:</strong> ${record.source}</p>
                    ${record.specific_topic ? `<p><strong>Tópico Específico:</strong> ${record.specific_topic}</p>` : ''}
                    <p><strong>Dificuldade:</strong> ${record.difficulty_level}</p>
                    <p><strong>Desempenho:</strong> ${record.correct_answers}/${record.total_questions} (${accuracy}%)</p>
                    ${record.notes ? `<p><strong>Observações:</strong> ${record.notes}</p>` : ''}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function updateQuestionCharts(records) {
    // Implementar gráficos de desempenho
    console.log('Atualizando gráficos de questões:', records);
}

// Carregar conteúdo do edital
function loadEditalContent() {
    console.log('Carregando conteúdo do edital...');
    // Implementar carregamento do edital
}

// Função para lidar com o logout
function handleLogout() {
    console.log('Processando logout...');
    
    fetch(`${BASE_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro no logout: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Logout realizado:', data);
        currentUser = null;
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('auth-container').style.display = 'block';
        // Limpar campos de formulário
        document.querySelectorAll('input').forEach(input => input.value = '');
    })
    .catch(error => {
        console.error('Erro no logout:', error);
        alert(`Erro ao fazer logout: ${error.message}`);
    });
}

// Configurar event listeners específicos das páginas
function setupTopicsEventListeners() {
    // Botão de adicionar tópico
    const addTopicBtn = document.getElementById('add-topic-btn');
    if (addTopicBtn) {
        addTopicBtn.addEventListener('click', () => {
            openTopicModal();
        });
    }
    
    // Filtro de grupo
    const filterGroup = document.getElementById('filter-group');
    if (filterGroup) {
        filterGroup.addEventListener('change', () => {
            renderTopicsList();
        });
    }
}


// ===== FUNCIONALIDADE DO CRONÔMETRO =====

let timerState = {
    isRunning: false,
    isPaused: false,
    startTime: null,
    pausedTime: 0,
    currentTime: 0,
    intervalId: null
};

function setupTimerEventListeners() {
    // Botões do cronômetro
    const startBtn = document.getElementById('timer-start-btn');
    const pauseBtn = document.getElementById('timer-pause-btn');
    const stopBtn = document.getElementById('timer-stop-btn');
    
    if (startBtn) {
        startBtn.addEventListener('click', startTimer);
    }
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseTimer);
    }
    if (stopBtn) {
        stopBtn.addEventListener('click', stopTimer);
    }
    
    // Carregar tópicos no select
    loadTopicsForTimer();
    
    // Carregar sessões recentes
    loadRecentSessions();
}

function startTimer() {
    if (!timerState.isRunning) {
        timerState.isRunning = true;
        timerState.isPaused = false;
        timerState.startTime = new Date().getTime() - timerState.pausedTime;
        
        timerState.intervalId = setInterval(updateTimerDisplay, 1000);
        
        // Atualizar estado dos botões
        updateTimerButtons();
        
        console.log('Timer iniciado');
    }
}

function pauseTimer() {
    if (timerState.isRunning && !timerState.isPaused) {
        timerState.isPaused = true;
        timerState.pausedTime = new Date().getTime() - timerState.startTime;
        
        clearInterval(timerState.intervalId);
        
        // Atualizar estado dos botões
        updateTimerButtons();
        
        console.log('Timer pausado');
    } else if (timerState.isPaused) {
        // Retomar timer
        timerState.isPaused = false;
        timerState.startTime = new Date().getTime() - timerState.pausedTime;
        
        timerState.intervalId = setInterval(updateTimerDisplay, 1000);
        
        // Atualizar estado dos botões
        updateTimerButtons();
        
        console.log('Timer retomado');
    }
}

function stopTimer() {
    if (timerState.isRunning) {
        clearInterval(timerState.intervalId);
        
        // Calcular duração total em minutos
        const totalTime = timerState.isPaused ? timerState.pausedTime : (new Date().getTime() - timerState.startTime);
        const durationMinutes = Math.floor(totalTime / 60000);
        
        if (durationMinutes > 0) {
            // Salvar sessão de estudo
            saveStudySession(durationMinutes);
        }
        
        // Reset timer
        resetTimer();
        
        console.log('Timer finalizado');
    }
}

function resetTimer() {
    timerState = {
        isRunning: false,
        isPaused: false,
        startTime: null,
        pausedTime: 0,
        currentTime: 0,
        intervalId: null
    };
    
    // Atualizar display
    updateTimerDisplay();
    updateTimerButtons();
}

function updateTimerDisplay() {
    const hoursElement = document.getElementById('timer-hours');
    const minutesElement = document.getElementById('timer-minutes');
    const secondsElement = document.getElementById('timer-seconds');
    
    if (!hoursElement || !minutesElement || !secondsElement) return;
    
    let currentTime = 0;
    
    if (timerState.isRunning && !timerState.isPaused) {
        currentTime = new Date().getTime() - timerState.startTime;
    } else if (timerState.isPaused) {
        currentTime = timerState.pausedTime;
    }
    
    const hours = Math.floor(currentTime / 3600000);
    const minutes = Math.floor((currentTime % 3600000) / 60000);
    const seconds = Math.floor((currentTime % 60000) / 1000);
    
    hoursElement.textContent = hours.toString().padStart(2, '0');
    minutesElement.textContent = minutes.toString().padStart(2, '0');
    secondsElement.textContent = seconds.toString().padStart(2, '0');
}

function updateTimerButtons() {
    const startBtn = document.getElementById('timer-start-btn');
    const pauseBtn = document.getElementById('timer-pause-btn');
    const stopBtn = document.getElementById('timer-stop-btn');
    
    if (startBtn && pauseBtn && stopBtn) {
        if (!timerState.isRunning) {
            startBtn.textContent = 'Iniciar';
            startBtn.disabled = false;
            pauseBtn.textContent = 'Pausar';
            pauseBtn.disabled = true;
            stopBtn.disabled = true;
        } else if (timerState.isPaused) {
            startBtn.textContent = 'Iniciar';
            startBtn.disabled = true;
            pauseBtn.textContent = 'Retomar';
            pauseBtn.disabled = false;
            stopBtn.disabled = false;
        } else {
            startBtn.textContent = 'Iniciar';
            startBtn.disabled = true;
            pauseBtn.textContent = 'Pausar';
            pauseBtn.disabled = false;
            stopBtn.disabled = false;
        }
    }
}

function loadTopicsForTimer() {
    fetch(`${BASE_URL}/api/topics`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById('timer-topic');
        if (select && data.topics) {
            // Limpar opções existentes exceto a primeira
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
            
            data.topics.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.id;
                option.textContent = topic.name;
                select.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Erro ao carregar tópicos:', error);
    });
}

function saveStudySession(durationMinutes) {
    const topicSelect = document.getElementById('timer-topic');
    const descriptionTextarea = document.getElementById('timer-description');
    
    const sessionData = {
        duration_minutes: durationMinutes,
        topic_id: topicSelect && topicSelect.value ? parseInt(topicSelect.value) : null,
        description: descriptionTextarea ? descriptionTextarea.value : ''
    };
    
    fetch(`${BASE_URL}/api/study/sessions`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sessionData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erro ao salvar sessão: ' + data.error);
        } else {
            alert(`Sessão de estudo salva! Duração: ${durationMinutes} minutos`);
            
            // Limpar campos
            if (topicSelect) topicSelect.selectedIndex = 0;
            if (descriptionTextarea) descriptionTextarea.value = '';
            
            // Recarregar sessões recentes
            loadRecentSessions();
        }
    })
    .catch(error => {
        console.error('Erro ao salvar sessão:', error);
        alert('Erro ao salvar sessão de estudo.');
    });
}

function loadRecentSessions() {
    fetch(`${BASE_URL}/api/study/sessions?limit=5`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(sessions => {
        displayRecentSessions(sessions);
    })
    .catch(error => {
        console.error('Erro ao carregar sessões:', error);
    });
}

function displayRecentSessions(sessions) {
    const container = document.querySelector('.study-sessions-list');
    if (!container) return;
    
    if (sessions.length === 0) {
        container.innerHTML = '<p>Nenhuma sessão de estudo registrada ainda.</p>';
        return;
    }
    
    let html = '<div class="sessions-list">';
    sessions.forEach(session => {
        const date = new Date(session.start_time).toLocaleDateString('pt-BR');
        const time = new Date(session.start_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        const duration = session.duration_minutes || 0;
        const hours = Math.floor(duration / 60);
        const minutes = duration % 60;
        const durationText = hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`;
        
        html += `
            <div class="session-item">
                <div class="session-header">
                    <span class="session-date">${date} às ${time}</span>
                    <span class="session-duration">${durationText}</span>
                </div>
                ${session.topic_name ? `<p><strong>Tópico:</strong> ${session.topic_name}</p>` : ''}
                ${session.description ? `<p><strong>Descrição:</strong> ${session.description}</p>` : ''}
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Adicionar ao switch de páginas
function loadTimerData() {
    console.log('Carregando dados do cronômetro...');
    setupTimerEventListeners();
    resetTimer();
}

