#!/usr/bin/env python3
"""A5 ElevenLabs provider-control reader/diff.

Read-only by construction. The only network operations are GET requests to the
five documented endpoint shapes required by A5. Output is sanitized.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
import urllib.error, urllib.parse, urllib.request
from dataclasses import dataclass
from typing import Any

API_BASE = "https://api.elevenlabs.io"
API_KEY_ENV = "ELEVENLABS_API_KEY"
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")

class HarnessError(RuntimeError):
    pass

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise HarnessError(f"Expected text, got {type(value).__name__}")
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()

def canonical_structured_content(value: Any) -> str:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise HarnessError("Structured Procedure content is not valid JSON") from exc
    if not isinstance(value, dict) or not isinstance(value.get("steps"), list):
        raise HarnessError("Structured Procedure content must be a JSON object with steps")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def safe_identifier(value: Any, label: str, reserved: set[str] | None = None) -> str:
    if not isinstance(value, str) or not value or not SAFE_ID.fullmatch(value):
        raise HarnessError(f"Invalid {label}")
    if reserved and value in reserved:
        raise HarnessError(f"Reserved token cannot be used as {label}")
    return urllib.parse.quote(value, safe="")

@dataclass
class ApiClient:
    api_key: str
    base_url: str = API_BASE

    def _get(self, path: str, query: dict[str, str] | None = None) -> dict[str, Any]:
        q = urllib.parse.urlencode(query or {})
        url = f"{self.base_url}{path}" + (f"?{q}" if q else "")
        request = urllib.request.Request(
            url, method="GET",
            headers={"accept":"application/json","xi-api-key":self.api_key,
                     "user-agent":"bodyshop-voice-poc-a5-read-only/1"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise HarnessError(f"ElevenLabs GET failed: HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise HarnessError("ElevenLabs GET failed due to a network error") from exc
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise HarnessError("ElevenLabs returned non-JSON data") from exc
        if not isinstance(parsed, dict):
            raise HarnessError("ElevenLabs returned an unexpected non-object response")
        return parsed

    def list_agents(self, name: str, cursor: str | None = None) -> dict[str, Any]:
        query={"page_size":"100","search":name,"archived":"false"}
        if cursor: query["cursor"]=cursor
        return self._get("/v1/convai/agents", query)

    def get_agent(self, agent_id: str) -> dict[str, Any]:
        aid=safe_identifier(agent_id,"agent_id")
        return self._get(f"/v1/convai/agents/{aid}")

    def list_procedures(self, agent_id: str, branch_id: str, agent_version_id: str | None) -> dict[str, Any]:
        aid=safe_identifier(agent_id,"agent_id")
        bid=safe_identifier(branch_id,"branch_id")
        query={"agent_version_id":agent_version_id} if agent_version_id else None
        return self._get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures",query)

    def get_procedure(self, agent_id: str, branch_id: str, procedure_id: str, agent_version_id: str | None) -> dict[str, Any]:
        aid=safe_identifier(agent_id,"agent_id")
        bid=safe_identifier(branch_id,"branch_id")
        pid=safe_identifier(procedure_id,"procedure_id",{"compile","draft"})
        query={"agent_version_id":agent_version_id} if agent_version_id else None
        return self._get(f"/v1/convai/agents/{aid}/branches/{bid}/procedures/{pid}",query)

    def get_voice(self, voice_id: str) -> dict[str, Any]:
        vid=safe_identifier(voice_id,"voice_id",{"settings"})
        return self._get(f"/v1/voices/{vid}")

def safe_id_fingerprint(value: Any) -> str | None:
    return sha256_text(value) if isinstance(value,str) and value else None

def find_exact_agent(client: ApiClient, name: str) -> dict[str, Any]:
    cursor=None; matches=[]
    while True:
        page=client.list_agents(name,cursor)
        for item in page.get("agents",[]):
            if isinstance(item,dict) and item.get("name")==name and not item.get("archived",False):
                matches.append(item)
        if not page.get("has_more"): break
        cursor=page.get("next_cursor")
        if not isinstance(cursor,str) or not cursor:
            raise HarnessError("Agent pagination advertised has_more without next_cursor")
    if len(matches)!=1:
        raise HarnessError(f"Expected exactly one non-archived agent named {name!r}; found {len(matches)}")
    return matches[0]

def dynamic_variable_names(agent: dict[str,Any]) -> list[str] | None:
    node=agent.get("conversation_config",{}).get("agent",{}).get("dynamic_variables",{}).get("dynamic_variable_placeholders")
    if node is None: return None
    if not isinstance(node,dict): raise HarnessError("dynamic_variable_placeholders is not an object")
    return sorted(str(k) for k in node)

def collect_procedures(client: ApiClient, agent_id: str, branch_id: Any, version_id: Any):
    if not isinstance(branch_id,str) or not branch_id:
        return None,"Provider did not expose branch_id; Procedures API requires branch_id."
    listing=client.list_procedures(agent_id,branch_id,version_id if isinstance(version_id,str) else None)
    out=[]
    for meta in listing.get("procedures",[]):
        if not isinstance(meta,dict): continue
        pid=meta.get("procedure_id")
        if not isinstance(pid,str) or not pid: raise HarnessError("Procedure listing omitted procedure_id")
        full=client.get_procedure(agent_id,branch_id,pid,version_id if isinstance(version_id,str) else None)
        ptype=full.get("type",meta.get("type","free_form"))
        raw=full.get("content","")
        canonical=canonical_structured_content(raw) if ptype=="structured" else (normalize_text(raw) or "")
        out.append({
          "name":full.get("name",meta.get("name")),"type":ptype,
          "trigger":normalize_text(full.get("trigger",meta.get("trigger",""))) or "",
          "content_canonical":canonical,"content_sha256":sha256_text(canonical),
          "has_draft":bool(meta.get("has_draft",False)),
          "procedure_version_present":bool(full.get("version_id") or meta.get("version_id")),
        })
    out.sort(key=lambda x:str(x.get("name")))
    return out,None

def collect_provider_state(client: ApiClient, agent_name: str) -> dict[str,Any]:
    listed=find_exact_agent(client,agent_name)
    agent_id=listed.get("agent_id")
    if not isinstance(agent_id,str) or not agent_id: raise HarnessError("Matched agent omitted agent_id")
    agent=client.get_agent(agent_id)
    cfg=agent.get("conversation_config",{})
    acfg=cfg.get("agent",{})
    pcfg=acfg.get("prompt",{})
    tts=cfg.get("tts",{})
    voice_id=tts.get("voice_id")
    voice=client.get_voice(voice_id) if isinstance(voice_id,str) and voice_id else {}
    branch_id=agent.get("branch_id"); version_id=agent.get("version_id")
    procedures,gap=collect_procedures(client,agent_id,branch_id,version_id)
    return {
      "agent":{
        "name":agent.get("name"),"language":acfg.get("language"),
        "first_message":normalize_text(acfg.get("first_message")),
        "system_prompt":normalize_text(pcfg.get("prompt")),
        "llm":{"id":pcfg.get("llm"),"temperature":pcfg.get("temperature"),"max_tokens":pcfg.get("max_tokens")},
        "voice":{
          "name":voice.get("name") if isinstance(voice.get("name"),str) else None,
          "id_sha256":safe_id_fingerprint(voice_id),
          "tts_model_id":tts.get("model_id"),"stability":tts.get("stability"),
          "speed":tts.get("speed"),"similarity_boost":tts.get("similarity_boost"),
        },
        "dynamic_variable_names":dynamic_variable_names(agent),
      },
      "procedures":procedures,"procedures_gap":gap,
      "provider_metadata":{
        "version_present":isinstance(version_id,str) and bool(version_id),
        "branch_present":isinstance(branch_id,str) and bool(branch_id),
        "main_branch_present":isinstance(agent.get("main_branch_id"),str) and bool(agent.get("main_branch_id")),
        "version_id_sha256":safe_id_fingerprint(version_id),
        "branch_id_sha256":safe_id_fingerprint(branch_id),
        "main_branch_id_sha256":safe_id_fingerprint(agent.get("main_branch_id")),
      },
    }

def result(field:str,status:str,expected:Any=None,actual:Any=None,note:str|None=None):
    item={"field":field,"status":status}
    if expected is not None: item["expected"]=expected
    if actual is not None: item["actual"]=actual
    if note: item["note"]=note
    return item

def compare_scalar(results,field,expected,actual):
    if expected is None:
        results.append(result(field,"UNVERIFIABLE",actual=actual,note="Expected value is not pinned in GitHub."))
    elif actual is None:
        results.append(result(field,"UNVERIFIABLE",expected=expected,note="Provider did not expose the value."))
    else:
        results.append(result(field,"NO_DRIFT" if expected==actual else "DRIFT",expected,actual))

def compare_text(results,field,expected,actual):
    exp=normalize_text(expected); act=normalize_text(actual)
    if exp is None:
        item={"field":field,"status":"UNVERIFIABLE","note":"Expected text is not pinned in GitHub."}
        if act is not None: item.update(actual_sha256=sha256_text(act),actual_length=len(act))
        results.append(item); return
    if act is None:
        results.append({"field":field,"status":"UNVERIFIABLE","expected_sha256":sha256_text(exp),"expected_length":len(exp)})
        return
    results.append({"field":field,"status":"NO_DRIFT" if exp==act else "DRIFT",
                    "expected_sha256":sha256_text(exp),"actual_sha256":sha256_text(act),
                    "expected_length":len(exp),"actual_length":len(act)})

def compare_expected(expected: dict[str,Any], actual: dict[str,Any]) -> list[dict[str,Any]]:
    r=[]; e=expected["agent"]; a=actual["agent"]
    compare_scalar(r,"agent.name",e.get("name"),a.get("name"))
    compare_scalar(r,"agent.language",e.get("language"),a.get("language"))
    compare_text(r,"agent.first_message",e.get("first_message"),a.get("first_message"))
    compare_text(r,"agent.system_prompt",e.get("system_prompt"),a.get("system_prompt"))
    for key in ("id","temperature","max_tokens"):
        compare_scalar(r,f"agent.llm.{key}",e.get("llm",{}).get(key),a.get("llm",{}).get(key))
    for key in ("name","id_sha256","tts_model_id","stability","speed","similarity_boost"):
        compare_scalar(r,f"agent.voice.{key}",e.get("voice",{}).get(key),a.get("voice",{}).get(key))
    ev=sorted(e.get("dynamic_variable_names",[])); av=a.get("dynamic_variable_names")
    if av is None: r.append(result("agent.dynamic_variable_names","UNVERIFIABLE",expected=ev))
    else: r.append(result("agent.dynamic_variable_names","NO_DRIFT" if ev==sorted(av) else "DRIFT",ev,sorted(av)))

    ep={p["name"]:p for p in expected.get("procedures",[])}
    raw=actual.get("procedures")
    if raw is None:
        note=actual.get("procedures_gap") or "Procedures unavailable"
        for name in sorted(ep): r.append(result(f"procedures.{name}","UNVERIFIABLE",note=note))
        return r
    ap={p.get("name"):p for p in raw if p.get("name")}
    for name in sorted(set(ep)|set(ap)):
        ex=ep.get(name); ac=ap.get(name)
        if ex is None: r.append(result(f"procedures.{name}","DRIFT",note="Unexpected provider Procedure")); continue
        if ac is None: r.append(result(f"procedures.{name}","DRIFT",note="Expected Procedure missing")); continue
        compare_scalar(r,f"procedures.{name}.type",ex.get("type"),ac.get("type"))
        compare_text(r,f"procedures.{name}.trigger",ex.get("trigger"),ac.get("trigger"))
        expc=canonical_structured_content(ex.get("content")) if ex.get("type")=="structured" else (normalize_text(ex.get("content")) or "")
        actc=ac.get("content_canonical")
        compare_text(r,f"procedures.{name}.content",expc,actc)
        if ac.get("has_draft"):
            r.append(result(f"procedures.{name}.has_draft","DRIFT",actual=True,note="Provider reports unpublished draft changes."))
    return r

def overall_status(results):
    statuses={x["status"] for x in results}
    return "DRIFT" if "DRIFT" in statuses else ("UNVERIFIABLE" if "UNVERIFIABLE" in statuses else "NO_DRIFT")

def sanitized_snapshot(actual):
    a=actual["agent"]
    safe={"agent":{
      "name":a.get("name"),"language":a.get("language"),"llm":a.get("llm"),"voice":a.get("voice"),
      "dynamic_variable_names":a.get("dynamic_variable_names"),
    },"provider_metadata":actual.get("provider_metadata"),"procedures_gap":actual.get("procedures_gap")}
    for key in ("first_message","system_prompt"):
        text=a.get(key)
        safe["agent"][f"{key}_sha256"]=sha256_text(text) if isinstance(text,str) else None
        safe["agent"][f"{key}_length"]=len(text) if isinstance(text,str) else None
    if actual.get("procedures") is None:
        safe["procedures"]=None
    else:
        safe["procedures"]=[{k:p.get(k) for k in ("name","type","content_sha256","has_draft","procedure_version_present")} |
                            {"trigger_sha256":sha256_text(p.get("trigger","")),"content_length":len(p.get("content_canonical",""))}
                            for p in actual["procedures"]]
    return safe

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--expected",required=True); p.add_argument("--output",required=True)
    p.add_argument("--agent-name",default="AI Control")
    args=p.parse_args(argv)
    key=os.getenv(API_KEY_ENV)
    if not key:
        print(f"ERROR: {API_KEY_ENV} is not set",file=sys.stderr); return 2
    try:
        with open(args.expected,encoding="utf-8") as f: expected=json.load(f)
        actual=collect_provider_state(ApiClient(key),args.agent_name)
        results=compare_expected(expected,actual)
        report={"schema_version":1,"overall":overall_status(results),"results":results,"snapshot":sanitized_snapshot(actual)}
        with open(args.output,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2); f.write("\n")
    except (HarnessError,OSError,ValueError,KeyError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2
    return 0 if report["overall"]=="NO_DRIFT" else 1

if __name__=="__main__":
    raise SystemExit(main())
