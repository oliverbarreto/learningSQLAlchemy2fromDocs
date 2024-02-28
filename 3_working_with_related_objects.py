# Working with ORM Related Objects

"""
In this section, we will cover one more essential ORM concept, which is how the ORM interacts with mapped classes that refer to other objects. In the section Declaring Mapped Classes, the mapped class examples made use of a construct called relationship(). This construct defines a linkage between two different mapped classes, or from a mapped class to itself, the latter of which is called a self-referential relationship.
To describe the basic idea of relationship(), first we’ll review the mapping in short form, omitting the mapped_column() mappings and other directives:
"""

"""
In this section we use the db_config file with the DB Configuration class to create a session object. We then use 
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from data.db_config import engine, User, Address



# Persisting and Loading Relationships (not in session)
"""
We can start by illustrating what relationship() does to instances of objects. 
If we make a new User object, we can note that there is a Python list when we access the .addresses element:
This object is a SQLAlchemy-specific version of Python list which has the ability to track and respond to changes made to it. The collection also appeared automatically when we accessed the attribute, even though we never assigned it to the object. This is similar to the behavior noted at Inserting Rows using the ORM Unit of Work pattern where it was observed that column-based attributes to which we don’t explicitly assign a value also display as None automatically, rather than raising an AttributeError as would be Python’s usual behavior.
As the u1 object is still transient and the list that we got from u1.addresses has not been mutated (i.e. appended or extended), it’s not actually associated with the object yet, but as we make changes to it, it will become part of the state of the User object.
The collection is specific to the Address class which is the only type of Python object that may be persisted within it. Using the list.append() method we may add an Address object:
"""


# u1 = User(name="pkrabs", fullname="Pearl Krabs")
# u1.addresses
# # print(u1)
# # print(u1.addresses)
# # User(id=None, name='pkrabs', fullname='Pearl Krabs')
# # []

# a1 = Address(email_address="pearl.krabs@gmail.com")
# u1.addresses.append(a1)
# a2 = Address(email_address="david.becks@gmail.com")
# u1.addresses.append(a2)
# print(a1)
# print(u1)
# print(u1.addresses)
# print(a1.user)
# Address(id=None, email_address='pearl.krabs@gmail.com', user_id=None)
# User(id=None, name='pkrabs', fullname='Pearl Krabs')
# [Address(id=None, email_address='pearl.krabs@gmail.com', user_id=None)]
# User(id=None, name='pkrabs', fullname='Pearl Krabs')
# objects are transient, but when accesed they refresh and synchronizes the object

# create a session
# with Session(engine) as session:
#     session.add(u1)                  # add u1 to the session
#     u1 in session
#     session.add(a1)
#     a1 in session
#     session.commit()                 # commit changes to the database
#     print(a1)
#     print(u1)


# Cascading Objects into the Session
"""
We now have a User and two Address objects that are associated in a bidirectional structure in memory, 
but as noted previously in Inserting Rows using the ORM Unit of Work pattern, 
these objects are said to be in the transient state until they are associated with a Session object.
We make use of the Session that’s still ongoing, and note that when we apply the Session.add() method 
to the lead User object, the related Address object also gets added to that same Session:
"""

# Loading Relationships
"""
In the last step, we called Session.commit() which emitted a COMMIT for the transaction, and then per Session.commit.expire_on_commit expired all objects so that they refresh for the next transaction.
When we next access an attribute on these objects, we’ll see the SELECT emitted for the primary attributes of the row, such as when we view the newly generated primary key for the u1 object:
"""
# will ERROR due to be outside os Session after commit() above in another session.
# print(u1)
# print(u1.addresses)

# Using Relationships to Join
# print("--- Option 1 ---")
# statement = select(Address.email_address, Address.id).select_from(User).join(User.addresses)
# print(statement)
# with Session(engine) as session:
#     rows = session.execute(statement)           # returns named tuples
#     for row in rows:
#         print(f"row: {row.email_address} - {row.id}")


# print("--- Option 2 ---")
# statementt = select(Address.email_address).join_from(User, Address)
# print(statement)



#  Load Strategies

# SelectIn Load
from sqlalchemy.orm import selectinload

with Session(engine) as session:
    stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
    for row in session.execute(stmt):
        print(
            f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
        )



# Explicit Join + Eager load¶
# from sqlalchemy.orm import contains_eager

# with Session(engine) as session:
#     stmt = (
#         select(Address)
#         .join(Address.user)
#         .where(User.name == "pkrabs")
#         .options(contains_eager(Address.user))
#         .order_by(Address.id)
#     )
#     for row in session.execute(stmt):
#         print(f"{row.Address.email_address} {row.Address.user.name}")