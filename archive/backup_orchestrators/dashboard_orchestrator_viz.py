#!/usr/bin/env python3
"""
Dashboard Visualization - データ可視化機能の追加

Chart.jsを使って、ダッシュボードにグラフやチャートを追加します。
"""

import os
from pathlib import Path

DASHBOARD_DIR = "/workspace/dashboard"


def add_visualization():
    """データ可視化機能を追加"""
    print("📊 Adding visualization features...")

    # Chart.jsを追加したHTML
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agents Dashboard</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI Agents Dashboard</h1>
            <p class="subtitle">AIエージェント管理システム</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-agents">-</div>
                <div class="stat-label">総エージェント数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-agents">-</div>
                <div class="stat-label">稼働中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="inactive-agents">-</div>
                <div class="stat-label">停止中</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-agents">-</div>
                <div class="stat-label">エラー</div>
            </div>
        </div>

        <!-- チャートセクション -->
        <div class="charts-section">
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </div>

        <div class="main-content">
            <section class="agent-list">
                <h2>エージェント一覧</h2>
                <div id="agent-cards" class="agent-cards"></div>
            </section>

            <section class="agent-details">
                <h2>詳細情報</h2>
                <div id="detail-view" class="detail-view">
                    <p class="empty-state">エージェントを選択してください</p>
                </div>
            </section>
        </div>
    </div>

    <script src="/static/js/app.js"></script>
</body>
</html>
"""

    # CSSにチャートスタイルを追加
    css_path = Path(f"{DASHBOARD_DIR}/static/css/style.css")
    with open(css_path, 'r') as f:
        css_content = f.read()

    css_addition = """

/* Charts */
.charts-section {
    margin-bottom: 40px;
}

.chart-container {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #334155;
    max-width: 800px;
    margin: 0 auto;
}

.chart-container canvas {
    max-height: 300px;
}
"""

    with open(css_path, 'w') as f:
        f.write(css_content + css_addition)

    # JavaScriptにチャート機能を追加
    js_path = Path(f"{DASHBOARD_DIR}/static/js/app.js")
    with open(js_path, 'r') as f:
        js_content = f.read()

    # Dashboardクラスにチャート関連メソッドを追加
    chart_js_addition = """

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
"""

    # init()メソッドにチャートレンダリングを追加
    js_content = js_content.replace(
        "        this.renderAgentCards();\n        this.setupEventListeners();\n        this.startAutoRefresh();",
        "        this.renderAgentCards();\n        this.renderCharts();\n        this.setupEventListeners();\n        this.startAutoRefresh();"
    )

    # クラスの最後にメソッドを追加
    js_content = js_content.rstrip() + "\n" + chart_js_addition

    # autoRefreshメソッドにチャート更新を追加
    js_content = js_content.replace(
        "            this.renderStats();\n                this.renderAgentCards();",
        "            this.renderStats();\n                this.renderAgentCards();\n                this.renderCharts();"
    )

    with open(js_path, 'w') as f:
        f.write(js_content)

    # HTMLを更新
    with open(f"{DASHBOARD_DIR}/templates/index.html", 'w') as f:
        f.write(html_content)

    print("✅ Visualization features added")
    return True


def main():
    """メイン処理"""
    print("🎨 Dashboard Visualization Starting...")
    print()

    if add_visualization():
        print()
        print("=" * 50)
        print("✅ Visualization completed successfully!")
        print("=" * 50)
        print()
        print("Added features:")
        print("- Status distribution chart (doughnut chart)")
        print("- Chart.js integration")
        print("- Auto-refreshing charts")
        print()
        print("To view the dashboard:")
        print("1. cd /workspace/dashboard")
        print("2. python3 api.py")
        print("3. Open http://localhost:8000 in your browser")


if __name__ == "__main__":
    main()
