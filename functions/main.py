import functions_framework
from google import genai
from google.genai import types as genai_types
import vertexai
from vertexai import types as vertexai_types
import os
from flask import jsonify
import json

# プロジェクト設定
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
PROMPT_ID = os.environ.get('SYSTEM_PROMPT_ID', None)

# Vertex AI Client初期化
vertex_client = vertexai.Client(project=PROJECT_ID, location=VERTEX_AI_LOCATION)

# Genai Client初期化（チャット用）
genai_client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=VERTEX_AI_LOCATION
)

# デフォルトのシステムプロンプト
DEFAULT_SYSTEM_INSTRUCTION = """あなたは優れた傾聴者です。以下の原則に従って対話してください：

1. 相手の気持ちに寄り添い、共感的に応答する
2. 相手の話を遮らず、じっくりと聞く姿勢を示す
3. 安易なアドバイスや解決策を押し付けない
4. 相手の感情を言語化し、理解を深める手助けをする
5. 温かく、受容的な態度を保つ
6. 相手のペースを尊重する

相手が抱える悩みや不安に気づき、それを言葉にするきっかけを提供してください。"""

def get_system_instruction():
    """Vertex AIからシステムプロンプトを取得"""
    if not PROMPT_ID:
        return DEFAULT_SYSTEM_INSTRUCTION

    try:
        prompt = vertex_client.prompts.get(prompt_id=PROMPT_ID)
        if prompt.prompt_data and prompt.prompt_data.system_instruction:
            parts = prompt.prompt_data.system_instruction.parts
            return parts[0].text if parts else DEFAULT_SYSTEM_INSTRUCTION
        return DEFAULT_SYSTEM_INSTRUCTION
    except Exception as e:
        print(f"Warning: プロンプト取得失敗。デフォルトを使用。Error: {str(e)}")
        return DEFAULT_SYSTEM_INSTRUCTION

@functions_framework.http
def get_prompt(request):
    """
    プロンプト取得エンドポイント
    """
    # CORS設定
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        system_instruction = get_system_instruction()
        return jsonify({'prompt': system_instruction}), 200, headers
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500, headers

@functions_framework.http
def update_prompt(request):
    """
    プロンプト更新エンドポイント
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
        request_json = request.get_json(silent=True)
        if not request_json or 'prompt' not in request_json:
            return jsonify({'error': 'プロンプトが必要です'}), 400, headers

        new_prompt_text = request_json['prompt']

        if not PROMPT_ID:
            return jsonify({'error': 'SYSTEM_PROMPT_IDが設定されていません'}), 400, headers

        # 既存のプロンプトを取得
        existing_prompt = vertex_client.prompts.get(prompt_id=PROMPT_ID)

        # 新しいプロンプトデータを作成
        updated_prompt = vertexai_types.Prompt(
            prompt_data=vertexai_types.PromptData(
                contents=existing_prompt.prompt_data.contents if existing_prompt.prompt_data else [],
                system_instruction=genai_types.Content(
                    parts=[genai_types.Part(text=new_prompt_text)]
                ),
                model=existing_prompt.prompt_data.model if existing_prompt.prompt_data else "gemini-2.5-flash-lite",
            ),
        )

        # 新しいバージョンを作成
        vertex_client.prompts.create_version(
            prompt=updated_prompt,
            prompt_id=PROMPT_ID
        )

        return jsonify({'success': True, 'message': 'プロンプトを更新しました'}), 200, headers

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'エラーが発生しました: {str(e)}'}), 500, headers

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

        # 履歴をgenai.types.Content形式に変換
        chat_history = []
        for msg in chat_history_json:
            chat_history.append(genai_types.Content(
                role=msg['role'],
                parts=[genai_types.Part(text=part['text']) for part in msg['parts']]
            ))

        # システムプロンプトを取得（Vertex AIまたはデフォルト）
        system_prompt = get_system_instruction()

        # 要約がある場合は追加
        if conversation_summary:
            system_prompt += f"\n\n【これまでの会話の要約】\n{conversation_summary}"

        # チャットセッションの設定
        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=1.0
        )

        # メッセージ送信（履歴を含む）
        contents = chat_history + [genai_types.Content(
            role='user',
            parts=[genai_types.Part(text=user_message)]
        )]

        response = genai_client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=contents,
            config=config
        )

        # 履歴を更新
        chat_history.append(genai_types.Content(
            role='user',
            parts=[genai_types.Part(text=user_message)]
        ))
        chat_history.append(genai_types.Content(
            role='model',
            parts=[genai_types.Part(text=response.text)]
        ))

        # 履歴をJSON化可能な形式に変換
        history_json = []
        for content in chat_history:
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

            summary_response = genai_client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=summary_prompt
            )
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
