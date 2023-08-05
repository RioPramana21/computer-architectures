# Proj1
# Rio Pramana - 2023318129

import sys # for receiving the command line argument

########## HELPER FUNCTIONS ##########
def read_file(file_name):
    with open(file_name, "rb") as f:
        file_contents = f.read()
    return file_contents

def get_instructions(file_contents):
    instructions = []
    for i in range(0, len(file_contents), 4):
        instruction = int.from_bytes(file_contents[i:i + 4], byteorder = "little")
        instructions.append(instruction)
    return instructions

def twos_complement(val, bits):
    return (1 << bits) + val if val < 0 else val

def sign_extend(val, bits):
    sign_bit = 1 << (bits - 1)
    return (val & (sign_bit - 1)) - (val & sign_bit)
########## HELPER FUNCTIONS ##########

########## MAIN FUNCTIONS ##########
def disassemble_instruction(inst):
    opcode = inst & 0b1111111
    rd = (inst >> 7) & 0b11111
    rs1 = (inst >> 15) & 0b11111
    rs2 = (inst >> 20) & 0b11111
    funct3 = (inst >> 12) & 0b111
    funct7 = (inst >> 25) & 0b1111111

    # Disassemble the instruction based on its opcode..
    # ..and funct3 and funct7 if necessary

    # LUI instruction
    if opcode == 0b0110111:
        imm_20 = inst >> 12
        imm = sign_extend(imm_20, 20) << 12
        return f"lui x{rd}, {imm}"
    
    # AUIPC instruction
    elif opcode == 0b0010111:
        imm = (inst >> 12) << 12
        return f"auipc x{rd}, {imm}"
    
    # JAL instruction
    elif opcode == 0b1101111:
        imm_20 = (inst >> 31) & 0b1
        imm_1_10 = (inst >> 21) & 0b1111111111
        imm_11 = (inst >> 20) & 0b1
        imm_12_19 = (inst >> 12) & 0b11111111
        # Get the immediate/offset
        imm = (imm_20 << 20) | (imm_12_19 << 12) | (imm_11 << 11) | (imm_1_10 << 1)
        # Sign-extending to 32 bits
        offset = sign_extend(imm, 21)
        # Return the output string according to the format
        return f"jal x{rd}, {offset}"
    
    # JALR instruction
    elif opcode == 0b1100111:
        if funct3 == 0b000:
            imm = inst >> 20
            return f"jalr x{rd}, {imm}(x{rs1})"
        
    # Branch instructions
    elif opcode == 0b1100011:
        imm_11 = (inst >> 7) & 0b1
        imm_1_4 = (inst >> 8) & 0b1111
        imm_5_10 = (inst >> 25) & 0b111111
        imm_12 = (inst >> 31) & 0b1
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_5_10 << 5) | (imm_1_4 << 1)
        offset = sign_extend(imm, 12)
        # Calculate the signed offset
        if offset & (1 << 11):
            offset = offset - (1 << 12)
        # Apply 2s complement
        offset = twos_complement(offset, 12)

        if funct3 == 0b000:
            return f"beq x{rs1}, x{rs2}, {offset}"
        elif funct3 == 0b001:
            return f"bne x{rs1}, x{rs2}, {offset}"
        elif funct3 == 0b100:
            return f"blt x{rs1}, x{rs2}, {offset}"
        elif funct3 == 0b101:
            return f"bge x{rs1}, x{rs2}, {offset}"
        elif funct3 == 0b110:
            return f"bltu x{rs1}, x{rs2}, {offset}"
        elif funct3 == 0b111:
            return f"bgeu x{rs1}, x{rs2}, {offset}"
        
    # Load instructions
    elif opcode == 0b0000011:
        imm = (inst >> 20) & 0xFFF
        if imm & 0x800:
            imm = (imm - 0x1000)
            
        if funct3 == 0b000:
            return f"lb x{rd}, {imm}(x{rs1})"
        elif funct3 == 0b001:
            return f"lh x{rd}, {imm}(x{rs1})"
        elif funct3 == 0b010:
            return f"lw x{rd}, {imm}(x{rs1})"
        elif funct3 == 0b100:
            return f"lbu x{rd}, {imm}(x{rs1})"
        elif funct3 == 0b101:
            return f"lhu x{rd}, {imm}(x{rs1})"
        
    # Store instructions
    elif opcode == 0b0100011:
        imm_11_5 = (inst >> 25) & 0b1111111
        imm_4_0 = inst >> 7 & 0b11111
        imm = (imm_11_5 << 5) | imm_4_0
        if imm >= (1 << 11):
            imm -= 1 << 12

        if funct3 == 0b000:
            return f"sb x{rs2}, {imm}(x{rs1})"
        elif funct3 == 0b001:
            return f"sh x{rs2}, {imm}(x{rs1})"
        elif funct3 == 0b010:
            return f"sw x{rs2}, {imm}(x{rs1})"
        
    # ALU instructions
    elif opcode == 0b0010011:
        imm = (inst & 0xFFF00000) >> 20
        shamt = (inst >> 20) & 0x1F
        if imm & 0x800:
            imm = imm - 0x1000

        if funct3 == 0b000:
            return f"addi x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b010:
            return f"slti x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b011:
            return f"sltiu x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b100:
            return f"xori x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b110:
            return f"ori x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b111:
            return f"andi x{rd}, x{rs1}, {imm}"
        elif funct3 == 0b001:
            return f"slli x{rd}, x{rs1}, {shamt}"
        elif funct3 == 0b101:
            if funct7 == 0b0000000:
                return f"srli x{rd}, x{rs1}, {shamt}"
            elif funct7 == 0b0100000:
                return f"srai x{rd}, x{rs1}, {shamt}"
            
    # R-type ALU instructions
    elif opcode == 0b0110011:
        if funct3 == 0b000 and funct7 == 0b0000000:
            return f"add x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b000 and funct7 == 0b0100000:
            return f"sub x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b001 and funct7 == 0b0000000:
            return f"sll x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b010 and funct7 == 0b0000000:
            return f"slt x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b011 and funct7 == 0b0000000:
            return f"sltu x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b100 and funct7 == 0b0000000:
            return f"xor x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b101 and funct7 == 0b0000000:
            return f"srl x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b101 and funct7 == 0b0100000:
            return f"sra x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b110 and funct7 == 0b0000000:
            return f"or x{rd}, x{rs1}, x{rs2}"
        elif funct3 == 0b111 and funct7 == 0b0000000:
            return f"and x{rd}, x{rs1}, x{rs2}"
    else:
        return "unknown instruction"
########## MAIN FUNCTIONS ##########

########## MAIN PROGRAM ##########
def main():
    file_name = "proj1_5.bin"
    # file_name = sys.argv[1]
    file_contents = read_file(file_name)
    instructions = get_instructions(file_contents)
    
    for i, instruction in enumerate(instructions):
        disassembled_instruction = disassemble_instruction(instruction)
        print(f"inst {i}: {instruction:08x} {disassembled_instruction}")

if __name__ == "__main__":
    main()
########## MAIN PROGRAM ##########