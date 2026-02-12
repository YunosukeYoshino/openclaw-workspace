// Dashboard Application

class Dashboard {
    constructor() {
        this.agents = [];
        this.logs = [];
        this.settings = {};
        this.selectedAgent = null;
        this.init();
    }

    async init() {
        await Promise.all([
            this.loadAgents(),
            this.loadLogs(),
            this.loadSettings(),
            this.loadActivityData(),
            this.loadAgentGraph()
        ]);
        this.renderStats();
        this.renderAgentCards();
        this.renderCharts();
        this.renderLogs();
        this.renderAgentGraph();
        this.renderSettings();
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

    async loadLogs() {
        try {
            const response = await fetch('/api/logs?limit=20');
            this.logs = await response.json();
        } catch (error) {
            console.error('Failed to load logs:', error);
            this.logs = [];
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            this.settings = await response.json();
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.settings = {
                theme: 'dark',
                refresh_interval: '30',
                log_level: 'info',
                notifications_enabled: 'true'
            };
        }
    }

    async loadActivityData() {
        try {
            const response = await fetch('/api/activity/chart');
            this.activityData = await response.json();
        } catch (error) {
            console.error('Failed to load activity data:', error);
            this.activityData = [];
        }
    }

    async loadAgentGraph() {
        try {
            const response = await fetch('/api/agents/graph');
            this.agentGraph = await response.json();
        } catch (error) {
            console.error('Failed to load agent graph:', error);
            this.agentGraph = { nodes: [], edges: [] };
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

    renderLogs() {
        const container = document.getElementById('logs-container');
        container.innerHTML = '';

        if (this.logs.length === 0) {
            container.innerHTML = '<p class="empty-state">ログがありません</p>';
            return;
        }

        this.logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry log-${log.level.toLowerCase()}`;

            const timestamp = new Date(log.timestamp).toLocaleString('ja-JP');
            logEntry.innerHTML = `
                <span class="log-timestamp">${timestamp}</span>
                <span class="log-level">[${log.level.toUpperCase()}]</span>
                <span class="log-agent">${log.agent}</span>
                <span class="log-message">${log.message}</span>
            `;

            container.appendChild(logEntry);
        });
    }

    renderAgentGraph() {
        const canvas = document.createElement('canvas');
        const container = document.getElementById('agent-graph');
        container.innerHTML = '';
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        canvas.width = container.clientWidth || 800;
        canvas.height = 400;

        // ノードの描画
        const nodes = this.agentGraph.nodes || [];
        const edges = this.agentGraph.edges || [];

        // ノードの位置を計算（簡易レイアウト）
        const positions = {};
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        nodes.forEach((node, index) => {
            const angle = (2 * Math.PI * index) / nodes.length;
            const radius = Math.min(canvas.width, canvas.height) / 3;
            positions[node.id] = {
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        });

        // エッジを描画
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 2;
        edges.forEach(edge => {
            const from = positions[edge.source];
            const to = positions[edge.target];
            if (from && to) {
                ctx.beginPath();
                ctx.moveTo(from.x, from.y);
                ctx.lineTo(to.x, to.y);
                ctx.stroke();
            }
        });

        // ノードを描画
        nodes.forEach(node => {
            const pos = positions[node.id];
            if (!pos) return;

            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 20, 0, 2 * Math.PI);

            // ノードタイプによって色を変える
            if (node.type === 'controller') {
                ctx.fillStyle = '#8b5cf6';
            } else {
                ctx.fillStyle = '#3b82f6';
            }
            ctx.fill();
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 2;
            ctx.stroke();

            // ラベル
            ctx.fillStyle = '#f1f5f9';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(node.label, pos.x, pos.y + 35);
        });
    }

    renderSettings() {
        document.getElementById('theme').value = this.settings.theme || 'dark';
        document.getElementById('refresh-interval').value = this.settings.refresh_interval || '30';
        document.getElementById('log-level').value = this.settings.log_level || 'info';
    }

    async saveSettings() {
        const theme = document.getElementById('theme').value;
        const refreshInterval = document.getElementById('refresh-interval').value;
        const logLevel = document.getElementById('log-level').value;

        try {
            await Promise.all([
                fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'theme', value: theme })
                }),
                fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'refresh_interval', value: refreshInterval })
                }),
                fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'log_level', value: logLevel })
                })
            ]);
            alert('設定を保存しました');
        } catch (error) {
            console.error('Failed to save settings:', error);
            alert('設定の保存に失敗しました');
        }
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
                this.renderCharts();
                this.selectAgent(result.agent);
            }
        } catch (error) {
            console.error('Failed to toggle agent:', error);
        }
    }

    setupEventListeners() {
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
    }

    startAutoRefresh() {
        const refreshInterval = (parseInt(this.settings.refresh_interval) || 30) * 1000;

        setInterval(async () => {
            await Promise.all([
                this.loadAgents(),
                this.loadLogs()
            ]);
            this.renderStats();
            this.renderLogs();
            if (this.selectedAgent) {
                const updated = this.agents.find(a => a.name === this.selectedAgent.name);
                if (updated) {
                    this.selectAgent(updated);
                }
            }
        }, refreshInterval);
    }
}

const dashboard = new Dashboard();


    renderCharts() {
        this.renderStatusChart();
    }

    renderStatusChart() {
        const ctx = document.getElementById('statusChart');
        if (!ctx) return;

        // 既存のチャートを破棄
        if (this.statusChart) {
            this.statusChart.destroy();
        }

        const active = this.agents.filter(a => a.status === 'active').length;
        const inactive = this.agents.filter(a => a.status === 'inactive').length;
        const error = this.agents.filter(a => a.status === 'error').length;

        this.statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['稼働中', '停止中', 'エラー'],
                datasets: [{
                    data: [active, inactive, error],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(148, 163, 184, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderColor: [
                        'rgba(16, 185, 129, 1)',
                        'rgba(148, 163, 184, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f1f5f9',
                            padding: 20,
                            font: {
                                size: 14
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'エージェントステータス分布',
                        color: '#f1f5f9',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: {
                            bottom: 20
                        }
                    }
                }
            }
        });
    }
