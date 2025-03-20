from pydantic.dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from copy import copy

from types_primitive import *


BPRE_OFFSETS = {
    "map_headers": 0x05524C,
    "map_labels": 0x3F1CAC,
    "sprites": 0x39FDB0,
    "spire_palettes": 0x3A5158,
}

#region lifted from blue-spider, refactor into the T_Pointer class

def get_rom_addr(ptr: T_Pointer) -> T_Pointer:
    if ptr >= 0x8000000:
        ptr -= 0x8000000
    return ptr

def check_rom_addr(ptr: T_Pointer) -> T_Pointer:
    if ptr & 0x8000000 == 0x8000000 or ptr & 0x9000000 == 0x9000000:
        return ptr
    else:
        return -1

def read_rom_addr_at(rom: bytes, ptr: T_Pointer) -> T_Pointer:
    addr = T_Pointer(rom[ptr:ptr+T_Pointer.size])
    return get_rom_addr(check_rom_addr(addr))

#endregion


@dataclass
class MapData(T_Struct):
    width: T_U32
    height: T_U32
    border_ptr: T_Pointer
    tilemap_ptr: T_Pointer
    global_tileset_ptr: T_Pointer
    local_tileset_ptr: T_Pointer

    # FR Only
    border_width: T_U8
    border_height: T_U8

class EventsHeader(T_Struct):
    n_people: T_U8
    n_warps: T_U8
    n_triggers: T_U8
    n_signposts: T_U8
    person_event_ptr: T_Pointer
    warp_event_ptr: T_Pointer
    trigger_event_ptr: T_Pointer
    signpost_event_ptr: T_Pointer

class EventPerson(T_Struct):
    person_id: T_U8
    sprite_id: T_U8
    unknown1: T_U8
    unknown2: T_U8
    posX: T_U16
    posY: T_U16
    unknown3: T_U8
    mov_type: T_U8
    mov: T_U8
    unknown4: T_U8
    is_trainer: T_U8
    unknown5: T_U8
    radius: T_U16
    script_ptr: T_Pointer
    flags: T_U16
    unknown6: T_U8
    unknown7: T_U8

class EventWarp(T_Struct):
    posX: T_U16
    posY: T_U16
    unknown: T_U8
    warp_id: T_U8
    map_id: T_U8
    bank_id: T_U8

class EventTrigger(T_Struct):
    posX: T_U16
    posY: T_U16
    unknown1: T_U8
    var_id: T_U16
    var_value: T_U16
    unknown2: T_U8
    unknown3: T_U8
    script_ptr: T_Pointer

class EventSignpost(T_Struct):
    posX: T_U16
    posY: T_U16
    talking_level: T_U8
    trigger_type: T_U8
    unknown1: T_U8
    unknown2: T_U8

@dataclass
class MapHeader(T_Struct):
    map_data_ptr: T_Pointer
    event_data_ptr: T_Pointer
    level_script_ptr: T_Pointer
    connections_ptr: T_Pointer
    song_index: T_U16
    map_ptr_index: T_U16
    label_index: T_U8
    is_cave: T_U8
    weather: T_U8
    map_type: T_U8

    # FR only
    unknown: T_U8
    show_label: T_U8
    battle_type: T_U8

    # Resolved pointers
    map_data: MapData = field(init=False)
    # event_data: MapEventData = field(init=False)
    # level_script: MapLevelScript = field(init=False)
    # connections: MapConnections = field(init=False)

    def __post_init__(self):
        print(self.label)
        self.map_data = MapData.from_bytes(self.rom_data, self.map_data_ptr.rom_addr)
        self.event_data = EventsHeader.from_bytes(self.rom_data, self.event_data_ptr.rom_addr)

    @property
    def label(self) -> str:
        """
        Return the map label from the label index.
        
        Heavily inspired by blue-spider
        The structure of the label pointer storage differs between games.
        On R/S/E, there are 4 padding bytes between each pointer: [4][ptr][4][ptr]...
        On FR(/LG?), there are no padding bytes: [ptr][ptr]... but the label index is 88 bytes off.

        Returns:
            str: The map label
        """
        label_store_ptr = get_rom_addr(T_Pointer.from_int(BPRE_OFFSETS["map_labels"]))

        # Only focusing on FR for now, but I'll include this in case I come back
        # to add game enums or something
        game = "FR"

        padding = {"FR": 0, "RS": 4, "EM": 4}[game]
        if game == "FR":
            self.label_index -= 88

        label_ptr_ptr = label_store_ptr + self.label_index * (T_Pointer.size + padding) + padding
        
        ptr = T_Pointer.from_bytes(
            self.rom_data[label_ptr_ptr:]
        )
        str_length = self.rom_data[ptr.rom_addr:].find(b"\xFF")
        mem = self.rom_data[ptr.rom_addr:ptr.rom_addr+str_length]# ?
        return T_String.from_bytes(mem)

#        labels = []
#
#        for i in range(0x59 if game == "FR" else 0x6D):
#            ptr = T_Pointer.from_bytes(
#                self.rom_data[label_store_ptr.rom_addr + i * (T_Pointer.size + padding) + padding :]
#            )
#            str_length = self.rom_data[ptr.rom_addr:].find(b"\xFF")
#            mem = self.rom_data[ptr.rom_addr:ptr.rom_addr+str_length]# ?
#            label = T_String.from_bytes(mem)
#            labels.append(label)
#            breakpoint()

#        if self.label_index >= len(labels):
#            return "INVALID_LABEL_INDEX"
#
#        return labels[self.label_index].value



@dataclass
class MapBank:
    base_offset: T_Pointer
    pointer_list: list[T_Pointer]
    headers: list[MapHeader] = field(init=False)

    @classmethod
    def from_rom(cls, data: bytes, base_offset: T_Pointer):
        seek_addr = copy(base_offset) 
        pointer_list = []
        headers = []

        # Read the header pointers
        while True:
            if (addr := read_rom_addr_at(data, seek_addr)) == -1:
                break
            pointer_list.append(addr)
            seek_addr += T_Pointer.size

        # Parse the headers
        for ptr in pointer_list:
            # print(f"Reading header at {ptr}")
            headers.append(MapHeader.from_bytes(data, ptr))
        
        return cls(base_offset=base_offset, pointer_list=pointer_list, headers=headers)


    def __repr__(self):
        return f"{self.__class__.__name__} @ {self.base_offset}, ({len(self.pointer_list)} pointers)"


@dataclass
class MapTable:
    banks: list[MapBank]

    @classmethod
    def from_rom(cls, data: bytes, offset: int):
        banks = []
        seek_addr = read_rom_addr_at(data, T_Pointer.from_int(offset))
        print(f"Reading map headers from {seek_addr}")

        while True:
            if (bank_addr := read_rom_addr_at(data, seek_addr)) == -1:
                break
            banks.append(MapBank.from_rom(data, bank_addr))
            print(f"Found bank at {seek_addr}: Addr {bank_addr} ({len(banks[-1].pointer_list)} headers)")
            seek_addr += T_Pointer.size
        
        return cls(banks)
    


@dataclass
class RomFile:
    path: Path
    data: bytes = field(init=False)

    def __post_init__(self):
        self.data = self.path.read_bytes()
