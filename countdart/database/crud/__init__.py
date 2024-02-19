"""Contains CRUD (Create, Read, Update, Delete) operations
for each database model/schema. These operations are used
to decouple database access from other operations (e.g. api).
Therefore, only operations in this module should access the
database directly. As an underlying framework, sqlmodel is
used for sql requests.
"""
