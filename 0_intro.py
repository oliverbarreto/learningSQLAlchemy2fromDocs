# SQLAlchemy 2.0 Tutorial - https://docs.sqlalchemy.org/en/20/tutorial/index.html
from sqlalchemy import create_engine, text

# Create the Engine
"""
With the Engine object ready to go, we may now proceed to dive into the basic operation of an Engine and its primary interactive endpoints, the Connection and Result. We will additionally introduce the ORM’s facade for these objects, known as the Session.
Note to ORM readers:
When using the ORM, the Engine is managed by another object called the Session. The Session in modern SQLAlchemy emphasizes a transactional and SQL execution pattern that is largely identical to that of the Connection discussed below, so while this subsection is Core-centric, all of the concepts here are essentially relevant to ORM use as well and is recommended for all ORM learners. The execution pattern used by the Connection will be contrasted with that of the Session at the end of this section.
As we have yet to introduce the SQLAlchemy Expression Language that is the primary feature of SQLAlchemy, we will make use of one simple construct within this package called the text() construct, which allows us to write SQL statements as textual SQL. Rest assured that textual SQL in day-to-day SQLAlchemy use is by far the exception rather than the rule for most tasks, even though it always remains fully available.
"""
# engine = create_engine('sqlite+pysqlite:///data/db.sqlite3', echo=True)
engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# Working with Transactions and the DBAPI
## Getting a Connection
"""
The sole purpose of the Engine object from a user-facing perspective is to provide a unit of connectivity to the database called the Connection. When working with the Core directly, the Connection object is how all interaction with the database is done. As the Connection represents an open resource against the database, we want to always limit the scope of our use of this object to a specific context, and the best way to do that is by using Python context manager form, also known as the with statement. Below we illustrate “Hello World”, using a textual SQL statement. Textual SQL is emitted using a construct called text() that will be discussed in more detail later:
In the above example, the context manager provided for a database connection and also framed the operation inside of a transaction. The default behavior of the Python DBAPI includes that a transaction is always in progress; when the scope of the connection is released, a ROLLBACK is emitted to end the transaction. The transaction is not committed automatically; when we want to commit data we normally need to call Connection.commit() as we’ll see in the next section.
The result of our SELECT was also returned in an object called Result that will be discussed later, however for the moment we’ll add that it’s best to ensure this object is consumed within the “connect” block, and is not passed along outside of the scope of our connection.
"""
# with engine.connect() as conn:
#     result = conn.execute(text("select 'hellow world'"))
#     print(result.all())

## Committing changes
"""
We just learned that the DBAPI connection is non-autocommitting. What if we want to commit some data? We can alter our above example to create a table and insert some data, and the transaction is then committed using the Connection.commit() method, invoked inside the block where we acquired the Connection object:
"""
# with engine.connect() as conn:
#     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
#     conn.execute(text("INSERT INTO some_table VALUES (1, 2)"))
#     # conn.execute(
#     #     text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#     #     [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
#     # )
#     conn.commit()

# Begin Block
"""
Above, we emitted two SQL statements that are generally transactional, a “CREATE TABLE” statement [1] and an “INSERT” statement that’s parameterized (the parameterization syntax above is discussed a few sections below in Sending Multiple Parameters). As we want the work we’ve done to be committed within our block, we invoke the Connection.commit() method which commits the transaction. After we call this method inside the block, we can continue to run more SQL statements and if we choose we may call Connection.commit() again for subsequent statements. SQLAlchemy refers to this style as commit as you go.
There is also another style of committing data, which is that we can declare our “connect” block to be a transaction block up front. For this mode of operation, we use the Engine.begin() method to acquire the connection, rather than the Engine.connect() method. This method will both manage the scope of the Connection and also enclose everything inside of a transaction with COMMIT at the end, assuming a successful block, or ROLLBACK in case of exception raise. This style is known as begin once:
“Begin once” style is often preferred as it is more succinct and indicates the intention of the entire block up front. However, within this tutorial we will normally use “commit as you go” style as it is more flexible for demonstration purposes.
What’s “BEGIN (implicit)”?
You might have noticed the log line “BEGIN (implicit)” at the start of a transaction block. “implicit” here means that SQLAlchemy did not actually send any command to the database; it just considers this to be the start of the DBAPI’s implicit transaction. You can register event hooks to intercept this event, for example.

[1]
DDL refers to the subset of SQL that instructs the database to create, modify, or remove schema-level constructs such as tables. DDL such as “CREATE TABLE” is recommended to be within a transaction block that ends with COMMIT, as many databases uses transactional DDL such that the schema changes don’t take place until the transaction is committed. However, as we’ll see later, we usually let SQLAlchemy run DDL sequences for us as part of a higher level operation where we don’t generally need to worry about the COMMIT.
"""
# There is also another style of committing data, which is that we can declare our “connect” block to be a transaction block up front.
# with engine.begin() as conn:
#     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 6, "y": 8}, {"x": 9, "y": 5}, {"x": 4, "y": 3}, {"x": 10, "y": 11}],
#     )

