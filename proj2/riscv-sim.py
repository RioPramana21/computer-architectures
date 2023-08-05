# Proj2
# Rio Pramana - 2023318129

import sys # for receiving the command line argument
from collections import defaultdict # for data memory

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
        imm_20 = inst >> 12
        imm = sign_extend(imm_20, 20) << 12
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
    
def execute_instruction(inst, pc, registers, data_memory):
    opcode = inst & 0b1111111
    rd = (inst >> 7) & 0b11111
    rs1 = (inst >> 15) & 0b11111
    rs2 = (inst >> 20) & 0b11111
    funct3 = (inst >> 12) & 0b111
    funct7 = (inst >> 25) & 0b1111111

    # LUI instruction
    if opcode == 0b0110111:
        imm_20 = inst >> 12
        imm = sign_extend(imm_20, 20) << 12
        if rd != 0:
            registers[rd] = imm
    
    # AUIPC instruction
    elif opcode == 0b0010111:
        imm_20 = inst >> 12
        imm = sign_extend(imm_20, 20) << 12
        if rd != 0:
            registers[rd] = pc + imm
    
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
        if rd != 0:
            registers[rd] = pc + 4
        pc += offset
        return pc

    # JALR instruction
    elif opcode == 0b1100111 and funct3 == 0b000:
        imm = (inst >> 20) & 0xFFF
        imm = sign_extend(imm, 12)
        tmp = registers[rs1] + imm
        if rd != 0:
            registers[rd] = pc + 4
        pc = tmp & ~1
        return pc

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

        # BEQ
        if funct3 == 0b000 and registers[rs1] == registers[rs2]:
            pc += offset
            return pc
        # BNE
        elif funct3 == 0b001 and registers[rs1] != registers[rs2]:
            pc += offset
            return pc
        # BLT
        elif funct3 == 0b100 and registers[rs1] < registers[rs2]:
            pc += offset
            return pc
        # BGE
        elif funct3 == 0b101 and registers[rs1] >= registers[rs2]:
            pc += offset
            return pc
        
        # # BLTU
        # elif funct3 == 0b110 and (registers[rs1] < registers[rs2] & 0xFFFFFFFF):
        #     pc += offset
        #     return pc
        # # BGEU
        # elif funct3 == 0b111 and (registers[rs1] >= registers[rs2] & 0xFFFFFFFF):
        #     pc += offset
        #     return pc
        
    # Load instructions
    elif opcode == 0b0000011:
        imm = (inst >> 20) & 0xFFF
        if imm & 0x800:
            imm = (imm - 0x1000)
        
        mem_addr = registers[rs1] + imm

        # # LB
        # if funct3 == 0b000:
        #     registers[rd] = sign_extend(data_memory[mem_addr], 8)
        # # LH
        # elif funct3 == 0b001:
        #     registers[rd] = sign_extend(data_memory[mem_addr] | (data_memory[mem_addr + 1] << 8), 16)

        # LW
        if funct3 == 0b010:
            if mem_addr == 0x20000000:
                registers[rd] = int(input())
            else:
                registers[rd] = data_memory[mem_addr] | (data_memory[mem_addr + 1] << 8) | (data_memory[mem_addr + 2] << 16) | (data_memory[mem_addr + 3] << 24)
                registers[rd] = sign_extend(registers[rd], 32)

        # # LBU
        # elif funct3 == 0b100:
        #     registers[rd] = data_memory[mem_addr]
        # # LHU
        # elif funct3 == 0b101:
        #     registers[rd] = data_memory[mem_addr] | (data_memory[mem_addr + 1] << 8)

    # Store instructions
    elif opcode == 0b0100011:
        imm_11_5 = (inst >> 25) & 0b1111111
        imm_4_0 = inst >> 7 & 0b11111
        imm = (imm_11_5 << 5) | imm_4_0
        if imm >= (1 << 11):
            imm -= 1 << 12

        mem_addr = registers[rs1] + imm

        # # SB
        # if funct3 == 0b000:
        #     data_memory[mem_addr] = registers[rs2] & 0xFF
        # # SH
        # elif funct3 == 0b001:
        #     data_memory[mem_addr] = registers[rs2] & 0xFF
        #     data_memory[mem_addr + 1] = (registers[rs2] >> 8) & 0xFF
        
        # SW
        if funct3 == 0b010:
            if mem_addr == 0x20000000:
                print(chr(registers[rs2] & 0xFF), end='')
            else:
                data_memory[mem_addr] = registers[rs2] & 0xFF
                data_memory[mem_addr + 1] = (registers[rs2] >> 8) & 0xFF
                data_memory[mem_addr + 2] = (registers[rs2] >> 16) & 0xFF
                data_memory[mem_addr + 3] = (registers[rs2] >> 24) & 0xFF

    # ALU instructions
    elif opcode == 0b0010011:
        imm = (inst & 0xFFF00000) >> 20
        shamt = (inst >> 20) & 0x1F
        imm = sign_extend(imm, 12)

        if rd != 0:
            # ADDI
            if funct3 == 0b000:
                registers[rd] = (registers[rs1] + imm) & 0xFFFFFFFF
            # SLTI
            elif funct3 == 0b010:
                registers[rd] = 1 if registers[rs1] < imm else 0
            
            # # SLTIU
            # elif funct3 == 0b011:
            #     registers[rd] = 1 if (registers[rs1] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
            
            # XORI
            elif funct3 == 0b100:
                registers[rd] = registers[rs1] ^ imm
            # ORI
            elif funct3 == 0b110:
                registers[rd] = registers[rs1] | imm
            # ANDI
            elif funct3 == 0b111:
                registers[rd] = registers[rs1] & imm
            # SLLI
            elif funct3 == 0b001:
                registers[rd] = (registers[rs1] & 0xFFFFFFFF) << shamt
            elif funct3 == 0b101:
                # SRLI
                if funct7 == 0b0000000:
                    registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> shamt
                # SRAI
                elif funct7 == 0b0100000:
                    temp = (registers[rs1] & 0xFFFFFFFF)
                    shamt = shamt & 0x1F
                    sign_bit = temp & 0x80000000
                    if sign_bit:
                        registers[rd] = (temp >> shamt) | ((0xFFFFFFFF << (32 - shamt)) & 0xFFFFFFFF)
                    else:
                        registers[rd] = temp >> shamt
                    registers[rd] = registers[rd] & 0xFFFFFFFF

    # R-type ALU instructions
    elif opcode == 0b0110011:
        if rd != 0:
            # ADD
            if funct3 == 0b000 and funct7 == 0b0000000:
                registers[rd] = registers[rs1] + registers[rs2]
            # SUB
            elif funct3 == 0b000 and funct7 == 0b0100000:
                registers[rd] = registers[rs1] - registers[rs2]
            # SLL
            elif funct3 == 0b001 and funct7 == 0b0000000:
                registers[rd] = registers[rs1] << (registers[rs2] & 0x1F)
            # SLT
            elif funct3 == 0b010 and funct7 == 0b0000000:
                rs1_val = registers[rs1]
                rs2_val = registers[rs2]
                if rs1_val & 0x80000000:
                    rs1_val -= 0x100000000
                if rs2_val & 0x80000000:
                    rs2_val -= 0x100000000
                registers[rd] = 1 if rs1_val < rs2_val else 0
            
            # # SLTU
            # elif funct3 == 0b011 and funct7 == 0b0000000:
            #     registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
            
            # XOR
            elif funct3 == 0b100 and funct7 == 0b0000000:
                registers[rd] = registers[rs1] ^ registers[rs2]
            # SRL
            elif funct3 == 0b101 and funct7 == 0b0000000:
                registers[rd] = (registers[rs1] & 0xFFFFFFFF) >> (registers[rs2] & 0x1F)
            # SRA
            elif funct3 == 0b101 and funct7 == 0b0100000:
                registers[rd] = registers[rs1] >> (registers[rs2] & 0x1F)
            # OR
            elif funct3 == 0b110 and funct7 == 0b0000000:
                registers[rd] = registers[rs1] | registers[rs2]
            # AND
            elif funct3 == 0b111 and funct7 == 0b0000000:
                registers[rd] = registers[rs1] & registers[rs2]
    else:
        print("unknown instruction")

    pc += 4
    return pc
