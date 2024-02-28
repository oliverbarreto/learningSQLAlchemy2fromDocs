# Working with Database Metadata
"""
> 💥💥💥 Read carefully the way of creating Base(DeclarativeBase) and MappedColumns: 
- https://docs.sqlalchemy.org/en/20/tutorial/metadata.html
Basics Steps:
1. Create the engine with db driver
2. Create a Base(DeclarativeBase) class
3. Create tables with MappedColumns
4. # Create DB with metadata witH:
Base.metadata.drop_all(engine)      # if desired !!!
Base.metadata.create_all(engine)
5. Take a look at your new db with new your ORM SQLAlchemy defined tables 
"""

# Create example db
from typing import Optional

from sqlalchemy import create_engine, MetaData, Integer, String, ForeignKey, union_all
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from sqlalchemy import insert, select, update, text
from sqlalchemy.orm import Session


# Create engine
engine = create_engine('sqlite+pysqlite:///data/db.sqlite3', echo=True)

# Create Metadata class
class Base(DeclarativeBase):
    pass

# Create ORM Tables
class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))
    
    user: Mapped[User] = relationship(back_populates="addresses")
    
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r}, user_id={self.user_id!r})"

# Create DB with metadata
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)



# Working with Data
"""
Working with Data
In Working with Transactions and the DBAPI, we learned the basics of how to interact with the Python DBAPI and its transactional state. Then, in Working with Database Metadata, we learned how to represent database tables, columns, and constraints within SQLAlchemy using the MetaData and related objects. In this section we will combine both concepts above to create, select and manipulate data within a relational database. Our interaction with the database is always in terms of a transaction, even if we’ve set our database driver to use autocommit behind the scenes.
The components of this section are as follows:
- Using INSERT Statements - to get some data into the database, we introduce and demonstrate the Core Insert construct. INSERTs from an ORM perspective are described in the next section Data Manipulation with the ORM.
- Using SELECT Statements - this section will describe in detail the Select construct, which is the most commonly used object in SQLAlchemy. The Select construct emits SELECT statements for both Core and ORM centric applications and both use cases will be described here. Additional ORM use cases are also noted in the later section Using Relationships in Queries as well as the ORM Querying Guide.
- Using UPDATE and DELETE Statements - Rounding out the INSERT and SELECTion of data, this section will describe from a Core perspective the use of the Update and Delete constructs. ORM-specific UPDATE and DELETE is similarly described in the Data Manipulation with the ORM section.

💥 session.execute(stmt) returns rows with Named-TUPPLES !!! Extract accordingly.
if a full object is inside the tupple, you can use scalars to access it, or row[0]
if only a few cols are inside, you can use row["col_name"] to access information on cols. If you use scalars on this case, you will get the value of the first column.
"""

# The insert() SQL Expression Construct
""""
When using Core as well as when using the ORM for bulk operations, a SQL INSERT statement is generated directly using the insert() function - this function generates a new instance of Insert which represents an INSERT statement in SQL, that adds new data into a table.
"""

# statement = insert(User).values(name="spongebob", fullname="Spongebob Squarepants")
# print(statement)
# INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)

# compiled = statement.compile()
# compiled.params
# {'name': 'spongebob', 'fullname': 'Spongebob Squarepants'}



# Executing the Statement
"""
Invoking the statement we can INSERT a row into user_table. The INSERT SQL as well as the bundled parameters can be seen in the SQL logging:
In its simple form above, the INSERT statement does not return any rows, and if only a single row is inserted, it will usually include the ability to return information about column-level default values that were generated during the INSERT of that row, most commonly an integer primary key value. In the above case the first row in a SQLite database will normally return 1 for the first integer primary key value, which we can acquire using the CursorResult.inserted_primary_key accessor:
> TIP: Changed in version 1.4.8: the tuple returned by CursorResult.inserted_primary_key is now a named tuple fulfilled by returning it as a Row object.
"""

# with Session(engine) as session:
#     statement = insert(User).values(name="spongebob", fullname="Spongebob Squarepants")
#     result = session.execute(statement)
#     session.commit()
#     print(result.inserted_primary_key)

