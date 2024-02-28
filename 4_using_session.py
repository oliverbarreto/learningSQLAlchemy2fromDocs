# Using the Session
# https://docs.sqlalchemy.org/en/20/orm/session.html
"""
The declarative base and ORM mapping functions described at ORM Mapped Class Configuration are the primary configurational interface for the ORM. Once mappings are configured, the primary usage interface for persistence operations is the Session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from data.db_config import engine, User, Address



# Basics of Using a Session
"""
The most basic Session use patterns are presented here.
Opening and Closing a Session
The Session may be constructed on its own or by using the sessionmaker class. It typically is passed a single Engine as a source of connectivity up front. A typical use may look like:
"""

u1 = User(name="Bill", fullname="Bill Gates")
a1 = Address(email_address="billgates@microsoft.com")
u1.addresses.append(a1)

# create session and add objects
# with Session(engine) as session:
#     session.add(u1)
#     session.add(a1)
#     session.commit()

# Framing out a begin / commit / rollback block
"""
We may also enclose the Session.commit() call and the overall “framing” of the transaction within a context manager 
for those cases where we will be committing data to the database. By “framing” we mean that if all operations succeed,
the Session.commit() method will be called, but if any exceptions are raised, the Session.rollback() method will be 
called so that the transaction is rolled back immediately, before propagating the exception outward. 
In Python this is most fundamentally expressed using a try: / except: / else: block such as:
"""

# verbose version of what a context manager will do
# with Session(engine) as session:
#     session.begin()
#     try:
#         session.add(u1)
#         session.add(a1)
#     except:
#         session.rollback()
#         raise
#     else:
#         session.commit()


"""
The long-form sequence of operations illustrated above can be achieved more succinctly by making use of the SessionTransaction object returned by the Session.begin() method, which provides a context manager interface for the same sequence of operations:
"""
# create session and add objects
# with Session(engine) as session:
#     with session.begin():
#         session.add(u1)
#         session.add(a1)
#     # inner context calls session.commit(), if there were no exceptions
# # outer context calls session.close()
        
"""
More succinctly, the two contexts may be combined:
"""
# create session and add objects
# with Session(engine) as session, session.begin():
#     session.add(u1)
#     session.add(a1)
# # inner context calls session.commit(), if there were no exceptions
# # outer context calls session.close()


# Using a sessionmaker
"""
The purpose of sessionmaker is to provide a factory for Session objects with a fixed configuration. 
As it is typical that an application will have an Engine object in module scope, the sessionmaker can provide a 
factory for Session objects that are against this engine:
"""

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# a sessionmaker(), also in the same scope as the engine
# Session = sessionmaker(engine)

# # we can now construct a Session() without needing to pass the
# # engine each time
# with Session() as session:
#     session.add(u1)
#     session.add(a1)
#     session.commit()
# # closes the session

"""
The sessionmaker is analogous to the Engine as a module-level factory for function-level sessions / connections. 
As such it also has its own sessionmaker.begin() method, analogous to Engine.begin(), which returns a 
Session object and also maintains a begin/commit/rollback block:
"""
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # a sessionmaker(), also in the same scope as the engine
# Session = sessionmaker(engine)

# # we can now construct a Session() and include begin()/commit()/rollback()
# # at once
# with Session.begin() as session:
#     session.add(u1)
#     session.add(a1)
# # commits the transaction, closes the session



#  AsyncSession
# Is the Session thread-safe? Is AsyncSession safe to share in concurrent tasks?
# https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks
# https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-core-connection-transaction
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""
The Session is a mutable, stateful object that represents a single database transaction. An instance of Session therefore cannot be shared among concurrent threads or asyncio tasks without careful synchronization. The Session is intended to be used in a non-concurrent fashion, that is, a particular instance of Session should be used in only one thread or task at a time.
When using the AsyncSession object from SQLAlchemy’s asyncio extension, this object is only a thin proxy on top of a Session, and the same rules apply; it is an unsynchronized, mutable, stateful object, so it is not safe to use a single instance of AsyncSession in multiple asyncio tasks at once.
An instance of Session or AsyncSession represents a single logical database transaction, referencing only a single Connection at a time for a particular Engine or AsyncEngine to which the object is bound (note that these objects both support being bound to multiple engines at once, however in this case there will still be only one connection per engine in play within the scope of a transaction).
A database connection within a transaction is also a stateful object that is intended to be operated upon in a non-concurrent, sequential fashion. Commands are issued on the connection in a sequence, which are handled by the database server in the exact order in which they are emitted. As the Session emits commands upon this connection and receives results, the Session itself is transitioning through internal state changes that align with the state of commands and data present on this connection; states which include if a transaction were begun, committed, or rolled back, what SAVEPOINTs if any are in play, as well as fine-grained synchronization of the state of individual database rows with local ORM-mapped objects.
When designing database applications for concurrency, the appropriate model is that each concurrent task / thread works with its own database transaction. This is why when discussing the issue of database concurrency, the standard terminology used is multiple, concurrent transactions. Within traditional RDMS there is no analogue for a single database transaction that is receiving and processing multiple commands concurrently.
The concurrency model for SQLAlchemy’s Session and AsyncSession is therefore Session per thread, AsyncSession per task. An application that uses multiple threads, or multiple tasks in asyncio such as when using an API like asyncio.gather() would want to ensure that each thread has its own Session, each asyncio task has its own AsyncSession.
The best way to ensure this use is by using the standard context manager pattern locally within the top level Python function that is inside the thread or task, which will ensure the lifespan of the Session or AsyncSession is maintained within a local scope.
For applications that benefit from having a “global” Session where it’s not an option to pass the Session object to specific functions and methods which require it, the scoped_session approach can provide for a “thread local” Session object; see the section Contextual/Thread-local Sessions for background. Within the asyncio context, the async_scoped_session object is the asyncio analogue for scoped_session, however is more challenging to configure as it requires a custom “context” function.
"""

