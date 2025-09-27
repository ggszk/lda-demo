from flask import Flask, render_template, jsonify, request
import json
import os
from analysis import analyze_receipt_data, generate_store_wordclouds

app = Flask(__name__)

@app.route('/')
def home():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    """データ分析を実行して結果を返す"""
    # URLパラメータからトピック数を取得（デフォルト: 5）
    n_topics = request.args.get('topics', 5, type=int)
    
    # トピック数の範囲チェック
    if n_topics < 2 or n_topics > 10:
        return jsonify({'error': 'トピック数は2-10の間で指定してください'}), 400
    
    try:
        # 分析実行
        results = analyze_receipt_data(n_topics)
        
        # 支店別ワードクラウドデータを追加
        results['store_wordclouds'] = generate_store_wordclouds()
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'分析エラー: {str(e)}'}), 500

@app.route('/results')
def get_results():
    """非推奨エンドポイント：リアルタイム分析を使用してください"""
    return jsonify({
        'error': 'この機能は無効化されています。「🔍 分析開始！」ボタンをクリックしてください。',
        'message': '複数ユーザーの同時使用に対応するため、保存機能を無効化しました。'
    }), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)