"""
INSERT usually generates the “values” clause automatically
The example above made use of the Insert.values() method to explicitly create the VALUES clause of the SQL INSERT statement. If we don’t actually use Insert.values() and just print out an “empty” statement, we get an INSERT for every column in the table:
"""
# with engine.connect() as conn:
#     result = conn.execute(
#         insert(User),
#         [
#             {"name": "sandy", "fullname": "Sandy Cheeks"},
#             {"name": "patrick", "fullname": "Patrick Star"},
#         ],
#     )
#     conn.commit()
#     # 2024-02-27 20:09:16,269 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)

# with engine.connect() as conn:
#     result = conn.execute(
#         insert(User).returning(User.name, User.fullname),
#         [
#             {"name": "Oliver", "fullname": "Sandy Cheeks"},
#             {"name": "Ana", "fullname": "Patrick Star"},
#         ],
#     )
#     conn.commit()
#     print(f"result: {result.scalars().all()}")
#     # 2024-02-27 20:09:16,269 INFO sqlalchemy.engine.Engine INSERT INTO user_account (name, fullname) VALUES (?, ?)

# INSERT…FROM SELECT
"""
A less used feature of Insert, but here for completeness, the Insert construct can compose an INSERT that gets rows directly from a SELECT using the Insert.from_select() method. This method accepts a select() construct, which is discussed in the next section, along with a list of column names to be targeted in the actual INSERT. In the example below, rows are added to the address table which are derived from rows in the user_account table, giving each user a free email address at aol.com:
"""



# The select() SQL Expression Construct
# Selecting ORM Entities and Columns
# https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#selecting-orm-entities-and-columns

"""
For both Core and ORM, the select() function generates a Select construct which is used for all SELECT queries. Passed to methods like Connection.execute() in Core and Session.execute() in ORM, a SELECT statement is emitted in the current transaction and the result rows available via the returned Result object.
The select() construct builds up a statement in the same way as that of insert(), using a generative approach where each method builds more state onto the object. Like the other SQL constructs, it can be stringified in place:
ORM entities, such our User class as well as the column-mapped attributes upon it such as User.name, also participate in the SQL Expression Language system representing tables and columns. Below illustrates an example of SELECTing from the User entity, which ultimately renders in the same way as if we had used user_table directly:
"""
print(select(User))
# SELECT user_account.id, user_account.name, user_account.fullname 
# FROM user_account

"""
When executing a statement like the above using the ORM Session.execute() method, there is an important difference when we select from a full entity such as User, as opposed to user_table, which is that the entity itself is returned as a single element within each row. That is, when we fetch rows from the above statement, as there is only the User entity in the list of things to fetch, we get back Row objects that have only one element, which contain instances of the User class:
"""
# with Session(engine) as session:
#     statement = select(User)
#     users = session.execute(statement)
#     for user in users:
#         print(user)
#     # (User(id=1, name='Oliver', fullname='Sandy Cheeks'),)
#     # (User(id=2, name='Ana', fullname='Patrick Star'),)

# with Session(engine) as session:
#     statement = select(User)
#     users = session.execute(statement).scalars()
#     for user in users:
#         print(user)
#     # User(id=1, name='Oliver', fullname='Sandy Cheeks')
#     # User(id=2, name='Ana', fullname='Patrick Star')


"""
A highly recommended convenience method of achieving the same result as above is to use the Session.scalars() method to execute the statement directly; this method will return a ScalarResult object that delivers the first “column” of each row at once, in this case, instances of the User class:
"""
# > Tip: It's recommended to call session.scalars(stmt) instead of session.execute(stmt).scalars(). 
# > and produces the same result
# with Session(engine) as session:
#     statement = select(User)
#     users = session.scalars(statement)
#     for user in users:
#         print(user)
#     # User(id=1, name='Oliver', fullname='Sandy Cheeks')
#     # User(id=2, name='Ana', fullname='Patrick Star')

