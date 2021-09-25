#!/usr/bin/env python3
import pathlib, re, textwrap, sys, os

def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Please specify both path to `types.cs` and output file")
        exit()
    elif len(args) < 2:
        print("Please specify path to output file")
        exit()

    path = pathlib.Path(args[0])
    if not path.exists():
        print(f"Path '{path}' doesn't exist")
        exit()

    with open(path, "r") as f:
        data = f.read()
    data = CsNamespace(data, "FlatData")

    output = pathlib.Path(args[1])
    with open(output, "w") as f:
        for typedef in data.typedefs():
            if typedef.kind == "enum":
                f.write(typedef.exportYaml())
                f.write("\n\n")
        f.truncate(f.tell() - len(os.linesep))


#================================================
UNUSED_KEYWORD = [
    "abstract",
    "checked",
    "const",
    "default",
    "event",
    "explicit",
    "extern",
    "fixed",
    "implicit",
    "new",
    "override",
    "readonly",
    "ref",
    "sealed",
    "stackalloc",
    "static",
    "unchecked",
    "unsafe",
    "virtual",
    "volatile",
]
REOR_UNUSED_KEYWORD = "|".join(UNUSED_KEYWORD)

ACCESSIBILITY = [
    "private",
    "private protected",
    "internal",
    "protected",
    "protected internal",
    "public",
]
REOR_ACCESSIBILITY = "|".join(ACCESSIBILITY)

TYPEDEFKIND = [
    "class",
    "struct",
    "enum",
    "interface",
    "record",
]
REOR_TYPEDEFKIND = "|".join(TYPEDEFKIND)


#================================================
class NotFoundNamespaceError(Exception):
    """Raised when can't find valid `namespace` in string"""
    pass

class CsNamespace():

    def __init__(self, code: str, name: str):
        if code:
            regex = r'^(\s*)namespace\s%s.*?^\1}' % (name)
            if (match := re.search(regex, code, flags = re.MULTILINE | re.DOTALL)):
                self.code = match.group()
            else:
                raise NotFoundNamespaceError

        # Beautify `self.code`
        self.code = textwrap.dedent(self.code).strip()

        if self.code:
            regex = r'(?:.*|\s*)namespace\s(\w+)\s.*'
            if (match := re.search(regex, self.code)):
                self.name = match.group(1)

    def typedefs(self):
        result = []

        i = 0

        regex = r'^(\s*)(?:\w|\s)*(?:%s)\s(\w+)\s.*?\1}' % (REOR_TYPEDEFKIND)
        for match in re.finditer(regex, self.code, re.MULTILINE | re.DOTALL):
            name = match.group(2)
            result.append(CsTypedef(match.group(0), name))
        return result


#================================================
class NotFoundTypedefError(Exception):
    """Raised when can't find valid `class`, `struct`, `interface` or `enum` in string"""
    pass

class CsTypedef():

    def __init__(self, code: str, name: str):
        if code:
            regex = r'^(\s*)(?:\w|\s)*(?:%s)\s%s\s.*?\1}' % (REOR_TYPEDEFKIND, name)
            if (match := re.search(regex, code, re.MULTILINE | re.DOTALL)):
                self.code = match.group()
            else:
                raise NotFoundTypedefError

        # Beautify `self.code`
        self.code = textwrap.dedent(self.code).strip()

        if self.code:
            regex = r'(?:.*|\s*)(%s)\s(\w+)\s.*' % (REOR_TYPEDEFKIND)
            if (match := re.search(regex, self.code)):
                self.name = match.group(2)
                self.kind = match.group(1)

    def members(self):
        result = []

        if self.kind == "enum":
            regex = r'^(?:\s+)(\w+)(?:\s*=\s*(\d+))?.*'
            for match in re.finditer(regex, self.code, re.MULTILINE):
                code = match.group()
                result.append(CsEnumMember(code))
            return result

        # TODO: Work on `class` and `struct`
        if self.kind in ["class", "struct"]:
            pass

    def exportYaml(self, ident: int = 2):
        if self.kind == "enum":
            return f"{self.name}:\n" + "\n".join([f"{' ' * ident}- {member.name}: {member.value}" for member in self.members()])

        # TODO: Work on `class` and `struct`
        if self.kind in ["class", "struct"]:
            pass


#================================================
class NotFoundEnumMember(Exception):
    """Raised when can't find valid enum `member` in string"""
    pass

class CsEnumMember():

    def __init__(self, code: str):
        if code:
            regex = r'^(?:\s*)(\w+)(?:\s*=\s*(\d+))?.*'
            if (match := re.search(regex, code)):
                self.name = match.group(1)
                self.value = match.group(2)
            else:
                raise NotFoundEnumMember


#================================================
class NotFoundEncapMember(Exception):
    """Raised when can't find valid class or struct `field`, `property` or `method` in string"""
    pass

# TODO: Work on `class` and `struct`
class CsEncapMember():

    def __init__(self, code: str):
        if code:
            regex = r''
            if (match := re.search(regex, code)):
                pass
            else:
                raise NotFoundEncapMember


#================================================
if __name__ == "__main__":
    main()