########## MAIN FUNCTIONS ##########

########## MAIN PROGRAM ##########
def main():
    # Read cmd arguments
    instructions_file = sys.argv[1]
    num_of_args = len(sys.argv)
    if(num_of_args == 3):
        num_instructions = int(sys.argv[2])
    else:
        data_file = sys.argv[2]
        num_instructions = int(sys.argv[3])
    
    # Read the files
    instructions_contents = read_file(instructions_file)
    data_contents = b'' if num_of_args == 3 else read_file(data_file)

    # Get the instructions and initialize registers + data memory
    instructions = get_instructions(instructions_contents)
    registers = [0x00000000] * 32
    DATA_MEMORY_START = 0x10000000

    data_memory = defaultdict(lambda: 0xFF)
    for j in range(len(data_contents)):
        data_memory[DATA_MEMORY_START + j] = data_contents[j]

    # Execute each instructions
    pc = 0
    for _ in range(num_instructions):
        if pc >= len(instructions) * 4:
            break
        inst = instructions[pc // 4]
        pc = execute_instruction(inst, pc, registers, data_memory)

    for i, reg in enumerate(registers):
        print(f"x{i}: {reg & 0xffffffff:#010x}")

if __name__ == "__main__":
    main()
########## MAIN PROGRAM ##########