from romfile import RomFile, T_String, BPRE_OFFSETS, MapTable
import pathlib

def main() -> None:
    # Create a path relative to the current file
    rom_path = pathlib.Path(__file__).parent / "resources" / "fr_rom.gba"
    rom = RomFile(rom_path)

    table = MapTable.from_rom(rom.data, BPRE_OFFSETS["map_headers"])

    breakpoint()



if __name__ == "__main__":
    main()