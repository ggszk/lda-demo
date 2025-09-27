import pandas as pd
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import json

def analyze_receipt_data(n_topics=5):
    """レシートデータを分析して、支店ごとの買い物トピックを見つける
    
    Args:
        n_topics (int): 分析するトピック数（デフォルト: 5）
    """
    
    print(f"📊 レシートデータの分析を開始します（{n_topics}トピックで分析）...")
    
    # 1. データを読み込み
    df = pd.read_csv('レシートデータ_v7_教育用.csv')
    print(f"✅ {len(df)}件のレシートデータを読み込みました")
    
    # 2. 商品名を数値データに変換
    vectorizer = CountVectorizer(
        token_pattern=r'\S+',  # スペース区切りで商品を分割
        min_df=2,              # 2回以上出現する商品のみ使用
        max_df=0.8             # 全体の80%以上で出現する商品は除外
    )
    
    X = vectorizer.fit_transform(df['購入商品'])
    feature_names = vectorizer.get_feature_names_out()
    print(f"✅ {len(feature_names)}種類の商品を分析対象にします")
    
    # 3. 買い物トピックを自動で見つける
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=20
    )
    
    # 各レシートがどのトピックに属するかの確率を計算
    topic_probs = lda.fit_transform(X)
    print(f"✅ {n_topics}つの買い物トピックを発見しました")
    
    # 4. 各トピックにどんな商品が含まれるかを分析
    topics_info = []
    for topic_idx, topic in enumerate(lda.components_):
        # 各トピックで重要な商品トップ5を取得
        top_words_idx = topic.argsort()[-5:][::-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics_info.append({
            'topic_name': f'トピック{topic_idx + 1}',
            'top_products': top_words
        })
        print(f"  {topics_info[-1]['topic_name']}: {', '.join(top_words)}")
    
    # 5. 支店ごとにトピックの割合を計算
    df_with_topics = df.copy()
    df_with_topics['topic_probs'] = list(topic_probs)
    
    store_analysis = {}
    stores = df['支店'].unique()
    
    for store in stores:
        store_data = df_with_topics[df_with_topics['支店'] == store]
        # この支店の全レシートでのトピック確率の平均を計算
        avg_topic_probs = np.mean([prob for prob in store_data['topic_probs']], axis=0)
        
        store_analysis[store] = {
            'receipt_count': len(store_data),
            'topic_ratios': avg_topic_probs.tolist()
        }
        
        print(f"\n🏪 {store}店の分析結果:")
        print(f"  レシート数: {len(store_data)}件")
        for i, ratio in enumerate(avg_topic_probs):
            print(f"  {topics_info[i]['topic_name']}: {ratio:.1%}")
    
    # 6. 結果をJSONファイルに保存
    results = {
        'topics': topics_info,
        'stores': store_analysis,
        'summary': {
            'total_receipts': len(df),
            'total_products': len(feature_names),
            'n_topics': n_topics
        }
    }
    
    with open('analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完了！結果をanalysis_results.jsonに保存しました")
    return results


if __name__ == "__main__":
    import sys
    # コマンドライン引数でトピック数指定可能
    n_topics = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"🎯 {n_topics}トピックで分析を実行します")
    analyze_receipt_data(n_topics)