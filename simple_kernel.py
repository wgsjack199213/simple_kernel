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
# Process related
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

PStack = simsym.tuninterpreted("Pstack")
PCode = simsym.tuninterpreted("Pcode")
PData = simsym.tuninterpreted("Pdata")

Prio = simsym.tsynonym("Prio", simsym.SInt)     # pocess priority


#=============================================
# Basic abstractions
#=============================================

class ProcessQueue(simsym.tstrutct(elts = symtypes.tlist(simsym.SInt, APref)):
    def is_empty(self):
        if self.elts.len() == 0:
            return {'r': True}
        else:
            return {'r': True}
    
    @model.methodwrap(x = APref)
    def enqueue(self, x):
        self.elts.append(x)
    
    def remove_first:
        simsym.assume(self.elts.len() > 0)        
        x = self.elts[0]
        self.elts.shift(1)
        return {'r': x}

    def queue_front:
        simsym.assume(self.elts.len() > 0)        
        x = self.elts[0]
        return {'r': x}

    @model.methodwrap(x = APref)
    def remove_element:
        
            
















