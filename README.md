<div align="center">
  <a href="https://oliverbarreto.com">
    <img src="https://www.oliverbarreto.com/images/site-logo.png" />
  </a>
</div>
<div align="center">
  <h1>LEarning SQL Alchemy 2.0 from the docs</h1>
  <strong>Reading (and typing) things from what the Docs say</strong>
</div>
<br>

# 🧪 SQLAlchemy 2.0 (with support for asyncio)

[https://docs.sqlalchemy.org/en/20/index.html](https://docs.sqlalchemy.org/en/20/index.html)

## Overview

The SQLAlchemy SQL Toolkit and Object Relational Mapper is a comprehensive set of tools for working with databases and Python. It has several distinct areas of functionality which can be used individually or combined together. Its major components are illustrated below, with component dependencies organized into layers:

![SQLAlchemy 2.0 Architecture Diagram](https://assets.digitalocean.com/articles/alligator/boo.svg "SQLAlchemy 2.0 Architecture Diagram")

Above, the two most significant front-facing portions of SQLAlchemy are the Object Relational Mapper (ORM) and the Core.

Core contains the breadth of SQLAlchemy’s SQL and database integration and description services, the most prominent part of this being the SQL Expression Language.

The SQL Expression Language is a toolkit on its own, independent of the ORM package, which provides a system of constructing SQL expressions represented by composable objects, which can then be “executed” against a target database within the scope of a specific transaction, returning a result set. Inserts, updates and deletes (i.e. DML) are achieved by passing SQL expression objects representing these statements along with dictionaries that represent parameters to be used with each statement.

The ORM builds upon Core to provide a means of working with a domain object model mapped to a database schema. When using the ORM, SQL statements are constructed in mostly the same way as when using Core, however the task of DML, which here refers to the persistence of business objects in a database, is automated using a pattern called unit of work, which translates changes in state against mutable objects into INSERT, UPDATE and DELETE constructs which are then invoked in terms of those objects. SELECT statements are also augmented by ORM-specific automations and object-centric querying capabilities.

Whereas working with Core and the SQL Expression language presents a schema-centric view of the database, along with a programming paradigm that is oriented around immutability, the ORM builds on top of this a domain-centric view of the database with a programming paradigm that is more explicitly object-oriented and reliant upon mutability. Since a relational database is itself a mutable service, the difference is that Core/SQL Expression language is command oriented whereas the ORM is state oriented.

## Otros Recursos

- [Dotfiles](https://github.com/oliverbarreto/.dotfiles) - Mi configuración personal para macOS

- [Homelab](https://github.com/oliverbarreto/homelab) - Configuración y documentación de mi HomeLab de infraestructura, networking, aplicaciones, etc.

- [Boilerplates]() - Templates de distintos tipos (docker, html, iOS, React, Python, etc.)