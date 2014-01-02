import simsym
import symtypes
import errno
import model
import signal


MAXPROCS = 1000         # ? maximum number of processes that the kernel can contain

NULLPROCREF = 0
IDLEPROCREF = MAXPROCS

#=============================================
#
# 3.3 Primary Types
#
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
#
# 3.4 Basic Abstractions
#
#=============================================


#=========================================
# Process Queue
#=========================================

class ProcessQueue(simsym.tstrutct(elts = symtypes.tlist(simsym.SInt, APref))):
    def _declare_assumptions(self, assume):
        super(ProcessQueue, self)._declare_assumptions(assume)
        # 'iseq' restriction
        i = simsym.SInt.var()
        j = simsym.SInt.var()
        assume(simsym.symnot(simsym.exists(i, simsym.exists(j, simsym.symand(i != j, i >= 0, j >= 0, i < self.elts.len(), j < self.elts.len(), self.elts[i] == self.elts[j])))))

    def init(self):
        length = self.elts.len()
        self.elts.shift(length)

    def is_empty(self):
        if self.elts.len() == 0:
            return True
        else:
            return True

    @model.methodwrap(x = APref)
    def enqueue(self, x):
        simsym.assume(x > NULLPROCREF)
        simsym.assume(x < IDLEPROCREF)
        self.elts.append(x)

    def remove_first(self):
        simsym.assume(self.elts.len() > 0)
        x = self.elts[0]
        self.elts.shift(1)
        return x

    def queue_front(self):
        simsym.assume(self.elts.len() > 0)
        x = self.elts[0]
        return x

    @model.methodwrap(x = APref)
    def remove_element(self, x):
        i = simsym.SInt.var()
        simsym.assume(simsym.exists(i, simsym.symand(self.elts.len() > i, self.elts[i] == x)))
        newElts = symtypes.tlist(simsym.SInt, APref).var()
        k = simsym.SInt.var()
        k = 0
        while k < self.elts.len():
            if k != i:
                newElts.append(elts[k])
            k = k + 1

        self.elts = newElts


#=========================================
# Hardware Register
#=========================================

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
    def set_gp_regs(self, regs):
        self.hwgenregs = regs

    def get_gp_regs(self):
        return self.hwgenregs

    def get_stack_reg(self):
        return self.hwstack

    @model.methodwrap(stk = PStack)
    def set_stack_reg(self, stk):
        self.hwstack = stk


    def get_ip(self):
        return self.hwip

    @model.methodwrap(ip = simsym.SInt)
    def set_ip(self, ip):
        self.hwip = ip

    def get_stat_wd(self):
        return self.hwstatwd

    @model.methodwrap(stwd = StatusWd)
    def set_stat_wd(self, stwd):
        self.hwstatwd = stwd

    def set_ints_off(self):
        intflg = INTOFF

    def set_ints_on(self):
        intflg = INTON

#=========================================
# Lock
#=========================================
class Lock(simsym.tstruct(hw = HardwareRegisters)):
    @model.methodwrap(hwrgs = HardwareRegisters)
    def init(self, hwrgs):
        hw = hwrgs

    def lock(self):
        hw.setIntsOff

    def unlock(self):
        hw.setIntsOn


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
# Process Descriptor
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



