import ast
import jinja2
import os

pyi_return_type_dict = {
    "char":"int",
    "short":"int",
    "int":"int",
    "ll":"int",
    "ubyte":"int",
    "ushort":"int",
    "uint":"int",
    "ull":"int",
    "u8":"int",
    "u16":"int",
    "u32":"int",
    "u64":"int",
    "i8":"int",
    "i16":"int",
    "i32":"int",
    "i64":"int",
    "float":"float",
    "double":"float",
    "char_p":"bytes|None",
    "bool":"bool",
    "void":"None",
}
type_dict = {
    "char":"ctypes.c_char",
    "short":"ctypes.c_short",
    "int":"ctypes.c_int",
    "ll":"ctypes.c_longlong",
    "ubyte":"ctypes.c_ubyte",
    "ushort":"ctypes.c_ushort",
    "uint":"ctypes.c_uint",
    "ull":"ctypes.c_ulonglong",
    "u8":"ctypes.c_uint8",
    "u16":"ctypes.c_uint16",
    "u32":"ctypes.c_uint32",
    "u64":"ctypes.c_uint64",
    "i8":"ctypes.c_int8",
    "i16":"ctypes.c_int16",
    "i32":"ctypes.c_int32",
    "i64":"ctypes.c_int64",
    "float":"ctypes.c_float",
    "double":"ctypes.c_double",
    "char_p":"ctypes.c_char_p",
    "bool":"ctypes.c_bool",
    "void":"None",
    "p":"ctypes._Pointer"
}


pyi_template = jinja2.Template(""" # This file is auto generated
import ctypes
import typing

def load_sdl3_dll(sdl_dll_path:str) -> SDL3DLL:...

{{ const_and_type_def }}

class SDL3DLL(ctypes.CDLL):
{% for def in func_def %}\
    def {{def.name}}(self,\
{% for arg,typ in def.args %}\
{{arg}}:{{typ}},\
{% endfor %})->{{def.returns}}:...
{% endfor %}

""")
py_template = jinja2.Template("""# This file is auto generated
import ctypes
import typing

{{ const_and_type_def }}

def load_sdl3_dll(sdl_dll_path):
    sdl3 = ctypes.cdll.LoadLibrary(sdl_dll_path)
{% for def in func_def %}\
{% if def.restype!="None"%}\
    sdl3.{{ def.name }}.restype = {{ def.restype }}
{% endif%}\
{% endfor %}
    return sdl3

""")
struct_template = jinja2.Template("""
class {{ name }}(ctypes.Structure):
{% for field in fields %}\
    {{ field.name }}:{{ field.alias }}
{% endfor %}\
    _fields_ = [ # type: ignore
{% for field in fields %}\
        ("{{ field.name }}",{{ field.type }}),
{% endfor %}\
    ]

""")
dir_name = os.path.dirname(__file__)

def load_stub(filename):
    with open(filename) as f:
        original_text = f.read()
    stub_text = original_text[original_text.find("# DEF_BEGIN"):]
    return ast.parse(stub_text).body

typedef_map:dict[str,str] = {}

def get_type_str(node):
    if isinstance(node, ast.Name):
        if node.id in type_dict:
            return type_dict[node.id]
        else:
            return node.id
    elif isinstance(node, ast.Subscript):
        assert isinstance(node.value,ast.Name) and node.value.id=="p"
        return f"ctypes._Pointer[{get_type_str(node.slice)}]"
    else:
        raise RuntimeError()

def get_restype(node):
    if isinstance(node, ast.Name):
        if node.id in type_dict:
            return type_dict[node.id]
        else:
            return node.id
    elif isinstance(node, ast.Subscript):
        assert isinstance(node.value,ast.Name) and node.value.id=="p"
        return f"ctypes.POINTER({get_type_str(node.slice)})"
    else:
        raise RuntimeError()

class FuncDef:
    name:str
    args:list[tuple[str,str]]
    returns:str
    restype:str

class StructFieldDef:
    name: str
    type: str
    alias: str