"""
To install SQLAlchemy while ensuring the greenlet dependency is present regardless of what platform is in use, 
the [asyncio] setuptools extra may be installed as follows, which will include also instruct pip to install greenlet:
Note that installation of greenlet on platforms that do not have a pre-built wheel file means that greenlet will 
be built from source, which requires that Python’s development libraries also be present.
"""
# pip install sqlalchemy[asyncio]

# Async with ORM - Synopsis - ORM
"""
Using 2.0 style querying, the AsyncSession class provides full ORM functionality.
Within the default mode of use, special care must be taken to avoid lazy loading or other expired-attribute access
 involving ORM relationships and column attributes; the next section Preventing Implicit IO when Using 
 AsyncSession details this.

> Warning: 
A single instance of AsyncSession is not safe for use in multiple, concurrent tasks. See the sections 
Using AsyncSession with Concurrent Tasks and Is the Session thread-safe? Is AsyncSession safe to share in 
concurrent tasks? for background.

The example below illustrates a complete example including mapper and session configuration:
In the example below, the AsyncSession is instantiated using the optional async_sessionmaker helper, which 
provides a factory for new AsyncSession objects with a fixed set of parameters, which here includes associating it
with an AsyncEngine against particular database URL. It is then passed to other methods where it may be used in 
a Python asynchronous context manager (i.e. async with: statement) so that it is automatically closed at the end
of the block; this is equivalent to calling the AsyncSession.close() method.
"""

# from __future__ import annotations

# import asyncio
# import datetime
# from typing import List

# from sqlalchemy import ForeignKey
# from sqlalchemy import func
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncAttrs
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column
# from sqlalchemy.orm import relationship
# from sqlalchemy.orm import selectinload


# class Base(AsyncAttrs, DeclarativeBase):
#     pass


# class A(Base):
#     __tablename__ = "a"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     data: Mapped[str]
#     create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
#     bs: Mapped[List[B]] = relationship()


# class B(Base):
#     __tablename__ = "b"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
#     data: Mapped[str]


# async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
#     async with async_session() as session:
#         async with session.begin():
#             session.add_all(
#                 [
#                     A(bs=[B(data="b1"), B(data="b2")], data="a1"),
#                     A(bs=[], data="a2"),
#                     A(bs=[B(data="b3"), B(data="b4")], data="a3"),
#                 ]
#             )


# async def select_and_update_objects(
#     async_session: async_sessionmaker[AsyncSession],
# ) -> None:
#     async with async_session() as session:
#         stmt = select(A).options(selectinload(A.bs))

#         result = await session.execute(stmt)

#         for a in result.scalars():
#             print(a)
#             print(f"created at: {a.create_date}")
#             for b in a.bs:
#                 print(b, b.data)

#         result = await session.execute(select(A).order_by(A.id).limit(1))

#         a1 = result.scalars().one()

#         a1.data = "new data"

#         await session.commit()

#         # access attribute subsequent to commit; this is what
#         # expire_on_commit=False allows
#         print(a1.data)

#         # alternatively, AsyncAttrs may be used to access any attribute
#         # as an awaitable (new in 2.0.13)
#         for b1 in await a1.awaitable_attrs.bs:
#             print(b1, b1.data)


# async def async_main() -> None:
#     engine = create_async_engine(
#         "postgresql+asyncpg://scott:tiger@localhost/test",
#         echo=True,
#     )

#     # async_sessionmaker: a factory for new AsyncSession objects.
#     # expire_on_commit - don't expire objects after transaction commit
#     async_session = async_sessionmaker(engine, expire_on_commit=False)

#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

#     await insert_objects(async_session)
#     await select_and_update_objects(async_session)

#     # for AsyncEngine created in function scope, close and
#     # clean-up pooled connections
#     await engine.dispose()


# asyncio.run(async_main())



# Using AsyncSession with Concurrent Tasks
"""
The AsyncSession object is a mutable, stateful object which represents a single, stateful database transaction in
progress. Using concurrent tasks with asyncio, with APIs such as asyncio.gather() for example, should use a 
separate AsyncSession per individual task.
See the section Is the Session thread-safe? Is AsyncSession safe to share in concurrent tasks? for a general 
description of the Session and AsyncSession with regards to how they should be used with concurrent workloads.
"""

# Preventing Implicit IO when Using AsyncSession¶
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession



# Running Synchronous Methods and Functions under asyncio - 
"""
Deep Alchemy
This approach is essentially exposing publicly the mechanism by which SQLAlchemy is able to provide the asyncio interface in the first place. While there is no technical issue with doing so, overall the approach can probably be considered “controversial” as it works against some of the central philosophies of the asyncio programming model, which is essentially that any programming statement that can potentially result in IO being invoked must have an await call, lest the program does not make it explicitly clear every line at which IO may occur. This approach does not change that general idea, except that it allows a series of synchronous IO instructions to be exempted from this rule within the scope of a function call, essentially bundled up into a single awaitable.
As an alternative means of integrating traditional SQLAlchemy “lazy loading” within an asyncio event loop, an optional method known as AsyncSession.run_sync() is provided which will run any Python function inside of a greenlet, where traditional synchronous programming concepts will be translated to use await when they reach the database driver. A hypothetical approach here is an asyncio-oriented application can package up database-related methods into functions that are invoked using AsyncSession.run_sync().
Altering the above example, if we didn’t use selectinload() for the A.bs collection, we could accomplish our treatment of these attribute accesses within a separate function:
"""