#=============================================
# Context
#=============================================
class Context(simsym.struct(ptab = ProcessTable, shed = LowLevelScheduler, hw = HardwareRegisters)):

    @model.methodwrap(ptb = ProcessTable, shd = LowLevelScheduler, hwregs = HardwareRegisters)
    def init(self,ptb,shd,hwregs):
        self.ptab = ptb
        self.shed = shd
        self.hw = hwregs

    @model.methodwrap()
    def save_state(self):
        cp = self.shed.current_process()
        pd = self.ptab.descr_of_process(cp)
        regs = self.hw.get_gp_regs()
        stk = self.hw.get_stack_regs()
        ip = self.hw.get_ip()
        stat = self.get_stat_wd()
        pd.set_full_context(regs, ip, stat, stk)

    @model.methodwrap()
    def restore_state(self):
        cp = self.shed.current_process()
        pd = self.ptab.descr_of_process(cp)
        regs,ip,stat,stk = pd.full_context()
        self.hw.set_gp_regs(regs)
        self.hw.set_stack_regs(stk)
        self.hw.set_ip(ip)
        self.hw.set_stat_wd(stat)

    @model.methodwrap()
    def swap_out(self):
        cp = self.shed.current_process()
        pd = self.ptab.descr_of_process(cp)
        pd.set_process_status_to_waiting
        self.save_state
        self.shed.make_unready(currentp)
        self.shed.schedule_next

    @model.methodwrap()
    def swap_in(self):
        cp = self.shed.current_process()
        pd = self.ptab.descr_of_process(cp)
        pd.set_process_status_to_running
        self.restore_state

    @model.methodwrap()
    def switch_context(self):
        self.swap_out()
        self.swap_in()

#=============================================
#
# 3.7 Messages and Semaphore Tables
#
#=============================================

MsgData = simsym.tuninterpreted("MsgData")
MsgSrc = simsym.tuninterpreted("MsgSrc")

class MboxMsg(simsym.struct(src = MsgSrc, data = MsgData)):
    @model.methodwrap(ms = MsgSrc, md = MsgData)
    def init(self, ms, md):
        self.src = ms
        self.data = md

    @model.methodwrap()
    def msgsender(self):
        return src

    @model.methodwrap()
    def msgdata(self):
        return data

class Mailbox(simsym.struct(msgs = symtypes.tlist(simsym.SInt, MboxMsg), lck = Lock)):
    @model.methodwrap(l = Lock)
    def init(self, l):
        # init msgs
        self.lck = l

    @model.methodwrap(m = MboxMsg)
    def post_message(self, m):
        self.lck.lock()
        self.msgs.append(m)
        self.lck.unlock()

    @model.methodwrap()
    def have_messages(self):
        self.lck.lock()
        r = (self.msgs.len() > 0)
        self.lck.unlock()
        return r

    @model.methodwrap()
    def next_message(self):
        self.lck.lock()
        x = self.msgs[0]
        self.msgs.shift(1)
        self.lck.unlock()
        return x

SemaId = simsym.tuninterpreted("SemaId")

class SemaphoreTable(simsym.struct(lck = Lock, stbl = simsym.tdict(SemaId, Semaphore))):
    @model.methodwrap(l = Lock)
    def init(self, l):
        self.lck = l
        #init stbl

    @model.methodwrap()
    def new_semaphore(self):
        self.lck.lock()
        s = Semaphore()
        s.init()
        sid = SemaId().var()
        self.stbl[sid] = s
        self.lck.unlock()

    @model.methodwrap(sid = SemaId)
    def del_semaphore(self, sid):
        self.lck.lock()
        del self.stbl[sid]
        self.lck.unlock()

    @model.methodwrap(sid = SemaId)
        self.lck.lock()
        s = self.stbl[sid]
        self.lck.unlock()
        return s

#=============================================
#
# 3.8 Process Creation and Destruction
#
#=============================================

class UserLibrary(simsym.struct(procid = IPREF, ptab = ProcessTable, sched = Scheduler)):
    @model.methodwrap(ptb = ProcessTable, schd = Scheduler)
    def init(self, ptb, schd):
        self.ptab = ptb
        self.sched = schd

    @model.methodwrap(pprio = Prio,
                      stat = StatusWd,
                      stkd = PStack,
                      datad = PData,
                      cdd = PCode,
                      allocin = MemDesc,
                      totmemsz = simsym.SInt
                      )
    def create_process(self, pprio, stat, stkd, datad, cdd, allocin, tomemsz):
        pd = ProcessDescr()
        pd.init(pprio, stat, stkd, datad, cdd, allocin, totmemsz)
        pid = self.ptab.add_process(pd)
        self.sched.make_ready(pid)
        proid = pid
        return pid

    @model.methodwrap()
    def terminate_proces(self):
        self.sched.make_unready(procid)
        self.ptab.del_process(procid)

    @model.methodwrap()
    def suspend(self):
        self.sched.suspend_current()


