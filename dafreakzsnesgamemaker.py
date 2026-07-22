import struct
import zlib

class DafreakzSNESGameMaker:
    def __init__(self, width=256, height=224):
        self.width = width
        self.height = height
        self.tiles = []
        self.palette = [(0,0,0)] * 16
        self.map = [[0]* (width // 8) for _ in range(height // 8)]
        self.sprites = []
        self.code = []
        self.rom = bytearray(0x8000)  # minimal ROM size 32KB

    def set_palette(self, palette):
        # palette: list of 16 RGB tuples (0-255)
        self.palette = palette[:16]

    def add_tile(self, tile_data):
        # tile_data: 8x8 pixels, each pixel 0-15 (4bpp)
        if len(tile_data) != 64:
            raise ValueError("Tile data must be 64 pixels")
        self.tiles.append(tile_data)
        return len(self.tiles) - 1

    def set_map_tile(self, x, y, tile_index):
        self.map[y][x] = tile_index

    def add_sprite(self, x, y, tile_index):
        self.sprites.append((x, y, tile_index))

    def add_code(self, asm_bytes):
        self.code.extend(asm_bytes)

    def build_header(self):
        # Build minimal SNES ROM header at 0x7FC0 (LoROM)
        header = bytearray(0x40)
        # Title (21 bytes)
        title = b'Dafreakz SNES Game Maker'
        header[0:len(title)] = title
        # Map mode (LoROM)
        header[0x15] = 0x20
        # Cartridge type (ROM only)
        header[0x16] = 0x00
        # ROM size (32KB = 0x00)
        header[0x17] = 0x00
        # SRAM size
        header[0x18] = 0x00
        # Country (NTSC USA)
        header[0x19] = 0x01
        # License code
        header[0x1A] = 0x33
        # Version
        header[0x1B] = 0x00
        # Checksum and complement (to be calculated)
        checksum = 0
        for b in self.rom[:-4]:
            checksum = (checksum + b) & 0xFFFF
        checksum_complement = 0xFFFF - checksum
        struct.pack_into('<H', header, 0x1C, checksum_complement)
        struct.pack_into('<H', header, 0x1E, checksum)
        return header

    def build_tile_data(self):
        # Convert tiles to SNES 4bpp planar format
        data = bytearray()
        for tile in self.tiles:
            # tile is 64 pixels 0-15
            # SNES 4bpp: 32 bytes per tile, 2 bits per plane per line
            for plane in range(4):
                for y in range(8):
                    byte1 = 0
                    byte2 = 0
                    for x in range(8):
                        pixel = tile[y*8 + x]
                        bit = (pixel >> plane) & 1
                        if x < 8:
                            byte1 |= bit << (7 - x)
                    data.append(byte1)
        return data

    def build_map_data(self):
        # Build map data as tile indices 16-bit little endian
        data = bytearray()
        for row in self.map:
            for tile_index in row:
                data += struct.pack('<H', tile_index)
        return data

    def build_rom(self):
        # Build ROM with header, tiles, map, code
        # Place header at 0x7FC0 (LoROM)
        header = self.build_header()
        # Place tiles at 0x0000
        tile_data = self.build_tile_data()
        # Place map after tiles
        map_data = self.build_map_data()
        # Place code after map
        code_data = bytes(self.code)

        # Clear ROM
        self.rom = bytearray(0x8000)
        # Copy tile data
        self.rom[0x0000:0x0000+len(tile_data)] = tile_data
        # Copy map data
        map_start = 0x0000 + len(tile_data)
        self.rom[map_start:map_start+len(map_data)] = map_data
        # Copy code data
        code_start = map_start + len(map_data)
        self.rom[code_start:code_start+len(code_data)] = code_data
        # Copy header
        self.rom[0x7FC0:0x7FC0+len(header)] = header
        return self.rom

    def save_rom(self, filename):
        rom = self.build_rom()
        with open(filename, 'wb') as f:
            f.write(rom)

# Example template game using DafreakzSNESGameMaker
def example_game():
    game = DafreakzSNESGameMaker()

    # Set a simple grayscale palette
    palette = [(i*17, i*17, i*17) for i in range(16)]
    game.set_palette(palette)

    # Create a simple tile: checkerboard 8x8
    tile = []
    for y in range(8):
        for x in range(8):
            tile.append((x+y) % 2 * 15)
    tile_index = game.add_tile(tile)

    # Fill map with the tile
    for y in range(game.height // 8):
        for x in range(game.width // 8):
            game.set_map_tile(x, y, tile_index)

    # Add a sprite at (100,100)
    game.add_sprite(100, 100, tile_index)

    # Add simple code (dummy NOPs for example)
    # SNES 65816 NOP opcode = 0xEA
    game.add_code([0xEA] * 16)

    # Save ROM
    game.save_rom('example.smc')

if __name__ == '__main__':
    example_game()
