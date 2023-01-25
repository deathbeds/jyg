"""opinionated re-purposing of ``jsonschema_gentypes``.

@see https://github.com/camptocamp/jsonschema-gentypes/issues/134
"""
import sys
from typing import Any, List, Optional, Type, TypeVar

T = TypeVar("T")

import jsonschema_gentypes as JGT


def _hash_colon(lines: List[str]) -> List[str]:
    return ["#: " + line[2:] if line.startswith("# ") else line for line in lines]


def _patch_one(Klass: Type[T]) -> None:
    _old_definition = getattr(Klass, "definition")

    def _new_definition(self: T, *args: Any, **kwargs: Any) -> List[str]:
        return _hash_colon(_old_definition(self, *args, **kwargs))

    setattr(Klass, "definition", _new_definition)


def _patch_definitions() -> None:
    def dict_definition(
        self: JGT.TypedDictType, line_length: Optional[int] = None
    ) -> List[str]:
        """Get the definition based on a dict."""
        result = ["", ""]
        result.append(f"class {self._name}(TypedDict, total=False): " + "\n")
        comments = [
            d
            for d in JGT.split_comment(
                self.descriptions, line_length - 2 if line_length else None
            )
        ]
        if comments:
            result.extend(['    """', *comments, '    """'])
        for property_, type_obj in self.struct.items():
            for comment in type_obj.comments():
                result.append(f"    #: {comment}")
            name = type_obj.name()
            if name[0] == '"':
                name = name[1:-1]
            result.append(f"    {property_}: {name}")
        return result

    setattr(JGT.TypedDictType, "definition", dict_definition)

    _patch_one(JGT.TypeAlias)
    _patch_one(JGT.Constant)
    _patch_one(JGT.NamedType)
    _patch_one(JGT.NativeType)
    _patch_one(JGT.TypeEnum)
    _patch_one(JGT.Constant)
    _patch_one(JGT.LiteralType)

    def combined_name(self: JGT.CombinedType) -> str:
        """Return what we need to use the type."""
        names = [sub_type.name() for sub_type in self.sub_types]
        names = [n[1:-1] if n[0] == '"' else n for n in names]
        return f"{self.base.name()}[{', '.join(names)}]"

    setattr(JGT.CombinedType, "name", combined_name)


if __name__ == "__main__":
    from jsonschema_gentypes.cli import main

    _patch_definitions()
    main()
    sys.exit(0)
