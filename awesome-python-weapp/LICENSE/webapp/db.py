#db.py
#coding=utf-8

#数据库引擎对象：
class _Engine(object):
    def __init__(self, connect):
        self._connect = connect;

    def conncet(self):
        return self._connect();

engine = None;

#持有数据库链接的上下文对象：
class _DbCtx(threading.local):
    def __init__(self):
        self.conncetion = None;
        self.transactions = 0;

    def is_init(self):
        return not self.conncetion is None;

    def init(self):
        self.conncetion = _LasyConnection()
        self.transactions = 0;

    def cleanup(self):
        self.conncetion.cleanup();
        self.conncetion = None;

    def curso(self):
        return self.conncetion.cursor()

_db_ctx = _DbCtx();

class _ConnectionCtx(object):
    def __enter__(self):
        global _db_ctx;
        self.should_cleanup = False;
        if not _db_ctx.is_init():
            _db_ctx.init();
            self.should_cleanup = True;
        return self;

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx;
        if self.should_cleanup:
            _db_ctx.cleanup();

def conncetion():
    return _ConnectionCtx()

class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx;
        self.should_close_conn = False;
        if not _db_ctx.is_init():
            _db_ctx.init();
            self.should_close_conn = True;
        _db_ctx.transactions = _db_ctx.transactions + 1;
        return self;

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx;
        _db_ctx.transactions = _db_ctx.transactions - 1;
        try:
            if _db_ctx.transactions==0:
                if exctype is None:
                    self.commit();
                else:
                    self.rollback();
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup();

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit();
        except:
            _db_ctx.connection.rollback();
            raise

    def rollback(self):
        global  _db_ctx;
        _db_ctx.connection.rollback();

    def select(self):
        global  _db_ctx;
        _db_ctx.connection.select();

    def update(self):
        global  _db_ctx;
        _db_ctx.connection.update();