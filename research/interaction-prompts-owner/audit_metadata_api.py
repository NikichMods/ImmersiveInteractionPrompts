# SPDX-License-Identifier: MPL-2.0
"""Offline source audit, NOT a UE4SS payload. Read only supplied source snapshots.

Run: python audit_metadata_api.py <directory-with-ue4ss-83330635-snapshots>
Output is a small JSON summary; proprietary files and live processes are not read.
This checks source expectations, not C++ execution or host ABI safety.
"""
import hashlib
import json
from pathlib import Path
import re
import sys


def audit(directory):
    names = [
        'LuaMod.cpp', 'LuaUFunction.cpp', 'LuaUStruct.cpp', 'LuaXProperty.cpp',
        'LuaXArrayProperty.cpp', 'LuaXProperty.hpp', 'LuaUObject.hpp', 'LuaObject.hpp',
    ]
    sources = {
        name: (directory / ('ue4ss-83330635-' + name)).read_text(encoding='utf-8')
        for name in names
    }
    expected = {
        'LuaMod.cpp': 'ecc9448999fdac16d4b9181d73f99aafeb8f75dd12ad921e3f7f7922d8298227',
        'LuaUFunction.cpp': '666aa018513f0e3297357f9463fa33e184b0c809725545a490b3c1dfdc190b14',
        'LuaUStruct.cpp': '794192fb1646a1ee5a35d8da0872335bb4a4032969cabbbae57e339e170667d8',
        'LuaXProperty.cpp': '9898a27956f5fe599f82ea8dc66b5d75581d78e9668bb23c1231402808482445',
        'LuaXArrayProperty.cpp': '0bf9584614f5f1971d4359d96fb07c2b1adcee39207110dbd19e6e2e37e85323',
        'LuaXProperty.hpp': '37f3ae149d0b99096ffa0a8417d1ea93890a12ac44301522af7cc57e6289960d',
        'LuaUObject.hpp': '1b011de1b90390abd02c9f11ebf9da7eb7b55b7d8b2c3f7040f749bd4649e157',
        'LuaObject.hpp': '1ea5ea6f9aa1905b7dcd9498a8fb988eb1e2bd4bd84c222c8a02b76c38cd50cd',
    }
    hashes = {name: hashlib.sha256(content.encode('utf-8')).hexdigest()
              for name, content in sources.items()}
    assert hashes == expected, 'Source snapshot identity changed; review before using audit'
    methods = {
        name: sorted(set(re.findall(r'table\.add_pair\("([^"]+)"', content)))
        for name, content in sources.items()
    }
    assert 'GetFunctionFlags' in methods['LuaUFunction.cpp']
    assert 'ForEachProperty' in methods['LuaUStruct.cpp']
    assert 'GetInner' in methods['LuaXArrayProperty.cpp']
    assert set(methods['LuaXProperty.cpp']) == {
        'GetClass', 'GetFullName', 'GetFName', 'GetOffset_Internal', 'IsA',
        'ContainerPtrToValuePtr', 'ImportText', 'type',
    }
    assert set(methods['LuaObject.hpp']) == {'GetAddress', 'IsValid', 'IsValidField'}
    assert 'using Super = RemoteObjectBase<Unreal::FProperty, FPropertyName>' in sources['LuaXProperty.hpp']
    assert 'using RemoteObjectBase = ObjectBase<DerivedType, LuaMadeSimple::Type::RemoteObject, ObjectName>' in sources['LuaUObject.hpp']
    for name in ('LuaXProperty.cpp', 'LuaUObject.hpp', 'LuaObject.hpp'):
        assert not any('PropertyFlags' in method for method in methods[name])
    src = sources['LuaMod.cpp']
    assert 'lua.register_function("StaticFindObject"' in src
    assert 'm_lua.register_function("ExecuteInGameThread"' in src
    assert 'actions.clear();' in src
    assert 'lua_data.lua->call_function(0, 0);' in src
    assert 'luaL_unref(lua_data.lua->get_lua_state(), LUA_REGISTRYINDEX, lua_data.lua_action_function_ref)' in src
    return {
        'revision': '83330635',
        'capture_ready': False,
        'blocker': 'No FProperty flag reader in inspected Lua binding hierarchy',
        'methods': {name: methods[name] for name in
                    ('LuaUFunction.cpp', 'LuaUStruct.cpp', 'LuaXProperty.cpp',
                     'LuaXArrayProperty.cpp', 'LuaObject.hpp')},
        'snapshot_sha256': hashes,
    }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Expected source-snapshot directory; does not run the game')
    print(json.dumps(audit(Path(sys.argv[1])), indent=2))
