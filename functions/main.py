import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
import os
from flask import jsonify
import json

# プロジェクト設定
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
LOCATION = os.environ.get('GCP_LOCATION', 'us-central1')

# Vertex AI初期化
vertexai.init(project=PROJECT_ID, location=LOCATION)

# システムプロンプト（傾聴に特化）
SYSTEM_INSTRUCTION = """
あなたは優れた傾聴者です。以下の原則に従って対話してください：

1. 相手の気持ちに寄り添い、共感的に応答する
2. 相手の話を遮らず、じっくりと聞く姿勢を示す
3. 安易なアドバイスや解決策を押し付けない
4. 相手の感情を言語化し、理解を深める手助けをする
5. 温かく、受容的な態度を保つ
6. 相手のペースを尊重する

相手が抱える悩みや不安に気づき、それを言葉にするきっかけを提供してください。
"""

@functions_framework.http
def chat(request):
    """
    チャットエンドポイント
    """
    # CORS設定
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        # リクエストボディ取得
        request_json = request.get_json(silent=True)

        if not request_json or 'message' not in request_json:
            return jsonify({'error': 'メッセージが必要です'}), 400, headers

        user_message = request_json['message']
        chat_history_json = request_json.get('history', [])
        conversation_summary = request_json.get('summary', None)

        # 履歴をContentオブジェクトに変換
        chat_history = []
        for msg in chat_history_json:
            parts = [Part.from_text(part['text']) for part in msg['parts']]
            chat_history.append(Content(role=msg['role'], parts=parts))

        # システムプロンプトに要約を含める
        system_prompt = SYSTEM_INSTRUCTION
        if conversation_summary:
            system_prompt += f"\n\n【これまでの会話の要約】\n{conversation_summary}"

        # Geminiモデル初期化
        model = GenerativeModel(
            "gemini-2.5-flash-lite",
            system_instruction=system_prompt
        )

        # チャット履歴を含めてセッション作成
        chat = model.start_chat(history=chat_history)

        # メッセージ送信
        response = chat.send_message(user_message)

        # 履歴をJSON化可能な形式に変換
        history_json = []
        for content in chat.history:
            history_json.append({
                'role': content.role,
                'parts': [{'text': part.text} for part in content.parts]
            })

        # 履歴数を制限してコスト最適化
        # - AI応答後の履歴が10件以上の場合、最古の10件を要約
        # - 要約後は直近2件のみを履歴として保持
        # - 結果: 要約 + 直近2件の履歴でコンテキストを維持
        ITEMS_TO_SUMMARIZE = 10  # 要約を作成する履歴の件数

        if len(history_json) >= ITEMS_TO_SUMMARIZE:
            # 最古の10件を要約対象、残りを保持
            messages_to_summarize = history_json[:ITEMS_TO_SUMMARIZE]
            history_json = history_json[ITEMS_TO_SUMMARIZE:]

            # 要約の作成または更新
            summary_model = GenerativeModel("gemini-2.5-flash-lite")

            if not conversation_summary:
                # 初回の要約作成
                summary_prompt = f"""以下の会話履歴を簡潔に要約してください。ユーザーが話した主な内容と、その背景にある感情や状況を中心にまとめてください。

会話履歴:
{chr(10).join([f"{'ユーザー' if msg['role'] == 'user' else 'AI'}: {msg['parts'][0]['text']}" for msg in messages_to_summarize])}

要約（200文字以内）:"""
            else:
                # 既存の要約と新しい履歴を統合
                summary_prompt = f"""以下の「これまでの要約」と「新しい会話履歴」を統合して、ユーザーが話した主な内容と、その背景にある感情や状況を簡潔にまとめてください。

【これまでの要約】
{conversation_summary}

【新しい会話履歴】
{chr(10).join([f"{'ユーザー' if msg['role'] == 'user' else 'AI'}: {msg['parts'][0]['text']}" for msg in messages_to_summarize])}

統合された要約（200文字以内）:"""

            summary_response = summary_model.generate_content(summary_prompt)
            conversation_summary = summary_response.text

        # レスポンス返却
        result = {
            'response': response.text,
            'history': history_json
        }

        # 要約がある場合は含める
        if conversation_summary:
            result['summary'] = conversation_summary

        return jsonify(result), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500, headers
