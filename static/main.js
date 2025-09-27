let currentChart = null;

async function runAnalysis() {
    const topicCount = document.getElementById('topicCount').value;
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // UI状態を更新
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '分析中...';
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        // タイムアウト付きfetch
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒タイムアウト
        
        const response = await fetch(`/analyze?topics=${topicCount}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            console.error('サーバーエラー:', data);
            alert(`分析エラー: ${data.error || '不明なエラー'}`);
        }
    } catch (error) {
        console.error('クライアントエラー:', error);
        if (error.name === 'AbortError') {
            alert('分析がタイムアウトしました。しばらく待ってから再試行してください。');
        } else {
            alert(`エラーが発生しました: ${error.message}`);
        }
    } finally {
        // UI状態を元に戻す
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 分析開始！';
        loading.style.display = 'none';
    }
}

function displayResults(data) {
    const results = document.getElementById('results');
    
    // サマリー情報を表示
    displaySummary(data.summary);
    
    // トピック情報を表示
    displayTopics(data.topics);
    
    // グラフを表示
    displayChart(data);
    
    // ワードクラウドを表示
    displayWordclouds(data.store_wordclouds);
    
    // インサイトを表示
    displayInsights(data);
    
    results.style.display = 'block';
}

function displaySummary(summary) {
    const summaryInfo = document.getElementById('summaryInfo');
    summaryInfo.innerHTML = `
        <p><strong>📋 分析対象:</strong> ${summary.total_receipts}件のレシート</p>
        <p><strong>🛍️ 商品種類:</strong> ${summary.total_products}種類</p>
        <p><strong>🎯 分析トピック数:</strong> ${summary.n_topics}トピック</p>
    `;
}

function displayTopics(topics) {
    const topicsInfo = document.getElementById('topicsInfo');
    topicsInfo.innerHTML = topics.map(topic => `
        <div class="topic-card">
            <h4>${topic.topic_name}</h4>
            <div class="products">主な商品: ${topic.top_products.join(', ')}</div>
        </div>
    `).join('');
}

function displayChart(data) {
    const ctx = document.getElementById('storeChart').getContext('2d');
    
    // 既存のチャートがあれば削除
    if (currentChart) {
        currentChart.destroy();
    }
    
    const stores = Object.keys(data.stores);
    const topics = data.topics;
    
    // データセットを準備
    const datasets = topics.map((topic, index) => ({
        label: topic.topic_name,
        data: stores.map(store => (data.stores[store].topic_ratios[index] * 100).toFixed(1)),
        backgroundColor: getTopicColor(index),
        borderColor: getTopicColor(index, 0.8),
        borderWidth: 2
    }));
    
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stores,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '支店別トピック分布（%）',
                    font: { size: 16 }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '支店'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '割合（%）'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

function displayInsights(data) {
    const insights = document.getElementById('insights');
    const stores = Object.keys(data.stores);
    const topics = data.topics;
    
    let insightsList = [];
    
    // 各支店で最も特徴的なトピックを見つける
    stores.forEach(store => {
        const ratios = data.stores[store].topic_ratios;
        const maxIndex = ratios.indexOf(Math.max(...ratios));
        const maxRatio = (ratios[maxIndex] * 100).toFixed(1);
        
        insightsList.push(`
            <div class="insight-item">
                <strong>${store}店</strong>は<strong>${topics[maxIndex].topic_name}</strong>が最も多く、
                全体の<strong>${maxRatio}%</strong>を占めています
            </div>
        `);
    });
    
    // トピック別で最も特徴的な支店を見つける
    topics.forEach((topic, topicIndex) => {
        const storeRatios = stores.map(store => ({
            store: store,
            ratio: data.stores[store].topic_ratios[topicIndex]
        }));
        
        const maxStore = storeRatios.reduce((max, current) => 
            current.ratio > max.ratio ? current : max
        );
        
        const maxRatio = (maxStore.ratio * 100).toFixed(1);
        
        insightsList.push(`
            <div class="insight-item">
                <strong>${topic.topic_name}</strong>は<strong>${maxStore.store}店</strong>で最も多く、
                <strong>${maxRatio}%</strong>の割合です
            </div>
        `);
    });
    
    insights.innerHTML = insightsList.join('');
}

function displayWordclouds(wordclouds) {
    const container = document.getElementById('wordcloudsContainer');
    
    if (!wordclouds || Object.keys(wordclouds).length === 0) {
        container.innerHTML = '<div class="error-message">ワードクラウドデータがありません</div>';
        return;
    }
    
    console.log('ワードクラウドデータ:', wordclouds);
    
    // 支店の順序を固定（グラフと同じ順序）
    const storeOrder = ['中央区', '北区', '東区', '西区'];
    
    container.innerHTML = storeOrder.map(store => {
        const data = wordclouds[store];
        if (!data) return '';
        
        return `
            <div class="wordcloud-card">
                <h4>${store}店</h4>
                <div class="wordcloud-image">
                    <img src="${data.image}" alt="${store}店のワードクラウド" />
                </div>
                <div class="wordcloud-info">
                    <p><strong>商品種類:</strong> ${data.product_count}種類</p>
                    <p><strong>上位3商品:</strong> ${data.top_products.slice(0, 3).map(item => item[0]).join(', ')}</p>
                </div>
            </div>
        `;
    }).join('');
}

function getTopicColor(index, alpha = 0.6) {
    const colors = [
        `rgba(239, 68, 68, ${alpha})`,   // 赤
        `rgba(34, 197, 94, ${alpha})`,   // 緑
        `rgba(59, 130, 246, ${alpha})`,  // 青
        `rgba(245, 158, 11, ${alpha})`,  // オレンジ
        `rgba(168, 85, 247, ${alpha})`,  // 紫
        `rgba(236, 72, 153, ${alpha})`,  // ピンク
        `rgba(14, 165, 233, ${alpha})`,  // 水色
        `rgba(132, 204, 22, ${alpha})`,  // ライム
        `rgba(251, 113, 133, ${alpha})`, // ローズ
        `rgba(156, 163, 175, ${alpha})`  // グレー
    ];
    return colors[index % colors.length];
}

// ページ読み込み時の処理（保存機能無効化のため削除）
window.addEventListener('DOMContentLoaded', async () => {
    console.log('アプリが読み込まれました。「🔍 分析開始！」ボタンで分析を開始してください。');
    // 複数ユーザー対応のため、保存された結果の読み込みは無効化
});