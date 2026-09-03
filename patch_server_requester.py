"""
patch_server_requester.py
Updates _acp_send_req in C:\LEO-LAB-ANTIGRAVITY\hermes-agent\acp_adapter\server.py to add _buzz/publish_in_channel_mention RPC handler and fallback.
"""
path = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent\acp_adapter\server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target_code = '''            def _acp_send_req(method: str, params: dict) -> Any:
                if not conn:
                    raise RuntimeError("ACP connection not established")
                ext_name = method[1:] if method.startswith("_") else method
                fut = asyncio.run_coroutine_threadsafe(conn.ext_method(ext_name, params), loop)
                return fut.result(timeout=15)'''

replacement_code = '''            def _acp_send_req(method: str, params: dict) -> Any:
                if not conn:
                    raise RuntimeError("ACP connection not established")
                ext_name = method[1:] if method.startswith("_") else method
                try:
                    fut = asyncio.run_coroutine_threadsafe(conn.ext_method(ext_name, params), loop)
                    return fut.result(timeout=15)
                except Exception as ex:
                    # Supervisor RPC fallback for _buzz/publish_in_channel_mention -> buzz/send_managed_agent with mention-only payload
                    if ext_name in ("buzz/publish_in_channel_mention", "publish_in_channel_mention"):
                        logger.info("publish_in_channel_mention supervisor fallback to buzz/send_managed_agent (in_channel_mention_only=True)")
                        fallback_payload = dict(params)
                        fallback_payload["action"] = "in_channel_mention_only"
                        fallback_payload["in_channel_mention_only"] = True
                        fallback_payload["is_task_delegation"] = False
                        fut = asyncio.run_coroutine_threadsafe(conn.ext_method("buzz/send_managed_agent", fallback_payload), loop)
                        return fut.result(timeout=15)
                    raise ex'''

if target_code in content:
    content = content.replace(target_code, replacement_code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully updated _acp_send_req in server.py!')
else:
    print('_acp_send_req target pattern not found or already updated.')
