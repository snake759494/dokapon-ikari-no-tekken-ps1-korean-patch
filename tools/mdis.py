import capstone,sys,struct
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
def load_ram(): return open('orig/ram1.bin','rb').read()
def dis(buf,addr,n,base=0x80000000):
    o=addr-base
    for i in md.disasm(buf[o:o+n*4],addr):
        print('%08x: %s %s'%(i.address,i.mnemonic,i.op_str))
if __name__=='__main__':
    r=load_ram(); dis(r,int(sys.argv[1],16),int(sys.argv[2]))
