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

class ProcessQueue(simsym.tstruct(elts = symtypes.tlist(simsym.SInt, APref)):
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



#=========================================
# Semaphore
#=========================================

class Semaphore(simsym.tstruct(waiters = ProcessQueue,
                               scnt = simsym.SInt,
                               initval = simsym.SInt,
                               ptab = ProcessTable,
                               sched = LowLevelScheduler,
                               ctxt = Context,
                               lck = Lock)):
    def _declare_assumptions():
        simsym.assume(scnt >= 0)
        simsym.assume(initval >= 0)

    @model.methodwrap(iv = simsym.SInt,
                      pt = ProcessTable,
                      sch = LowLevelScheduler,
                      ct = Context,
                      lk = Lock)
    def init(self):
        initval = iv
        scnt = iv
        ptab = pt
        sched = sch
        ctxt = ct
        lck = lk
        waiters.init()

    @model.methodwrap()
    def wait(self):
        lck.lock()
        scnt = scnt - 1
        if scnt < 0:
            waiters.enqueue(currentp)
            cpd = ptab.descr_of_process(currentp)
            cpd.set_process_status_to_waiting()
            ctxt.switch_context_out()
            shed.make_unready(currentp)
            shed.run_next_process()
        else:
            sched.continue_current()
        lck.unlock()

    @model.methodwrap()
    def signal(self):
        lck.lock()
        scnt = scnt + 1
        if scnt <= 0:
            waiters.remove_first_proc(currentp)
            cpd = ptab.descr_of_process(currentp)
            cpd.set_process_status_to_ready()
            sched.make_ready(currentp)
        else:
            sched.continue_current()
        lck.unlock()





