"""
Vertex AIにシステムプロンプトを作成するスクリプト
"""
import vertexai
from vertexai import types
from google.genai import types as genai_types

# プロジェクト設定
PROJECT_ID = "active-listening-chat-app"
LOCATION = "us-central1"

# Vertex AI初期化
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# デフォルトのシステムプロンプト
DEFAULT_SYSTEM_INSTRUCTION = """あなたは優れた傾聴者です。以下の原則に従って対話してください：

1. 相手の気持ちに寄り添い、共感的に応答する
2. 相手の話を遮らず、じっくりと聞く姿勢を示す
3. 安易なアドバイスや解決策を押し付けない
4. 相手の感情を言語化し、理解を深める手助けをする
5. 温かく、受容的な態度を保つ
6. 相手のペースを尊重する

相手が抱える悩みや不安に気づき、それを言葉にするきっかけを提供してください。"""

print("=== Vertex AI プロンプト作成スクリプト ===\n")

# プロンプトを作成
print("1. プロンプトを作成中...")
prompt = types.Prompt(
    prompt_data=types.PromptData(
        contents=[
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text="こんにちは")]
            )
        ],
        system_instruction=genai_types.Content(
            parts=[genai_types.Part(text=DEFAULT_SYSTEM_INSTRUCTION)]
        ),
        model="gemini-2.0-flash-lite",
    ),
)

print("2. Vertex AIにプロンプトリソースを保存中...")
try:
    prompt_resource = client.prompts.create(prompt=prompt)
    print(f"   ✓ プロンプトリソースが作成されました")
    print(f"   Prompt ID: {prompt_resource.prompt_id}")
    print(f"   Attributes: {dir(prompt_resource)}")

    print("\n3. 初期バージョンを作成中...")
    prompt_version_resource = client.prompts.create_version(
        prompt=prompt,
        prompt_id=prompt_resource.prompt_id
    )
    print(f"   ✓ バージョンが作成されました")
    print(f"   Version ID: {prompt_version_resource.version_id}")

    print("\n=== 完了 ===")
    print(f"\n環境変数に以下を設定してください:")
    print(f"SYSTEM_PROMPT_ID={prompt_resource.prompt_id}")

except Exception as e:
    print(f"   ✗ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()