const_and_type_def = []
function_def = []
for def_ in load_stub(os.path.join(dir_name,"sdl3.pyi.in")):
    if isinstance(def_,ast.AnnAssign):
        assert isinstance(def_.target, ast.Name)
        assert isinstance(def_.annotation, ast.Name)
        if def_.annotation.id=="TypeAlias":
            if isinstance(def_.value,ast.Name):
                typedef_map[def_.target.id] = def_.value.id
            const_and_type_def.append(
                f"{def_.target.id}:typing.TypeAlias={get_type_str(def_.value)}"
            )
        elif def_.annotation.id=="CallbackDef":
            const_and_type_def.append(f"if typing.TYPE_CHECKING:\n    {def_.target.id}:typing.TypeAlias=ctypes._FuncPointer")
            assert isinstance(def_.value, ast.Subscript) and isinstance(def_.value.value, ast.Name)
            assert def_.value.value.id=="fp"
            assert isinstance(def_.value.slice, ast.Tuple)
            decorator_args = []
            for arg in def_.value.slice.elts:
                if isinstance(arg, ast.Name):
                    decorator_args.append(get_type_str(arg))
                elif isinstance(arg, ast.Subscript):
                    decorator_args.append(get_restype(arg))
            decorator_args_str = ", ".join(decorator_args)
            const_and_type_def.append(f"else:\n    {def_.target.id}=ctypes.CFUNCTYPE({decorator_args_str})")
        else:
            raise RuntimeError()

    elif isinstance(def_,ast.Assign):
        assert len(def_.targets)==1 and isinstance(def_.targets[0], ast.Name)
        assert isinstance(def_.value,ast.Call) and isinstance(def_.value.func,ast.Name)
        assert len(def_.value.args)==1
        const_value:str
        if isinstance(def_.value.args[0],ast.Constant):
            const_value = repr(def_.value.args[0].value)
        elif isinstance(def_.value.args[0],ast.Name):
            const_value = def_.value.args[0].id
        else:
            raise RuntimeError()
        const_and_type_def.append(
            f"{def_.targets[0].id}={def_.value.func.id}({const_value})"
        )
    elif isinstance(def_,ast.FunctionDef):
        f_def = FuncDef()
        f_def.name = def_.name
        if isinstance(def_.returns, ast.Name):
            if def_.returns.id in pyi_return_type_dict:
                f_def.returns = pyi_return_type_dict[def_.returns.id]
            else:
                original_type  = typedef_map[def_.returns.id]
                if original_type in pyi_return_type_dict:
                    f_def.returns = pyi_return_type_dict[original_type]
                else:
                    f_def.returns = original_type
            f_def.restype = get_type_str(def_.returns)
        else:
            f_def.restype = get_restype(def_.returns)
            f_def.returns = get_type_str(def_.returns)
            
        f_def.args = []
        assert isinstance(def_.args,ast.arguments)
        for _arg in def_.args.args:
            assert isinstance(_arg,ast.arg)
            f_def.args.append((_arg.arg, get_type_str(_arg.annotation)))

        function_def.append(f_def)
    elif isinstance(def_, ast.ClassDef):
        assert len(def_.bases)==1 and isinstance(def_.bases[0], ast.Name)
        assert def_.bases[0].id=="struct"
        struct_name = def_.name
        fields = []
        for field_node in def_.body:
            if isinstance(field_node, ast.Pass):
                continue
            assert isinstance(field_node, ast.AnnAssign)
            assert isinstance(field_node.target, ast.Name)
            field = StructFieldDef()
            field.name = field_node.target.id
            field.type = get_type_str(field_node.annotation)
            if isinstance(field_node.annotation, ast.Name):
                if field_node.annotation.id in pyi_return_type_dict:
                    field.alias = pyi_return_type_dict[field_node.annotation.id]
                else:
                    original_type = typedef_map[field_node.annotation.id]
                    if original_type in pyi_return_type_dict:
                        field.alias = pyi_return_type_dict[original_type]
                    else:
                        field.alias = original_type
            else:
                field.alias = field.type

            fields.append(field)
        
        const_and_type_def.append(
            struct_template.render(
                name = struct_name,
                fields = fields
            )
        )

const_and_type_def_str = "\n".join(const_and_type_def)
with open(os.path.join(dir_name,"__init__.pyi"),"w") as f:
    f.write(pyi_template.render(
        const_and_type_def = const_and_type_def_str,
        func_def = function_def
    ))
with open(os.path.join(dir_name,"__init__.py"),"w") as f:
    f.write(py_template.render(
        const_and_type_def = const_and_type_def_str,
        func_def = function_def
    ))
