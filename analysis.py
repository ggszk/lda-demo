import pandas as pd
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import json
from wordcloud import WordCloud
from collections import Counter
import base64
from io import BytesIO
import requests
import os
import platform
import matplotlib.pyplot as plt

def analyze_receipt_data(n_topics=5):
    """レシートデータを分析して、支店ごとの買い物トピックを見つける
    
    Args:
        n_topics (int): 分析するトピック数（デフォルト: 5）
    """
    
    print(f"📊 レシートデータの分析を開始します（{n_topics}トピックで分析）...")
    
    # 1. データを読み込み
    df = pd.read_csv('レシートデータ.csv')
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
    
    # 6. 結果を返す（ファイル保存はしない）
    results = {
        'topics': topics_info,
        'stores': store_analysis,
        'summary': {
            'total_receipts': len(df),
            'total_products': len(feature_names),
            'n_topics': n_topics
        }
    }
    
    print(f"\n✅ 分析完了！結果を返します")
    return results


def generate_store_wordclouds():
    """支店別ワードクラウドを生成する
    
    Returns:
        dict: 各支店のワードクラウド画像（Base64エンコード）
    """
    print("📊 支店別ワードクラウドを生成中...")
    
    # データを読み込み
    df = pd.read_csv('レシートデータ.csv')
    
    # 支店の順序を固定（グラフと同じ順序）
    stores = ['中央区', '北区', '東区', '西区']
    store_wordclouds = {}
    
    for store in stores:
        # 各支店のデータをフィルタリング
        store_data = df[df['支店'] == store]
        
        # 購入商品を結合してテキストを作成
        all_products = ' '.join(store_data['購入商品'].astype(str))
        
        # 商品の出現回数をカウント
        products_list = all_products.split()
        product_counts = Counter(products_list)
        
        # 日本語フォントパスを取得
        japanese_font_path = get_japanese_font_path()
        
        # ワードクラウドを生成（日本語対応）
        wordcloud = WordCloud(
            font_path=japanese_font_path,
            width=250,  # サイズを小さく
            height=150,
            background_color='white',
            max_words=30,  # 単語数を減らす
            colormap='viridis',
            prefer_horizontal=0.9  # 水平テキストを優先
        ).generate_from_frequencies(product_counts)
        
        # 画像をBase64エンコード（最適化）
        img_buffer = BytesIO()
        # matplotlibを使わずにPillowで直接保存
        wordcloud_image = wordcloud.to_image()
        wordcloud_image.save(img_buffer, format='PNG', optimize=True)
        
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        store_wordclouds[store] = {
            'image': f'data:image/png;base64,{img_base64}',
            'product_count': len(product_counts),
            'top_products': list(product_counts.most_common(10))
        }
        
        print(f"✅ {store}店のワードクラウドを生成（{len(product_counts)}種類の商品）")
    
    return store_wordclouds


def download_japanese_font():
    """クラウド環境用：Google FontsからNoto Sans JPをダウンロード
    
    Returns:
        str: ダウンロードしたフォントのパス、またはNone
    """
    font_path = "/tmp/NotoSansJP-Regular.ttf"
    
    # 既にダウンロード済みの場合はそのまま使用
    if os.path.exists(font_path):
        print(f"✅ キャッシュされた日本語フォントを使用: {font_path}")
        return font_path
    
    try:
        print("🔄 Google FontsからNoto Sans JPをダウンロード中...")
        # GitHubのGoogle Fontsリポジトリからダウンロード
        font_url = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
        
        response = requests.get(font_url, timeout=30)
        response.raise_for_status()
        
        # /tmpディレクトリがない場合は作成
        os.makedirs("/tmp", exist_ok=True)
        
        with open(font_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 日本語フォントダウンロード完了: {font_path}")
        return font_path
        
    except Exception as e:
        print(f"⚠️ フォントダウンロード失敗: {e}")
        return None


def get_japanese_font_path():
    """環境に応じた日本語フォントのパスを取得
    
    Returns:
        str: 日本語フォントのパス、またはNone
    """
    # 1. クラウド環境（Render等）用: Google Fontsからダウンロード
    cloud_font = download_japanese_font()
    if cloud_font and os.path.exists(cloud_font):
        return cloud_font
    
    # 2. ローカル環境用: システムフォントを探す
    system_fonts = []
    
    if platform.system() == 'Darwin':  # macOS
        system_fonts = [
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/ヒラギノ角ゴ ProN W3.ttc',
            '/Library/Fonts/Arial Unicode MS.ttf',
            '/System/Library/Fonts/Apple Gothic.ttf'
        ]
    elif platform.system() == 'Linux':
        system_fonts = [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
    elif platform.system() == 'Windows':
        system_fonts = [
            'C:/Windows/Fonts/msgothic.ttc',
            'C:/Windows/Fonts/meiryo.ttc',
            'C:/Windows/Fonts/arial.ttf'
        ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            print(f"✅ システム日本語フォントを発見: {font_path}")
            return font_path
    
    print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。")
    return None


if __name__ == "__main__":
    import sys
    # コマンドライン引数でトピック数指定可能
    n_topics = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"🎯 {n_topics}トピックで分析を実行します")
    analyze_receipt_data(n_topics)