# Basics of Statement Execution
"""
We have seen a few examples that run SQL statements against a database, making use of a method called Connection.execute(), in conjunction with an object called text(), and returning an object called Result. In this section we’ll illustrate more closely the mechanics and interactions of these components.
Most of the content in this section applies equally well to modern ORM use when using the Session.execute() method, which works very similarly to that of Connection.execute(), including that ORM result rows are delivered using the same Result interface used by Core.
We’ll first illustrate the Result object more closely by making use of the rows we’ve inserted previously, running a textual SELECT statement on the table we’ve created:
Above, the “SELECT” string we executed selected all rows from our table. The object returned is called Result and represents an iterable object of result rows.
Result has lots of methods for fetching and transforming rows, such as the Result.all() method illustrated previously, which returns a list of all Row objects. It also implements the Python iterator interface so that we can iterate over the collection of Row objects directly.
The Row objects themselves are intended to act like Python named tuples. Below we illustrate a variety of ways to access rows.
"""
# Fetching Rows
# with engine.begin() as conn:
#     # Assignment
#     statement = text("SELECT x, y FROM some_table")
#     result = conn.execute(statement)
#     for row in result:
#         print(f"x: {row.x} y: {row.y}")
#         print(f"x: {row[0]} y: {row[1]}")

# with engine.begin() as conn:
#     # Mapping Access - To receive rows as Python mapping objects, which is essentially a read-only version of Python’s interface to the common dict object, the Result may be transformed into a MappingResult object using the Result.mappings() modifier; this is a result object that yields dictionary-like RowMapping objects rather than Row objects:
#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for dict_row in result.mappings():
#         x = dict_row["x"]
#         y = dict_row["y"]


## Sending Parameters
"""
💥💥💥 Always use bound parameters !!!
As mentioned at the beginning of this section, textual SQL is not the usual way we work with SQLAlchemy. However, when using textual SQL, a Python literal value, even non-strings like integers or dates, should never be stringified into SQL string directly; a parameter should always be used. This is most famously known as how to avoid SQL injection attacks when the data is untrusted. However it also allows the SQLAlchemy dialects and/or DBAPI to correctly handle the incoming input for the backend. Outside of plain textual SQL use cases, SQLAlchemy’s Core Expression API otherwise ensures that Python literal values are passed as bound parameters where appropriate.
"""
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT x, y FROM some_table WHERE y >= :limit"), {"limit": 5})
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")

## Sending Multiple Parameters
# with engine.connect() as conn:
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
#     )
#     conn.commit()

# with engine.connect() as conn:
#     statement = """
#     SELECT x, y 
#     FROM some_table 
#     WHERE x >= :bottomlimit AND y <= :toplimit
#     """
#     parameters = [{"bottomlimit": 5, "toplimit": 10 }]
#     result = conn.execute(text(statement), parameters)
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")

"""
In the example at Committing Changes, we executed an INSERT statement where it appeared that we were able to INSERT multiple rows into the database at once. For DML statements such as “INSERT”, “UPDATE” and “DELETE”, we can send multiple parameter sets to the Connection.execute() method by passing a list of dictionaries instead of a single dictionary, which indicates that the single SQL statement should be invoked multiple times, once for each parameter set. 
This style of execution is known as executemany:
The above operation is equivalent to running the given INSERT statement once for each parameter set, except that the operation will be optimized for better performance across many rows.
A key behavioral difference between “execute” and “executemany” is that the latter doesn’t support returning of result rows, even if the statement includes the RETURNING clause. The one exception to this is when using a Core insert() construct, introduced later in this tutorial at Using INSERT Statements, which also indicates RETURNING using the Insert.returning() method. In that case, SQLAlchemy makes use of special logic to reorganize the INSERT statement so that it can be invoked for many rows while still supporting RETURNING.
"""
# with engine.connect() as conn:
#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")
    
#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
#     )
#     conn.commit()
#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")


# Executing with an ORM Session
"""
As mentioned previously, most of the patterns and examples above apply to use with the ORM as well, so here we will introduce this usage so that as the tutorial proceeds, we will be able to illustrate each pattern in terms of Core and ORM use together.
The fundamental transactional / database interactive object when using the ORM is called the Session. In modern SQLAlchemy, this object is used in a manner very similar to that of the Connection, and in fact as the Session is used, it refers to a Connection internally which it uses to emit SQL.
When the Session is used with non-ORM constructs, it passes through the SQL statements we give it and does not generally do things much differently from how the Connection does directly, so we can illustrate it here in terms of the simple textual SQL operations we’ve already learned.
The Session has a few different creational patterns, but here we will illustrate the most basic one that tracks exactly with how the Connection is used which is to construct it within a context manager:

The example above can be compared to the example in the preceding section in Sending Parameters - we directly replace the call to with engine.connect() as conn with with Session(engine) as session, and then make use of the Session.execute() method just like we do with the Connection.execute() method.
Also, like the Connection, the Session features “commit as you go” behavior using the Session.commit() method, illustrated below using a textual UPDATE statement to alter some of our data:
"""

from sqlalchemy.orm import Session

with Session(engine) as session:
    session.execute(text("CREATE TABLE some_table (x int, y int)"))

    session.execute(text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 5}, {"x": 4, "y": 3}, {"x": 10, "y": 11}],
    )

    session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
    )
    session.commit()

stmt = text("SELECT x, y FROM some_table WHERE y > :rate ORDER BY x, y")
params = [{"rate": 6}]

with Session(engine) as session:
    result = session.execute(statement=stmt, params=params)
    for row in result:
        print(f"x: {row.x}  y: {row.y}")