"""
When executing a statement like the above using the ORM Session.execute() method, 
there is an important difference when we select from a full entity such as User, as opposed to user_table, which is that the entity itself is returned as a single element within each row. That is, when we fetch rows from the above statement, as there is only the User entity in the list of things to fetch, we get back Row objects that have only one element, which contain instances of the User class:
"""
# Returning Rows
# with Session(engine) as session:
#     statement = select(User)
#     row = session.execute(statement).first()
#     print(row)            # we get the tuple
#     # (User(id=1, name='Oliver', fullname='Sandy Cheeks'),)   
# 
#     print(row[0])         # we get the object
#     # The above Row has just one element, representing the User entity:
#     # User(id=1, name='Oliver', fullname='Sandy Cheeks')

# with Session(engine) as session:
    # statement = select(User)
    # row = session.execute(statement).first()
    # print(row)
    # (User(id=1, name='Oliver', fullname='Sandy Cheeks'),)    
    
    # row = session.scalars(statement).first()
    # print(row)
    # User(id=1, name='Oliver', fullname='Sandy Cheeks')
    
    # rows = session.execute(statement).scalars()
    # for user in rows:
    #     print(user)
    #     # User(id=1, name='Oliver', fullname='Sandy Cheeks')
    #     # User(id=2, name='Ana', fullname='Patrick Star')

    # rows = session.scalars(statement)
    # for user in rows:
    #     print(user)
        # User(id=1, name='Oliver', fullname='Sandy Cheeks')
        # User(id=2, name='Ana', fullname='Patrick Star')

    # row = session.execute(statement).first()
    # print(row[0])
    # User(id=1, name='Oliver', fullname='Sandy Cheeks')


# Selecting Columns
# print(select(User.name, User.fullname))        
# SELECT user_account.name, user_account.fullname 
# FROM user_account


# with Session(engine) as session:
    # statement = select(User.name, User.fullname)
    # rows = session.execute(statement)
    # for user in rows:
    #   print(user)
        # ('Oliver', 'Sandy Cheeks')
        # ('Ana', 'Patrick Star') 
    
    # for user in rows:
    #     print(f"{user.name} - {user.fullname}")
        # Oliver - Sandy Cheeks
        # Ana - Patrick Star
        
    # for user in rows:
        # print(user)
        # Oliver
        # Ana
"""
Hay un par de razones por las que el código dado solo está imprimiendo el nombre de usuario (name) en lugar de name y fullname:
El objeto Row que se obtiene al iterar sobre el resultado de session.execute() es esencialmente una tupla. Por defecto, imprimir una tupla solo muestra el primer elemento.
Las columnas seleccionadas en el statement (name y fullname) se convierten en atributos del objeto Row. Pero al imprimir Row, solo se muestra el primer atributo.
"""

"""
💥Cuando seleccionamos determinadas columnas ya los resultados (las tuplas) 
de rows no pueden ser objetos ORM de la tabla, 
por lo que scalars y resultados devolverán los valores de las columnas
"""
    # statement = select(User.name, User.fullname)
    # users = session.execute(statement)
    # for user in users:
    #     print(user)
        # ('Oliver', 'Sandy Cheeks')
        # ('Ana', 'Patrick Star')
    # user = session.execute(statement).first()
    # print(user)
    # ('Oliver', 'Sandy Cheeks')

    # stament = "SELECT user_account.id as id, user_account.name as name from user_account"
    # result = session.execute(text(stament))
    # for row in result:
    #     print(row)



    
    # statement = select(User.name, User.fullname)   
    # users = session.execute(statement).scalars()
    # for u in users:
    #     print(u)
    #     # Oliver
    #     # Ana

    # users = session.scalars(statement)
    # for u in users:
    #     print(u)
        # Oliver
        # Ana


    # users = session.execute(statement).first().scalars()
    # for user in users:
    #     print(user)
    

# TODO:✅ 💥 CREAR registros en address !!!
# with Session(engine) as session:
#     # create user
#     user1 = User(name='Luke', fullname='Luke Skywalker')
#     user2 = User(name='Anakin', fullname='Anakin Skywalker')
#     session.add_all([user1, user2])
#     session.commit()
#     session.expire_all()
    