#=============================================
#
# 3.5 Priority Queue
#
#=============================================

# In order to define the var 'procs' of ProcPrioQueue,
# new var should be defined to implement the operation described below conveniently.
# Each element should be described as two maps:
# [(current.id => current.prev().id), (current.id => current.next().id)]
# use tdict for implementation
# Notice the sets of keys of the two dictionary procs_prev and procs_next shold be identical!!!
class ProcPrioQueue(simsym.struct(qprio = simsym.tdict(PRef, Prio),
                                  procs_prev = simsym.tdict(PRef, PRef),
                                  procs_next = simsym.tdict(PRef, PRef))):
    def _declare_assumptions(self, assume):
        super(ProcessQueue, self)._declare_assumptions(assume)
        # injection restriction
        k = PRef.var()
        assume(forall(k, implies(qprio.contains(k), symand(procs_prev.contains(k), procs_next.contains(k)))))
        # 'iseq' restriction
        # ? As I use two dicts rather than one queue to define procs, maybe I do not need to specify this restriction?

        # priority order restriction
        assume(forall(k, implies(qprio.contains(k), symand(symor(procs_prev[k] == NULLPROCREF, qprio[procs_prev[k]] < qprio[k]), symor(procs_next[k] == NULLPROCREF, qprio[procs_next[k]] > qprio[k]))))

    def init(self):
        self.procs_prev = simsym.tdict(PRef, PRef).var()
        self.procs_next = simsym.tdict(PRef, PRef).var()

    @model.methodwrap(pid = PRef, pprio = Prio)
    def enqueue_proc_prio_queue(self, pid, pprio):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        simsym.assume(pprio >= 0)
        simsym.assume(pprio <= MAXPROCS)

        self.qprio.create(pid)
        self.qprio[pid] = pprio

        if procs_prev.empty():                  # empty queue
            procs_prev.create(pid)
            procs_prev[pid] = NULLPROCREF
            procs_next.create(pid)
            procs_next[pid] = NULLPROCREF
        else:                                   # find the right place to add the new pid in
            pcut = PRef.var()
            simsym.assume(simsym.exists(pcut, symand(qprio.contains(pcut), symor(symand(qprio[pcut] >= pprio, symor(qprio[proces_prev[pcut]] < pprio, proces_prev[pcut] == NULLPROCREF), symand(qprio[pcut] <= pprio, symor(qprio[proces_next[pcut]] > pprio, proces_next[pcut] == NULLPROCREF)))  )))):
                # find a process with higer priority
                if qprio[proces_prev[pcut]] < pprio or proces_prev[pcut] == NULLPROCREF:
                    # --- < pid <= pcut <= ---
                    procs_prev.create(pid)
                    procs_prev[pid] = proces_prev[pcut]
                    procs_next.create(pid)
                    procs_next[pid] = pcut
                    proces_prev[pcut] = pid
                # find a process with lower priority
                else:
                    # --- <= pcut <= pid < ---
                    procs_next.create(pid)
                    procs_next[pid] = proces_next[pcut]
                    procs_prev.create(pid)
                    procs_prev[pid] = pcut
                    proces_next[pcut] = pid


    def next_from_proc_prio_queue(self):
        simsym.assume
        phead = PRef.var()        
        simsym.assume(simsym.exists(phead, procs_prev[phead] == NULLPROCREF))
        if (procs_next[phead] != NULLPROCREF):
            procs_prev[procs_next[phead]] = NULLPROCREF
        # is this the correct way to delete an element from the tdict?
        del procs_next[phead]
        del procs_prev[phead]
        def qprio[phead]

        return phead;

    @model.methodwrap(self, pid = PRef)
    def is_in_proc_prio_queue(self):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        return self.procs_prev.contains(pid)

    def is_empty_proc_prio_queue(self):
        return  self.procs_prev.empty()

    @model.methodwrap(pid = PRef)
    def prio_of_proc_in_proc_prio_queue(self, pid):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF) 
        simsym.assume(qprio.contains(pid)) 
        return self.qprio[pid]

    @model.methodwrap(pid = PRef)

    def remove_prio_queue_elem(self, pid):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        simsym.assume(qprio.contains(pid))

        if (procs_next[pid] != NULLPROCREF):
            procs_prev[procs_next[pid]] = procs_prev[pid]
        if (procs_prev[pid] != NULLPROCREF):
            procs_next[procs_prev[pid]] = procs_next[pid]

        # is this the correct way to delete an element from the tdict?
        del procs_next[phead]
        del procs_prev[phead]
        def qprio[phead]

    @model.methodwrap(pid = PRef, newprio = Prio)    
    def reorder_proc_prio_queue(pid, newprio):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        simsym.assume(qprio.contains(pid))
        simsym.assume(newprio >= 0)
        simsym.assume(newprio <= MAXPROCS)
 
        self.remove_prio_queue_elem(pid)
        self.enqueue_proc_prio_queue(pid, newprio)


