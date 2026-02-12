// Dashboard Application

class Dashboard {
    constructor() {
        this.agents = [];
        this.selectedAgent = null;
        this.init();
    }

    async init() {
        await this.loadAgents();
        this.renderStats();
        this.renderAgentCards();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            this.agents = await response.json();
        } catch (error) {
            console.error('Failed to load agents:', error);
            this.agents = [];
        }
    }

    renderStats() {
        const total = this.agents.length;
        const active = this.agents.filter(a => a.status === 'active').length;
        const inactive = this.agents.filter(a => a.status === 'inactive').length;
        const error = this.agents.filter(a => a.status === 'error').length;

        document.getElementById('total-agents').textContent = total;
        document.getElementById('active-agents').textContent = active;
        document.getElementById('inactive-agents').textContent = inactive;
        document.getElementById('error-agents').textContent = error;
    }

    renderAgentCards() {
        const container = document.getElementById('agent-cards');
        container.innerHTML = '';

        this.agents.forEach(agent => {
            const card = document.createElement('div');
            card.className = 'agent-card';
            card.dataset.name = agent.name;

            card.innerHTML = `
                <div class="name">${agent.displayName || agent.name}</div>
                <div class="status status-${agent.status}">${this.getStatusText(agent.status)}</div>
            `;

            card.addEventListener('click', () => this.selectAgent(agent));
            container.appendChild(card);
        });
    }

    getStatusText(status) {
        const statusMap = {
            'active': '稼働中',
            'inactive': '停止中',
            'error': 'エラー'
        };
        return statusMap[status] || status;
    }

    selectAgent(agent) {
        this.selectedAgent = agent;

        // Update card selection
        document.querySelectorAll('.agent-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.name === agent.name);
        });

        this.renderDetail(agent);
    }

    renderDetail(agent) {
        const container = document.getElementById('detail-view');

        container.innerHTML = `
            <div class="detail-header">
                <h3>${agent.displayName || agent.name}</h3>
                <span class="status status-${agent.status}">${this.getStatusText(agent.status)}</span>
            </div>
            <div class="detail-info">
                <p><strong>説明:</strong> ${agent.description || '説明なし'}</p>
                <p><strong>作成日時:</strong> ${new Date(agent.createdAt).toLocaleString('ja-JP')}</p>
                <p><strong>最終更新:</strong> ${new Date(agent.updatedAt).toLocaleString('ja-JP')}</p>
            </div>
            <div class="detail-actions">
                <button onclick="dashboard.toggleAgent('${agent.name}')" class="btn btn-primary">
                    ${agent.status === 'active' ? '停止' : '起動'}
                </button>
            </div>
        `;
    }

    async toggleAgent(name) {
        const agent = this.agents.find(a => a.name === name);
        if (!agent) return;

        try {
            const action = agent.status === 'active' ? 'stop' : 'start';
            const response = await fetch(`/api/agents/${name}/${action}`, { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                await this.loadAgents();
                this.renderStats();
                this.renderAgentCards();
                this.selectAgent(result.agent);
            }
        } catch (error) {
            console.error('Failed to toggle agent:', error);
        }
    }

    setupEventListeners() {
        // Additional event listeners can be added here
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        setInterval(() => {
            this.loadAgents().then(() => {
                this.renderStats();
                if (this.selectedAgent) {
                    const updated = this.agents.find(a => a.name === this.selectedAgent.name);
                    if (updated) {
                        this.selectAgent(updated);
                    }
                }
            });
        }, 30000);
    }
}

const dashboard = new Dashboard();
