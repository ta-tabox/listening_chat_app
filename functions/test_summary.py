#!/usr/bin/env python3
"""
要約機能のテストスクリプト
12件の履歴を作成して要約機能が正しく動作するかテストする
"""

import requests
import json

API_URL = "http://localhost:8080"

def test_summary_creation():
    """10件の履歴で要約が作成されることをテスト"""

    print("=" * 80)
    print("要約機能テスト開始")
    print("=" * 80)

    # 10件の履歴を作成（user + model で5往復 = 10件）
    history = []

    # 1往復目
    history.append({"role": "user", "parts": [{"text": "最近、仕事で悩んでいます"}]})
    history.append({"role": "model", "parts": [{"text": "そうなんですね。どのようなことで悩んでいるのか、お聞かせいただけますか？"}]})

    # 2往復目
    history.append({"role": "user", "parts": [{"text": "上司との関係がうまくいっていないんです"}]})
    history.append({"role": "model", "parts": [{"text": "上司との関係で困っているのですね。それは辛いですね。"}]})

    # 3往復目
    history.append({"role": "user", "parts": [{"text": "コミュニケーションがうまく取れなくて"}]})
    history.append({"role": "model", "parts": [{"text": "コミュニケーションの難しさを感じているのですね。"}]})

    # 4往復目
    history.append({"role": "user", "parts": [{"text": "自分の意見を言うのが怖いです"}]})
    history.append({"role": "model", "parts": [{"text": "意見を言うことに恐怖を感じているのですね。"}]})

    # 5往復目（これで10件）
    history.append({"role": "user", "parts": [{"text": "否定されるのが怖くて"}]})
    history.append({"role": "model", "parts": [{"text": "否定されることへの不安があるのですね。"}]})

    print(f"\n履歴件数: {len(history)}件")
    print("\n履歴が10件に達したので、次のメッセージで要約が作成されるはずです。")

    # 11件目のメッセージを送信（これで要約が作成される）
    payload = {
        "message": "どうしたらいいでしょうか",
        "history": history
    }

    print("\n" + "=" * 80)
    print("リクエスト送信中...")
    print("=" * 80)

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        result = response.json()

        print("\n✅ リクエスト成功!")
        print(f"\nレスポンス: {result['response']}")
        print(f"\n返却された履歴件数: {len(result.get('history', []))}件")

        if 'summary' in result:
            print("\n✅ 要約が作成されました!")
            print(f"\n要約内容:\n{result['summary']}")
            print(f"\n履歴は最新{len(result['history'])}件のみが残っています（期待値: 2件）")

            if len(result['history']) == 2:
                print("\n✅ テスト成功: 履歴が正しく2件に削減されました")
            else:
                print(f"\n❌ テスト失敗: 履歴が{len(result['history'])}件です（期待値: 2件）")
        else:
            print("\n❌ 要約が作成されていません")

        # 次のリクエストで要約の統合をテスト
        print("\n" + "=" * 80)
        print("要約統合のテスト")
        print("=" * 80)

        # さらに4往復（8件）追加して、再度10件に達するようにする
        new_history = result['history']
        summary = result.get('summary')

        for i in range(4):
            new_history.append({"role": "user", "parts": [{"text": f"追加メッセージ{i+1}"}]})
            new_history.append({"role": "model", "parts": [{"text": f"応答{i+1}"}]})

        print(f"\n現在の履歴件数: {len(new_history)}件（期待値: 10件 = 元の2件 + 新規8件）")

        # 11件目のメッセージを送信
        payload2 = {
            "message": "さらに話を続けます",
            "history": new_history,
            "summary": summary
        }

        print("\n2回目のリクエスト送信中...")

        response2 = requests.post(API_URL, json=payload2)

        if response2.status_code == 200:
            result2 = response2.json()

            print("\n✅ 2回目のリクエスト成功!")
            print(f"\n返却された履歴件数: {len(result2.get('history', []))}件")

            if 'summary' in result2:
                print("\n✅ 要約が更新されました!")
                print(f"\n更新された要約:\n{result2['summary']}")

                if result2['summary'] != summary:
                    print("\n✅ 要約が既存の要約と統合されました")
                else:
                    print("\n⚠️  要約が更新されていない可能性があります")

                if len(result2['history']) == 2:
                    print("\n✅ テスト成功: 履歴が再び2件に削減されました")
                else:
                    print(f"\n❌ テスト失敗: 履歴が{len(result2['history'])}件です（期待値: 2件）")
            else:
                print("\n❌ 要約が含まれていません")
        else:
            print(f"\n❌ 2回目のリクエスト失敗: {response2.status_code}")
            print(response2.text)
    else:
        print(f"\n❌ リクエスト失敗: {response.status_code}")
        print(response.text)

    print("\n" + "=" * 80)
    print("テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_summary_creation()