#=============================================
#
# 3.6 Current Process and Prioritised Read Queue
#
#=============================================
class CurrentProcess(simsym.struct(currentp = PRef,
                                   readyqp = ProcPrioQueue,
                                   ctxt = Context,
                                   lck = Lock,
                                   ptab = ProcessTable)):
    @model.methodwrap(ct = Context, lk = Lock)
    def init(self, ct, lk):
        self.readyqp.init()
        self.currenttp = NULLPROCREF
        self.lck = lk
        self.ctxt = ct

    def current_process(self):
        return self.currentp
    
    @model.methodwrap(pid = PRef)
    def make_current(self, pid):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        self.currentp = pid

    def make_ready(self):
        # Where the hell does the 'ptab' come from?!?! 凸=_=
        # I don't know why there shoud be an 'exists' here =___=
        pd = self.ptab.descr_of_process(self.currentp)
        prio = pd.process_priority()
        pd.set_process_status_to_ready()
        self.readyqp.enqueue_proc_prio_queue(prio)
        return pd, prio

    def reload_current(self):
        self.currentp = self.currentp
        self.readyqp = self.readyqp

    def continue_current(self):
        reload_current()
        ctxt.restore_state()

    @model.methodwrap(p = PRef)
    def is_current_proc(self, p):
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        return self.currentp == p
    
    @model.methodwrap(pid = PRef)
    def make_unready(self, pid):
        
        simsym.assume(pid >= NULLPROCREF)
        simsym.assume(pid <= IDLEPROCREF)
        self.lck.lock()
        if is_current_proc(pid):
            self.ctxt.save_state()
            self.run_next_process()
            self.lck.unlock()
        else:
            self.readyqp.remove_prio_queue_elem(pid)
            self.lck.unlock()

    def suspend_current(self):
        # Where the hell does the 'ptab' come from again?!?! 凸=_=
        self.lck.lock()
        self.ctxt.save_state()
        pd = self.ptab.descr_of_process(self.currentp)
        prio = pd.process_priority()
        pd.set_process_status_to_waiting()
        self.readyqp.enqueue_proc_prio_queue(currentp, prio)
        self.run_next_process()
        self.lck.lock()

        return pd, prio
        
    def run_next_process(self):
        self.schedule_next()
        self.ctxt.restore_state()

    def schedule_next(self):
        self.lck.lock()
        # I added a new instance variable ptab in this class
        # I don't know how to implement schedule_next
        if self.readyqp.is_empty():
            self.select_idle_process()
        else:
            p = self.readyqp.next_from_proc_prio_queue()
            pd = self.ptab.descr_of_process(p)
            self.readyqp.make_current(p)
            pd.set_process_status_to_running(p)
        
        self.run_next_process()
        self.lck.unlock()

        return pd, p

    def select_idle_process(self):
        self.currentp = IDLEPROCREF







