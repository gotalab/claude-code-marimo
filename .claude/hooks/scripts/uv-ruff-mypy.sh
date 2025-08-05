#!/bin/bash
# uv-ruff-mypy.sh
# Python ファイル編集時に自動的にRuffフォーマット・リント・型チェックを実行するフック

echo "🔵 [DEBUG] UV Ruff-Mypy hook started at $(date)" >&2

# Check if required commands are available
if ! command -v uv &> /dev/null || ! command -v jq &> /dev/null; then
    echo "⚠️ Ruff-Mypy check skipped: uv or jq not found"
    exit 0
fi

input=$(cat)
echo "🔵 [DEBUG] Received input: $input" >&2

# Validate input
if [ -z "$input" ]; then
  exit 0
fi

# Extract fields with error handling
tool_name=$(echo "$input" | jq -r '.tool_name // ""' 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$tool_name" ]; then
  exit 0
fi

file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$file_path" ]; then
  exit 0
fi

# Check if tool execution was successful
tool_success=$(echo "$input" | jq -r '.tool_response.success // true' 2>/dev/null)
if [ "$tool_success" = "false" ]; then
  error_msg=$(echo "$input" | jq -r '.tool_response.error // "Unknown error"' 2>/dev/null)
  cat <<EOF
{
  "decision": "block",
  "reason": "Tool execution failed: $error_msg\n\nPlease fix the issue and try again."
}
EOF
  exit 0
fi

# Only process Edit, Write, MultiEdit and Update tools
if [[ "$tool_name" != "Edit" && "$tool_name" != "Write" && "$tool_name" != "MultiEdit" && "$tool_name" != "Update" ]]; then
  exit 0
fi

# Check if it's a Python file
if [[ ! "$file_path" =~ \.py$ ]]; then
  exit 0
fi

# Validate path security - ensure file is within project directory
project_root=$(pwd)
real_file_path=$(realpath "$file_path" 2>/dev/null)
if [[ -z "$real_file_path" ]] || [[ ! "$real_file_path" =~ ^"$project_root" ]]; then
  echo "⚠️ Ruff-Mypy check skipped: file path outside project directory"
  exit 0
fi

# Check if file exists
if [[ ! -f "$file_path" ]]; then
  exit 0
fi

# Check file size (skip large files > 1MB)
file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)
if [[ $file_size -gt 1048576 ]]; then
  echo "⚠️ Ruff-Mypy check skipped: file too large (>1MB)"
  exit 0
fi

echo "🎨 Step 1/3: Running Ruff format on $file_path..."

# Step 1: Ruff Format
ruff_format_output=$(uv run ruff format "$file_path" 2>&1)
ruff_format_exit_code=$?

if [[ $ruff_format_exit_code -ne 0 ]]; then
  cat <<EOF
{
  "decision": "block",
  "reason": "🚫 Ruff format failed for $file_path:\n\n$ruff_format_output\n\nPlease check the file syntax and try again."
}
EOF
  exit 0
fi

# Check if formatting was applied
if [[ "$ruff_format_output" == *"1 file reformatted"* ]]; then
  echo "✨ Ruff format applied changes"
else
  echo "✅ File was already properly formatted"
fi

echo "🔍 Step 2/3: Running Ruff lint check on $file_path..."

# Step 2: Ruff Check (with auto-fix)
ruff_check_output=$(uv run ruff check "$file_path" 2>&1)
ruff_check_exit_code=$?

if [[ $ruff_check_exit_code -ne 0 ]]; then
  # Try auto-fix
  echo "🔧 Attempting to auto-fix lint issues..."
  ruff_fix_output=$(uv run ruff check "$file_path" --fix --exit-zero 2>&1)
  
  # Check if any fixes were applied
  if [[ "$ruff_fix_output" == *"Found"*"violation"*"Fixed"* ]]; then
    echo "🔧 Ruff auto-fixes applied. Re-running lint check..."
    
    # Re-run check after fixes
    ruff_check_retry_output=$(uv run ruff check "$file_path" 2>&1)
    ruff_check_retry_exit_code=$?
    
    if [[ $ruff_check_retry_exit_code -ne 0 ]]; then
      cat <<EOF
{
  "decision": "block",
  "reason": "🚫 Some lint errors remain after auto-fix in $file_path:\n\n$ruff_check_retry_output\n\nManual intervention required. Fix these remaining lint errors and try again."
}
EOF
      exit 0
    fi
    echo "✅ Ruff lint check passed after auto-fix"
  else
    cat <<EOF
{
  "decision": "block",
  "reason": "🚫 Lint errors detected in $file_path:\n\n$ruff_check_output\n\nFix these lint errors and try again."
}
EOF
    exit 0
  fi
else
  echo "✅ Ruff lint check passed"
fi

echo "🔍 Step 3/3: Running mypy type check on $file_path..."

# Step 3: Mypy Type Check (strict settings)
mypy_output=$(uv run mypy "$file_path" --disallow-any-explicit --disallow-any-generics --disallow-any-unimported 2>&1)
mypy_exit_code=$?

if [[ $mypy_exit_code -ne 0 ]]; then
  cat <<EOF
{
  "decision": "block",
  "reason": "🚫 Mypy type errors detected in $file_path:\n\n$mypy_output\n\nFix these type errors and try again."
}
EOF
  exit 0
fi

echo "✅ Mypy type check passed"
echo "🎉 All checks passed: Format ✓ Lint ✓ Types ✓"
echo '{"decision": "approve"}'
exit 0