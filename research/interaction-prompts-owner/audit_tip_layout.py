# SPDX-License-Identifier: MPL-2.0
"""Read retained CUE4Parse exports; never load the game or modify input files.

Usage: python audit_tip_layout.py PATH_TO_STATIC_EXPORTS
Outputs derived layout facts and input hashes, not extracted asset payloads.
"""
import hashlib
import json
import sys
from pathlib import Path


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def audit(root):
    def read(name):
        return json.loads((root / name).read_text(encoding="utf-8-sig"))

    exports = read("TipHUD.json")
    widgets = {x["Name"]: x for x in exports if x.get("Outer") == "WidgetTree"}

    def resolve(ref):
        index = int(ref["ObjectPath"].rsplit(".", 1)[1])
        item = exports[index]
        assert ref["ObjectName"].endswith(item["Name"] + "'")
        return item

    edges = []
    for parent in widgets.values():
        for ref in parent.get("Properties", {}).get("Slots", []):
            slot = resolve(ref)
            props = slot["Properties"]
            assert resolve(props["Parent"]) is parent
            child = resolve(props["Content"])
            assert resolve(child["Properties"]["Slot"]) is slot
            edges.append({"parent": parent["Name"], "child": child["Name"],
                          "slot": slot["Name"], "slot_type": slot["Type"],
                          "layout": {k: v for k, v in props.items()
                                     if k not in ("Parent", "Content")}})
    tree = next(x for x in exports if x["Type"] == "WidgetTree")
    root_widget = resolve(tree["Properties"]["RootWidget"])["Name"]
    assert root_widget == "CanvasPanel_0"
    assert len(edges) == 7
    assert len({e["child"] for e in edges}) == len(edges)
    by_child = {e["child"]: e for e in edges}
    assert by_child["TextBlock_89"]["parent"] == "CanvasPanel_6"
    assert by_child["RetainerBox_0"]["parent"] == "CanvasPanel_6"
    assert by_child["ImageInteractAllowed"]["parent"] == "RetainerBox_0"
    assert by_child["ImageInteractNotAllowed"]["parent"] == "CanvasPanel_2"

    bytecode = read("TipHUD--ExecuteUbergraph_TipHUD.bytecode.json")
    offsets = {x["Offset"]: x["Code"] for x in bytecode}
    assert offsets[713]["Function"]["ObjectName"] == "Class'ExtendedUserWidget:SetupTipMessage2'"
    assert len(offsets[661]["Elements"]) == 1
    assert offsets[661]["Elements"][0]["Variable"]["Property"]["Name"] == "TextBlock_89"
    calls = []
    for row in bytecode:
        names = sorted({n["Function"]["ObjectName"] for n in walk(row["Code"])
                        if isinstance(n.get("Function"), dict)})
        if names:
            calls.append({"offset": row["Offset"], "functions": names})

    composite = read("Umg_Font.json")[0]["Properties"]
    assert composite["FontCacheType"] == "EFontCacheType::Runtime"
    faces = sorted({n["LocalFontFaceAsset"]["ObjectPath"] for n in walk(composite)
                    if "LocalFontFaceAsset" in n})
    assert not any("aphes" in face.lower() for face in faces)
    refs = []
    for path in sorted(root.glob("*.json")):
        if path.name == "TipHUD.json" or ".bytecode." in path.name:
            continue
        if "/Game/MainContent/Template/UMG/TipHUD." in path.read_text(encoding="utf-8-sig"):
            refs.append(path.name)
    filenames = ["TipHUD.json", "TipHUD--ExecuteUbergraph_TipHUD.bytecode.json", "Umg_Font.json"]
    return {"result": "STATIC_LAYOUT_CONFIRMED_FONT_BRIDGE_UNPROVED",
            "root": root_widget, "edges": edges,
            "text_properties": {k: v for k, v in widgets["TextBlock_89"]["Properties"].items()
                                if k in ("Font", "Justification", "WrapTextAt")},
            "ubergraph_calls": calls, "existing_font_faces": faces,
            "tip_class_references_in_retained_exports_only": refs,
            "sha256": {n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in filenames}}


if __name__ == "__main__":
    print(json.dumps(audit(Path(sys.argv[1])), ensure_ascii=False, indent=2))
