import copy, importlib.util, json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("a5",ROOT/"tools/a5_provider_control.py")
a5=importlib.util.module_from_spec(spec); sys.modules[spec.name]=a5; spec.loader.exec_module(a5)

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected=json.loads((ROOT/"elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json").read_text(encoding="utf-8"))

    def actual(self):
        e=self.expected["agent"]; ps=[]
        for p in self.expected["procedures"]:
            c=a5.canonical_structured_content(p["content"]) if p["type"]=="structured" else a5.normalize_text(p["content"]) or ""
            ps.append({"name":p["name"],"type":p["type"],"trigger":p["trigger"],"content_canonical":c,
                       "content_sha256":a5.sha256_text(c),"has_draft":False,"procedure_version_present":False})
        return {"agent":{"name":e["name"],"language":e["language"],"first_message":"provider greeting",
                         "system_prompt":e["system_prompt"],
                         "llm":{"id":e["llm"]["id"],"temperature":0.1,"max_tokens":-1},
                         "voice":{"name":e["voice"]["name"],"id_sha256":e["voice"]["id_sha256"] or "voicehash","tts_model_id":"model",
                                  "stability":0.5,"speed":1.0,"similarity_boost":0.8},
                         "dynamic_variable_names":sorted(e["dynamic_variable_names"])},
                "procedures":ps,"procedures_gap":None,
                "provider_metadata":{"version_present":False,"branch_present":True,"main_branch_present":False,
                                     "version_id_sha256":None,"branch_id_sha256":"b","main_branch_id_sha256":None}}

    def pinned(self):
        e=copy.deepcopy(self.expected)
        a=self.actual()
        e["agent"]["first_message"]=a["agent"]["first_message"]
        for k,v in a["agent"]["llm"].items(): e["agent"]["llm"][k]=v
        for k,v in a["agent"]["voice"].items(): e["agent"]["voice"][k]=v
        return e

    def test_fully_pinned_exact_is_no_drift(self):
        r=a5.compare_expected(self.pinned(),self.actual())
        self.assertEqual("NO_DRIFT",a5.overall_status(r))

    def test_unpinned_fields_are_unverifiable(self):
        r=a5.compare_expected(self.expected,self.actual())
        self.assertEqual("UNVERIFIABLE",a5.overall_status(r))
        fields={x["field"]:x["status"] for x in r}
        self.assertEqual("UNVERIFIABLE",fields["agent.first_message"])
        self.assertEqual("UNVERIFIABLE",fields["agent.llm.temperature"])
        self.assertEqual("NO_DRIFT",fields["agent.voice.id_sha256"])

    def test_material_difference_is_drift(self):
        a=self.actual(); a["agent"]["llm"]["id"]="other"; a["procedures"][0]["type"]="free_form"
        r=a5.compare_expected(self.pinned(),a)
        self.assertEqual("DRIFT",a5.overall_status(r))

    def test_outer_whitespace_is_material_drift(self):
        a=self.actual()
        a["agent"]["system_prompt"]=" " + a["agent"]["system_prompt"]
        r=a5.compare_expected(self.pinned(),a)
        fields={x["field"]:x["status"] for x in r}
        self.assertEqual("DRIFT",a5.overall_status(r))
        self.assertEqual("DRIFT",fields["agent.system_prompt"])

    def test_duplicate_provider_procedure_names_fail_closed(self):
        a=self.actual()
        a["procedures"].append(copy.deepcopy(a["procedures"][0]))
        with self.assertRaises(a5.HarnessError):
            a5.compare_expected(self.pinned(),a)

    def test_pinned_voice_resource_difference_is_drift(self):
        a=self.actual()
        a["agent"]["voice"]["id_sha256"]="different-voice-fingerprint"
        r=a5.compare_expected(self.expected,a)
        fields={x["field"]:x["status"] for x in r}
        self.assertEqual("DRIFT",a5.overall_status(r))
        self.assertEqual("DRIFT",fields["agent.voice.id_sha256"])

    def test_missing_branch_is_unverifiable(self):
        a=self.actual(); a["procedures"]=None; a["procedures_gap"]="no branch"
        r=a5.compare_expected(self.pinned(),a)
        self.assertEqual("UNVERIFIABLE",a5.overall_status(r))

    def test_sanitized_snapshot_has_no_raw_text_or_ids(self):
        s=json.dumps(a5.sanitized_snapshot(self.actual()),ensure_ascii=False)
        self.assertNotIn(self.expected["agent"]["system_prompt"],s)
        self.assertNotIn("provider greeting",s)
        self.assertNotIn("procedure_id",s)
        self.assertIn("system_prompt_sha256",s)

    def test_reserved_adjacent_tokens_rejected(self):
        with self.assertRaises(a5.HarnessError): a5.safe_identifier("compile","procedure_id",{"compile","draft"})
        with self.assertRaises(a5.HarnessError): a5.safe_identifier("draft","procedure_id",{"compile","draft"})
        with self.assertRaises(a5.HarnessError): a5.safe_identifier("settings","voice_id",{"settings"})

    def test_structured_content_requires_steps(self):
        with self.assertRaises(a5.HarnessError): a5.canonical_structured_content({"foo":[]})

if __name__=="__main__": unittest.main()
