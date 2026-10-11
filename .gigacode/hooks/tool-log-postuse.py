#!/usr/bin/env python3
import sys
import json
import os

def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"decision": "allow", "reason": f"parse_error: {e}"}))
        sys.exit(0)

    event = data.get("hook_event_name", "")
    tool = data.get("tool_name", "unknown")
    
    log_path = os.path.join(os.path.expanduser("~"), ".gigacode", "hooks", "tool-log-postuse.jsonl")
    
    if event == "PostToolUse":
        tool_input = data.get("tool_input", {})
        tool_response = data.get("tool_response", {})
        
        cmd = tool_input.get("command", "")
        file_path = tool_input.get("filePath", "")
        pattern = tool_input.get("pattern", "")
        
        exit_code = tool_response.get("exitCode")
        if exit_code is None:
            exit_code = tool_response.get("editsApplied")
        if exit_code is None:
            exit_code = tool_response.get("contentLength")
        if exit_code is None:
            exit_code = tool_response.get("count")
        if exit_code is None:
            exit_code = "N/A"
        
        entry = {
            "timestamp": data.get("timestamp"),
            "event": event,
            "tool": tool,
            "command": cmd,
            "file": file_path,
            "pattern": pattern,
            "exit_code": exit_code,
            "session": data.get("session_id")
        }
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(json.dumps({"decision": "allow", "reason": "ok"}))

if __name__ == "__main__":
    main()