#     address1 = Address(email_address="123 Tatooine St, Two Sun Desert, SW", user_id=user1.id)
#     address2 = Address(email_address="123 Plaza España, Naboo SW", user_id=user2.id)
#     session.add_all([address1, address2])
#     session.commit()
    
"""
There are a couple ways to refresh the users that were just created in the session:

1. Refresh the individual objects:
session.add_all([user1, user2]) 
session.commit()

session.refresh(user1)
session.refresh(user2)

This will requery each user object to reload the data from the database.

2. Refresh the entire session:
session.add_all([user1, user2])
session.commit()

session.expire_all() 

Calling session.expire_all() will expire all instances in the session and they will be refreshed on next access.

3. Requery the users:
session.add_all([user1, user2])
session.commit() 
user1 = session.query(User).get(user1.id)
user2 = session.query(User).get(user2.id) 

Requerying will load a fresh instance from the database.

So in summary, you can either refresh individual objects, expire the whole session, or requery to get fresh data. This is useful if you want to load any defaults, auto-generated values, or defaults after an INSERT.
"""
    # session.refresh(address)
    # session.refresh(user)
    # print(user)
    # print(address)
# with Session(engine) as session:
#     statement = select(User.name, Address.id, Address.email_address).where(User.name == "Oliver").order_by(Address.id)
#     results = session.execute(statement)
#     print(results)
#     print(f"results type: {type(results)}")
#     for tuple in results:
#         print(f"User: {tuple [0]}, Address.id: {tuple[1]}, eMail Address: {tuple[2]}")
    # [print(user) for user in results]

# Creating a Python Generator to return an Iterable with one user at a time from a list
# from typing import Generator, Any, Iterable
# # def user_generator(users: list[User]) -> Generator[User, Any, Any]:
# def user_generator(users: list[User]) -> Iterable[User]:
#     for user in users:
#         yield user

# with Session(engine) as session:
#     statement = select(User)
#     users = session.execute(statement).scalars()
#     print(users)
#     [print(user) for user in user_generator(users)]


# Use of scalars
"""
The scalars() method in SQLAlchemy is used to return just the scalar values from a query result rather than model instances or result rows.

Some common cases where scalars() is useful:

- When you want just a single scalar value like a count or aggregation result:
num_users = session.query(User.id).count().scalars().one()

- When you want the first scalar value from a row:
username = session.query(User.name).first().scalars().one() 

- When you want to iterate over a column of scalars from multiple rows:
names = [name for name in session.query(User.name).scalars()]

- When you don't need the overhead of full model instances and just want raw values.
- When you want to reduce the result to scalars before additional processing.

So in summary, scalars() is useful for extracting just the scalar column values from a query, rather than complete model objects or result rows. It's a convenience method for limiting the query result to raw scalar data.
"""


"""
is not quite correct for using SQLAlchemy. There are a couple issues:
- session.execute(statement) returns a ResultProxy object, not a scalar row value directly.
- first() on a ResultProxy gets the first row, but it will still be a Row object.
- scalars() is a method on ResultProxy to get scalar values, not on a Row object.

The proper way to get a scalar value from the first row would be:
- result = session.execute(statement)
- first_row = result.first()
- user = first_row[0] # get first column 

Or using scalars():
- result = session.execute(statement) 
- user = result.scalars().first()

So the key points are:
- Execute to get a ResultProxy
- Call first() on ResultProxy to get the Row
- Index into the Row or use scalars() on ResultProxy
"""



# ORM Entity Aliases
"""
The ORM equivalent of the FromClause.alias() method is the ORM aliased() function, which may be applied to an entity such as User and Address. 
This produces a Alias object internally that’s against the original mapped Table object, while maintaining ORM functionality. The SELECT below selects from the User entity all objects that include two particular email addresses:
"""

from sqlalchemy.orm import aliased

# address_alias_1 = aliased(Address)
# address_alias_2 = aliased(Address)

# print(
#     select(User)
#     .join_from(User, address_alias_1)
#     .where(address_alias_1.id == 1)
#     # .join_from(User, address_alias_2)
#     # .where(address_alias_2.user_id == 2)
# )


