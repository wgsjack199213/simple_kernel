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
PSTTERM = 5

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
        simsym.assume(self.scnt >= 0)
        simsym.assume(self.initval >= 0)

    @model.methodwrap(iv = simsym.SInt,
                      pt = ProcessTable,
                      sch = LowLevelScheduler,
                      ct = Context,
                      lk = Lock)
    def init(self,iv,pt,sch.ct,lk):
        self.initval = iv
        self.scnt = iv
        self.ptab = pt
        self.sched = sch
        self.ctxt = ct
        self.lck = lk
        self.waiters.init()

    @model.methodwrap()
    def wait(self):
        self.lck.lock()
        self.scnt = self.scnt - 1
        if self.scnt < 0:
            self.waiters.enqueue(currentp)
            self.cpd = self.ptab.descr_of_process(currentp)
            self.cpd.set_process_status_to_waiting()
            self.ctxt.switch_context_out()
            self.shed.make_unready(currentp)
            self.shed.run_next_process()
        else:
            self.sched.continue_current()
        self.lck.unlock()

    @model.methodwrap()
    def signal(self):
        self.lck.lock()
        self.scnt = self.scnt + 1
        if self.scnt <= 0:
            self.waiters.remove_first_proc(currentp)
            self.cpd = self.ptab.descr_of_process(currentp)
            self.cpd.set_process_status_to_ready()
            self.sched.make_ready(currentp)
        else:
            self.sched.continue_current()
        self.lck.unlock()

#=========================================
# ProcessDescr
#=========================================

class ProcessDescr(simsym.struct(prio = Prio,
                                 status = ProcStatus,
                                 regs = GenRegSet,
                                 statwd = StatusWd,
                                 ip = simsym.SInt,
                                 stack = PStack,
                                 data = PData,
                                 code = PCode,
                                 mem = MemDesc,
                                 memsize = simsym.SInt):
    def _declare_assumptions():
        simsym.assume(self.ip >= 0)
        simsym.assume(self.memsize >= 0)

    @model.methodwrap(pr = Prio,
                      stat = ProcStatus,
                      pstack = PStack,
                      pdata = PData,
                      pcode = PCode,
                      mem = MemDesc,
                      msz = simsym.SInt)
    def init(self, pr, stat, pstack, pdata, pcode, mem, msz):
        self.prio = pr,
        self.status = stat
        self.regs.init()
        self.statwd = 0
        self.ip = 0
        self.data = pdata
        self.code = pcode
        self.mem = mem
        self.memsize = msz

    @model.methodwrap()
    def priority(self):
        return self.prio

    @model.methodwrap(pr = Prio)
    def set_priority(self, pr):
        self.prio = pr

    @model.methodwrap()
    def process_status(self):
        return self.status

    @model.methodwrap()
    def set_process_status_to_new(self):
        self.status = PSTNEW

    @model.methodwrap()
    def set_process_status_to_terminated(self):
        self.status = PSTTERM

    @model.methodwrap()
    def set_process_status_to_ready(self):
        self.status = PSTREADY

    @model.methodwrap()
    def set_process_status_to_running(self):
        self.status = PSTRUNNING

    @model.methodwrap()
    def set_process_status_to_waiting(self):
        self.status = PSTWAITING

    @model.methodwrap()
    def store_size(self):
        return self.memsize

    @model.methodwrap()
    def store_descr(self):
        return self.mem

    @model.methodwrap(newmem = MemDesc)
    def set_store_descr(self, newmem):
        self.mem = newmem

    @model.methodwrap()
    def full_context(self):
        return self.regs, self.ip, self.statwd, self.stack

    @model.methodwrap(pregs = GenRegSet, pip = simsym.SInt, pstatwd = StatusWd, pstack = PStack)
    def set_full_context(self, pregs, pip, pstatwd, pstack):
        self.regs = pregs
        self.ip = pip
        self.statuswd = pstatwd
        self.pstack = pstack


