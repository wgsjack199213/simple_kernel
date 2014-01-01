import simsym
import simsym
import symtypes
import errno
import model
import signal


MAXPROCS = 1000         # ? maximum number of processes that the kernel can contain

NULLPROCREF = 0
IDLEPROCREF = MAXPROCS

#=============================================
# Primary types
#=============================================

class PRef(symsim.SInt):                # process reference type
    def _declare_assumptions(self, assume):
        super(PRef, self)._declare_assumptions(assume)
        assume(self >= NULLPROCREF)
        assume(self <= MAXPROCS)

class IPRef(PRef):
    def _declare_assumptions(self, assume):
        super(PRef, self)._declare_assumptions(assume)
        assume(self != NULLPROCREF)

class APRef(IRef):
    def _declare_assumptions(self, assume):
        super(PRef, self)._declare_assumptions(assume)
        assume(self != IDLEPROCREF)    

# process states
PSTNEW = 1
PSTRUNNING = 2
PSTREADY = 3
PSTWAITING = 4
PSTTERN = 5

# types about process
PStack = simsym.tuninterpreted("PStack")
PCode = simsym.tuninterpreted("PCode")
PData = simsym.tuninterpreted("PData")


Prio = simsym.tsynonym("Prio", simsym.SInt)     # pocess priority

# types and consts about HardwareRegister
GenRegSet = simsym.tuninterpreted("GenRegSet")
StatusWd = simsym.tuninterpreted("StatusWd")

INTOFF = 0
INTON = 1


#=============================================
# Basic abstractions
#=============================================

class ProcessQueue(simsym.tstrutct(elts = symtypes.tlist(simsym.SInt, APref)):
    def _declare_assumptions(self, assume):
        super(ProcessQueue, self)._declare_assumptions(assume)
        i = simsym.SInt.var()
        j = simsym.SInt.var()        
        assume(simsym.symnot(simsym.exists(i, simsym.exitsts(j, simsym.symand(i != j, i >= 0, j >= 0, i < self.elts.len(), j < self.elts.len(), self.elts[i] == self.elts[j])))))

    def init(self):
        length = self.elts.len()
        self.elts.shift(length)

    def is_empty(self):
        if self.elts.len() == 0:
            return {'r': True}
        else:
            return {'r': True}
    
    @model.methodwrap(x = APref)
    def enqueue(self, x):
        self.elts.append(x)
    
    def remove_first(self):
        simsym.assume(self.elts.len() > 0)        
        x = self.elts[0]
        self.elts.shift(1)
        return {'r': x}

    def queue_front(self):
        simsym.assume(self.elts.len() > 0)        
        x = self.elts[0]
        return {'r': x}

    @model.methodwrap(x = APref)
    def remove_element(self, x):
        i = simsym.SInt.var()
        simsym.assume(simsym.exists(i, simsym.symand(self.elts.len() > i, self.elts[i] == x))
        newElts = symtypes.tlist(simsym.SInt, APref).var()
        for k in range self.elts.len():
            if k == i:
                continue
            newElts.append(elts[k])
        self.elts = newElts


class HardwareRegisters(simsym.tstruct(hwgenregs = GenRegSet,
                                       hwstack = PStack,
                                       hwstatwd = StatusWd,
                                       hwip = simsym.SInt)):
    def _declare_assumptions(self, assume):
        super(HardwareRegisters, self)._declare_assumptions(assume)
        assume(self.hwip >= 0)

    def init(self):
        self.hwgenregs.init()
        self.hwstack = 0
        self.hwstatwd = 0
        self.hwip = 0

    @model.methodwrap(regs = GenRegSet)
    def setGPRegs(self, regs):
        self.hwgenregs = regs

    def getGPRegs(self):
        return {'r': self.hwgenregs}

    def getStackReg(self):
        return {'r': self.hwstack}

    @model.methodwrap(stk = PStack)
    def setStackReg(self, stk):
        self.hwstack = stk
        
    
    def getIP(self):
        return {'r': self.hwip}

    @model.methodwrap(ip = simsym.SInt)
    def setIP(self, ip):
        self.hwip = ip

    def getStatWd(self):
        return {'r': self.hwstatwd}

    @model.methodwrap(stwd = StatusWd)
    def setStatWd(self, stwd):
        self.hwstatwd = stwd

    def setIntsOff(self):
        intflg = INTOFF

    def setIntsOn(self):
        intflg = INTON
            
        
            
