# ORM Entity Subqueries/CTEs
"""
In the ORM, the aliased() construct may be used to associate an ORM entity, such as our User or Address class, with any FromClause concept that represents a source of rows. The preceding section ORM Entity Aliases illustrates using aliased() to associate the mapped class with an Alias of its mapped Table. Here we illustrate aliased() doing the same thing against both a Subquery as well as a CTE generated against a Select construct, that ultimately derives from that same mapped Table.
Below is an example of applying aliased() to the Subquery construct, so that ORM entities can be extracted from its rows. The result shows a series of User and Address objects, where the data for each Address object ultimately came from a subquery against the address table rather than that table directly:

Este código está haciendo una consulta a la tabla User join con la tabla Address, pero filtrando las direcciones primero para excluir aquellas que contengan "@Any" en el email. 
Vamos por partes:
- El operador ~ en Python se utiliza para negar una expresión. Entonces aquí se está negando el like:
- subq = select(Address).where(~Address.email_address.like("%@Any")) crea una subconsulta que selecciona las filas de Address donde el email no contenga "@Any".

- address_subq = aliased(Address, subq) crea un alias de la tabla Address basado en la subconsulta anterior. 
Esto nos permite tratar la subconsulta como una tabla separada.

- Luego se crea la consulta principal join entre User y el alias address_subq.
- Se ejecuta la consulta y se itera sobre los resultados, imprimiendo cada usuario junto con su dirección filtrada.

En resumen, estamos filtrando primero las direcciones para excluir aquellas con "@Any", y luego join eso con la tabla User para mostrar los usuarios junto con sus direcciones filtradas.
Esto es útil cuando necesitamos filtrar o modificar una tabla antes de hacer join, para cambiar el conjunto de datos que se une. El alias y subconsulta nos permite lograr esto de una manera limpia en SQLAlchemy.
"""

# subq = select(Address).where(Address.email_address.like("%@Any")).subquery()
# subq = select(Address).where(Address.email_address.like("%boo%")).subquery()
# address_subq = aliased(Address, subq)
# stmt = (
#     select(User, address_subq)
#     .join_from(User, address_subq)
#     .order_by(User.id, address_subq.id)
# )
# with Session(engine) as session:
#     for user, address in session.execute(stmt):
#         print(f"{user} {address}")


# Selecting ORM Entities from Unions (two approaches)
"""
The preceding examples illustrated how to construct a UNION given two Table objects, to then return database rows. 
If we wanted to use a UNION or other set operation to select rows that we then receive as ORM objects, there are two approaches that may be used. 
- In both cases, we first construct a select() or CompoundSelect object that represents the SELECT / UNION / etc statement we want to execute; 
this statement should be composed against the target ORM entities or their underlying mapped Table objects:
"""

# In both cases, we first construct a select() or CompoundSelect object that represents the SELECT / UNION / etc statement we want to execute
stmt1 = select(User).where(User.name == "Ana")
stmt2 = select(User).where(User.name == "Oliver")
u = union_all(stmt1, stmt2)

# Creating a query from a statement created with the union select, returning user objects
orm_stmt = select(User).from_statement(u)
with Session(engine) as session:
    results = session.execute(orm_stmt).scalars()
    for obj in results:
        print(obj)


"""
To use a UNION or other set-related construct as an entity-related component in in a more flexible manner, the CompoundSelect construct may be 
organized into a subquery using CompoundSelect.subquery(), which then links to ORM objects using the aliased() function. 
This works in the same way introduced at ORM Entity Subqueries/CTEs, to first create an ad-hoc “mapping” of our desired entity to the subquery, 
then selecting from that new entity as though it were any other mapped class. In the example below, we are able to add additional criteria 
such as ORDER BY outside of the UNION itself, as we can filter or order by the columns exported by the subquery:
"""

# Creating an aliased subquery with the union, and creating a select on the user ttable, returning user objects
user_alias = aliased(User, u.subquery())
orm_stmt = select(user_alias).order_by(user_alias.id)
with Session(engine) as session:
    for obj in session.execute(orm_stmt).scalars():
        print(obj)


