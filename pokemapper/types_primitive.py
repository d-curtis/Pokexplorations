from pydantic.dataclasses import dataclass
from dataclasses import field
from typing import ClassVar

CHAR_ENCODING = [
    # These are AI formatted and likely a bit broken
    [" ", "À", "Á", "Â", "Ç", "È", "É", "Ê", "Ë", "Ì", "", "Î", "Ï", "Ò", "Ó", "Ô"],
    ["Œ", "Ù", "Ú", "Û", "Ñ", "ß", "à", "á", "", "ç", "è", "é", "ê", "ë", "ì", ""],
    ["î", "ï", "ò", "ó", "ô", "œ", "ù", "ú", "û", "ñ", "º", "ª", "ᵉʳ", "&", "+", ""],
    ["", "", "", "", "Lv", "=", ";", "", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ["▯", "¿", "¡", "PK", "MN", "", "", "", "", "", "", "", "Í", "%", "(", ")"],
    ["", "", "", "", "", "â", "", "", "", "", "", "", "", "", "í", ""],
    ["", "", "", "", "", "", "", "", "↑", "↓", "←", "→", "*", "*", "*", ""],
    ["*", "*", "*", "*", "ᵉ", "<", ">", "", "", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ["ʳᵉ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "!", "?", ".", "-", "･"],

    # Actually checked these ones...
    ["‥", "“", "”", "‘", "'", "♂", "♀", "$", ",", "×", "/", "A", "B", "C", "D", "E"],
    ["F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"],
    ["V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
    ["l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "►"],
    [":", "Ä", "Ö", "Ü", "ä", "ö", "ü", "", "", "", "", "", "", "", "", ""],
]

@dataclass
class T_Base:
    """
    Base class for all primitive types, providing deserialization and comparison methods
    """
    size: ClassVar[int] = 0
    value: int = field(init=False)
    data: bytes

    def __eq__(self, other):
        if isinstance(other, T_Base):
            return self.value == other.value
        else:
            return self.value == other
    
    def __lt__(self, other):
        if isinstance(other, T_Base):
            return self.value < other.value
        else:
            return self.value < other
    
    def __gt__(self, other):
        if isinstance(other, T_Base):
            return self.value > other.value
        else:
            return self.value > other
    
    def __le__(self, other):
        if isinstance(other, T_Base):
            return self.value <= other.value
        else:
            return self.value <= other

    def __ge__(self, other):
        if isinstance(other, T_Base):
            return self.value >= other.value
        else:
            return self.value >= other

    def __and__(self, other):
        if isinstance(other, T_Base):
            return self.value & other.value
        else:
            return self.value & other
    
    def __or__(self, other):
        if isinstance(other, T_Base):
            return self.value | other.value
        else:
            return self.value | other
    
    def __nor__(self, other):
        if isinstance(other, T_Base):
            return self.value ^ other.value
        else:
            return self.value ^ other
    
    def __xor__(self, other):
        if isinstance(other, T_Base):
            return self.value ^ other.value
        else:
            return self.value ^ other
    
    def __lshift__(self, other):
        if isinstance(other, T_Base):
            return self.value << other.value
        else:
            return self.value << other

    def __rshift__(self, other):
        if isinstance(other, T_Base):
            return self.value >> other.value
        else:
            return self.value >> other
    
    def __add__(self, other):
        if isinstance(other, T_Base):
            return self.value + other.value
        else:
            return self.value + other
    
    def __sub__(self, other):
        if isinstance(other, T_Base):
            return self.value - other.value
        else:
            return self.value - other
    
    def __iadd__(self, other):
        if isinstance(other, T_Base):
            self.value += other.value
        else:
            self.value += other
        return self

    def __isub__(self, other):
        if isinstance(other, T_Base):
            self.value -= other.value
        else:
            self.value -= other
        return self
    
    def __mul__(self, other):
        if isinstance(other, T_Base):
            return self.value * other.value
        else:
            return self.value * other
    
    def __rmul__(self, other):
        if isinstance(other, T_Base):
            return self.value * other.value
        else:
            return self.value * other
    
    def __div__(self, other):
        if isinstance(other, T_Base):
            return self.value / other.value
        else:
            return self.value / other
    
    def __index__(self):
        return self.value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value:X})"
    
    def __str__(self):
        return f"{self.__class__.__name__}(0x{self.value:X})"

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Parse a primitive type from a byte array

        Args:
            data (bytes): Byte array of data

        Returns:
            T_Base: an instance of the subclass
        """
        return cls(data=data[:cls.size])
    


@dataclass
class T_Pointer(T_Base):
    """
    Represents a pointer to a location in the ROM
    Occasionally, pointers have the high bit set for some reason
    Use `value` for the raw pointer as it was stored in the ROM (which may be out of bounds)
    Use `rom_addr` for the actual address in the ROM (correcting for the high bit)
    """
    size: ClassVar[int] = 4
    value: int = field(init=False)
    rom_addr: int = field(init=False)

    data: bytes

    def __post_init__(self) -> None:
        """
        Correct for the high bit in the pointer so `rom_addr` is always a valid address
        """
        self.value = int.from_bytes(self.data, "little")
        self.rom_addr = self.value if self.value < 0x8000000 else self.value - 0x8000000
        if self.rom_addr & 0x8000000 == 0x8000000 or self.rom_addr & 0x9000000 == 0x9000000:
            self.rom_addr = -1

    @classmethod
    def from_int(cls, value: int) -> "T_Pointer":
        """
        Create a T_Pointer from an int address

        Args:
            value (int): Address for the pointer

        Returns:
            T_Pointer: An instance of the class
        """
        return cls(data=value.to_bytes(cls.size, "little"))
    


@dataclass
class T_U8(T_Base):
    """
    Unsigned 8-bit int
    """
    size: ClassVar[int] = 1

    def __post_init__(self) -> None:
        self.value = int.from_bytes(self.data, "little")


@dataclass
class T_U16(T_Base):
    """
    Unsigned 16-bit int
    """
    size: ClassVar[int] = 2

    def __post_init__(self) -> None:
        self.value = int.from_bytes(self.data, "little")

@dataclass
class T_U32(T_Base):
    """
    Unsigned 32-bit int
    """
    size: ClassVar[int] = 4

    def __post_init__(self) -> None:
        self.value = int.from_bytes(self.data, "little")


@dataclass
class T_String(T_Base):
    """
    A string of characters
    The pokemon games use a custom encoding for strings, see `CHAR_ENCODING` table
    """

    data: bytes

    def __post_init__(self) -> None:
        self.value = str(self)

    def __str__(self) -> str:
        buf = ""
        for byte in self.data:
            lsb = byte & 0x0F
            msb = (byte & 0xF0) >> 4
            buf += CHAR_ENCODING[msb][lsb]
        return buf
    
    @classmethod
    def from_str(cls, string: str) -> "T_String":
        """
        Create a T_String from a Python string

        Args:
            string (str): Python string to encode

        Returns:
            T_String: An instance of the class
        """
        buf = bytearray()
        for char in string:
            for i, row in enumerate(CHAR_ENCODING):
                for j, cell in enumerate(row):
                    if cell == char:
                        buf.append((i << 4) + j)
        return cls(buf)
        
    @classmethod
    def from_bytes(cls, data: bytes) -> "T_String":
        """
        Parse a string from a byte array
        T_String doesn't have a fixed length, needs to be handled differently to other T_Base types
        """
        return cls(data=data)


@dataclass
class T_Struct:
    """
    A struct base type that can be parsed from a byte array

    Returns:
        T_Struct: An instance of the child class
    """
    rom_data: bytes

    @classmethod
    def from_bytes(cls, data: bytes, offset: T_Pointer = T_Pointer.from_int(0)):
        """
        Parse a generic struct type from a byte array
        Fields are populated in order of definition in the child class
        only fields that are T_Base types are considered

        Args:
            data (bytes): Byte array of struct data. If passing the entire ROM, provide an `offset` pointer.
            offset (T_Pointer): Pointer to the start of the struct data

        Returns:
            T_Struct: An instance of the child class
        """

        fields = [
            f for f in cls.__dataclass_fields__.values() 
            if issubclass(f.type, T_Base)
        ]

        constructor_args = {}

        for field in fields:
            field_value = field.type.from_bytes(data[offset:offset+field.type.size])
            constructor_args[field.name] = field_value
            offset += field.type.size
        
        constructor_args["rom_data"] = data

        return cls(**constructor_args)
