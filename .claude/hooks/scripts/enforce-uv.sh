#!/bin/bash
# enforce-uv.sh
# uvを使用するように強制するフック

# ログファイルの設定
LOG_FILE="/tmp/enforce_uv_hook.log"
echo "[$(date)] Hook executed" >> "$LOG_FILE"

input=$(cat)
echo "[$(date)] Input received: $input" >> "$LOG_FILE"

# デバッグログ（stderrに出力）
echo "[DEBUG] Hook triggered at $(date)" >&2
echo "[DEBUG] Input received: $input" >&2

# Validate input
if [ -z "$input" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi

# Extract fields with error handling
tool_name=$(echo "$input" | jq -r '.tool_name' 2>/dev/null || echo "")
command=$(echo "$input" | jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null || echo "")
current_dir=$(pwd)

# デバッグ: 抽出した値を表示
echo "[DEBUG] tool_name: $tool_name" >&2
echo "[DEBUG] command: $command" >&2

# ===== pip関連コマンド =====
if [[ "$tool_name" == "Bash" ]]; then
  echo "[DEBUG] Bash tool detected, checking command..." >&2
  
  # 早期チェック: pipコマンドを最優先でブロック
  if [[ "$command" =~ pip ]] || [[ "$command" =~ pip3 ]]; then
    echo "[DEBUG] pip command detected in: $command" >&2
    
    # python -m pip形式のチェック
    if [[ "$command" =~ python.*-m.*pip ]]; then
      echo "[DEBUG] python -m pip format detected" >&2
      echo '{
        "decision": "block",
        "reason": "⛔ pipの直接使用は禁止されています\\n\\n✅ uvを使用してください:\\n• インストール: uv add <package>\\n• アンインストール: uv remove <package>\\n• 一覧表示: uv tree\\n\\n💡 uvはPythonプロジェクト管理を簡素化します"
      }'
      exit 0
    fi
  fi
  
  echo "[DEBUG] Checking command patterns..." >&2
  case "$command" in
    pip\ *|pip3\ *)
      # pipコマンドの詳細な解析
      pip_cmd=$(echo "$command" | sed -E 's/^pip[0-9]? *//' | xargs)
      
      case "$pip_cmd" in
        install\ *)
          packages=$(echo "$pip_cmd" | sed 's/install//' | sed 's/--[^ ]*//g' | xargs)
          
          # -r requirements.txt
          if [[ "$pip_cmd" =~ -r\ .*\.txt ]]; then
            req_file=$(echo "$pip_cmd" | sed -n 's/.*-r \([^ ]*\).*/\1/p')
            echo "{
              \"decision\": \"block\",
              \"reason\": \"📋 requirements.txtからインストール:\\n\\n✅ 推奨方法:\\nuv add -r $req_file\\n\\nこれにより:\\n• requirements.txt内のすべての依存関係をpyproject.tomlに追加\\n• uv.lockファイルを自動生成/更新\\n• 仮想環境を自動的に同期\\n\\n💡 制約ファイルがある場合:\\nuv add -r $req_file -c constraints.txt\\n\\n📌 注意: この方法が最も確実で、バージョン指定も正しく処理されます\"
            }"
            exit 0
          fi
          
          # 開発依存関係
          if [[ "$pip_cmd" =~ --dev ]] || [[ "$pip_cmd" =~ -e ]]; then
            echo "{
              \"decision\": \"block\",
              \"reason\": \"🔧 開発依存関係をインストール:\\n\\nuv add --dev $packages\\n\\n編集可能インストール: uv add -e .\"
            }"
            exit 0
          fi
          
          # 通常のインストール
          echo "{
            \"decision\": \"block\",
            \"reason\": \"📦 パッケージをインストール:\\n\\nuv add $packages\\n\\n💾 'uv add' はpyproject.tomlに依存関係を保存します\\n🔒 uv.lockで再現可能な環境を保証\\n\\n💡 特殊なケース:\\n• URLからのインストール: パッケージを手動でダウンロードしてから追加\\n• 開発版: uv add --dev $packages\\n• ローカルパッケージ: uv add -e ./path/to/package\"
          }"
          exit 0
          ;;
        
        uninstall\ *)
          packages=$(echo "$pip_cmd" | sed 's/uninstall//' | sed 's/-y//g' | xargs)
          echo "{
            \"decision\": \"block\",
            \"reason\": \"🗑️ パッケージを削除:\\n\\nuv remove $packages\\n\\n✨ 依存関係も自動的にクリーンアップされます\"
          }"
          exit 0
          ;;
        
        list*|freeze*)
          echo '{
            "decision": "block",
            "reason": "📊 パッケージ一覧を確認:\n\n• プロジェクト依存関係: cat pyproject.toml\n• ロックファイル詳細: cat uv.lock\n• インストール済み一覧: uv tree\n• requirements.txt形式でエクスポート: uv export --format requirements-txt\n\n💡 'uv tree'はプロジェクトの依存関係ツリーを表示します"
          }'
          exit 0
          ;;
        
        *)
          # その他のpipコマンド（show, check, etc.）
          echo "{
            \"decision\": \"block\",
            \"reason\": \"🔀 pipコマンドをuvで実行:\\n\\nuv $pip_cmd\\n\\n💡 パッケージのインストール/削除には 'uv add/remove' を使用してください\"
          }"
          exit 0
          ;;
      esac
      ;;
    
    # ===== 直接的なPython実行の処理 =====
    python*\ -m\ pip*|python3*\ -m\ pip*)
      echo "[DEBUG] Direct python -m pip detected" >&2
      echo '{
        "decision": "block",
        "reason": "⛔ python -m pipの使用は禁止されています\\n\\n✅ uvを使用してください:\\n• インストール: uv add <package>\\n• アンインストール: uv remove <package>\\n• 一覧表示: uv tree\\n\\n💡 uvはPythonプロジェクト管理を簡素化します"
      }'
      exit 0
      ;;
    
    python*|python3*|py\ *)
      # 通常のuvへの変換
      args=$(echo "$command" | sed -E 's/^python[0-9]? //' | xargs)
      
      # -m オプションの特別処理
      if [[ "$args" =~ ^-m ]]; then
        module=$(echo "$args" | sed 's/-m //')
        
        case "$module" in
          pip\ *)
            pip_cmd=$(echo "$module" | sed 's/pip //')
            # Parse pip install commands
            if [[ "$pip_cmd" =~ ^install ]]; then
              packages=$(echo "$pip_cmd" | sed 's/install//' | sed 's/--[^ ]*//g' | xargs)
              if [[ "$pip_cmd" =~ -r\ .*\.txt ]]; then
                req_file=$(echo "$pip_cmd" | sed -n 's/.*-r \([^ ]*\).*/\1/p')
                echo "{
                  \"decision\": \"block\",
                  \"reason\": \"📋 requirements.txtからインストール:\\n\\n✅ 推奨方法:\\nuv add -r $req_file\\n\\n💡 これによりすべての依存関係がpyproject.tomlに追加されます\"
                }"
              else
                echo "{
                  \"decision\": \"block\",
                  \"reason\": \"📦 パッケージをインストール:\\n\\nuv add $packages\\n\\n💡 'uv add' はpyproject.tomlに依存関係を保存します\"
                }"
              fi
            else
              echo "{
                \"decision\": \"block\",
                \"reason\": \"🔀 pipコマンドをuvで実行:\\n\\nuv $pip_cmd\\n\\n💡 パッケージ管理には 'uv add/remove' を使用してください\"
              }"
            fi
            exit 0
            ;;
          *)
            echo "{
              \"decision\": \"block\",
              \"reason\": \"uvでモジュールを実行:\\n\\nuv run python -m $module\\n\\n🔄 uvは自動的に環境を同期してから実行します。\"
            }"
            exit 0
            ;;
        esac
      fi
      
      # 基本的なPython実行
      echo "{
        \"decision\": \"block\",
        \"reason\": \"uvでPythonを実行:\\n\\nuv run python $args\\n\\n✅ 仮想環境のアクティベーションは不要です！\"
      }"
      exit 0
      ;;
  esac
fi

# デフォルトは承認
echo '{"decision": "approve"}'